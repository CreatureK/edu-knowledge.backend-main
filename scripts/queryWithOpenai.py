import os
from typing import List
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores.supabase import SupabaseVectorStore
import requests
import json
from supabase import create_client,Client
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.document_loaders  import TextLoader , PDFMinerLoader ,  UnstructuredEPubLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from langchain_core.prompts import HumanMessagePromptTemplate
from langchain_core.documents import Document
from langchain_community.llms.chatglm3 import ChatGLM3
from langchain_core.embeddings import Embeddings
from lib.Embeddings import bgeEmbeddings
from lib.chat_utils import(
    get_markdownurls_from_qadocuments,
    get_qadocuments_with_limit,
    get_langchain_documents_from_qadocuments,
    )

from config import ChatGLM3_endpoint_url

from langchain.chains import (
    StuffDocumentsChain,
    LLMChain,
    ReduceDocumentsChain,
    MapReduceDocumentsChain,
)
from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAI
from lib.supabase.initSupabaseClient import supabaseClient
from lib.supabase.QaVectorStore import SupabaseQaVectorStore
from .fileLoadHelper import FileLoadHelper
import logging
def addQaFromJson(data):
    return FileLoadHelper.upsert_from_formatJsonList(data)

def addQaFromJson_bge_by_table(json_list,table_name):
    question_texts = []
    answer_texts = []
    metadatas = []
    for qa_json in json_list:
        question_texts.append(qa_json['exampleQ']),
        answer_texts.append(qa_json['exampleA'])
        metadatas.append({"doc_url":qa_json['exampleUrl']})

    if(table_name == None) : return "false"

    embeddings = bgeEmbeddings()
    vectorStore = SupabaseQaVectorStore(
        client=supabaseClient,
        embedding=embeddings,
        table_name=table_name,
        query_name='match_qadocuments_bge',
    )

    return vectorStore.add_QaTexts(question_texts,answer_texts,metadatas)

def addQaFromJson_bge(f_json_list):
    question_texts = []
    answer_texts = []

    for qa_json in f_json_list:
        question_texts.append(qa_json['exampleQ']),
        answer_texts.append(qa_json['exampleA'])

    embeddings = bgeEmbeddings()
    vectorStore = SupabaseQaVectorStore(
        client=supabaseClient,
        embedding=embeddings,
        table_name='qadocuments_bge',
        query_name='match_qadocuments_bge',
    )

    return vectorStore.add_QaTexts(question_texts,answer_texts)


def addQaFromJsonFilePath(path):
    return FileLoadHelper.upsert_from_file_path(path)

def addQaFromJsonFile(file):
    return FileLoadHelper.upsert_from_file(file)
  
def addQaFromText(text:str):
    f_json = FileLoadHelper.get_formatJsonList_from_text(text)
    return FileLoadHelper.upsert_from_formatJsonList(f_json)
    print(f_json)
    return True

def addQaText(questioncontent:str , answercontent: str):
    embeddings = OpenAIEmbeddings()
    vectorStore = SupabaseQaVectorStore(
        client=supabaseClient,
        embedding=embeddings,
        table_name='qadocuments',
        query_name='match_qadocuments',
    )
    return vectorStore.add_QaTexts(question_texts=[questioncontent],answer_texts=[answercontent])

def queryQADB(queryMessage):
    embeddings = OpenAIEmbeddings()

    vectorStore = SupabaseQaVectorStore(
        client=supabaseClient,
        embedding=embeddings,
        table_name='qadocuments',
        query_name='match_qadocuments',
    )
    res = vectorStore.similarity_search(query=queryMessage)
    documents = [
        (
            Document("exampleQ:\n{question}\n\nexampleA:\n{answer}\n\n exampleUrl:\n{doc_url}".
                         format(question = qadoc.question_text,answer=qadoc.answer_text,doc_url = qadoc.metadata["doc_url"]))
        )
        for qadoc in res
    ]
    # print(documents)
    document_prompt = PromptTemplate(
        input_variables=["page_content"],
        template="{page_content}"
    )
    document_variable_name = "context"
    stuff_prompt = PromptTemplate.from_template(
        """
我希望你来扮演一个数据分析师来帮忙分析文本数据，下面是文本数据的例子：
定义问答格式文本,文本中exampleQ是一个问题或者一个摘要,exampleA是exampleQ的答案或者摘要具体内容。
对于这样一个用三个反括号括起来的文本
```
exampleQ:
什么是python
exampleA:
python 是一个编程语言
exampleQ:
树的作用很多
exampleA:
树可以帮人遮风挡雨
```
"python 是一个编程语言"是"什么是python"的答案，"树可以帮人遮风挡雨"是"树的作用很多"的具体内容。
下面你将接受到很多该格式的文本文本，根据这些问答格式文本的信息，将与用户问题相关的信息总结后，回答用户问题，如果信息不足请提醒"信息不足"。
用三个反括号括起来的是提供的问答格式文本：
```
{context}
```
用户问题：{question}
回答:
"""
    )
    llm = OpenAI(max_tokens=-1,temperature=0.3)
    
    llm_chain = LLMChain(llm=llm, prompt=stuff_prompt,verbose=True)
    
    stuff_chain = StuffDocumentsChain(
        llm_chain=llm_chain,
        document_prompt= document_prompt,
        document_variable_name= document_variable_name
    )
    res = stuff_chain.invoke({'input_documents':documents,'question':queryMessage})
    return res['output_text']

