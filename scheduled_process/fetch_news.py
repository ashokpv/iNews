import feedparser
from bs4 import BeautifulSoup
from dateutil import parser as date_parser
from pymongo import MongoClient
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

client = MongoClient("mongodb://localhost:27017/")
db = client["iNews"]
rss_feeds_headlines = ['https://www.indiatoday.in/rss/home',
                       'https://economictimes.indiatimes.com/rssfeedstopstories.cms'
    , 'http://rss.cnn.com/rss/edition.rss']
limit = 12 * 3600 * 1000


def get_images(html):
    soup = BeautifulSoup(html)
    images = []
    for img in soup.findAll('img'):
        images.append(img.get('src'))
    return images


def datetime_convert(date_string):
    date_time = date_parser.parse(date_string)
    return date_time


def parse_economic_times(rss):
    resp = requests.get(rss)

    tree = ET.ElementTree(ET.fromstring(resp.content))
    economic_times = list()
    root = tree.getroot()
    for item in root.findall('./channel/item'):
        final_dict = {"source": "Economic Times"}
        for child in item:
            if child.tag == 'pubDate':
                final_dict["datetime"] = datetime_convert(child.text)
            elif child.tag == 'image':
                final_dict["images"] = [child.text]

            else:
                final_dict[child.tag] = child.text
        economic_times.append(final_dict)
    db["news_headlines"].insert_many(economic_times)


def parse_indiatoday(feed_entries):
    indiatoday_news_list = list()

    for entry in feed_entries:
        data_feed = {"title": entry.title_detail.value,
                     "link": entry.link,
                     "images": get_images(entry.description),
                     "datetime": datetime_convert(entry.published),
                     "source": "India Today"}
        indiatoday_news_list.append(data_feed)
    db["news_headlines"].insert_many(indiatoday_news_list)


def parse_cnn(feed_entries):
    cnn_news_list = []
    for entry in feed_entries:

        data_feed = {"title": entry.title_detail.value,
                     "link": entry.link,
                     "source": "CNN"}
        try:
            data_feed["datetime"] = datetime_convert(entry.published)
        except:
            data_feed["datetime"] = datetime.utcnow()
        try:
            for media in entry.media_content:
                if media["medium"] == "image":
                    data_feed["images"] = [media["url"]]
        except:
            continue
        cnn_news_list.append(data_feed)
    db["news_headlines"].insert_many(cnn_news_list)


def process():
    for rss in rss_feeds_headlines:
        if 'economictimes' in rss:
            parse_economic_times(rss)
        feed = feedparser.parse(rss)
        feed_entries = feed.entries
        if 'cnn' in rss:
            parse_cnn(feed_entries)
        elif 'indiatoday' in rss:
            parse_indiatoday(feed_entries)


if __name__ == '__main__':
    process()
