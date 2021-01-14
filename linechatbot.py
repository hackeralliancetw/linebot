

Purpose = 'Used' # Used or Test
IDE = 'Local' # Colab  or Local
LineTestAccount = 'Team' # Test or Team

# if IDE == 'Colab':
  # !pip install line-bot-sdk
  # !pip install flask-ngrok
  # !pip install boto3
  # !pip install -U azure-cosmosdb-table
  # !pip install azure-cosmos
  # !mkdir temp
  # !mkdir temp/image
  # !mkdir temp/video
  # !mkdir temp/audio

# import firebase package
from azure.cosmosdb.table.tableservice import TableService
from azure.cosmosdb.table.models import Entity
from azure.cosmos import exceptions, CosmosClient, PartitionKey

# import line package
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,UnfollowEvent,TemplateSendMessage, ImagemapSendMessage, PostbackEvent, ImageSendMessage,
    ImageMessage, VideoMessage, AudioMessage, LocationMessage, StickerMessage, FlexSendMessage, BubbleContainer, CarouselContainer,
    AudioSendMessage, StickerSendMessage, LocationSendMessage, VideoSendMessage
)
from linebot.models.events import (
    FollowEvent
)
import boto3
from flask import Flask, request, abort, make_response
# from flask_ngrok import run_with_ngrok
import os
import cv2
import json
import random

import datetime
import pandas as pd
import flask

# for AI module
from AIModule import algorithm_top
from CNN import CNN_model_ini
from Yolo import Yolo_model_ini
cnn = CNN_model_ini()
yolo = Yolo_model_ini()


# from environment import keys
AWS_ACCESS_KEY_ID = 'AKIAIFPZYEKVPVQLVFOA'
AWS_SECRET_ACCESS_KEY ='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'
s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

# 從S3 抓取 Module py,  要確認 h5 所放的位置
if IDE == 'Colab':
  s3_client.download_file('fish-save-file', 'AIModule/Colab/AIModule.py', 'AIModule.py')
  s3_client.download_file('fish-save-file', 'AIModule/Colab/AIModule2.py', 'AIModule2.py')
# elif IDE == 'Local':
#   s3_client.download_file(+'fish-save-file', 'AIModule/Local/AIModule.py', 'AIModule.py')
#   s3_client.download_file('fish-save-file', 'AIModule/Local/AIModule2.py', 'AIModule2.py')

# from AI Module import algorithm_top

#  連結 Azure  資料表
table_service = TableService(account_name='fishstorages', account_key='gXRRnoVs3RxAcziHSa6xVWncDk1qaYRqQnmbHTemns8DpJwsE7IRpn22GKhupeAFjBeXkhXbWFanogRTDb8w7A==')

# Line相關 key
if LineTestAccount == 'Team':
  line_bot_api = LineBotApi("oZLqMBoifHLLQGKlojr2DXd6H3YvtDIYqx5ZFzf3x25xUmoNPcHBOwgYvpx4spcBSZYSSCctI0vMWgq+nE9F6T56wI/Tw7uLciWaeezCFnlV7MQJyNx11GT+6+e9ELRpYZIfMbfQDg++P5mmm33vKQdB04t89/1O/w1cDnyilFU=")
  handler = WebhookHandler("6de1ad9fe8a4aa3acbbcc945217b04ec")
elif LineTestAccount == 'Test':
  line_bot_api = LineBotApi("ecd1/lTYxKvSGvjAZeEqji/95ho6n/V18u4M2/763UBY/0+A2fu+FZRbscj/lLHBugLUP8venMBuVIpAzb6jWMfejT6ATNpn4CzQ1Mb+Asmmxb65KphCBGxNjl6gmZRN7Te+jDUF7oepmOvOrNIzYAdB04t89/1O/w1cDnyilFU=")
  handler = WebhookHandler("d06801ea25738846597eaf10d44e2316")

# Step 2 : 伺服器準備

from flask import session
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = str(time.time)
# if IDE == 'Colab':
# run_with_ngrok(app)