def get_url_fromat_str(metadata:dict) :
    if("doc_url" in metadata.keys()): return "exampleUrl:\n" + metadata['doc_url']
    else : return ""



def queryQADB_bge(queryMessage):
    embeddings = bgeEmbeddings()

    vectorStore = SupabaseQaVectorStore(
        client=supabaseClient,
        embedding=embeddings,
        table_name='qadocuments_bge',
        query_name='match_qadocuments_bge_both',
    )
    res = vectorStore.similarity_search(query=queryMessage,k=4)
    documents = [
        (
            Document("exampleQ:\n{question}\n\nexampleA:\n{answer}\n\n{doc_url}".
                         format(question = qadoc.question_text,answer=qadoc.answer_text,doc_url = get_url_fromat_str(qadoc.metadata)))
        )
        for qadoc in res
    ]
    for qadoc in res:
        logging.info(qadoc.question_text)
        logging.info(qadoc.answer_text)
    
    document_prompt = PromptTemplate(
        input_variables=["page_content"],
        template="{page_content}"
    )
    document_variable_name = "context"
    stuff_prompt = PromptTemplate.from_template(
        """
我希望你来扮演一个数据分析师来帮忙分析文本数据，下面是文本数据的例子：
定义问答格式文本,文本中exampleQ是一个问题或者一个摘要,exampleA是exampleQ的答案或者摘要具体内容,exampleUrl是当前exampleA与exampleQ的参考链接，exampleUrl可能不存在。
对于这样一个用三个反括号括起来的文本
```
exampleQ:
什么是python
exampleA:
python 是一个编程语言
exampleQ:
树的作用很多
exampleA:
树可以帮人遮风挡雨
exampleUrl:
http://www.example.com
```
"python 是一个编程语言"是"什么是python"的答案，"树可以帮人遮风挡雨"是"树的作用很多"的具体内容,"http://www.example.com"是"树可以帮人遮风挡雨"与"树的作用很多"这种信息出现的链接。
你将接受到很多该格式的文本文本，根据这些问答格式文本的信息，将与用户问题相关的信息总结后，回答用户问题，输出格式为markdown。
回答问题时，除非用户明确不需要参考链接，否则总是列出参考链接，如果信息不足请提醒"信息不足"。
下面用三个反括号括起来的是提供的问答格式文本：
```
{context}
```
用户问题：{question}
回答:
"""
    )
    endpoint_url = ChatGLM3_endpoint_url
    # llm = OpenAI(max_tokens=-1,temperature=0.3)
    llm = ChatGLM3(
            endpoint_url=endpoint_url,
            max_tokens=2000,
            top_p=0.3,
            verbose=True
        )
    llm = OpenAI(max_tokens=-1,temperature=0.3)

    llm_chain = LLMChain(llm=llm, prompt=stuff_prompt)

   
    
    stuff_chain = StuffDocumentsChain(
        llm_chain=llm_chain,
        document_prompt= document_prompt,
        document_variable_name= document_variable_name
    )
    res = stuff_chain.invoke({'input_documents':documents,'question':queryMessage})
    return res['output_text']


def get_documents_bge_guides_with_embedding(query_embedding):
    #对于guides进行查询
    embeddings = bgeEmbeddings()
    documents = []
    #对于question查询
    vectorStore_guides_q  = SupabaseQaVectorStore(
        client=supabaseClient,
        embedding=embeddings,
        table_name='qadocuments_bge_guides',
        query_name='match_qadocuments_bge_guides_q',
    )

    res_guides_q = vectorStore_guides_q.similarity_search_by_vector(embedding=query_embedding,k=2)

    documents_guides_q = [
        (
            Document("exampleQ:\n{question}\n\nexampleA:\n{answer}\n\n{doc_url}".
                         format(question = qadoc.question_text,answer=qadoc.answer_text,doc_url = get_url_fromat_str(qadoc.metadata)))
        )
        for qadoc in res_guides_q
    ]
    
    documents += documents_guides_q

    #对于answer查询
    vectorStore_guides_a  = SupabaseQaVectorStore(
        client=supabaseClient,
        embedding=embeddings,
        table_name='qadocuments_bge_guides',
        query_name='match_qadocuments_bge_guides_a',
    )

    res_guides_a = vectorStore_guides_a.similarity_search_by_vector(embedding=query_embedding,k=2)

    documents_guides_a = [
        (
            Document("exampleQ:\n{question}\n\nexampleA:\n{answer}\n\n{doc_url}".
                         format(question = qadoc.question_text,answer=qadoc.answer_text,doc_url = get_url_fromat_str(qadoc.metadata)))
        )
        for qadoc in res_guides_a
    ]
    
    documents += documents_guides_a

    return documents


