import feedparser
from bs4 import BeautifulSoup
from dateutil import parser as date_parser
from pymongo import MongoClient
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import sys
import os
sys.path.append(os.path.abspath("/home/bharath/Desktop/iNews/static/"))
from metadata import Metadata

client = MongoClient("mongodb://localhost:27017/")
db = client["iNews"]
rss_feeds_headlines = ['https://www.indiatoday.in/rss/home',
                       'https://economictimes.indiatimes.com/rssfeedstopstories.cms',
                       'http://rss.cnn.com/rss/edition.rss']
limit = 12 * 3600 * 1000
categories = ["Money", "Technology", "space", "Entertainment", "sport",
              "Motorsport", "Travel", "latest"]


def get_images(html):
    soup = BeautifulSoup(html)
    images = []
    for img in soup.findAll('img'):
        images.append(img.get('src'))
    return images


def datetime_convert(date_string):
    date_time = date_parser.parse(date_string, tzinfos={"CDT": "UTC-5"})
    return date_time


def parse_economic_times(rss, collection, category=None):
    resp = requests.get(rss)
    tree = ET.ElementTree(ET.fromstring(resp.content))
    economic_times = list()
    root = tree.getroot()
    for item in root.findall('./channel/item'):
        final_dict = {"source": "Economic Times"}
        if category:
            final_dict["category"] = category
        for child in item:
            if child.tag == 'pubDate':
                final_dict["datetime"] = datetime_convert(child.text)
            elif child.tag == 'image':
                final_dict["images"] = [child.text]

            else:
                final_dict[child.tag] = child.text
        economic_times.append(final_dict)

    try:
        db[collection].insert_many(economic_times)
    except Exception as e:
        print(str(e))


def parse_indiatoday(feed_entries, collection, category=None):
    indiatoday_news_list = list()

    for entry in feed_entries:
        data_feed = {"title": entry.title_detail.value,
                     "link": entry.link,
                     "images": get_images(entry.description),
                     "datetime": datetime_convert(entry.published),
                     "source": "India Today"}
        if category:
            data_feed["category"] = category
        indiatoday_news_list.append(data_feed)
    try:
        db[collection].insert_many(indiatoday_news_list)
    except Exception as e:
        print(str(e))


def parse_cnn(feed_entries, collection, category=None):
    cnn_news_list = []
    for entry in feed_entries:

        data_feed = {"title": entry.title_detail.value,
                     "link": entry.link,
                     "images": [],
                     "source": "CNN"}
        try:
            data_feed["datetime"] = datetime_convert(entry.published)
        except:
            data_feed["datetime"] = datetime.utcnow()
        try:
            for media in entry.media_content:
                if media["medium"] == "image":
                    data_feed["images"].append(media["url"])
        except:
            try:
                for media in entry.media_thumbnail:
                    data_feed["images"].append(media["url"])
            except:
                continue
        if category:
            data_feed["category"] = category
        cnn_news_list.append(data_feed)
    if cnn_news_list:
        try:
            db[collection].insert_many(cnn_news_list)
        except Exception as e:
            print(str(e))
    else:
        print("empty list in %s", category)


def parse_ndtv(feed_entries, collection, category=None):
    ndtv_news_list = []
    for entry in feed_entries:
        data_feed = {"title": entry.title_detail.value,
                     "link": entry.link,
                     "description": entry.summary,
                     "images": [entry.storyimage],
                     "datetime": datetime_convert(entry.published),
                     "source": "Ndtv"}

        if category:
            data_feed["category"] = category
        ndtv_news_list.append(data_feed)
    if ndtv_news_list:
        try:
            db[collection].insert_many(ndtv_news_list)
        except Exception as e:
            print(str(e))


def process_category_news():
    for source, value in Metadata.rss_feeds.items():
        for category, rss_feed_link in value.items():
            print(category)
            print(rss_feed_link)
            if 'economictimes' in rss_feed_link:
                parse_economic_times(rss_feed_link, "news_articles",
                                     category=category)

            if 'cnn' in rss_feed_link:
                feed = feedparser.parse(rss_feed_link)
                feed_entries = feed.entries
                parse_cnn(feed_entries, "news_articles", category=category)
            elif 'indiatoday' in rss_feed_link:
                feed = feedparser.parse(rss_feed_link)
                feed_entries = feed.entries
                parse_indiatoday(feed_entries, "news_articles",
                                 category=category)

            elif source == "ndtv":
                feed = feedparser.parse(rss_feed_link)
                feed_entries = feed.entries
                parse_ndtv(feed_entries, "news_articles", category=category)


def process():
    for rss in rss_feeds_headlines:
        if 'economictimes' in rss:
            parse_economic_times(rss, "news_headlines")
        feed = feedparser.parse(rss)
        feed_entries = feed.entries
        if 'cnn' in rss:
            parse_cnn(feed_entries, "news_headlines")
        elif 'indiatoday' in rss:
            parse_indiatoday(feed_entries, "news_headlines")


if __name__ == '__main__':
    process_category_news()
    process()
