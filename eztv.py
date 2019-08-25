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
import transmissionrpc
import re

MONGO_HOST = "localhost"
MONGO_PORT = 27017
MONGO_DB = 'yts'
EZTV_API = "https://eztv.io/api"

MOVIEDB_API_KEY="6b830dfc3adea7a73458188602bf1b0a"
MOVIEDB_REQUEST_FORMAT="https://api.themoviedb.org/3/find/{}}?api_key=" + MOVIEDB_API_KEY + "&language=en-US&external_source=imdb_id"


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
        response = requests.get("{}/get-torrents?limit=50&page={}".format(EZTV_API, page))
        if response.status_code == 200:
            response_json = response.json()
            try:
                shows = response_json['torrents']
            except KeyError:
                print colored("DONE:", "cyan") + "No shows remaining"
                run = False
            for show in shows:
                show_title = show['title'].strip().encode("utf-8")
                show['downloaded'] = False
                curr_show = shows_collection.find_one({"$or":[{'hash': show['hash']}, {'title': show_title}]})
                if not curr_show:
                    print colored("INSRT:", "yellow") +  "{}".format(show_title)
                    try:
                        shows_collection.insert(show)
                    except pymongo.errors.DuplicateKeyError:
                        print colored("ERROR: Duplicate hash very close together", "red")
                else:
                    print colored("EXIST:", "green") + "{}".format(show_title)
                    show['downloaded'] = curr_show['downloaded']
                    shows_collection.replace_one({"_id":curr_show['_id']}, show)
                total +=1
        page += 1

def scan_shows():
    SHOW_GRP=1
    SEP_GROUP=2
    SEASON_GROUP=3
    EPISODE_GROUP=4

    count=0
    mongo = MongoClient(MONGO_HOST, MONGO_PORT)
    eztv_db = mongo['eztv']
    shows_collection = eztv_db['eztv']


    print colored("MESSG:Scanning & Parsing Shows...", "cyan")
    shows = shows_collection.find()
    for show in shows:
        print "Testing {}".format(show['title'].encode("utf-8"))
        result = re.match(r"(^[\w\s-]+)(S([0-9])*E([0-9]*))",show['title'].encode("utf-8"))
        
        try:
            print "Show: {} - Season: {} Episode: {}".format(result.group(SHOW_GRP),result.group(SEASON_GROUP), result.group(EPISODE_GROUP))
            show['show_title'] = result.group(SHOW_GRP)
            show['season'] = result.group(SEASON_GROUP)
            show['episode'] = result.group(EPISODE_GROUP)
            show['parsed'] = True
            shows_collection.save(show)
        except:
            print colored("Couln't parse.","red")
        count+=1
    print "Count: {}".format(count)

def enqueue_transmission():
    max_items=5
    mongo = MongoClient(MONGO_HOST, MONGO_PORT)
    eztv_db = mongo['eztv']
    shows_collection = eztv_db['eztv']

    BASE_DOWNLOAD_PATH='/synology/jordan/Downloads/incoming_tv'
    download_candidates = shows_collection.find({"parsed": True}).sort({"seeds": -1})
    for candidate in download_candidates:
        print download_candidates['show_title']







if __name__ == "__main__":
    #update_eztv_data(1)
    #scan_shows()