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
        current_news = fetch_news(keyword)
        if current_news and "results" in current_news:
            for item in current_news["results"]:
                # print ("*"*120)
                existing_items = pb_news.get_items_with_filter(column_name="url", column_value=item["url"], perPage=1)
                if existing_items:
                    # print (f"Item already exists: {item['title']}")
                    for existing_item in existing_items:
                        # print (f"Comparing with existing item: {existing_item.title}")
                        similarity = calculate_cosine_similarity(item["title"], existing_item.title)
                        if similarity > 0.8:  # If similarity is above 0.8, consider it a duplicate
                            # print(f"- {item['title']}")
                            break
                        else:
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
                            count_added += 1
                            response = pb_news.add_item(data)
                            if response == "Error":
                                pass
                                # print(f"Error adding item: {item['title']}")
                            else:
                                # print(f"+ {item['title']}")
                                pass
        else:
            print(f"No news found for keyword: {keyword}")
    print ("Count: ", count_added)

#schedule.every().day.at("05:00").do(getNews)
while True:
    print (f"Running at {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
	#schedule.run_pending()
    get_post_news()
    
    print ("Sleeping for 30 mins...")
    time.sleep(60 * 30)
    
