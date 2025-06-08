import os

from pocketbaseorm import PocketbaseORM
from dotenv import load_dotenv
load_dotenv()
pb_news = PocketbaseORM(os.getenv("PB_URL"), os.getenv("PB_EMAIL"), os.getenv("PB_PASSWORD"), "news")

def delete_all_news():
    print("Deleting all news items...")
    results = pb_news.get_items(perPage=999)
    for item in results:
        pb_news.delete_id(item.id)
    print("All news items deleted.")