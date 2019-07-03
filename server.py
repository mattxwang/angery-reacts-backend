import base64, os, requests, time
from bs4 import BeautifulSoup
from flask import Flask
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS

app = Flask(__name__)
api = Api(app)
CORS(app)

genius_api_key = os.environ["GENIUS_API_KEY"]
genius_api_website = "https://api.genius.com"

spotify_client_id = os.environ["SPOTIFY_CLIENT_ID"]
spotify_client_secret = os.environ["SPOTIFY_CLIENT_SECRET"]
spotify_client_b64 = str(base64.b64encode((spotify_client_id + ":" + spotify_client_secret).encode()))[2::][:-1] # the [2::] removes the leading b', the [:-1] the last '
spotify_token_url = "https://accounts.spotify.com/api/token"
spotify_playlist_url = "https://api.spotify.com/v1/playlists/"
spotify_playlist_url_append = "/tracks?fields=items(track(name, artists))"

lyrics_parser = reqparse.RequestParser()
lyrics_parser.add_argument('title')
lyrics_parser.add_argument('artist')

playlist_parser = reqparse.RequestParser()
playlist_parser.add_argument('playlist')

def request_song_info(song_title, artist_name):
    headers = {'Authorization': 'Bearer ' + genius_api_key}
    data = {'q': song_title + ' ' + artist_name}
    response = requests.get(genius_api_website + '/search', data=data, headers=headers)
    return response

def scrape_song_url(url):
    page = requests.get(url)
    html = BeautifulSoup(page.text, 'html.parser')
    [h.extract() for h in html('script')]
    lyrics = html.find('div', class_='lyrics').get_text()
    return lyrics

def get_info_from_song(song_title, artist_name):
    response = request_song_info(song_title, artist_name)
    json = response.json()
    remote_song_info = None
    for hit in json['response']['hits']:
        if artist_name.lower() in hit['result']['primary_artist']['name'].lower():
            remote_song_info = hit
            break

    if remote_song_info:
        song_url = remote_song_info['result']['url']
        lyrics = scrape_song_url(song_url)
        return {'title': remote_song_info['result']['title'], 'artist': remote_song_info['result']['primary_artist']['name'], 'img_url': remote_song_info['result']['song_art_image_url'], 'lyrics': lyrics}
    else:
        return {'error': "song not found!"}

def request_spotify_token():
    headers = {'Authorization': 'Basic ' +  spotify_client_b64 }
    data = {'grant_type': 'client_credentials'}
    url = spotify_token_url
    response = requests.post(url, data=data, headers=headers)
    return response

def get_spotify_playlist(playlist_id, token):
    headers = {'Authorization': 'Bearer ' + token}
    url = spotify_playlist_url + playlist_id + spotify_playlist_url_append
    response = requests.get(url, headers=headers)
    response = response.json()
    if 'error' in response:
        print("error: " + response['error'])
        return False
    else:
        return response

def get_and_parse_playlist(playlist_id, token):
    playlist_obj = get_spotify_playlist(playlist_id, token)
    if not playlist_obj:
        return {'error': "error getting playlist info"}
    songs = []
    for song in playlist_obj["items"]:
        print("Getting " + song['track']['name'] + " by " + song['track']['artists'][0]['name'])
        songs.append(get_info_from_song(song['track']['name'], song['track']['artists'][0]['name']))
    return {'songs': songs}

class GetSong(Resource):
    def get(self):
        return {'usage': 'usage is incorrect! please use a POST request!'}
    def post(self):
        args = lyrics_parser.parse_args()
        return get_info_from_song(args['title'], args['artist'])

class GetPlaylist(Resource):
    def get(self):
        return {'usage': 'usage is incorrect! please use a POST request!'}
    def post(self):
        args = playlist_parser.parse_args()
        get_token = request_spotify_token()
        print(get_token.json())
        if 'error' in get_token.json():
            return({'error': "error getting token!"})
        token = get_token.json()['access_token']
        return get_and_parse_playlist(args['playlist'], token)

api.add_resource(GetSong, '/lyrics')
api.add_resource(GetPlaylist, '/playlist')

if __name__ == '__main__':
    app.run(debug=True)