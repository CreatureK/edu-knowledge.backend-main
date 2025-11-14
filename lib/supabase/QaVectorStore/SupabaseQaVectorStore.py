from __future__ import annotations

import uuid
import warnings
from itertools import repeat
from typing import (
    TYPE_CHECKING,
    Any,
    Coroutine,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
    Type,
    Union,
)

from langchain_core.embeddings import Embeddings
from lib.QaVectorStore.QaVectorStore import QaVectorStore,QaDocument
from lib.supabase.initSupabaseClient import supabaseClient
# if TYPE_CHECKING:
import supabase
import logging

class SupabaseQaVectorStore(QaVectorStore):
    def __init__(
        self,
        client: supabase.Client,
        embedding: Embeddings,
        table_name: str = "",
        query_name: Union[str,None] = None,    
        chunk_size: int = 500,
    )->None:
        self._client = client
        self._embedding: Embeddings = embedding
        self.table_name = table_name or "documents"
        self.query_name = query_name or "match_documents"
        self.chunk_size = chunk_size or 500
    

    def add_QaTexts(
            self, 
            question_texts: Iterable[str], 
            answer_texts: Iterable[str], 
            metadatas: List[Dict] | None = None, 
            **kwargs: Any
    ) -> List[str]:
        ids = [str(uuid.uuid4()) for _ in question_texts]
        docs = self._QaTexts_to_QaDocuments(question_texts,answer_texts,metadatas)
        question_vectors = self._embedding.embed_documents(list(question_texts))
        answer_vectors = self._embedding.embed_documents(list(answer_texts))

        return self.add_QaVectors(question_vectors,answer_vectors,docs,ids)
    
    @staticmethod 
    def _QaTexts_to_QaDocuments(
        question_texts: Iterable[str], 
        answer_texts: Iterable[str], 
        metadatas: Optional[Iterable[Dict[Any, Any]]] = None,
    )->List[QaDocument]:
        """Return list of QaDocuments from list of texts and metadatas."""
        if metadatas is None:
            metadatas = repeat({})
        docs = [
            QaDocument(question_text=question_text,answer_text=answer_text,metadata=metadata)
            for question_text,answer_text,metadata in zip(question_texts,answer_texts,metadatas)
        ]
        return docs
           

    @property
    def embeddings(self) -> Embeddings:
        return self._embedding

    def add_QaVectors(
        self,
        question_vectors: List[List[float]],
        answer_vectors: List[List[float]],
        qaDocuments: List[QaDocument],
        ids:List[str] = None,
    ) -> List[str]:
        return self._add_QaVectors(
            self._client,
            self.table_name,
            question_vectors,
            answer_vectors,
            qaDocuments,
            ids,
            self.chunk_size 
        )

    @staticmethod
    def _add_QaVectors(
        client: supabase.Client,
        table_name: str, 
        question_vectors: List[List[float]],
        answer_vectors: List[List[float]],
        qaDocuments: List[QaDocument],
        ids:List[str] = None,
        chunk_size:int = 500
    ) -> List[str]:
        """add vectors to supabase table"""
        if ids is None : 
            ids = [str(uuid.uuid4()) for _ in question_vectors]
        # print(len(ids),len(qaDocuments))
        rows: List[Dict[str,Any]] = [
            {
                "id": id,
                "question_content": qaDocuments[idx].question_text,
                "answer_content": qaDocuments[idx].answer_text,
                "question_embedding": question_vectors[idx],
                "answer_embedding": answer_vectors[idx],
                "metadata": qaDocuments[idx].metadata
            }
            for idx,id in enumerate(ids)
        ]
        id_list: List[str] = []
        for i in range(0, len(rows), chunk_size):
            chunk = rows[i : i + chunk_size]

            result = client.from_(table_name).upsert(chunk).execute()  # type: ignore

            if len(result.data) == 0:
                raise Exception("Error inserting: No rows added")

            # VectorStore.add_vectors returns ids as strings
            ids = [str(i.get("id")) for i in result.data if i.get("id")]

            id_list.extend(ids)
        return id_list
    
    def similarity_search(self, 
        query: str, 
        k: int = 4, 
        filter: Optional[Dict[str,Any]] = None,
        **kwargs: Any
    ) -> List[QaDocument]:
        vector = self._embedding.embed_query(query)
        return self.similarity_search_by_vector(vector,k=k,filter=filter,**kwargs)
    
    def similarity_search_by_vector(
            self,
            embedding: List[float],
            k: int = 4,
            filter: Optional[Dict[str,Any]] = None,
            **kwargs: Any
    )-> List[QaDocument]:
        result = self.similarity_search_by_vector_with_relevance_scores(
            embedding, k=k, filter=filter, **kwargs
        )
        qa_documents = [doc for doc,_ in result]
        # logging.info(qa_documents[0].metadata)
        return qa_documents
    
    def similarity_search_with_relevance_scores(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> List[Tuple[QaDocument, float]]:
        vector = self._embedding.embed_query(query)
        return self.similarity_search_by_vector_with_relevance_scores(
            vector, k=k, filter=filter, **kwargs
        )
    
    def match_args(
        self, query: List[float], filter: Optional[Dict[str, Any]] 
    ) -> Dict[str,Any]:
        ret: Dict[str,Any] = dict(query_embedding=query)
        if filter:
            ret["filter"] = filter
        return ret

    def similarity_search_by_vector_with_relevance_scores(
        self,
        query: List[float],
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None,
        postgrest_filter: Optional[str] = None,
        score_threshold: Optional[float] = None,
    ) -> List[Tuple[QaDocument,float]]:
        match_documents_params = self.match_args(query, filter)
        query_builder = self._client.rpc(self.query_name,match_documents_params)

        if postgrest_filter:
            query_builder.params = query_builder.params.set(
                "and", f"({postgrest_filter})"
            )
        query_builder.params = query_builder.params.set("limit", k)
        res = query_builder.execute()


        match_result = [
            (
                QaDocument(
                    metadata = search.get("metadata",{}),
                    question_text=search.get("question_content",""),
                    answer_text=search.get("answer_content","")
                ),
                search.get('similarity',0.0)
            )
            for search in res.data
            if search.get("question_content")
        ]
        # print(res)

        return match_result
    
    def delete(
        self, 
        ids: List[str] | None = None, 
        **kwargs: Any
    ) -> TYPE_CHECKING | None:
        if ids is None:
            raise ValueError("No ids provided to delete.")
        rows: List[Dict[str,Any]] = [
            {
                "id":id,
            }
            for id in ids
        ]
        for row in rows:
            self._client.from_(self.table_name).delete().eq("id",row["id"]).execute()

    @classmethod 
    def from_QaTexts(
        cls: type["SupabaseQaVectorStore"], 
        question_texts: List[str], 
        answer_texts: List[str], 
        embedding: Embeddings, 
        metadatas: List[Dict] | None = None,
        client: Optional[supabase.Client] = None,
        table_name:Optional[str] = "qadocuments",
        query_name: Union[str,None] = "match_qadocuments" ,
        chunk_size: int = 500,
        ids: Optional[List[str]] = None,
        **kwargs: Any
    ) -> "SupabaseQaVectorStore":
        if not client:
            raise ValueError("Supabase client is required.")
        if not table_name:
            raise ValueError("Supabase qadocuments table_name is required.")
        question_vectors = embedding.embed_documents(question_texts)
        answer_vectors = embedding.embed_documents(answer_texts)
        ids = [str(uuid.uuid4()) for _ in question_vectors ]
        docs = cls._QaTexts_to_QaDocuments(question_texts,answer_texts,metadatas)
        cls._add_QaVectors(client,table_name,question_vectors,answer_vectors,ids,chunk_size)

        return cls(
            client=client,
            embedding=embedding,
            table_name=table_name,
            query_name=query_name,
            chunk_size=chunk_size
        )