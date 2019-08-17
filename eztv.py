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
import transmissionrpc

MONGO_HOST = "localhost"
MONGO_PORT = 27017
MONGO_DB = 'yts'
EZTv_API = "https://eztv.io/api"


def update_eztv_data(num_pages=-1):
    page = 1
    total = 0
    run = True
    
    mongo = MongoClient(MONGO_HOST, MONGO_PORT)
    eztv_db = mongo['eztv']
    shows_collection = eztv_db['eztv']

    while(run):
        if num_pages != -1 and page > num_pages:
            break
        print colored("Pulling page: {}".format(page), "cyan")
        print colored("Total pulled: {}".format(total), "blue")
        response = requests.get("{}/lget-torrents?limit=50=100&page={}".format(YTS_API, page))
        if response.status_code == 200:
            response_json = response.json()
            try:
                shows = response_json['data']['torrents']
            except KeyError:
                print colored("DONE:", "cyan") + "No shows remaining"
                run = False
            for show in shows:
                movie_title = show['title'].strip().encode("utf-8")
                show_title['downloaded'] = False
                curr_show = shows_collection.find_one({"$or":[{'hash': show['hash']}, {'title': show_title}]})
                if not curr_show:
                    print colored("INSRT:", "yellow") +  "{}".format(show_title)
                    try:
                        shows_collection.insert(movie)
                    except pymongo.errors.DuplicateKeyError:
                        print colored("ERROR: Duplicate hash very close together", "red")
                else:
                    print colored("EXIST:", "green") + "{}".format(show_title)
                    show['downloaded'] = curr_show['downloaded']
                    shows_collection.replace_one({"_id":curr_show['_id']}, show)
                    total +=1
        page += 1


if __name__ == "__main__":
    update_yts_data()