#240418
def get_documents_bge(queryMessage):
    #获取查询语句的embedding
    embeddings = bgeEmbeddings()
    query_embedding = embeddings.embed_query(queryMessage)
    documents = []
    #对于guides进行查询
    documents_guides = get_documents_bge_guides_with_embedding(query_embedding)
    
    documents += documents_guides

    return documents
    
#240418
def queryQADB_bge_mutiple_table(queryMessage):

    qadocuments = get_qadocuments_with_limit(query_message=queryMessage,min_similarity=0.2)
    markdownurls = get_markdownurls_from_qadocuments(qadocuments)
    documents = get_langchain_documents_from_qadocuments(qadocuments)

    document_prompt = PromptTemplate(
        input_variables=["page_content"],
        template="{page_content}"
    )
    document_variable_name = "context"
    stuff_prompt = PromptTemplate.from_template(
        """
你是一个教育知识库的专家，你将根据知识库中的内容回答用户问题。知识库的内容将以如下格式给出。\
```
exampleQ:
什么是python
exampleA:
python 是一个编程语言
exampleUrl:
http://www.example.com
```
其中，exampleQ是知识库中的标题，描述了知识的主题，exampleA对应了exampleQ的答案或具体内容, \
exampleUrl是当前exampleA与exampleQ的参考链接。exampleUrl可能缺失。\
你将接收到用户提出的问题，并提取上述知识库中的相关信息来回答问题。如果发现知识库中不存在任何与用户提问相关的信息，则严格输出一行字符串,不要对该字符串做任何修改："很抱歉，我没有找到相关信息"；\
否则输出多组回答。

下面是知识库相关文档：
```
{context}
```
下面是用户的问题：
```
用户问题：{question}
```
请按前面的要求输出回答。
"""
    )
#并附上参考链接。参考链接必须附带。
# ！请注意！输出中，不得修改任何知识库中的链接。切记！
    endpoint_url = ChatGLM3_endpoint_url
    # llm = OpenAI(max_tokens=-1,temperature=0.3)
    llm = ChatGLM3(
            endpoint_url=endpoint_url,
            max_tokens=2000,
            top_p=0.3,
            verbose=True,
            timeout=120
        )
    llm_chain = LLMChain(llm=llm, prompt=stuff_prompt,verbose=True)
    
    stuff_chain = StuffDocumentsChain(
        llm_chain=llm_chain,
        document_prompt= document_prompt,
        document_variable_name= document_variable_name
    )
    res = stuff_chain.invoke({'input_documents':documents,'question':queryMessage})
    

    markdownurls_text = "官方文档参考链接："
    for url in markdownurls:
        markdownurls_text += '\n\n' + url
    response_text = res['output_text'] + "\n\n" + markdownurls_text

    return response_text

#240421
def queryQADB_bge_mutiple_table_for_wechat(queryMessage):

    qadocuments = get_qadocuments_with_limit(query_message=queryMessage,min_similarity=0.2)
    markdownurls = get_markdownurls_from_qadocuments(qadocuments)
    documents = get_langchain_documents_from_qadocuments(qadocuments)

    document_prompt = PromptTemplate(
        input_variables=["page_content"],
        template="{page_content}"
    )
    document_variable_name = "context"
    stuff_prompt = PromptTemplate.from_template(
        """
你是一个教育知识库的专家，你将根据知识库中的内容回答用户问题。知识库的内容将以如下格式给出。\
```
exampleQ:
什么是python
exampleA:
python 是一个编程语言
```
其中，exampleQ是知识库中的标题，描述了知识的主题，exampleA对应了exampleQ的答案或具体内容。
你将接收到用户提出的问题，并提取上述知识库中的相关信息来回答问题。如果发现知识库中不存在任何与用户提问相关的信息，则严格输出一行字符串,不要对该字符串做任何修改："很抱歉，我没有找到相关信息"，\
否则输出多组回答。
下面是知识库相关文档：
```
{context}
```
下面是用户的问题：
```
用户问题：{question}
```
回答：
"""
    )
#并附上参考链接。参考链接必须附带。
# ！请注意！输出中，不得修改任何知识库中的链接。切记！
    endpoint_url =ChatGLM3_endpoint_url
    # llm = OpenAI(max_tokens=-1,temperature=0.3)
    llm = ChatGLM3(
            endpoint_url=endpoint_url,
            max_tokens=2000,
            top_p=0.3,
            verbose=True,
            timeout=120
        )
    llm_chain = LLMChain(llm=llm, prompt=stuff_prompt,verbose=True)
    
    stuff_chain = StuffDocumentsChain(
        llm_chain=llm_chain,
        document_prompt= document_prompt,
        document_variable_name= document_variable_name
    )
    res = stuff_chain.invoke({'input_documents':documents,'question':queryMessage})
    
    wechat_exampleQ_urls = [
        (
            (qadoc.question_text,qadoc.metadata["doc_url"])
        )
        for qadoc in qadocuments
    ]

    return  (res['output_text'],wechat_exampleQ_urls)