from lib.QaVectorStore.QaVectorStore import QaVectorStore,QaDocument
from lib.Embeddings import bgeEmbeddings
from langchain_core.documents import Document
from lib.supabase.QaVectorStore import SupabaseQaVectorStore
from lib.supabase.initSupabaseClient import supabaseClient
from typing import List,Dict, Tuple

def get_markdownurls_from_qadocuments(qadocuments: List[QaDocument]) -> List[str]: 
    markdownurls = [
        (
            "[{exampleQ}]({exampleUrl})".
                        format(exampleQ = qadoc.question_text,exampleUrl = qadoc.metadata["doc_url"])
        )
        for qadoc in qadocuments
    ]

    return markdownurls

def get_url_fromat_str(metadata:dict) :
    if("doc_url" in metadata.keys()): return "exampleUrl:\n" + metadata['doc_url']
    else : return ""

def get_langchain_documents_from_qadocuments(qadocuments: List[QaDocument]) -> List[Document]:
    # documents = [
    #         (
    #             Document("exampleQ:\n{question}\n\nexampleA:\n{answer}\n\n{doc_url}".
    #                             format(question = qadoc.question_text,answer=qadoc.answer_text,doc_url = get_url_fromat_str(qadoc.metadata)))
    #         )
    #         for qadoc in qadocuments
    #     ]
    documents = [
        (
            Document("exampleQ:\n{question}\n\nexampleA:\n{answer}".
                            format(question = qadoc.question_text,answer=qadoc.answer_text))
        )
        for qadoc in qadocuments
    ]
    return documents

def get_qadocuments_from_table_by_embedding_with_similarity(embedding,table_name,query_name,k=4) -> List[Tuple[QaDocument,float]]:
    VectorStore = SupabaseQaVectorStore(
        client=supabaseClient,
        embedding=None,
        table_name=table_name,
        query_name=query_name
    )
    return VectorStore.similarity_search_by_vector_with_relevance_scores(query=embedding,k=k)

def get_qadocuments_from_table_by_embedding(embedding,table_name,query_name,k=4) -> List[Tuple[QaDocument,float]]:
    result = get_qadocuments_from_table_by_embedding_with_similarity(
            embedding,table_name,query_name,k
        )
    qa_documents = [doc for doc,_ in result]
    # logging.info(qa_documents[0].metadata)
    return qa_documents

def get_documents_bge_guides_by_embedding_with_similartity(query_embedding) -> List[Tuple[QaDocument,float]]:
 #对于guides进行查询
    result_q = get_qadocuments_from_table_by_embedding_with_similarity(
        query_embedding,table_name='qadocuments_bge_guides',query_name='match_qadocuments_bge_guides_q')
    
    result_a = get_qadocuments_from_table_by_embedding_with_similarity(
        query_embedding,table_name='qadocuments_bge_guides',query_name='match_qadocuments_bge_guides_a')
    

    return result_q + result_a


def get_qadocuments_with_limit( query_message,embeddings = bgeEmbeddings(),min_similarity: float = 0.5,max_length:int = -1) -> List[QaDocument]:
    query_embedding = embeddings.embed_query(query_message)
    qadocuments = []
    guides = get_documents_bge_guides_by_embedding_with_similartity(query_embedding)
    guides_qadocuments = [ qadoc for qadoc,_ in guides if _ > min_similarity]
    qadocuments += guides_qadocuments

    
    return qadocuments