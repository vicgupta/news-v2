import os
import schedule
import time
import datetime as dt
from functions import calculate_cosine_similarity
from pocketbaseorm import PocketbaseORM
from dotenv import load_dotenv
load_dotenv()
pb_news = PocketbaseORM(os.getenv("PB_URL"), os.getenv("PB_EMAIL"), os.getenv("PB_PASSWORD"), "news")
pb_news_keywords = PocketbaseORM(os.getenv("PB_URL"), os.getenv("PB_EMAIL"), os.getenv("PB_PASSWORD"), "news_keywords")

def get_all_keywords():
    results = pb_news_keywords.get_items(perPage=999)
    keywords = set()
    for item in results:
        if item.keyword is not None:
            keywords.add(item.keyword)
    return list(keywords)

def fetch_news(query):
    import requests
    url = f"{(os.getenv('SEARCH_URL'))}/search?q={query}&format=json&timerange=1d&categories=news&lang=en"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching news: {response.status_code}")
        return None

def get_post_news():
    count_added = 0
    keywords = get_all_keywords()
    for keyword in keywords:
        print(f"Fetching news for keyword: {keyword}")
        new_news = fetch_news(keyword)
        for item in new_news["results"]:
            print ("*"*120)
            
            if 'publishedDate' in item:
                published_date = dt.datetime.fromisoformat(item['publishedDate'].replace("Z", "+00:00"))
            else:
                published_date = dt.date.today()
            data = {
                "keyword": keyword,
                "title": item["title"],
                "content": item["content"],
                "url": item["url"],
                "date": published_date.strftime('%Y-%m-%d'),
            }
            response = pb_news.add_item(data)
            if response == "Error":
                print(f"- {item['title']}")
            else:
                count_added += 1
                print(f"+ {item['title']}")
    else:
        print(f"No news found for keyword: {keyword}")
    print ("Count: ", count_added)
def deleteYesterdayNews():
    yesterday = dt.date.today() - dt.timedelta(days=1)
    results = pb_news.get_items_with_filter(column_name="date", column_value=str(yesterday) + " 00:00:00", perPage=999)
    for item in results:
        pb_news.delete_id(item.id)

def deleteNews(id):
    print(f"Deleting item {id}")
    pb_news.delete_id(id)

def detectDuplicate():
    results = pb_news.get_items_with_filter(column_name="date", column_value=str(dt.date.today()) + " 00:00:00", perPage=999)
    for i in range (len(results)-1):
        # print (i, results[i].title)
        if calculate_cosine_similarity(results[i].title, results[i+1].title) > 0.7:
            print (results[i].title)
            deleteNews(results[i].id)
		
#schedule.every().day.at("05:00").do(getNews)
while True:
    print (f"Running at {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
	#schedule.run_pending()
    get_post_news()
    detectDuplicate()
    deleteYesterdayNews()
    print ("Sleeping for 60 mins...")
    time.sleep(60 * 60)
    
