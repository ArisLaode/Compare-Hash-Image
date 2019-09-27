from flask import Flask, request, jsonify
from PIL import Image
from flask_pymongo import PyMongo, pymongo
from datetime import datetime
from flask_script import Manager
from operator import itemgetter
import urllib.request
import io
import imagehash
import json
import certifi
import requests
import sys

app = Flask(__name__)

# DB get id & url
app.config['MONGO_DBNAME'] = 'news'
app.config['MONGO_URI'] = 'mongodb://192.168.20.189:27017/news'
mongo = PyMongo(app)


@app.route("/compare-url", methods=['POST', 'GET'])
def image_compare():
    
    url_image = request.form['url_image']

    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 5.1; rv:43.0) Gecko/20100101 Firefox/43.0')]
    urllib.request.install_opener(opener)
    resp = urllib.request.urlopen(url_image, cafile=certifi.where())

    image_file = io.BytesIO(resp.read())

    imageUrl = Image.open(image_file)
    value_hash = imagehash.phash(imageUrl, hash_size=8)
    img_hash = str(value_hash)

    variabel_1 = []
    variabel_2 = []
    variabel_3 = []

    start = datetime(2000, 1, 1)
    end = datetime(2000, 1, 29)
    
    collection = mongo.db.collection

    hash_mongo = collection.find({"pubdate": {"$gte": start, "$lte": end}}).limit(10)
    
    for i in hash_mongo:

        variabel_1.append(img_hash)
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
                    
                    comparison_dict['url input'] = url_image
                    
                    comparison_list.append(comparison_dict)

    comparison_list = sorted(comparison_list, key=itemgetter("accuracy"), reverse=True)
    print('Compare URL Image Finish')
  
    return json.dumps(comparison_list)

if __name__ == "__main__":
    app.run()