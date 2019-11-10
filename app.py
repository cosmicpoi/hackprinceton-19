from flask import Flask, render_template
from newsapi import NewsApiClient
import math
import datetime
import json
import re

app = Flask(__name__)
newsapi = NewsApiClient(api_key='c25beebd44994e62a96ff204cad8043f')
top_topics = ['impeachment', 'vaping', 'election', 'hong kong']
news_source_stats = {
    "buzzfeed":             {'Name':'Buzzfeed','Bias': -68, 'Impact': 3.00, 'Locality': 0.10, 'Sensationalism': 0.96, 'Writing Quality': 0.24, 'Credibility': 0.28, 'Updatedness': 0.70},
    "the-huffington-post":  {'Name':'The Huffington Post','Bias': -61, 'Impact': 5.00, 'Locality': 0.40, 'Sensationalism': 0.98, 'Writing Quality': 0.48, 'Credibility': 0.15, 'Updatedness': 0.92},
    "msnbc":                {'Name':'MSNBC','Bias': -52, 'Impact': 4.60, 'Locality': 0.30, 'Sensationalism': 0.87, 'Writing Quality': 0.76, 'Credibility': 0.28, 'Updatedness': 0.94},
    "the-new-yorker":       {'Name':'The New Yorker','Bias': -48, 'Impact': 4.20, 'Locality': 0.48, 'Sensationalism': 0.56, 'Writing Quality': 0.70, 'Credibility': 0.90, 'Updatedness': 0.86},
    "the-guardian":         {'Name':'The Guardian','Bias': -34, 'Impact': 4.50, 'Locality': 0.18, 'Sensationalism': 0.72, 'Writing Quality': 0.68, 'Credibility': 0.98, 'Updatedness': 0.92},
    "the-washington-post":  {'Name':'The Washington Post','Bias': -25, 'Impact': 5.70, 'Locality': 0.34, 'Sensationalism': 0.43, 'Writing Quality': 0.62, 'Credibility': 0.94, 'Updatedness': 0.78},
    "the-new-york-times":   {'Name':'The New York Times','Bias': -25, 'Impact': 9.70, 'Locality': 0.26, 'Sensationalism': 0.68, 'Writing Quality': 0.90, 'Credibility': 1.00, 'Updatedness': 1.00},
    "politico":             {'Name':'Politico','Bias': -17, 'Impact': 3.60, 'Locality': 0.32, 'Sensationalism': 0.24, 'Writing Quality': 0.76, 'Credibility': 0.92, 'Updatedness': 0.64},
    "bbc-news":             {'Name':'BBC News','Bias': -10, 'Impact': 9.80, 'Locality': 0.52, 'Sensationalism': 0.10, 'Writing Quality': 0.92, 'Credibility': 0.98, 'Updatedness': 0.86},
    "cnn":                  {'Name':'CNN','Bias': -14, 'Impact': 9.50, 'Locality': 0.28, 'Sensationalism': 0.59, 'Writing Quality': 0.84, 'Credibility': 1.00, 'Updatedness': 0.94},
    "nbc-news":             {'Name':'NBC News','Bias': -6, 'Impact': 8.70, 'Locality': 0.26, 'Sensationalism': 0.57, 'Writing Quality': 0.78, 'Credibility': 0.94, 'Updatedness': 0.98},
    "usa-today":            {'Name':'USA Today','Bias': 0, 'Impact': 5.40, 'Locality': 0.22, 'Sensationalism': 0.78, 'Writing Quality': 0.50, 'Credibility': 0.98, 'Updatedness': 0.76},
    "abc-news":             {'Name':'ABC News','Bias': -1, 'Impact': 8.20, 'Locality': 0.10, 'Sensationalism': 0.35, 'Writing Quality': 0.86, 'Credibility': 0.67, 'Updatedness': 0.94},
    "cbs-news":                 {'Name':'CBS News','Bias': 4, 'Impact': 6.50, 'Locality': 0.16, 'Sensationalism': 0.28, 'Writing Quality': 0.94, 'Credibility': 0.94, 'Updatedness': 0.96},
    "the-wall-street-journal": {'Name':'The Wall Street Journal','Bias':    3, 'Impact': 5.90, 'Locality': 0.26, 'Sensationalism': 0.03, 'Writing Quality': 0.94, 'Credibility': 1.00, 'Updatedness': 0.76},
    "bloomberg":            {'Name':'Bloomberg','Bias': 0, 'Impact': 6.80, 'Locality': 0.34, 'Sensationalism': 0.52, 'Writing Quality': 0.90, 'Credibility': 0.98, 'Updatedness': 0.72},
    "the-washington-times":     {'Name':'The Washington Times','Bias':  17, 'Impact': 4.10, 'Locality': 0.10, 'Sensationalism': 0.63, 'Writing Quality': 0.76, 'Credibility': 0.82, 'Updatedness': 0.74},
    "fox-news":                 {'Name':'Fox News','Bias': 39, 'Impact': 9.50, 'Locality': 0.36, 'Sensationalism': 0.89, 'Writing Quality': 0.64, 'Credibility': 0.60, 'Updatedness': 0.99},
    "breitbart-news":       {'Name':'Breitbart News','Bias': 84, 'Impact': 2.00, 'Locality': 0.34, 'Sensationalism': 0.99, 'Writing Quality': 0.28, 'Credibility': 0.04, 'Updatedness': 0.70},
};


@app.route('/')
def main():
    articles = []
    messages = []
    for topic in top_topics:
        articles.append(get_topic(topic))
        messages.append("<a href='/topic/"+topic+"'>topic: <b>"+topic+"</b></a>")

    return render_template('topic.html', article_lists=articles, message_list = messages)

