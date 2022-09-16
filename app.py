from flask import Flask, request, url_for, session, redirect, jsonify, render_template
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import json
import pandas as pd

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = "Secret_Key"
app.config['SESSION_COOKIE_NAME'] = 'Cookie Name'
TOKEN_INFO = "token_info"

@app.route('/')
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/redirect')
def redirectPage():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect('/getPlaylist')

@app.route('/getPlaylist', methods=["GET", "POST"])
def getPlaylist():
    if request.method == 'GET':
        try:
            token_info = get_token()
        except:
            print("user not logged in")
            return redirect("/")

        sp = spotipy.Spotify(auth=token_info['access_token'])
        playlist_names = []

        playlist_info = sp.current_user_playlists(limit=50, offset=0)
        for playlist_info in playlist_info["items"]:
            playlist_names.append(playlist_info["name"])
        return render_template("playlist.html", names = playlist_names)
    else:
        try:
            token_info = get_token()
        except:
            print("user not logged in")
            return redirect("/")
        sp = spotipy.Spotify(auth=token_info['access_token'])
        playlist_info = sp.current_user_playlists(limit=50, offset=0)
        playlist_name = request.form.get('playlist')
        empty_playlist_id = ""
        for playlist_info in playlist_info["items"]:
            if playlist_name in playlist_info.values():
                playlist_id = empty_playlist_id + playlist_info["id"]
        song_names = []
        iter = 0
        while True:
            playlist_items = sp.playlist_items(playlist_id, limit=100, offset=iter*100)["items"]
            for track_data in playlist_items:
                track_access = track_data["track"]
                song_names.append(track_access["name"])
            iter += 1
            titles = []
            for idx, item in enumerate(playlist_items):
                track = item["track"]
                title = track["name"] + " - " + track["artists"][0]["name"]
                titles += [title]
            if len(playlist_items) < 100:
                break

        df = pd.DataFrame(titles, columns=[f"Song Names, - {playlist_name}"])
        df.to_csv('songs.csv', index=False)
        return render_template("tracks.html", songs = song_names, totals = len(song_names), chosen_playlist = playlist_name)

def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        raise "exception"
    now = int(time.time())

    is_expired = token_info['expires_at'] - now < 60
    if (is_expired):
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
    return token_info

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id = 'CLIENT_ID',
        client_secret = 'CLIENT_SECRET',
        redirect_uri = url_for('redirectPage', _external=True),
        scope="playlist-read-private"
    )