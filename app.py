from flask import Flask, request, render_template, jsonify
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup
import pymongo
from dotenv import load_dotenv, dotenv_values
import os, logging
load_dotenv()
logging.basicConfig(filename="scrapper.log", level=logging.INFO)

app = Flask(__name__)

@app.route('/', methods=["GET"])
def homepage():
    return render_template('index.html')

@app.route('/images', methods=["POST", "GET"])
def index():
    if request.method == "POST":
        try:
            query = request.form['query'].replace(" ", "")

            user_agent = request.headers.get('User-Agent', 'unknown device')
            client = pymongo.MongoClient(os.getenv("MONGO_URI"))
            db = client["image_scrap"]
            query_col = db["user_queries"]

            query_data = {
                "query": query,
                "device": user_agent
            }
            query_col.insert_one(query_data)

            headers = {"User-Agent": user_agent}
            response = requests.get(f"https://www.google.co.in/search?sca_esv=c75784e51e2fff17&q={query}&udm=2")
            soup = BeautifulSoup(response.content, "html.parser")
            image_tags = soup.find_all("img")
            del image_tags[0]  
            all_images = {}
            for index, image_tag in enumerate(image_tags):
                image_url = image_tag["src"]
                all_images[index] = image_url
            
            return render_template("result.html", fetched_data=all_images)
        
        except Exception as e:
            logging.error(e)
            return "Something went wrong"
    else:
        return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
