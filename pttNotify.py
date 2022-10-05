import os
import psycopg2
import requests
import urllib
from bs4 import BeautifulSoup
from apscheduler.schedulers.blocking import BlockingScheduler
from linebot import LineBotApi
from linebot.models import TextSendMessage

sched = BlockingScheduler()
line_bot_api = LineBotApi(os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")) #get token from heroku config var

def formatPushString(board,keyword,title,href):
    s = "有新文章!\n訂閱看板:{}\n關鍵字:{}\n{}\n{}"
    return s.format(board,keyword,title,"https://www.ptt.cc" + href)

@sched.scheduled_job('interval', minutes=5, id="MyJob") #
def crawlPtt(): 
    requests.get("https://yclinebot.herokuapp.com") #wake up idle dyno
    DATABASE_URL = os.environ['DATABASE_URL']  #the last character is \n, so discard it
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()

    SQL_order = "SELECT board,keyword,date from pttsubscribe;"
    cursor.execute(SQL_order)
    data = []
    while True: #store database data in list
        temp = cursor.fetchone()
        if temp:
            data.append(temp)
        else:
            break

    for record in data: #crawl every record
        board = record[0]
        keyword = record[1]
        lastDateDB = record[2]

        url = "https://www.ptt.cc/bbs/" + board + "/index.html"
        header = {"cookie":"over18=1"}
        response = requests.get(url,headers=header)
        soup = BeautifulSoup(response.text,"html.parser")

        title_list = []
        href_list = []
        result = soup.select("div.title a")
        for i in result: #get all title
            title_list.append(i.text)
            href_list.append(i["href"]) 
        
        notifyIndex = 0
        count=0
        correspond = []
        correspond_href = []
        lastPostTime = ""
        for i in range(len(title_list)):
            if keyword in title_list[i]:
                count+=1
                correspond.append(title_list[i])
                correspond_href.append(href_list[i])
                header = {"cookie":"over18=1"}
                article_response = requests.get("https://www.ptt.cc" + href_list[i],headers=header)
                article_soup = BeautifulSoup(article_response.text,"html.parser")
                info = article_soup.find_all("span","article-meta-value") #get post time
                date = info[3].text

                #print("correspond article:",title_list[i],href_list[i],date)

                if date != lastDateDB:
                    lastPostTime = date
                else:
                    notifyIndex = count
                    #print("the article is the latest")

        if(notifyIndex != len(correspond)):
            for i in range(notifyIndex,len(correspond)):
                #print("need to notify:",correspond[i])
                line_bot_api.push_message(os.environ.get("uid_ycliang"),TextSendMessage(text=formatPushString(board,keyword,correspond[i],correspond_href[i]))) #send notify to user
            #print(lastPostTime) #update lastday to database(write lastDate to DB)

            SQL_order = "UPDATE pttsubscribe SET date = %s WHERE board = %s AND keyword = %s;"
            cursor.execute(SQL_order,(lastPostTime,board,keyword))
            conn.commit()
            
    cursor.close()
    conn.close()


sched.start()