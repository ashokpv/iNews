import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from datetime import datetime, timedelta
# Below libraries are for similarity matrices using sklearn
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import pairwise_distances

from pymongo import MongoClient

user_recommend = 'user_recommendation'
categories = [
    "Automobiles",
    "Business",
    "Celebrity",
    "Cricket",
    "Entertainment",
    "Health",
    "Latest",
    "Lifestyle",
    "Money",
    "Movies",
    "Politics",
    "Science",
    "Sports",
    "StartUps",
    "Technology",
    "Travel",
    "World",
    "stocks"
]
client = MongoClient("mongodb://localhost:27017/")
db = client["iNews"]
fetch_news_date = datetime.utcnow() - timedelta(days=10)


class Recommend_Based_on_Likes():

    def fetch_users(self, category):
        users = db["user_activity"].find({"news_ids." + category: {
            "$exists": True}})
        if users.count():
            news_articles = self.fetch_news_based_on_title(category)
            for user in users:
                news_ids = user.get("news_ids").get(category)
                final_recommendation_ids = list()
                for id in news_ids:
                    news_title = db["news_articles"].find_one({"_id": id})
                    print("Fetching for title", news_title["title"])
                    news_articles_temp, news_articles_latest = \
                        self.combine_title_with_datafram(
                            news_title["title"], news_articles)
                    news_articles_temp = \
                        self.parse_stop_words_and_lemmatize(news_articles_temp)
                    tf_idf_vect = self.tf_idf_vect(news_articles_temp)
                    recommendation_ids, recommendation_news = self.fetch_recommended_news_ids(
                        5,
                        tf_idf_vect,
                        news_articles_latest)
                    if id in recommendation_ids:
                        recommendation_ids.remove(id)
                    print(recommendation_news)
                    if recommendation_ids:
                        final_recommendation_ids = final_recommendation_ids + \
                                                   recommendation_ids
                print(category, user['user_id'])
                if final_recommendation_ids:
                    db["user_recommendation"].update(
                        {"user_id": user["user_id"]},
                        {"$set": {"user_id": user["user_id"],
                                  "recommendation." + category:
                                      final_recommendation_ids}}
                        , upsert=True
                    )

    def fetch_news_based_on_title(self, category):
        df = pd.DataFrame(
            list(db["news_articles"].find(
                {"category": category,
                 "datetime": {"$gt": fetch_news_date}})))
        news_articles = df[df['title'].apply(lambda x: len(x.split()) > 5)]
        news_articles.sort_values('title', inplace=True, ascending=False)
        duplicated_articles_series = news_articles.duplicated('title',
                                                              keep=False)
        news_articles = news_articles[~duplicated_articles_series]
        news_articles.isna().sum()
        news_articles.index = range(news_articles.shape[0])
        return news_articles

    def combine_title_with_datafram(self, news_title, news_articles_df):
        top_row = pd.DataFrame(
            {'title': [news_title]})
        # Concat with old DataFrame and reset the Index.
        news_articles = pd.concat([top_row, news_articles_df]).reset_index(
            drop=True)
        news_articles_temp = news_articles.copy()
        return news_articles_temp, news_articles

    def parse_stop_words_and_lemmatize(self, news_articles_temp):
        stop_words = set(stopwords.words('english'))
        for i in range(len(news_articles_temp["title"])):
            string = ""
            for word in news_articles_temp["title"][i].split():
                word = ("".join(e for e in word if e.isalnum()))
                word = word.lower()
                if not word in stop_words:
                    string += word + " "
            news_articles_temp.at[i, "title"] = string.strip()
        lemmatizer = WordNetLemmatizer()
        for i in range(len(news_articles_temp["title"])):
            string = ""
            for w in word_tokenize(news_articles_temp["title"][i]):
                string += lemmatizer.lemmatize(w, pos="v") + " "
            news_articles_temp.at[i, "title"] = string.strip()
        return news_articles_temp

    def tf_idf_vect(self, news_articles_temp):
        tfidf_headline_vectorizer = TfidfVectorizer(min_df=0)
        tfidf_headline_features = tfidf_headline_vectorizer.fit_transform(
            news_articles_temp['title'])
        return tfidf_headline_features

    def tfidf_based_model(self, row_index, num_similar_items,
                          tfidf_headline_features, news_articles):
        couple_dist = pairwise_distances(tfidf_headline_features,
                                         tfidf_headline_features[row_index])
        indices = np.argsort(couple_dist.ravel())[0:num_similar_items]
        df = pd.DataFrame({
            'headline': news_articles['title'][indices].values,
            'ids': news_articles['_id'][indices].values,
            'Euclidean similarity with the queried article': couple_dist[
                indices].ravel()})
        return df.iloc[1:, ]

    def fetch_recommended_news_ids(self, number_of_recommendations,
                                   tfidf_headline_features, news_articles):
        df = self.tfidf_based_model(0, number_of_recommendations,
                                    tfidf_headline_features,
                                    news_articles)
        print(df.headline.tolist())
        print(df.ids.tolist())
        return df.ids.tolist(), df.headline.tolist()


if __name__ == '__main__':
    for category in categories:
        print("For Category", category)
        Recommend_Based_on_Likes().fetch_users(category)