# code copy from line > Synopsis
@app.route("/", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # print(body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

# 建立要傳送的訊息list, 並傳送給user
def Send_Messages(event,reply_messages_list):
  reply_messages = []
  for i in reply_messages_list:
    for j in i:
      if j == 'TextSendMessage':
        if i["TextSendMessage"] != "":
          print("[LineBot] : TextSendMessage")
          reply_messages.append(TextSendMessage(i["TextSendMessage"]))

      if j == 'TextWithQuickReply':
        if i["TextWithQuickReply"] != "":
          print("[LineBot] : TextWithQuickReply")
          reply_json = json.loads(i["TextWithQuickReply"])
          reply_messages.append(TextSendMessage.new_from_json_dict(reply_json))

      if j == 'TemplateWithQuickReply':
        if i["TemplateWithQuickReply"] != "":
          print("[LineBot] : TemplateWithQuickReply")
          reply_json = json.loads(i["TemplateWithQuickReply"])
          reply_messages.append(TextSendMessage.new_from_json_dict(reply_json))

      if j == 'TemplateSendMessage':
        if i["TemplateSendMessage"] != "":
          print("[LineBot] : TemplateSendMessage")
          reply_json = json.loads(i["TemplateSendMessage"])
          reply_messages.append(TemplateSendMessage.new_from_json_dict(reply_json))

      if j == 'ImageSendMessage':
        if i["ImageSendMessage"] !="":
          print("[LineBot] : ImageSendMessage")
          reply_json = json.loads(i["ImageSendMessage"])
          reply_messages.append(ImageSendMessage.new_from_json_dict(reply_json))

      if j == 'AudioSendMessage':
        if i["AudioSendMessage"] !="":
          print("[LineBot] : AudioSendMessage")
          reply_json = json.loads(i["AudioSendMessage"])
          reply_messages.append(AudioSendMessage.new_from_json_dict(reply_json))

      if j == 'VideoSendMessage':
        if i["VideoSendMessage"] !="":
          print("[LineBot] : VideoSendMessage")
          reply_json = json.loads(i["VideoSendMessage"])
          reply_messages.append(VideoSendMessage.new_from_json_dict(reply_json))

      if j == 'LocationSendMessage':
        if i["LocationSendMessage"] !="":
          print("[LineBot] : LocationSendMessage")
          reply_json = json.loads(i["LocationSendMessage"])
          reply_messages.append(LocationSendMessage.new_from_json_dict(reply_json))

      if j == 'StickerSendMessage':
        if i["StickerSendMessage"] !="":
          print("[LineBot] : StickerSendMessage")
          reply_json = json.loads(i["StickerSendMessage"])
          reply_messages.append(StickerSendMessage.new_from_json_dict(reply_json))

      if j == 'ImagemapSendMessage':
        if i["ImagemapSendMessage"] !="":
          print("[LineBot] : ImagemapSendMessage")
          reply_json = json.loads(i["ImagemapSendMessage"])
          reply_messages.append(ImagemapSendMessage.new_from_json_dict(reply_json))

      if j == 'FlexSendMessage':
        if i["FlexSendMessage"] !="":
          print("[LineBot] : FlexSendMessage")
          reply_json = json.loads(i["FlexSendMessage"])
          bubbleContainer = BubbleContainer.new_from_json_dict(reply_json)
          reply_messages.append(FlexSendMessage(alt_text="hello", contents=bubbleContainer))

      if j == 'CarouselContainer':
        if i["CarouselContainer"] !="":
          print("[LineBot] : CarouselContainer")
          reply_json = json.loads(i["CarouselContainer"])
          carouselContainer = CarouselContainer.new_from_json_dict(reply_json)
          reply_messages.append(FlexSendMessage(alt_text="hello", contents=carouselContainer))

      if j == 'QuickReply':
        if i["QuickReply"] != "":
          print("[LineBot] : QuickReply")
          reply_messages.append(TextSendMessage(i["QuickReply"]))

      if j == 'RichMenuId':
        if i["RichMenuId"] != "":
          print("[LineBot] : RichMenuId")
          user_profile_dict = eval(str(event))
          line_bot_api.link_rich_menu_to_user(user_profile_dict["source"]["userId"], i["RichMenuId"])

      if j == 'RichMenuUnlock':
        if i["RichMenuUnlock"] == "Close":
          print("[LineBot] : RichMenuUnlock")
          user_profile_dict = eval(str(event))
          line_bot_api.unlink_rich_menu_from_user(user_profile_dict["source"]["userId"])
  print('[LineBot] 回應訊息list : ',reply_messages)
  if len(reply_messages) > 0:
    line_bot_api.reply_message(event.reply_token, reply_messages)

# 透過文字訊息去DB爪取回應訊息
def Get_Reply_Messages(MessageType,UserMessages):
  # print('get reply messages')
  tasks = table_service.query_entities(MessageType, filter="PartitionKey eq '"+UserMessages+"'")
  reply_messages_list = []
  # print(MessageType,UserMessages,len(tasks.items))
  if len(tasks.items) != 0:
    for task in tasks:
      dict2 = {}
      for i in sorted(task.keys(),reverse=True):
        dict2[i]=task[i]
      reply_messages_list.append(dict2)
  return reply_messages_list

def Get_Reply_Messages_OtherEvent(MessageType):
  # print('get reply messages')
  tasks = table_service.query_entities(MessageType, filter="PartitionKey eq 'Default Reply'")
  reply_messages_list = []
  if len(tasks.items) != 0:
    for task in tasks:
      dict2 = {}
      for i in sorted(task.keys(),reverse=True):
        dict2[i]=task[i]
      reply_messages_list.append(dict2)
  return reply_messages_list

def Get_Reply_Messages_list(MessageType,UserMessages_list):
  reply_messages_list = []
  for i in UserMessages_list:
    tasks = table_service.query_entities(MessageType, filter="PartitionKey eq '"+i+"'")
    if len(tasks.items) != 0:
      for task in tasks:
        dict2 = {}
        for i in sorted(task.keys(),reverse=True):
          dict2[i]=task[i]
        reply_messages_list.append(dict2)
    if Purpose == 'Test':
      dict3 = {'TextSendMessage':i}
      reply_messages_list.append(dict3)
  return reply_messages_list

# 儲存檔案至S3
# def Save_File_S3(filename,path):
#   filepath = 'temp/'+path+'/'+filename
#   if path == "image":                                                           # 比例縮圖
#     pic = cv2.imread(filepath)
#     h = 500
#     math1 = h/pic.shape[0]
#     pic = cv2.resize(pic, (int(pic.shape[1]*math1),h),interpolation=cv2.INTER_AREA)
#     cv2.imwrite(filepath, pic)
#   s3_client.upload_file(filepath,'fish-save-file', path+'/'+filename )
#   os.remove(filepath)

#  儲存檔案至 Locol
def Save_UserFile(filename,extension):
  message_content = line_bot_api.get_message_content(filename)
  path = "temp/image"
  if extension == 'mp3':
    path = "temp/audio"
  elif extension == "mp4":
    path = 'temp/video'
  image_file_name= path+'/'+filename+'.'+extension
  with open(image_file_name, 'wb') as fd:
    for chunk in message_content.iter_content():
        fd.write(chunk)
  # if path == "jpg":                                                           # 比例縮圖
  #   pic = cv2.imread(image_file_name)
  #   h = 500
  #   math1 = h/pic.shape[0]
  #   pic = cv2.resize(pic, (int(pic.shape[1]*math1),h),interpolation=cv2.INTER_AREA)
  #   cv2.imwrite(image_file_name, pic)

#  對應所輸入的文字是否在白名單中
def Check_MessageList_In_FishNameTable(list):
  returnlist = []
  for i in list:
    tasks = table_service.query_entities('FishNameMaping', filter="RowKey eq '"+i+"'", select='PartitionKey')
    if len(tasks.items) != 0:
      for task in tasks:
        # print('check : '+task.PartitionKey)
        returnlist.append(task.PartitionKey)
    else:
      if Purpose == 'Used':
        # print('check : 沒有這條魚資料')
        returnlist.append('None')
      elif Purpose == 'Test':
        returnlist.append(i)
  return returnlist

def Check_MessageText_In_FishNameTable(Message):
  returntext = ""
  tasks = table_service.query_entities('FishNameMaping', filter="RowKey eq '"+Message+"'", select='PartitionKey')
  if len(tasks.items) != 0:
    for task in tasks:
      returntext = task.PartitionKey
  else:
    # print('check : 沒有這條魚資料')
    returntext = 'None'
  return returntext

# 儲存文字訊息
def Save_Event_Log(event,fishname='None'):
  user_profile = line_bot_api.get_profile(event.source.user_id)
  user_profile_dict = eval(str(user_profile))                                   # line_bot_api.get_profile 轉 str 再轉成 dict
  dict_con = {'PartitionKey':str(event.source.user_id), 'RowKey':str(event.timestamp), 'MessageType':"", 'Description':"", "User_Name" : user_profile_dict["displayName"]}
  if event.type == "message":
    # 文字訊息  {"events":[{"type":"message","replyToken":"a0baaf5753744fc9847745f45c7b4485","source":{"userId":"Ud4005387b2e4d399f476ed65cd2054cf","type":"user"},"timestamp":1605538943556,"mode":"active","message":{"type":"text","id":"13042142615951","text":"Dddf"}}],"destination":"U7099a426c60eb284672918c8f4e308fe"}
    if event.message.type == "text":
      # if event.message.text == '知識+魚'  or event.message.text == '查詢時價' or event.message.text == '線上訂購' or event.message.text == '料理食譜' or event.message.text == '幫我選魚' or event.message.text == '傳送相片':
      #   dict_con['MessageType'] = 'TextMessage_GraphicMenu_知識+魚'
      if event.message.text == '知識+魚':
        dict_con['MessageType'] = 'TextMessage_GraphicMenu_知識+魚'
        dict_con['Description'] = str(event.message.text)
      elif event.message.text == '查詢時價':
        dict_con['MessageType'] = 'TextMessage_GraphicMenu_查詢時價'
        dict_con['Description'] = str(event.message.text)
      elif event.message.text == '線上訂購':
        dict_con['MessageType'] = 'TextMessage_GraphicMenu_線上訂購'
        dict_con['Description'] = str(event.message.text)
      elif event.message.text == '料理食譜':
        dict_con['MessageType'] = 'TextMessage_GraphicMenu_料理食譜'
        dict_con['Description'] = str(event.message.text)
      elif event.message.text == '幫我選魚':
        dict_con['MessageType'] = 'TextMessage_GraphicMenu_幫我選魚'
        dict_con['Description'] = str(event.message.text)
        table_service.insert_or_replace_entity('UserDataConversation', dict_con)
        dict_con['MessageType'] = 'TextMessage_GraphicMenu_幫我選魚_SaveFishName'
        dict_con['Description'] = fishname
        dict_con['RowKey'] = dict_con['RowKey']+'-F'
      elif event.message.text == '傳送相片':
        dict_con['MessageType'] = 'TextMessage_GraphicMenu_傳送相片'
        dict_con['Description'] = str(event.message.text)
      else:
        dict_con['MessageType'] = 'TextMessage_UserInput'
        dict_con['Description'] = str(event.message.text)

    # 照片訊息  {"events":[{"type":"message","replyToken":"6a7d1f4ed1df436d8ebbd81da727a96a","source":{"userId":"Ud4005387b2e4d399f476ed65cd2054cf","type":"user"},"timestamp":1605538811910,"mode":"active","message":{"type":"image","id":"13042132840532","contentProvider":{"type":"line"}}}],"destination":"U7099a426c60eb284672918c8f4e308fe"}
    elif event.message.type == "image":
      dict_con['MessageType'] = 'ImageMessage'
      dict_con['Description'] = str(fishname)+'_'+str(event.message.id)+".jpg"

    # 音訊訊息 {"events":[{"type":"message","replyToken":"21d038156c8747759000d388e6d963ca","source":{"userId":"Ud4005387b2e4d399f476ed65cd2054cf","type":"user"},"timestamp":1605539428137,"mode":"active","message":{"type":"audio","id":"13042177633914","contentProvider":{"type":"line"},"duration":1124}}],"destination":"U7099a426c60eb284672918c8f4e308fe"}
    elif event.message.type == "audio":
      dict_con['MessageType'] = 'AudioMessage'
      dict_con['Description'] = str(event.message.id)+".mp3"

    # 影片訊息 {"events":[{"type":"message","replyToken":"785ee30a110944418ce3c2b1a450b34d","source":{"userId":"Ud4005387b2e4d399f476ed65cd2054cf","type":"user"},"timestamp":1605539597795,"mode":"active","message":{"type":"video","id":"13042189620133","contentProvider":{"type":"line"},"duration":1707}}],"destination":"U7099a426c60eb284672918c8f4e308fe"}
    elif event.message.type == "video":
      dict_con['MessageType'] = 'VideoMessage'
      dict_con['Description'] = str(event.message.id)+".mp4"

    # 位置訊息 {"events":[{"type":"message","replyToken":"9034f9181cb943a1a0df94594bfcebf5","source":{"userId":"Ud4005387b2e4d399f476ed65cd2054cf","type":"user"},"timestamp":1605539888668,"mode":"active","message":{"type":"location","id":"13042209767674","address":"238台灣新北市樹林區新北市樹林區","latitude":24.946104,"longitude":121.384433}}],"destination":"U7099a426c60eb284672918c8f4e308fe"}
    elif event.message.type == "location":
      dict_con['MessageType'] = 'LocationMessage'
      # dict_con['Description'] = '('+str(event.message.latitude)+","+str(event.message.longitude)+") "+event.message.address
      dict_con['Description'] = str(event.message.latitude)+","+str(event.message.longitude)

    # 貼圖訊息 {"events":[{"type":"message","replyToken":"d71de9468d784da78575d6077213113d","source":{"userId":"Ud4005387b2e4d399f476ed65cd2054cf","type":"user"},"timestamp":1605540911648,"mode":"active","message":{"type":"sticker","id":"13042277580057","stickerId":"2654396","packageId":"1064176","stickerResourceType":"STATIC"}}],"destination":"U7099a426c60eb284672918c8f4e308fe"}
    elif event.message.type == "sticker":
      dict_con['MessageType'] = 'StickerMessage'
      dict_con['Description'] = str(event.message)

  elif event.type == "postback":
    # 功能表單回傳訊息 {"events":[{"type":"postback","replyToken":"ecaad5ca26844e488326649eadcc85d2","source":{"userId":"Ud4005387b2e4d399f476ed65cd2054cf","type":"user"},"timestamp":1605713160186,"mode":"active","postback":{"data":"Event"}}],"destination":"U7099a426c60eb284672918c8f4e308fe"}
    if event.type == "postback":
      sp = event.postback.data.split('=',1)
      if sp[0] == 'GoTo':
        dict_con['MessageType'] = 'Postback_ShoppingLink'
        dict_con['Description'] = str(sp[1])
      elif sp[0] == 'SelectMenu':
        dict_con['MessageType'] = 'Postback_FishRecipe'
        dict_con['Description'] = str(sp[1])
      elif sp[0] == 'UserData&Location':
        dict_con['MessageType'] = 'Postback_UserLocation'
        dict_con['Description'] = str(sp[1])
      elif sp[0] == 'SelectInformation':
        dict_con['MessageType'] = 'Postback_FishInformation'
        dict_con['Description'] = str(sp[1])
      elif sp[0] == 'SelectPrice':
        dict_con['MessageType'] = 'Postback_SelectPrice'
        dict_con['Description'] = str(sp[1])
      elif sp[0] == 'BuyFish':
        dict_con['MessageType'] = 'Postback_BuyFish'
        dict_con['Description'] = str(sp[1])
      else:
        dict_con['MessageType'] = 'Postback'
        dict_con['Description'] = str(event.postback.data)

  table_service.insert_or_replace_entity('UserDataConversation', dict_con) # 儲存資料到資料庫


# 文字訊息處理
@handler.add(MessageEvent, message=TextMessage)
def User_MessageEvent(event):
  random_fish = 'None'
  if event.message.text == '幫我選魚':
    random_fish = random.choice(['七星鱸', '午仔魚', '吳郭魚', '黃花魚', '白帶魚', '白鯧魚', '石斑魚',  '紅目鰱',  '肉魚',  '赤宗', '鮭魚', '鱈魚'])
    Get_MessageText = Check_MessageText_In_FishNameTable(random_fish)
  else:
    Get_MessageText = Check_MessageText_In_FishNameTable(event.message.text)

  # Get_MessageText = event.message.text
  Reply_Messages_List = Get_Reply_Messages("MessageEventTextMessage",Get_MessageText)

  # 替換文字
  change_price = ''
  for i in Reply_Messages_List:
    if 'FlexSendMessage' in i.keys():
      if i['FlexSendMessage'].find('價格區間:') != -1:
        AvgRange = get_AvageRange(str(event.source.user_id), i)
        change_price = i['FlexSendMessage'].replace('價格區間:', '昨日價格區間 : ' + AvgRange)
        Reply_Messages_List[0]['FlexSendMessage'] = change_price

  if Reply_Messages_List != None:
    Send_Messages(event,Reply_Messages_List)
  Save_Event_Log(event, fishname = random_fish)


# 圖片訊息處理
@handler.add(MessageEvent,message=ImageMessage)
def User_ImageMessageEvent(event):
  Save_UserFile(event.message.id,"jpg")

  # ++++++++++++++++++++++++++++++++++++  AI  分析  ++++++++++++++++++++++++++++++++++++++++++++++++
  AI_result_dict = algorithm_top('temp/image/'+event.message.id+".jpg", 80, cnn, yolo)
  print('[CNN] AI Result : ', AI_result_dict)

  # resule
  AI_result_list = []
  if Purpose == 'Test':
    rt_text = 'V5 '
    for i in AI_result_dict:
      for j in i:
        rt_text = rt_text + str(j+'='+str(i[j])+'% | ')
    AI_result_list.append(rt_text)
  elif Purpose == 'Used':
    list_tmp = []
    for i in AI_result_dict:
      for j in i:
        list_tmp.append(j)
    unique = []
    for name in list_tmp:
      if name not in unique:
        unique.append(name)
    AI_result_list = unique

  Get_MessageList = Check_MessageList_In_FishNameTable(AI_result_list)
  for n in Get_MessageList:
    if n == "None":
      Get_MessageList.remove('None')
  if len(Get_MessageList) > 0:
    Reply_Messages_List = Get_Reply_Messages_list("MessageEventTextMessage",Get_MessageList)

    # bubble to carousel
    if Purpose == 'Used':
      # FlexSendMessage to CarouselContainer
      contents = '"contents":['
      bubble = '{"type": "carousel",'
      len_RML = len(Reply_Messages_List)
      len_num = 1
      for i in Reply_Messages_List:
        if len_num == len_RML:
          # 替換文字
          change_price = ''
          if 'FlexSendMessage' in i.keys():
            if i['FlexSendMessage'].find('價格區間:') != -1:
              AvgRange = get_AvageRange(str(event.source.user_id), i)
              change_price = i['FlexSendMessage'].replace('價格區間:', '昨日價格區間 : ' + AvgRange)
          contents = contents + change_price
        else:
          # 替換文字
          change_price = ''
          if 'FlexSendMessage' in i.keys():
            if i['FlexSendMessage'].find('價格區間:') != -1:
              AvgRange = get_AvageRange(str(event.source.user_id), i)
              change_price = i['FlexSendMessage'].replace('價格區間:', '昨日價格區間 : ' + AvgRange)
          contents = contents + change_price + ','
          len_num += 1
      jsonfile = bubble + contents + "]}"
      Reply_Carousel = {"CarouselContainer": jsonfile}
      Reply_Messages_List = [Reply_Carousel]
  else:
    Reply_Messages_List = Get_Reply_Messages_OtherEvent("MessageEventImageMessage")
    Reply_Messages_List = Get_Reply_Messages("MessageEventTextMessage", "None")

  # ++++++++++++++++++++++++++++++++++++  AI  分析  ++++++++++++++++++++++++++++++++++++++++++++++++
  # print('Reply_Messages_List = '+ str(Reply_Messages_List))
  if Reply_Messages_List != None:
    Send_Messages(event,Reply_Messages_List)
  # Save_File_S3(event.message.id+'.jpg',"image")
  Save_Event_Log(event, fishname = Get_MessageList)

# 影片訊息處理
@handler.add(MessageEvent,message=VideoMessage)
def User_VideoMessage(event):
  Save_UserFile(event.message.id,"mp4")
  Reply_Messages_List = Get_Reply_Messages_OtherEvent("MessageEventVideoMessage")
  if Reply_Messages_List != None:
    Send_Messages(event,Reply_Messages_List)
  # Save_File_S3(event.message.id+'.mp4',"video")
  Save_Event_Log(event)

# 音訊訊息處理
@handler.add(MessageEvent,message=AudioMessage)
def User_AudioMessage(event):
  Save_UserFile(event.message.id,"mp3")
  Reply_Messages_List = Get_Reply_Messages_OtherEvent("MessageEventAudioMessage")
  if Reply_Messages_List != None:
    Send_Messages(event,Reply_Messages_List)
  # Save_File_S3(event.message.id+'.mp3',"audio")
  Save_Event_Log(event)

# 位置訊息處理
@handler.add(MessageEvent,message=LocationMessage)
def User_LocationMessage(event):
  Reply_Messages_List = Get_Reply_Messages_OtherEvent("MessageEventLocationMessage")
  if Reply_Messages_List != None:
    Send_Messages(event,Reply_Messages_List)
  Save_Event_Log(event)

# 貼圖訊息處理
@handler.add(MessageEvent,message=StickerMessage)
def User_StickerMessage(event):
  Reply_Messages_List = Get_Reply_Messages_OtherEvent("MessageEventStickerMessage")
  if Reply_Messages_List != None:
    Send_Messages(event,Reply_Messages_List)
  Save_Event_Log(event)

# 功能表單回傳訊息處理
@handler.add(PostbackEvent)
def User_PostbackEvent(event):
  if event.postback.data == 'UserData&Location=北部':
    dict1 = {'PartitionKey':str(event.source.user_id), 'RowKey':str(event.source.user_id), 'UserLocation':'北部'}
    table_service.insert_or_replace_entity('UserLocation', dict1)
  elif event.postback.data == 'UserData&Location=中部':
    dict1 = {'PartitionKey':str(event.source.user_id), 'RowKey':str(event.source.user_id), 'UserLocation':'中部'}
    table_service.insert_or_replace_entity('UserLocation', dict1)
  elif event.postback.data == 'UserData&Location=南部':
    dict1 = {'PartitionKey':str(event.source.user_id), 'RowKey':str(event.source.user_id), 'UserLocation':'南部'}
    table_service.insert_or_replace_entity('UserLocation', dict1)
  elif event.postback.data == 'UserData&Location=東部':
    dict1 = {'PartitionKey':str(event.source.user_id), 'RowKey':str(event.source.user_id), 'UserLocation':'東部'}
    table_service.insert_or_replace_entity('UserLocation', dict1)
  Reply_Messages_List = Get_Reply_Messages("PostbackEvent",event.postback.data)
  if Reply_Messages_List != None:
    Send_Messages(event,Reply_Messages_List)
  Save_Event_Log(event)

# Follow訊息處理
@handler.add(FollowEvent)
def User_FollowEvent(event):
  user_profile = line_bot_api.get_profile(event.source.user_id)
  user_profile_dict = eval(str(user_profile))                                   # line_bot_api.get_profile 轉 str 再轉成 dict

  dict1 = {'PartitionKey':str(event.source.user_id),
          #  'RowKey':str(event.timestamp),
           'RowKey':event.type,
           "Follow_Timestamp":event.timestamp,
           "User_Name":user_profile_dict["displayName"],
           "Type":event.type,
           }
  for i in user_profile_dict:
    if i == 'language':
      dict1['Language'] = user_profile_dict[i]
    elif i == 'pictureUrl':
      dict1['Url'] = user_profile_dict[i]
    elif i == 'statusMessage':
      dict1['Status_Message'] = user_profile_dict[i]

  table_service.insert_or_replace_entity('UserDataInformation', dict1)      # 將User data 存入 table

  Reply_Messages_List = Get_Reply_Messages_OtherEvent("FollowEvent")
  if Reply_Messages_List != None:
    Send_Messages(event,Reply_Messages_List)

# Unfollow訊息處理
@handler.add(UnfollowEvent)
def User_UnfollowEvent(event):
  dict_udata = {
    "Type" : event.type,
    "Unfollow_Timestamp": event.timestamp,
    'PartitionKey':str(event.source.user_id),
    'RowKey':event.type
  }
  table_service.insert_or_replace_entity('UserDataInformation', dict_udata)     # 將User data 存入 table

def Get_Fish_Price(FishName=''):
  ti = datetime.datetime.now() + datetime.timedelta(days=-1)
  Y = str(int(ti.strftime("%Y")) - 1911)
  M = ti.strftime("/%m/%d")
  date = Y + M

  htmlhigh = """<head><meta name="viewport" content="width=device-width, initial-scale=1.0, minimum-scale=0.5, maximum-scale=2.0, user-scalable=yes" /> """
  htmlcolor = """<body bgcolor="#F0F8FF">"""
  fishname_web = FishName
  if FishName == '午仔魚(沿海)' or FishName == '午仔魚(養殖)':
    fishname_web = '午仔魚'
  if FishName == '鮭魚(凍)' or FishName == '鮭魚片':
    fishname_web = '鮭魚'
  if FishName == '比目魚' or FishName == '比目魚片':
    fishname_web = '鱈魚'
  if FishName == '白鯧':
    fishname_web = '白鯧魚'
  if FishName == '黃花(沿海)' or FishName == '黃花(養殖)':
    fishname_web = '黃花魚'
  htmlimage = '<img src="https://www.hackeralliance.icu/FishImage?FishName='+fishname_web+'" width="250"><br />'
  text = "魚名： " + FishName + "<br />日期： " + date + "</p>單位： 台斤<br />"
  # image = """<img src="https://example.com/media/photo.jpg" with="600" heigh="400" alt="一張圖片">"""

  # tasks = table_service.query_entities('FishPrice', filter="(交易日期 eq '"+date+"' and 魚名 eq '"+FishName+"') and (RowKey eq '基隆' or RowKey eq '台北' or RowKey eq '三重' or RowKey eq '桃園' or RowKey eq '新竹' or RowKey eq '頭城' or RowKey eq '蘇澳')")
  tasks = table_service.query_entities('FishPrice', filter="交易日期 eq '"+date+"' and 魚名 eq '"+FishName+"'")

  a = []
  for task in tasks:
    task['市場'] = task.pop("RowKey")
    b = {}
    b['市場'] = task['市場']
    b['平均價'] = str(int(float(task['平均價'])*0.6))
    b['上價'] = str(int(float(task['上價'])*0.6))
    b['下價'] = str(int(float(task['下價'])*0.6))
    # print(b)
    a.append(b)
  if len(a) == 0:
    df = "目前無資料"
  else:
    df = pd.DataFrame(data=a).to_html()
    # df.set_index('市場', inplace=True)
    # df.to_html()
  return htmlhigh + htmlimage + htmlcolor + text + df

# 瀏覽網頁 Fish price
@app.route("/FishPrice", methods=["GET", "POST"])
def FishPrice():
    Fishname = flask.request.args.get('FishName')
    return Get_Fish_Price(FishName=Fishname)


def Get_Fish_Information(FishName=''):
  htmlhigh = """<head><meta name="viewport" content="width=device-width, initial-scale=1.0, minimum-scale=0.5, maximum-scale=2.0, user-scalable=yes" /> """
  htmlcolor = """<body bgcolor="#F0F8FF">"""
  fishname_web = FishName
  if FishName == '午仔魚(沿海)' or FishName == '午仔魚(養殖)':
    fishname_web = '午仔魚'
  if FishName == '鮭魚(凍)' or FishName == '鮭魚片':
    fishname_web = '鮭魚'
  if FishName == '比目魚' or FishName == '比目魚片':
    fishname_web = '鱈魚'
  if FishName == '白鯧':
    fishname_web = '白鯧魚'
  if FishName == '黃花(沿海)' or FishName == '黃花(養殖)':
    fishname_web = '黃花魚'
  htmlimage = '<img src="https://www.hackeralliance.icu/FishImage?FishName='+fishname_web+'" width="250></img><br />'
  tasks = table_service.query_entities(
    'FishInformation', filter="RowKey eq '" + FishName + "'")

  a = []
  for task in tasks:
    b = {}
    b['魚名'] = task["name"]
    b['中文學名'] = task["中文名"]
    b['介紹'] = task['介紹']
    b['料理方式'] = task['料理方式']
    b['台灣分布'] = task['台灣分布']
    b['地理分布'] = task['地理分布']
    b['形態特徵'] = task['形態特徵']
    b['棲息環境'] = task['棲息環境']
    a.append(b)
  if len(a) == 0:
    df = "目前無資料"
  else:
    df = pd.DataFrame(data=a, index=["詳細資訊"]).T.to_html()
    # df.set_index('魚名', inplace=True)
    # df.T.to_html()
  return htmlhigh + htmlcolor + htmlimage + htmlcolor + df

# 瀏覽網頁 Fish information
@app.route("/FishInformation", methods=["GET"])
def FishInformation():
    Fishname = flask.request.args.get('FishName')
    return Get_Fish_Information(FishName=Fishname)

# 瀏覽網頁 Fish image
@app.route("/FishImage", methods=["GET"])
def FishImage():
    Fishname = flask.request.args.get('FishName')
    image_data = open("/home/FishVM/linebot/v5/FishImage/"+ Fishname + ".jpg", "rb").read()
    response = make_response(image_data)
    response.headers['Content-Type'] = 'image/jpg'
    return response

def get_AvageRange(userid, dict1):
  # 從資料庫取得位置資料
  ti = datetime.datetime.now() + datetime.timedelta(days=-1)
  Y = str(int(ti.strftime("%Y")) - 1911)
  M = ti.strftime("/%m/%d")
  date = Y + M
  user_location = table_service.query_entities('UserLocation', filter="PartitionKey eq '"+userid+"'")
  location = ""
  AvgRange = ""
  for i in user_location:
    location = i['UserLocation']
  # 取得Avg價格
  fishname = dict1['PartitionKey']
  if dict1['PartitionKey'] == '午仔魚':
    fishname = '午仔魚(養殖)'
  if dict1['PartitionKey'] == '黃花魚':
    fishname = '黃花(養殖)'
  if dict1['PartitionKey'] == '白鯧魚':
    fishname = '白鯧'
  if dict1['PartitionKey'] == '鱈魚':
    fishname = '比目魚'
  tasks = table_service.query_entities('FishPriceAvageRange', filter="地區 eq '" + location + "' and 魚名 eq '" + fishname + "' and 交易日期 eq '" + date + "'")
  for j in tasks:
    if j['Avg下價'] == 0 and j['Avg上價'] == 0:
      AvgRange = location + ' 無價格資訊'
    elif j['Avg下價'] == 0 and j['Avg上價'] != 0:
      AvgRange = location + ' ' + str(int(float(j['Avg上價'])*0.6)) + ' /斤'
    else:
      AvgRange = location + ' ' + str(int(float(j['Avg下價'])*0.6)) + '  ~  ' + str(int(float(j['Avg上價'])*0.6)) + ' /斤'
  return AvgRange

# Stpe 4 : 伺服器啟動
if __name__ == '__main__':
    app.run(debug=False, threaded=False)