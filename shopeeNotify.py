import requests
import os
from apscheduler.schedulers.blocking import BlockingScheduler
from linebot import LineBotApi
from linebot.models import TextSendMessage

sched = BlockingScheduler()
line_bot_api = LineBotApi(os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")) #get token from heroku config var

def crawl_shelf():
    url = "https://shopee.tw/api/v4/search/search_items?by=pop&entry_point=ShopByPDP&limit=30&match_id=5843773&newest=0&order=desc&page_type=shop&scenario=PAGE_OTHERS&version=2"
    response = requests.get(url)
    data = response.json()

    #data["items"][0]["item_basic"]["name"]
    for items in data["items"]: 
        if "Bellemond" in items["item_basic"]["name"]:
            line_bot_api.push_message(os.environ.get("uid_ycliang"),TextSendMessage(text="Bellemond上架了")) #send notify to user
            #print("Bellemond上架了")

def crawl_stock():
    urls = "https://shopee.tw/api/v2/item/get?itemid=3376224269&shopid=5843773"
    headers = {"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"}
    response = requests.get(urls,headers=headers)
    data = response.json()
    data["item"]["models"][0]["stock"]
    for items in data["item"]["models"]:
        if "Air4" in items["name"]:
            if ("上質" in items["name"] or "書寫" in items["name"])and items["stock"] > 0:
                line_bot_api.push_message(os.environ.get("uid_ycliang"),TextSendMessage(text=f"{items['name']}有貨了")) #send notify to user
                #print(f"{items['name']}有貨了")


@sched.scheduled_job('interval', minutes=3, id="MyJob") #
def notify():
    requests.get("https://yclinebot.herokuapp.com") #wake up idle dyno
    #crawl_shelf()
    crawl_stock()

sched.start()