import requests
import os
import psycopg2
from datetime import datetime

def getHelp():
    text = "!ptt list (取得以訂閱看板)\n!ptt add <board> <keyword> (新增訂閱)\n!ptt cancel <board> <keyword> (取消訂閱)"
    return text

def getSubList():
    DATABASE_URL = os.environ['DATABASE_URL'] 
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    SQL_order = "SELECT board,keyword from pttsubscribe;"
    cursor.execute(SQL_order)

    text = "已訂閱看板及關鍵字\n"
    data = []
    while True:
        temp = cursor.fetchone()
        if temp:
            data.append(temp)
        else:
            break
    
    data.sort(key= lambda x:x[0]) #sort list of tuple by board
    for i in data:
        text += i[0] + ":" + i[1] + "\n"
    
    return text

def addKeyword(board, keyword):
    url = "https://www.ptt.cc/bbs/" + board + "/index.html"
    header = {"cookie":"over18=1"}
    response = requests.get(url,headers=header)
    if response.status_code == 404:
        return "無此看板 請重新輸入"
    
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    SQL_order = "INSERT INTO pttSubscribe (board, keyword, date) VALUES(%s,%s,%s) RETURNING sub_id;"
    cursor.execute(SQL_order,(board,keyword,datetime.now().strftime("%Y/%m/%d")))
    sub_id = cursor.fetchone()[0]
    conn.commit() #only create, delete, update need to use conn.commit()
    cursor.close()
    conn.close()

    if sub_id:
        return "新增成功"
    else:
        return "新增失敗"
    
def deleteKeyword(board, keyword):
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    SQL_order = "DELETE FROM pttsubscribe WHERE board = %s AND keyword = %s;"
    cursor.execute(SQL_order,(board,keyword))
    rows_deleted = cursor.rowcount
    conn.commit() #only create, delete, update need to use conn.commit()
    cursor.close()
    conn.close()

    if rows_deleted:
        return "刪除成功"
    else:
        return "查無此訂閱資訊 刪除失敗"
    
    
