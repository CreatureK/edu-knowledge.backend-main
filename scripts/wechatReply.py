from wechatpy import parse_message
from wechatpy.replies import TextReply
import math



from .queryWithOpenai import queryQADB,queryQADB_bge_mutiple_table,queryQADB_bge_mutiple_table_for_wechat

import requests
import json
import os
import logging


def get_access_token(appid,appsecret):
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={appsecret}"
    response = requests.get(url)
    access_token = response.json()['access_token']
    logging.info(access_token)
    return access_token

def construct_customer_reply_message(openid,content):
    message = {
        "touser": openid,
        "msgtype" : "text",
        "text": {
            "content": content
        }
    }
    # return message
    return json.dumps(message,ensure_ascii=False)

def send_customer_reply_message(access_token,message):
    url = f"https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={access_token}"
    headers = {
     "Content-Type": "application/json"
    }
    response = requests.post(url,data=message.encode('utf-8'),headers=headers)

    return response.json()

def reply_text(msg,reply_text):
    reply_data = TextReply(content = reply_text,message=msg)
    reply_xml = reply_data.render()
    return reply_xml

def query_chatdb(msg,query_message):
    res = "hello"
    res = queryQADB_bge_mutiple_table(query_message)
    #res = queryQADB(query_message)
    return reply_text(msg,res)

def split_string(input_string:str):
    max_chars = 600
    chunks = []
    num_chunks = math.ceil(len(input_string) / max_chars)
    for i in range(num_chunks):
        start_index = i * max_chars
        end_index = (i + 1) * max_chars
        chunk = input_string[start_index:end_index]
        chunks.append(chunk)
    return chunks

def query_and_reply(msg,query_message):
    access_token = get_access_token( os.environ.get('WECHAT_APPID'), os.environ.get('WECHAT_APPSECRET'))
    # content = queryQADB(query_message)
    content,q_and_url_list = queryQADB_bge_mutiple_table_for_wechat(query_message)

    # 找到最后一次出现的位置
    
    last_not_find = content.rfind("我没有找到相关信息")
    last_occurrence = content.rfind("官方文档参考链接：")

    content_chunks = []
    # 如果找到了最后一次出现的位置，则拆分文本
    if last_occurrence != -1:
        text_before_last_occurrence = content[:last_occurrence]
        text_after_last_occurrence = content[last_occurrence:]
        content_chunks += split_string(text_before_last_occurrence)
        content_chunks.append(text_after_last_occurrence)
    else :
        content_chunks += split_string(content)

    #如果没有回复我没有找到相关信息
    if last_not_find == -1 : 
        q_and_url_reply = "官方文档参考链接："
        for q_and_url in q_and_url_list:
            q_and_url_reply += f"\n<a href='{ q_and_url[1]}'>{q_and_url[0]}</a>\n"
        content_chunks.append(q_and_url_reply)

    for text in content_chunks:
        reply_message = construct_customer_reply_message(msg.source,text)
        logging.info(reply_message)
        json = send_customer_reply_message(access_token,reply_message)
        logging.info(json)
    
def query_and_reply_dxy(msg,query_message):
    access_token = get_access_token( os.environ.get('WECHAT_APPID_DXY'), os.environ.get('WECHAT_APPSECRET_DXY'))
    # content = queryQADB(query_message)
    content,q_and_url_list = queryQADB_bge_mutiple_table_for_wechat(query_message)

    # 找到最后一次出现的位置
    
    last_not_find = content.rfind("我没有找到相关信息")
    last_occurrence = content.rfind("官方文档参考链接：")

    content_chunks = []
    # 如果找到了最后一次出现的位置，则拆分文本
    if last_occurrence != -1:
        text_before_last_occurrence = content[:last_occurrence]
        text_after_last_occurrence = content[last_occurrence:]
        content_chunks += split_string(text_before_last_occurrence)
        content_chunks.append(text_after_last_occurrence)
    else :
        content_chunks += split_string(content)

    #如果没有回复我没有找到相关信息
    if last_not_find == -1 : 
        q_and_url_reply = "官方文档参考链接："
        for q_and_url in q_and_url_list:
            q_and_url_reply += f"\n<a href='{ q_and_url[1]}'>{q_and_url[0]}</a>\n"
        content_chunks.append(q_and_url_reply)

    for text in content_chunks:
        reply_message = construct_customer_reply_message(msg.source,text)
        logging.info(reply_message)
        json = send_customer_reply_message(access_token,reply_message)
        logging.info(json)