#!/usr/bin/python
import requests
import json
import urllib
import pymongo
from pymongo import MongoClient
from time import sleep
from base64 import b64encode, b64decode
from termcolor import colored
from pprint import pprint
from deluge_client import DelugeRPCClient as Deluge

MONGO_HOST = "deluge.lan"
MONGO_PORT = 27017
MONGO_DB = 'yts'
YTS_API = "https://yts.am/api/v2"

#Template args: hash, url encoded movie name
MAGNET_TEMPLATE = 'magnet:?xt=urn:btih:{}&dn={}&tr=udp://open.demonii.com:1337/announce&tr=udp://tracker.openbittorrent.com:80&tr=udp://tracker.coppersurfer.tk:6969&tr=udp://glotorrents.pw:6969/announce&tr=udp://tracker.opentrackr.org:1337/announce&tr=udp://torrent.gresille.org:80/announce&tr=udp://p4p.arenabg.com:1337&tr=udp://tracker.leechers-paradise.org:6969'


def update_yts_data(num_pages=-1):
    page = 1
    total = 0
    run = True
    
    mongo = MongoClient(MONGO_HOST, MONGO_PORT)
    yts_db = mongo['yts']
    movies_collection = yts_db['movies']

    while(run):
        print colored("Pulling page: {}".format(page), "cyan")
        print colored("Total pulled: {}".format(total), "blue")
        response = requests.get("{}/list_movies.json?limit=50&page={}".format(YTS_API, page))
        if response.status_code == 200:
            response_json = response.json()
            try:
                movies = response_json['data']['movies']
            except KeyError:
                print colored("DONE:", "cyan") + "No movies remaining"
                run = False
            for movie in movies:
                if not movie.has_key("torrents"):
                    continue
                for torrent in movie['torrents']:
                    if torrent['quality'] == "720p":
                        movie_title = movie['title'].strip().encode("utf-8")
                        url_encoded_movie_name = urllib.quote_plus(movie_title)
                        movie['magnet_url'] = MAGNET_TEMPLATE.format(torrent['hash'], url_encoded_movie_name)
                        movie['torrent_hash'] = str(torrent['hash'])
                        movie['downloaded'] = False
                        if not movies_collection.find_one({"$or":[{'torrent_hash': movie['torrent_hash']}, {'title': movie_title}]}):
                            print colored("INSRT:", "yellow") +  "{} - {}".format(movie['year'], movie_title)
                            try:
                                movies_collection.insert(movie)
                            except pymongo.errors.DuplicateKeyError:
                                print colored("ERROR: Duplicate hash very close together", "red")
                        else:
                            print colored("EXIST:", "green") + "{} - {}".format(movie['year'], movie_title)
                        total +=1
        page += 1
                
    


if __name__ == "__main__":
    #update_yts_data()

    mongo = MongoClient(MONGO_HOST, MONGO_PORT)
    yts_db = mongo['yts']
    movies_collection = yts_db['movies']

    deluge = Deluge("localhost", 58846)
    deluge.connect()
    

    movies = movies_collection.find({"downloaded": False})
    for movie in movies:
        print movie['title']


    





