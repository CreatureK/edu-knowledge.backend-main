import hashlib
from flask import Flask, jsonify, request
from flask_cors import CORS 
import time
import subprocess
import socket
from scripts.queryWithOpenai import (
    queryQADB,
    addQaFromText,
    addQaText,
    addQaFromJsonFilePath,
    addQaFromJson,
    queryQADB_bge,
    addQaFromJson_bge,
    addQaFromJson_bge_by_table,
    queryQADB_bge_mutiple_table
    )
from wechatpy import parse_message
from scripts.wechatReply import query_chatdb,query_and_reply,query_and_reply_dxy
import threading
import logging
import os

app = Flask(__name__)



@app.route('/addQaFromJson', methods=['POST'])
def IaddQaFromJson():
    data = request.json
    res = addQaFromJson(data)
    return jsonify(qaDucomentsIds = res)

@app.route('/addQaFromJson_bge', methods=['POST'])
def IaddQaFromJson_bge():
    data = request.json
    res = addQaFromJson_bge(data)
    return jsonify(qaDucomentsIds = res)



@app.route('/addQaFromJson_bge_by_table', methods=['POST'])
def IaddQaFromJson_bge_guides():
    data = request.json
    table_name = data["table"]
    qa_json_list = data["qa_json_list"]
    res = addQaFromJson_bge_by_table(qa_json_list,table_name)
    return jsonify(qaDucomentsIds = res)


@app.route('/addQaFromJsonFile', methods=['POST'])
def IaddQaFromJsonFile():
    if 'file' not in request.files:
        return 500
    file = request.files['file']
    file.save('uploads/' + file.name +'.json')
    
    res = addQaFromJsonFilePath('uploads/' + file.name + '.json')
    return jsonify(qaDucomentsIds = res)

@app.route('/addQaFromText', methods=['POST'])
def IaddText():
    text = request.form.get('text')
    res = addQaFromText(text)
    return jsonify(qaDucomentsIds = res)

@app.route('/addQaExample_bge', methods=['POST'])
def IaddQaExample_bge():
    data = request.get_json()
    question_content =data['question_content']
    answer_content = data['answer_content']

    #question_content = request.form.get('question_content')
    #answer_content = request.form.get('answer_content')
    res = addQaText(question_content,answer_content)
    return res

@app.route('/addQaExample', methods=['POST'])
def IaddQaExample():
    data = request.get_json()
    question_content =data['question_content']
    answer_content = data['answer_content']

    #question_content = request.form.get('question_content')
    #answer_content = request.form.get('answer_content')
    res = addQaText(question_content,answer_content)
    return res

@app.route('/queryQADB_bge', methods=['POST'])
def IqueryQADB_bge():
    data =  request.get_json()
    query_message = data['query_message']
    res = queryQADB_bge(query_message)
    return res

@app.route('/queryQADB', methods=['POST'])
def IqueryQADB():
    data =  request.get_json()
    query_message = data['query_message']
    res = queryQADB_bge_mutiple_table(query_message)
    return res

@app.route('/wechat',methods=['Get','POST'])
def wxbind():
    if(request.method == 'GET'):
        signature = request.args.get('signature')
        timestamp = request.args.get('timestamp')
        nonce = request.args.get('nonce')
        echostr = request.args.get('echostr')
        return echostr
        token = 'this_is_a_wechat_token'
        tmparr = [token,timestamp,nonce]
        tmparr.sort()

        s = tmparr[0]+tmparr[1]+tmparr[2]
        sha1 = hashlib.sha1(s.encode('utf-8')).hexdigest()
        logging.info(sha1)
        logging.info(echostr)
        if(sha1 == echostr): return echostr
        else: return ''
    elif(request.method =="POST"): 
        wechat_send_data = request.data
        msg = parse_message(wechat_send_data)
        from_user_name = msg.source
        create_time = msg.create_time
        to_user_name = msg.target
        if(msg.type == "text"):
            send_text = msg.content
            query_thread = threading.Thread(target=query_and_reply,args=(msg,send_text))
            print("get in ")
            query_thread.start()
            print("in thread")
            logging.info("thread started")
            return 'success'

@app.route('/',methods=['Get','POST'])
def wxbind_dxy():
    if(request.method == 'GET'):
        signature = request.args.get('signature')
        timestamp = request.args.get('timestamp')
        nonce = request.args.get('nonce')
        echostr = request.args.get('echostr')
        return echostr
        token = 'this_is_a_wechat_token'
        tmparr = [token,timestamp,nonce]
        tmparr.sort()
        s = tmparr[0]+tmparr[1]+tmparr[2]
        sha1 = hashlib.sha1(s.encode('utf-8')).hexdigest()
        if(sha1 == echostr): return echostr
        else: return ''
    elif(request.method =="POST"): 
        wechat_send_data = request.data
        msg = parse_message(wechat_send_data)
        from_user_name = msg.source
        create_time = msg.create_time
        to_user_name = msg.target
        if(msg.type == "text"):
            send_text = msg.content
            query_thread = threading.Thread(target=query_and_reply_dxy,args=(msg,send_text))
            print("get in ")
            query_thread.start()
            print("in thread")
            logging.info("thread started")
            return 'success'


if __name__ == '__main__':
    CORS(app, origins='*')
    app.run(host='0.0.0.0',port=5000,debug=True)
