import os, requests
from bs4 import BeautifulSoup
from flask import Flask
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS

app = Flask(__name__)
api = Api(app)
CORS(app)

genius_api_key = os.environ["GENIUS_API_KEY"]
genius_api_website = "https://api.genius.com"
parser = reqparse.RequestParser()
parser.add_argument('title')
parser.add_argument('artist')

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

class GetSong(Resource):
    def get(self):
        return {'usage': 'usage is incorrect! please use a POST request!'}
    def post(self):
        args = parser.parse_args()
        response = request_song_info(args['title'], args['artist'])
        json = response.json()
        remote_song_info = None
        for hit in json['response']['hits']:
            if args['artist'].lower() in hit['result']['primary_artist']['name'].lower():
                remote_song_info = hit
                break

        if remote_song_info:
            # print(remote_song_info)
            song_url = remote_song_info['result']['url']
            lyrics = scrape_song_url(song_url)
            return {'title': remote_song_info['result']['title'], 'artist': remote_song_info['result']['primary_artist']['name'], 'img_url': remote_song_info['result']['song_art_image_url'], 'lyrics': lyrics}
        else:
            return {'error': "song not found!"}

api.add_resource(GetSong, '/lyrics')

if __name__ == '__main__':
    app.run(debug=True)