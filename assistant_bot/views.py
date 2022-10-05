import os

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
 
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage, QuickReply, QuickReplyButton, MessageAction, PostbackAction, PostbackEvent

from .thsr import TimeTable, SelectStart, SelectEnd
from .ptt import getHelp, getSubList, addKeyword, deleteKeyword
import ast
 
line_bot_api = LineBotApi(os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")) #get token from heroku config var
parser = WebhookParser(os.environ.get("LINE_CHANNEL_SECRET")) #get secret from heroku config var
 
 
@csrf_exempt
def callback(request):
 
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
 
        try:
            events = parser.parse(body, signature)  # 傳入的事件
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()
 
        for event in events:
            if isinstance(event, MessageEvent):  # 如果有訊息事件
                if event.message.text == "!thsr":
                    line_bot_api.reply_message(  # 回復傳入的訊息文字
                        event.reply_token,
                        TextSendMessage(text=TimeTable("Tainan","Zuoying"))
                    )
                elif event.message.text == "!ptt help": #獲得ptt 指令幫助
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=getHelp())
                    )
                elif event.message.text == "!ptt list": #獲得已訂閱看板
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=getSubList())
                    )
                elif "!ptt add" in event.message.text:
                    tokens = event.message.text.split(" ")
                    board = tokens[2]
                    keyword = tokens[3]
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=addKeyword(board,keyword))
                    )
                elif "!ptt cancel" in event.message.text:
                    tokens = event.message.text.split(" ")
                    board = tokens[2]
                    keyword = tokens[3]
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=deleteKeyword(board,keyword))
                    )
                elif event.message.text == "!uid":
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=str(event.source.user_id))
                    )
                else:
                    line_bot_api.reply_message(  # 回復傳入的訊息文字
                        event.reply_token,
                        TextSendMessage(text=event.message.text)
                    )

            elif isinstance(event, PostbackEvent):  # 如果有postback事件
                query = ast.literal_eval(event.postback.data)
                if query["action"] == "SelectStart": #若從選單點選高鐵 要求輸入起程站
                    line_bot_api.reply_message(event.reply_token,SelectStart())
                elif query["action"] == "SelectEnd": #點選完起程站 要求輸入到達站
                    line_bot_api.reply_message(event.reply_token,SelectEnd(query["Start"]))
                elif query["action"] == "Check": #點選到達站 開始查詢
                    line_bot_api.reply_message(event.reply_token,TextSendMessage(text = TimeTable(query["Start"],query["End"])))
        return HttpResponse()
    else:
        return HttpResponseBadRequest()