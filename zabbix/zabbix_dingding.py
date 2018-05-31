#!/usr/bin/env python
# -*- coding: utf-8 -*-
#zabbix alarm sent to dingding

import requests
import json
import sys
import os
import time
import redis
import logging

#http://doc.xiaopeng.local:18090/pages/viewpage.action?pageId=17274279
from landcruiser_sdk.oauth2_client import OAuth2Client
from requests.exceptions import HTTPError

reload(sys)
sys.setdefaultencoding('utf8')

# 客户端ID及Secret请联系SA获取
ClientId = 'client_for_read'
ClientSecret = 'HbU3MwoyP7W8KsFPW28ckVrLd5OlzStr'
AccessTokenUrl = 'https://lc.xiaopeng.com/oauth/token'
logging.basicConfig(level=logging.ERROR, handlers=[logging.StreamHandler()])
Cli = OAuth2Client(ClientId, ClientSecret, AccessTokenUrl)

#获取当前时间
Ctime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

#连接redis
r = redis.StrictRedis(host='127.0.0.1', port=6379)

#设置http/https 头部
Headers = {'Content-Type': 'application/json;charset=utf-8'}

LogFile = "/home/xpmotors/logs/zabbix/zabbix_dingding.log"
DefaultRobot = "https://oapi.dingtalk.com/robot/send?access_token=cce90653d971fc7ae40223ecbbf35e24dc64f2ad27d5e86c056603dcf70c4d59"

#get dingding robot
def GetDingdingRobot(ip):
    # 获取列表型数据
    url = "https://lc.xiaopeng.com/api/cmdb/v1/machines/notifyurls?address=%s" % ip
    data = Cli.get_for_list(url)
    dictUrls = {x['code']: x['url'] for x in data}

    return dictUrls


def Log(info):
        #注意权限,否则写不进去日志
        if os.path.isfile(LogFile) == False:
                FH = open(LogFile, 'a+')
        FH = open(LogFile, 'a+')
        FH.write(info)
        FH.close()

def Message(text, dictUrls, user = None):
    str(text) 
    json_text= {
     "msgtype": "text",
        "text": {
            "content": text
        },
        "at": {
            "atMobiles": [
                user
            ],
            "isAtAll": False
        }
    }

    if len(dictUrls) == 0:
        response = requests.post(DefaultRobot, data=json.dumps(json_text), headers=Headers).json()
        code = response["errcode"]
        if code == 0:
            Log(Ctime + ":消息发送成功 返回码: " + str(code) + "\n")
        else:
            Log(Ctime + ":消息发送失败 返回码: " + str(code) + "\n")
    else:
        keys = dictUrls.keys()
        for k in keys:
            response = requests.post(dictUrls[k], data=json.dumps(json_text), headers=Headers).json()
            code = response["errcode"]
            if code == 0:
                Log(Ctime + ":消息发送成功 返回码: " + str(code) + "\n")
            else:
                Log(Ctime + ":消息发送失败 返回码: " + str(code) + "\n")

#set redis ex time 86400
def SetRedisKey(event_id, text):
    r.set(event_id, text, ex=86400)
    k = r.exists(event_id)
    if k == True:
        Log(Ctime + ":故障已被人确认，Redis Set成功: " + event_id + "\n")
    else:
        Log(Ctime + ":故障已被人确认，Redis Set失败: " + event_id + "\n")

#delete key
def DelRedisKey(event_id):
    Key = r.exists(event_id)
    if Key == True:
        r.delete(event_id)
        k = r.exists(event_id)
        if k == False:
            Log(Ctime + ":故障恢复，Redis Delete成功: " + event_id + "\n")
        else:
            Log(Ctime + ":故障恢复，Redis Delete失败: " + event_id + "\n")

def CheckRule(event_id, text):
    Key = r.exists(event_id)
    if Key == False:
        Message(text, dictUrls) # Send message if the key is not exist
    else:
        Log(Ctime + ":故障已被确认, 一天内不再推送告警: " + event_id + "\n") 

if __name__ == '__main__':
        subject = sys.argv[1]  #{ALERT.SUBJECT}
        text = sys.argv[2]  #{ALERT.MESSAGE}
        event_id, option, ip = subject.split('_')  #{event.id}_1_{HOST.IP} eg: 13452_1_172.22.1.1

        Log(Ctime + " 参数信息: " + subject + " " + " "+ event_id + "\n")
        Log(text + "\n")

        dictUrls = GetDingdingRobot(ip)
        #The event alarm
        if option == '1':
            CheckRule(event_id, text)

        #The event recovery
        elif option == '0':
            DelRedisKey(event_id)
            Message(text, dictUrls)
            Log(Ctime + ":故障恢复, 删除Redis中的事件Key: " + event_id + "\n")

        #The event_id has been confirmed
        elif option == '3':
            #set in redis
            SetRedisKey(event_id, text)
            Message(text, dictUrls)
            Log(Ctime + ":故障已被人确认,自动设置一天内不再推送告警信息: " + event_id + "\n")


