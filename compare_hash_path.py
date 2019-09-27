from flask import Flask, request, jsonify
from PIL import Image
from flask_pymongo import PyMongo
from datetime import datetime
from operator import itemgetter
import urllib.request
import io
import imagehash
import json
import certifi
import requests
import os

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'news'
app.config['MONGO_URI'] = 'mongodb://127.0.0.1:27017/news'
mongo = PyMongo(app)


@app.route("/compare-path", methods=['POST', 'GET'])
def image_compare():
    variabel_4 = []

    path_image = request.files['path_image']
    string_path = str(path_image)
    replace_path_image = string_path.replace('<FileStorage: ', '').replace('>', '')

    imagePath = Image.open(path_image)
    value_hash = imagehash.phash(imagePath, hash_size=8)
    path_hash = str(value_hash)

    variabel_1 = []
    variabel_2 = []
    variabel_3 = []


    start = datetime(2000, 1, 1)
    end = datetime(2000, 1, 29)
    
    collection = mongo.db.collection
    hash_mongo = collection.find({"pubdate": {"$gte": start, "$lte": end}}).limit(10)
    
    for i in hash_mongo:

        variabel_1.append(path_hash)
        variabel_2.append(i['hash'])
        variabel_3.append(i['url'])
        
        comparison_list = []
        
        for j in variabel_1:
            for k in variabel_2:
                for l in variabel_3:
                
                    comparison_dict = {}
                    
                    hash1 = j
                    hash2 = k

                    dec1 = int(hash1, 16)
                    dec2 = int(hash2, 16)
                    bin1 = bin(dec1)
                    bin2 = bin(dec2)
                    xor_bin = int(bin1, 2) ^ int(bin2, 2)
                    distance = bin(xor_bin).count("1")
                    divider = len(hash1) * 4
                    
                    result =  1 - (distance / float(divider))
                    
                    comparison_dict['accuracy'] = float(result)
                    comparison_dict['url mongo'] = l
                    comparison_dict['path input'] = replace_path_image
                    
                    comparison_list.append(comparison_dict)

    comparison_list = sorted(comparison_list, key=itemgetter("accuracy"), reverse=True)

    print('Compare Path Image Finish')
  
    return json.dumps(comparison_list)

if __name__ == "__main__":
    app.run()