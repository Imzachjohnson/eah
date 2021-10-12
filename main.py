from fastapi import FastAPI
import requests
from fake_useragent import UserAgent
from typing import List
from dataclasses import dataclass
from newspaper import Article
from mongoengine import *
from langdetect import detect
import redis
from rq import Queue
r= redis.Redis()
q = Queue(connection=r)
from methods import ArticleMethods
from flask import Flask

app = Flask(__name__)

# API_URL = "https://api-inference.huggingface.co/models/imzachjohnson/autonlp-spinner-check-16492731"
# headers = {"Authorization": "Bearer api_ovQXHEKfhZEfUBJKXXDKLUcznopcXPHYdg"}

# def query(payload):
# 	response = requests.post(API_URL, headers=headers, json=payload)
# 	return response.json()

# output = query({"inputs": "Nonetheless, it's probably better to be safe than sorry, by getting the most effective germ-killing soap possible."})

# print(output)
connect(
    host="mongodb+srv://zjohnson:coopalex0912@cluster0.2amvb.mongodb.net/eah?retryWrites=true&w=majority"
)
URL_FILTERS = [
    "/category/",
    "/author/",
    ".min.js",
    ".jpg",
    ".png",
    "/wp-content/uploads/",
    "/tag/",
    "/wp-content/plugins/",
    "?wc-ajax=%%Endpoint%%",
    "/wp-admin/",
]


ua = UserAgent()
header = {"User-Agent": str(ua.chrome)}


class WaybackArticle(Document):
    title = StringField(required=True)
    wordcount = IntField(required=True)
    text = StringField()
    original_url = URLField(required=True)
    author = StringField()
    html = StringField(required=False)
    keywords = ListField(required=False)
    language = StringField(required=False)
    topimage = URLField(required=False)
    videos = ListField(required=False)


@dataclass
class WaybackURL:
    url: str
    timecode: str


@dataclass
class Domain:
    domain: str
    wayback_urls: List[WaybackURL]
    articles: List[Article]
    scraped: bool = False


def get_waback_urls(domain: str, limit: int):
    url = f"https://web.archive.org/cdx/search/cdx?url={domain}&matchType=domain&limit={limit}&output=json&filter=statuscode:200&filter=mimetype:text/html&&collapse=urlkey"
    r = requests.get(url, headers=header)
    urls_temp = []
    if r.status_code == 200:
        for url in r.json():
            res = [ele for ele in URL_FILTERS if (ele in url[2])]
            if not bool(res):
                wurl = WaybackURL(url=url[2], timecode=url[1])
                urls_temp.append(wurl)
        return urls_temp
    else:
        return False

def detect_language(text:str):
    return detect(text)



################################################################
# Queue items for processing

def enqueue_get_article(url, min_length=300, max_length=None, language="en", check_spun=False):
    job = q.enqueue(ArticleMethods.get_article, url, min_length,max_length,language,check_spun)
    print(len(q))


@app.route("/test")
def test_task():
    test = enqueue_get_article('https://web.archive.org/web/20170924011835/http://www.footcarefacts.com/consider-set-half-marathon-pace/')
    if test:
        print(test.wordcount)
    return test.text

if __name__ == '__main__':
    app.run()