def process_dates(arts):
    articles = arts
    for article in articles:
        article['publishedAt'] = article['publishedAt'][:19]
        mydate = datetime.datetime.strptime(article['publishedAt'], "%Y-%m-%dT%H:%M:%S")
        mydelta = datetime.datetime.utcnow()-mydate
        # for now do this in python, in the future want to do this on jinja side
        if mydelta.days == 0:
            hours = math.floor(mydelta.seconds / 3600)
            if hours == 0:
                minutes = math.floor(mydelta.seconds / 60)
                if minutes == 0:
                    article['timesince'] = str(int(mydelta.seconds)) + " second" + ("s" if mydelta.seconds > 1 else "")
                else:
                    article['timesince'] = str(int(minutes)) + " minute" + ("s" if minutes > 1 else "")
            else: 
                article['timesince'] = str(int(hours)) + " hour" + ("s" if hours > 1 else "")
        else: 
            article['timesince'] = str(mydelta.days) + " day" + ("s" if mydelta.days > 1 else "")
        
    return articles

@app.route('/topic/<topic_name>')
def render_topic(topic_name):
    articles = []
    messages = []

    topic_articles = get_topic(topic_name)
    articles.append(topic_articles)
    messages.append("All articles about <b>"+topic_name+"</b>")

    if(topic_name == "impeachment"):
        left_articles = get_topic(topic_name, alignment="left", sort_by="publishedAt")
        articles.append(left_articles)
        messages.append("Views from the left")
        right_articles = get_topic(topic_name, alignment="right", sort_by="publishedAt")
        articles.append(right_articles)
        messages.append("Views from the right")
    if(topic_name == "vaping"):
        articles_1 = get_topic("vaping AND cdc", alignment="left", sort_by="publishedAt")
        articles.append(articles_1)
        messages.append("keyword: <b>cdc</b>")
        articles_2 = get_topic("vaping AND death", alignment="right", sort_by="publishedAt")
        articles.append(articles_2)
        messages.append("keyword: <b>death</b>")
    if(topic_name == "election"):
        articles_1 = get_topic("election AND bernie sanders", alignment="left", sort_by="publishedAt")
        articles.append(articles_1)
        messages.append("keyword: <b>bernie sanders</b>")
        articles_2 = get_topic("election AND donald trump", alignment="right", sort_by="publishedAt")
        articles.append(articles_2)
        messages.append("keyword: <b>donald trump</b>")
    if(topic_name == "hong kong"):
        articles_1 = get_topic("hong kong AND police", alignment="left", sort_by="publishedAt")
        articles.append(articles_1)
        messages.append("keyword: <b>police</b>")
        articles_2 = get_topic("hong kong AND china", alignment="right", sort_by="publishedAt")
        articles.append(articles_2)
        messages.append("keyword: <b>china</b>")
    
        # return render_template('topic.html', topic=topic_name, articles_list=topic_articles, topics_list=top_topics, articles_left=left_articles, articles_right=right_articles)        
    return render_template('topic.html', topic=topic_name, article_lists=articles, message_list = messages)

@app.route('/query/<my_query>')
def get_query(my_query):
    articles = []
    messages = []

    q = None
    about_result = re.search('about (.+)', my_query)
    if about_result != None:
        my_topic = about_result.group(0).split(" ")[1]
        topic_articles = get_topic(my_topic)
        articles.append(topic_articles)
        messages.append("All articles about <b>"+my_topic+"</b>")

    my_alignment = None
    alignment_result = re.search('from the (left|right)', my_query)
    if alignment_result != None:
        my_alignment = alignment_result.group(0).split(" ")[2]
        alignment_articles = get_topic(my_topic, alignment=my_alignment)
        articles.append(alignment_articles)
        messages.append("All articles about <b>"+my_topic+"</b> from the "+my_alignment)

    return render_template('topic.html', article_lists=articles, message_list = messages, query=my_query)

@app.route('/viz')
def viz():
    return render_template('sourceGraphs.html', topics_list=top_topics)




@app.route('/get_topic/<topic_name>')
def get_topic_view(topic_name):
    return json.dumps(get_topic(topic_name))
def get_topic(topic_name, **kwargs):
    encoded = topic_name.encode("ascii")
    if isinstance(topic_name, str):
        topic_str = topic_name
    else:
        topic_str = encoded


    alignment_list = "cnn,the-new-york-times,bbc-news,the-huffington-post"
    if kwargs.get("alignment") != None:
        if kwargs.get("alignment") == "right":
            alignment_list = "fox-news,the-washington-times,breitbart-news,bloomberg"

    articles = newsapi.get_everything(q=topic_str, language='en', page_size=20, 
        sources=None if 'alignment' in kwargs else alignment_list, 
        sort_by=None if 'sort_by' in kwargs else kwargs.get("sort_by")
        ).get('articles')
    return process_dates(articles)
        


@app.route('/view-source-stats/<query>')
def view_news_source_stats(query):
    data = get_news_source_stats(query)
    source_dict = news_source_stats[query]
    name = source_dict.get('Name')
    return render_template('sourceSpiderGraph.html', source_data=data, source=name)


@app.route('/get-source-stats/<query>')
def get_news_source_stats(query):
    return news_source_stats.get(query)


@app.route('/votes/<query>', methods=['GET'])
def get_votes(query):
    return


@app.route('/target-audience/<query>', methods=['GET'])
def get_target_audience(query):
    return


@app.route('/locality/<query>', methods=['GET'])
def get_locality(query):
    return


@app.route('/reporting-topics/<query>', methods=['GET'])
def get_reporting_topics(query):
    return


if __name__ == '__main__':
    app.run()
