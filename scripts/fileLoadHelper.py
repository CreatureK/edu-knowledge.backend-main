from __future__ import annotations

import os
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List
)
from lib.supabase.initSupabaseClient import supabaseClient
from lib.QaVectorStore.QaVectorStore import QaDocument
from lib.supabase.QaVectorStore import SupabaseQaVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAI
from langchain.chains import (
    StuffDocumentsChain,
    LLMChain,
    ReduceDocumentsChain,
    MapReduceDocumentsChain,
)
from langchain_community.llms.chatglm3 import ChatGLM3
import json

class FileLoadHelper():
    def __init__(
            self,
    )->None:
        pass
    
    @staticmethod
    def upsert_from_file(file):
        res:List[str]
        data = json.load(file)
        res = FileLoadHelper.upsert_from_formatJsonList(data)
        return res

    

    @staticmethod
    def upsert_from_file_path(filepath):
        # str.
        res:List[str]
        if(filepath.endswith('.json')):
            with open(filepath, 'r') as file:
                data = json.load(file)
                res = FileLoadHelper.upsert_from_formatJsonList(data)

        return res

    @staticmethod
    def upsert_from_formatJsonList(f_json_list: List[Dict[Any,Any]]):
        question_texts = []
        answer_texts = []

        for qa_json in f_json_list:
            question_texts.append(qa_json['exampleQ']),
            answer_texts.append(qa_json['exampleA'])

        embeddings = OpenAIEmbeddings()
        vectorStore = SupabaseQaVectorStore(
            client=supabaseClient,
            embedding=embeddings,
            table_name='qadocuments',
            query_name='match_qadocuments',
        )

        return vectorStore.add_QaTexts(question_texts,answer_texts)
    
    @staticmethod
    def get_formatJsonList_from_text(text:str):
        stuff_prompt = PromptTemplate(
            input_variables=["context"],
            template=
"""
我希望你扮演一个数据处理师，来处理一些文本后得到格式化的json文本，下面是json字段的描述：
字段"exampleQ"代表一个问题或者一段摘要总结，字段"exampleA"是字段"exampleQ"中问题的答案或者摘要总结的具体内容,exampleQ，exampleA总是成对出现。
下面你将接受到很多文本，提取适当多个问题、摘要形成多个exampleQ，对应的答案、具体内容形成exampleA,尽可能保留信息,尽可能细化问题，不要添加文本外的信息。exampleQ，exampleA总是要成对出现。
将下列六个反括号括起来的文本是需要你处理的文本,最后形成Json列表,PYthon可读的list[dict]输出。
``````
{context}
``````
"""
        )
        document_prompt = PromptTemplate(
        input_variables=["page_content"],
        template="{page_content}" 
        )
        
        document_variable_name = "context"
        doc = Document(text)
        
        # endpoint_url = "http://10.10.109.2:8000/v1/chat/completions"
        llm = OpenAI(max_tokens=-1,temperature=0.3)
        # llm = ChatGLM3(
        #     endpoint_url=endpoint_url,
        #     max_tokens=80000,
        #     top_p=0.3
        # )

        llm_chain = LLMChain(llm=llm,prompt=stuff_prompt)
        stuff_chain = StuffDocumentsChain(
            llm_chain=llm_chain,
            document_prompt= document_prompt,
            document_variable_name= document_variable_name
        )

        res = stuff_chain.invoke({'input_documents':[doc]})
        json_list = json.loads(res["output_text"])
        return json_list
        