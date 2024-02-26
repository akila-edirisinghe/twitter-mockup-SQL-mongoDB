from pymongo import MongoClient
import sys
import os
from pymongo.collation import Collation


#perhaps a try execepy block here
client = MongoClient('mongodb://localhost:{}'.format(sys.argv[2]))

db = client["291db"]

drop = db['tweets'].drop()
        
tweets_collection = db['tweets']

# mongoimport --host "hostname" --port "port" --db "databasename" --collection "collectionName" --file "filePath"
os.system("mongoimport --port {} --db 291db --collection tweets --file {}".format(sys.argv[2],sys.argv[1])) 
tweets_collection.create_index("content", collation = Collation(locale = "en", strength = 4))
tweets_collection.create_index("user.displayname", collation = Collation(locale = "en", strength = 4))
tweets_collection.create_index("user.location", collation = Collation(locale = "en", strength = 4))

