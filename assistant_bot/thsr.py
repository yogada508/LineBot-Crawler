import requests
from hyper.contrib import HTTP20Adapter
import json
from datetime import datetime,timedelta

from linebot.models import  TextSendMessage, QuickReply, QuickReplyButton, PostbackAction


def TimeTable(DepartureStation,DestinationStation):
    
    url = 'https://www.thsrc.com.tw/tw/TimeTable/Search'
    headers = {
    ':authority': 'www.thsrc.com.tw',
    'x-requested-with': 'XMLHttpRequest',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    ':method': 'POST',
    ':path': '/TimeTable/Search',
    ':scheme': 'https' 
    }
    StationName ={"台北":"TaiPei","南港":"NanGang","新竹":"XinZhu","左營":"ZuoYing","台南":"TaiNan","台中":"TaiZhong","板橋":"BanQiao",
    "桃園":"TaoYuan","苗栗":"MiaoLi","彰化":"ZhangHua","雲林":"YunLin","嘉義":"JiaYi"}

    dt = datetime.now()
    dt = dt + timedelta(hours=8)
    queryDate = dt.strftime("%Y/%m/%d") #convert datetime(Date) to str
    queryTime = dt.strftime("%H:%M") #convert datetime(Time) to str

    form_data = {
    'SearchType': 'S',
    'Lang': 'TW',
    'StartStation': StationName[DepartureStation],
    'EndStation': StationName[DestinationStation],
    'OutWardSearchDate': queryDate,
    'OutWardSearchTime': queryTime,
    'ReturnSearchDate': queryDate,
    'ReturnSearchTime': queryTime,
    'DiscountType': ''
    }

    s = requests.session()
    s.mount('https://', HTTP20Adapter())
    r = s.post(url,data=form_data,headers=headers)

    timetable = r.json()

    count = 0
    content = "從" + DepartureStation + "到" + DestinationStation + "的車次為\n"
    for train in timetable["data"]["DepartureTable"]["TrainItem"]:
        departTime_dt = datetime.strptime(train["DepartureTime"],"%H:%M") #str to datetime
        if departTime_dt.hour*60+departTime_dt.minute > dt.hour*60+dt.minute:
            content += "No." + train["TrainNumber"] + "\n出發:" + train["DepartureTime"] + " 抵達:" + train["DestinationTime"] + "\n歷經:" + train["Duration"] +"\n\n"
            count += 1
            if count==10:
                break
    return content

def SelectStart():
    text_message = TextSendMessage(text='請選擇起程站',
                    quick_reply=QuickReply(items=[
                        QuickReplyButton(action=PostbackAction(label="左營", displayText="左營",data= '{"action":"SelectEnd","Start":"左營"}')),
                        QuickReplyButton(action=PostbackAction(label="台南", displayText="台南",data= '{"action":"SelectEnd","Start":"台南"}')),
                        QuickReplyButton(action=PostbackAction(label="嘉義", displayText="嘉義",data= '{"action":"SelectEnd","Start":"嘉義"}')),
                        QuickReplyButton(action=PostbackAction(label="雲林", displayText="雲林",data= '{"action":"SelectEnd","Start":"雲林"}')),
                        QuickReplyButton(action=PostbackAction(label="彰化", displayText="彰化",data= '{"action":"SelectEnd","Start":"彰化"}')),
                        QuickReplyButton(action=PostbackAction(label="台中", displayText="台中",data= '{"action":"SelectEnd","Start":"台中"}')),
                        QuickReplyButton(action=PostbackAction(label="苗栗", displayText="苗栗",data= '{"action":"SelectEnd","Start":"苗栗"}')),
                        QuickReplyButton(action=PostbackAction(label="新竹", displayText="新竹",data= '{"action":"SelectEnd","Start":"新竹"}')),
                        QuickReplyButton(action=PostbackAction(label="桃園", displayText="桃園",data= '{"action":"SelectEnd","Start":"桃園"}')),
                        QuickReplyButton(action=PostbackAction(label="板橋", displayText="板橋",data= '{"action":"SelectEnd","Start":"板橋"}')),
                        QuickReplyButton(action=PostbackAction(label="台北", displayText="台北",data= '{"action":"SelectEnd","Start":"台北"}')),
                        QuickReplyButton(action=PostbackAction(label="南港", displayText="南港",data= '{"action":"SelectEnd","Start":"南港"}')),
                    ]))
    return text_message

def SelectEnd(StartStation):
    text_message = TextSendMessage(text='請選擇到達站',
                    quick_reply=QuickReply(items=[
                        QuickReplyButton(action=PostbackAction(label="左營", displayText="左營",data= '{"action":"Check","End":"左營","Start"'+':"'+StartStation+'"}')),
                        QuickReplyButton(action=PostbackAction(label="台南", displayText="台南",data= '{"action":"Check","End":"台南","Start"'+':"'+StartStation+'"}')),
                        QuickReplyButton(action=PostbackAction(label="嘉義", displayText="嘉義",data= '{"action":"Check","End":"嘉義","Start"'+':"'+StartStation+'"}')),
                        QuickReplyButton(action=PostbackAction(label="雲林", displayText="雲林",data= '{"action":"Check","End":"雲林","Start"'+':"'+StartStation+'"}')),
                        QuickReplyButton(action=PostbackAction(label="彰化", displayText="彰化",data= '{"action":"Check","End":"彰化","Start"'+':"'+StartStation+'"}')),
                        QuickReplyButton(action=PostbackAction(label="台中", displayText="台中",data= '{"action":"Check","End":"台中","Start"'+':"'+StartStation+'"}')),
                        QuickReplyButton(action=PostbackAction(label="苗栗", displayText="苗栗",data= '{"action":"Check","End":"苗栗","Start"'+':"'+StartStation+'"}')),
                        QuickReplyButton(action=PostbackAction(label="新竹", displayText="新竹",data= '{"action":"Check","End":"新竹","Start"'+':"'+StartStation+'"}')),
                        QuickReplyButton(action=PostbackAction(label="桃園", displayText="桃園",data= '{"action":"Check","End":"桃園","Start"'+':"'+StartStation+'"}')),
                        QuickReplyButton(action=PostbackAction(label="板橋", displayText="板橋",data= '{"action":"Check","End":"板橋","Start"'+':"'+StartStation+'"}')),
                        QuickReplyButton(action=PostbackAction(label="台北", displayText="台北",data= '{"action":"Check","End":"台北","Start"'+':"'+StartStation+'"}')),
                        QuickReplyButton(action=PostbackAction(label="南港", displayText="南港",data= '{"action":"Check","End":"南港","Start"'+':"'+StartStation+'"}')),
                    ]))
    return text_message
