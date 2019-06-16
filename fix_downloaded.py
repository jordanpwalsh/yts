#!/usr/bin/python
from pymongo import MongoClient
import os


MONGO_HOST = "localhost"
MONGO_PORT = 27017
MONGO_DB = 'yts'
DIR = "/synology/jordan/Plex/Movies/YIFFY"

mongo = MongoClient(MONGO_HOST, MONGO_PORT)
yts_db = mongo['yts']
movies_collection = yts_db['movies']

for dir in os.listdir(DIR):
   movie_check = dir.split("(")[0].strip()
   matched_movie = movies_collection.find_one({"title":movie_check})
   if matched_movie:
       print "Marked {} as downloaded".format(matched_movie['title'].encode("utf-8"))
       movies_collection.update_one({"_id":matched_movie['_id']}, {'$set':{"downloaded":True}})