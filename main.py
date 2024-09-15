from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import base64
import requests
import json 
import oauthlib.oauth2
import string
import random
import os
import http.server
import socketserver
import threading
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import webbrowser

CHROMEDRIVERPATH = "ENTER CHROMEDRIVER PATH" # PATH to Chrome's driver
SPOTIFYAPIURL = "https://api.spotify.com/v1"
SPOTIFYAPITOKEN = "ENTER YOUR TOKEN"
SPOTIFYAPICLIENTID = "ENTER YOUR CLIENTID"
SPOTIFYHEADERS = {}

class Handler(http.server.SimpleHTTPRequestHandler): # handler for web server
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.server.data = self.path
        self.wfile.write(b'<html><body><script>window.close();</script></body></html>')
        return

def getRYMSongs(artist):
    service = Service(CHROMEDRIVERPATH)
    options = Options()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # options.add_experimental_option("detach", True) # prevent closing
    options.add_argument('--headless=new') #run in background
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(f"https://rateyourmusic.com/charts/top/song/all-time/a:{artist}")
    try :
        driver.find_element(By.CLASS_NAME, "fc-cta-consent").click()
    except Exception:
        pass

    query = driver.find_elements(By.CLASS_NAME, "song")
    songs = []
    counter = 0 # add a counter to parse iteration
    for i in query:
        counter += 1
        if counter > 40: # make sure that we dont go over 40 songs (might be the case with some artists idk whty (example : kendrick lamar))
            break
        a = i.find_element(By.CLASS_NAME, "ui_name_locale")
        song = a.find_element(By.CLASS_NAME, "ui_name_locale_original")
        songs.append(song.get_attribute("innerHTML"))
    driver.close()
    return songs

def formatArtistName(artist):
    if "-" in artist:
        newArtist = artist.replace("-", ' ')
        correctArtist = input(f"Artist name detected : {newArtist} \nIs it right ? (y/n)")
        if correctArtist != "y":
            artist = input("Enter artist name correctly : \n")
        else:
            artist = newArtist.title()
    else:
        correctArtist = input(f"Artist name detected : {artist} \nIs it right ? (y/n)")
        if correctArtist != "y":
            artist = input("Enter artist name correctly : \n")
        else:
            artist = artist.title()
    return artist

def getAuthSpotify():
    client = oauthlib.oauth2.WebApplicationClient(SPOTIFYAPICLIENTID)
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))
    url = client.prepare_request_uri( # first token request (code)
        "https://accounts.spotify.com/authorize?",
        redirect_uri="http://localhost:4356",
        scope=["playlist-modify-public", "playlist-modify-private"],
        state=state
    )

    with socketserver.TCPServer(("localhost", 4356), Handler) as httpd: # web server to get token access
        threading.Thread(target=lambda: webbrowser.open(url)).start()
        httpd.handle_request()
    data = httpd.data
    code = data[7:].split("&state")[0]
    if data.split("&state=")[1] != state:
        raise ValueError
   
    base = str(base64.b64encode(bytes((SPOTIFYAPICLIENTID + ":" + SPOTIFYAPITOKEN), "utf-8")))[2:][:-1]

    r = requests.post("https://accounts.spotify.com/api/token", # second token request (access_token)
        data = {'code': code, "redirect_uri": "http://localhost:4356", "grant_type": "authorization_code"},
        headers={"Authorization": "Basic " + base, "content-type": "application/x-www-form-urlencoded"})

    return r.json()["access_token"]

def searchForSong(track, artist): 
    if SPOTIFYHEADERS == {}:
        SPOTIFYHEADERS["Authorization"]  = "Bearer " + getAuthSpotify()
    client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIFYAPICLIENTID, client_secret=SPOTIFYAPITOKEN)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    query = f"track:{track} artist:{artist}"
    results = sp.search(q=query, type='track', limit=1)
    if results['tracks']['items']:
        track_id = results['tracks']['items'][0]['id']
        return track_id
    else:
        return None

def getAndUpdatePlaylist(tracks, artist):
    if SPOTIFYHEADERS == {}:
        SPOTIFYHEADERS["Authorization"]  = "Bearer " + getAuthSpotify()

    uris = []

    for i in tracks:
        a = searchForSong(i, artist)
        if a != None:
            uris.append(f"spotify:track:{a}")

    dict_request = {"uris" : uris}
    userid = requests.get(SPOTIFYAPIURL + "/me/", headers=SPOTIFYHEADERS).json()['id']
    data={"name": f"{artist}'s Top 40 Songs", "description": "according to RYM ratings", "public": False}
    r = requests.post(SPOTIFYAPIURL + f"/users/{userid}/playlists", headers=SPOTIFYHEADERS, data=json.dumps(data))
    id = r.json()["id"]
    r = requests.post(SPOTIFYAPIURL + f"/playlists/{id}/tracks", headers=SPOTIFYHEADERS, data=json.dumps(dict_request))
    return r.json()
    
def main ():
    artist = input("Enter RYM artist URL : \n").split("/") #get artist url
    artist = artist[len(artist)-1]
    tracks = getRYMSongs(artist)
    getAndUpdatePlaylist(tracks, formatArtistName(artist))

main()