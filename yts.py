#!/usr/bin/python
import requests
import json
import urllib
from pymongo import MongoClient
from time import sleep
from base64 import b64encode, b64decode

MONGO_HOST = "deluge.lan"
MONGO_PORT = 27017
MONGO_DB = 'yts'
YTS_API = "https://yts.am/api/v2"

#Template args: hash, url encoded movie name
MAGNET_TEMPLATE = 'magnet:?xt=urn:btih:{}&dn={}&tr=udp://open.demonii.com:1337/announce&tr=udp://tracker.openbittorrent.com:80&tr=udp://tracker.coppersurfer.tk:6969&tr=udp://glotorrents.pw:6969/announce&tr=udp://tracker.opentrackr.org:1337/announce&tr=udp://torrent.gresille.org:80/announce&tr=udp://p4p.arenabg.com:1337&tr=udp://tracker.leechers-paradise.org:6969'





if __name__ == "__main__":
    page = 1
    run = True
    
    mongo = MongoClient(MONGO_HOST, MONGO_PORT)
    yts_db = mongo['yts']
    movies_collection = yts_db['movies']

    response = requests.get("{}/list_movies.json?limit=50&page={}".format(YTS_API, page))
    if response.status_code == 200:
        response_json = response.json()
        movies = response_json['data']['movies']
        print type(movies)
        for movie in movies:
            print "Inserting: {}".format(movie['title'])
            for torrent in movie['torrents']:
                if torrent['quality'] == "720p":
                    url_encoded_movie_name = urllib.quote_plus(movie['title'])
                    movie['magnet_url'] = MAGNET_TEMPLATE.format(torrent['hash'], url_encoded_movie_name)
                    movie.pop("torrents")
            movies_collection.insert(movie)





