#!/usr/bin/python
from pymongo import MongoClient
import os


MONGO_HOST = "deluge.lan"
MONGO_PORT = 27017
MONGO_DB = 'yts'

mongo = MongoClient(MONGO_HOST, MONGO_PORT)
yts_db = mongo['yts']
movies_collection = yts_db['movies']

movies = movies_collection.find().limit(250).sort([("_id",-1)])
for movie in movies:
    movies_collection.update_one({"_id": movie['_id']},{"$set":{"downloaded":False}})