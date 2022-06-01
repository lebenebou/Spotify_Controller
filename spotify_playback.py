
import spotipy.util as util
from requests import get as rget
import json

import os
current_dir = os.path.dirname(__file__)
os.chdir(current_dir)

def refresh_token():

    # refreshes spotify access token, token is saved in .cache-user file
    print("Attempting to refresh token...", end="\r")

    with open("credentials.json", "r") as f:

        creds = json.load(f)
        my_client_id = creds["client_id"]
        my_client_secret = creds["client_secret"]
    
    redirect_url = "http://localhost:8888/callback"
    scopes = "user-read-currently-playing"

    util.prompt_for_user_token("user", scopes, my_client_id, my_client_secret, redirect_url)
    # this function saves the token into .cache-user file
    # it also returns the token itself, this functionality is not used here

    print("Token successfuly refreshed.")

def update_playback_info():

    # updates the current spotify playing track info and dumps into a json file: song_info.json
    # if errors occur, the following format is dumped: {"error_message: <error_type>"}
    response = " _NONE_ "

    print("Getting playback info...", end="\r")

    with open(".cache-user", "r") as f:
        token = json.load(f)["access_token"]

    header = {"Authorization": f"Bearer {token}"}
    url = "https://api.spotify.com/v1/me/player/currently-playing"

    try:
        response = rget(url, headers=header)
    except:

        print("Playback info unavailable, not connected to the internet")

        with open("song_info.json", "w") as f:
            json.dump({"error_message":"no_internet"}, f)

        return
    
    if response.status_code==204:

        print("Playback info unavailable, Spotify closed or not playing.")

        with open("song_info.json", "w") as f:
            json.dump({"error_message":"not_playing"}, f)

    elif response.status_code==401:

        print("Playback info unreachable, token may have expired.")

        with open("song_info.json", "w") as f:
            json.dump({"error_message":"expired_token"}, f)

    elif response.json()["item"]==None:
        
        print("Playback info unavailable, Spotify closed or not playing.")

        with open("song_info.json", "w") as f:
            json.dump({"error_message":"not_playing"}, f)

    elif response.json()["currently_playing_type"]=="ad":

        print("An advertisement is being played.")

        with open("song_info.json", "w") as f:
            json.dump({"error_message":"ad"}, f)

    else:
        print("Successfully got playback info.", end="\r")

        with open("song_info.json", "w") as f:
            json.dump(response.json(), f)

def fetched_song_info():

    # returns json object of dumped song info
    with open("song_info.json", "r") as f:

        return json.load(f)

if __name__=="__main__":

    # this showcases what this file can do
    os.system("cls")
    
    update_playback_info()
    song_info = fetched_song_info()

    if len(song_info) < 2:

        if song_info["error_message"]=="expired_token":
            refresh_token()
            update_playback_info()

        else:
            exit()

    song_info = fetched_song_info()

    print("\n")
    print("Track ID:", song_info["item"]["id"])
    print("Song Title:", song_info["item"]["name"])
    print("Album Title:", song_info["item"]["album"]["name"])
    print("Artists:", ", ".join(artist["name"] for artist in song_info["item"]["artists"]))
    print("Progress Percentage:", int(100*(song_info["progress_ms"]/song_info["item"]["duration_ms"])))
    print("Artwork URL:", song_info["item"]["album"]["images"][0]["url"])