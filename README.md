# angery-reacts-backend
basically, a very quick python flask backend that forwards the genius API so I don't expose secret keys!

this might eventually contain a spotify backend wrapper too - we'll see how the react frontend plays out


## development setup 

You'll need Python 3 and pip (which is bundled) to install and run the server, which uses `flask` and `flask-restful`. Note that the genius API key is stored in an environment variable called `GENIUS_API_KEY`; it should be the client access token from [the Genius API](https://genius.com/api-clients).

```
pip3 install -r requirements.txt
python3 server.py
```