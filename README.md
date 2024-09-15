# RYMTopSongsPlaylist
Create a top 40 playlist of given artist based on RateYourMusic ratings

## Usage :
 - You need to input the artist's RYM URL
 - The script will ask you if the detected name is correct (to prevent search issues)
 - You'll need to connect to your Spotify account if it's not already the case
 - The playlist is created
  
![example of usage of script](https://i.imgur.com/GtlWtof.png)

## Installation : 
You can either download the code or one of the releases that already contains the **ChromeDriver** (up to date as of 15 September 2024) for Selenium usage.

If you choose to download the code then download the chromedriver that match your OS and CPU architecture and specify the PATH of chromedriver in main.py

### Spotify API :
You'll need to register a new app in order to use Spotify's API.
Go to [this link](https://developer.spotify.com/dashboard/create), then choose a app name and a app description. 

For Redirect URIs, enter ***http://localhost:4356*** and select Web API.

![example of creating spotify app](https://i.imgur.com/xAnYm1q.png)

Enter the new creds in main.py.