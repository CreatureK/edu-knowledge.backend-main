

from __future__ import annotations


from langchain_core.embeddings import Embeddings
import logging
import math
import warnings
from abc import ABC,abstractmethod

from typing import Any, List, Literal

from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Collection,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
)

class QaDocument():
    # question_text: str
    # answer_text: str
    # metadata: dict = {}
    type: Literal["QaDocument"]="QaDocument"

    def __init__(self, question_text: str,answer_text: str,metadata: dict={}, **kwargs: Any) -> None:
        self.question_text = question_text
        self.answer_text = answer_text
        self.metadata = metadata


logger = logging.getLogger(__name__)

QAVST = TypeVar("QAVST",bound="QaVectorStore")

class QaVectorStore(ABC):
    """Interface for Qa vector store"""

    @abstractmethod
    def add_QaTexts(
        self,
        question_texts: Iterable[str],
        answer_texts: Iterable[str],
        metadatas: Optional[List[dict]] = None,
        **kwargs: Any,
    ) -> List[str]:
        """Run more qaTexts
        
        Args:
            question_texts: question string to add to the qavectorstore.
            answer_texts: answer string to add to the answer qavectorstore.
            metadatas: Optional list of metadatas associated with the qa.
        
        Returns:
        List of ids from adding the texts into the vectorstore
        """
    @property
    def embedding(self) -> Optional[Embeddings]:
        """Access the query embedding object if available"""
        logger.debug(
            f"{Embeddings.__name__} is not implemented for {self.__class__.__name__}"
        )
        return None
    def delete(self,ids: Optional[List[str]] = None, **kwargs:Any) -> Optional[bool]:
        """Delete by vector ID or other criteria."""

        raise NotImplementedError("delete method must be implemented by subclass.")
    
    async def adelete(
        self,ids: Optional[List[str]] = None, **kwargs:Any
    ) -> Optional[bool]:
        """Delete by vector ID or other criteria."""

    async def add_QaTexts(
        self,
        question_texts: Iterable[str],
        answer_texts: Iterable[str],
        metadatas: Optional[List[dict]] = None,
        ids: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> List[str]:
       """Run more texts through the embeddings and add to the Qavectorstore."""
    
    def add_QaDocuments(self, qaDocuments: List[QaDocument], **kwargs: Any) -> List[str]:
        question_texts = [doc.question_content for doc in qaDocuments]
        answer_texts = [doc.answer_content for doc in qaDocuments]
        metadatas = [doc.metadata for doc in qaDocuments]
        return self.add_QaTexts(question_texts,answer_texts, metadatas, **kwargs)
    
    @abstractmethod
    def similarity_search(
        self, query: str, k: int = 4, **kwargs: Any
    ) -> List[QaDocument]:
        """Return docs most similar to query."""

    @classmethod
    def from_documents(
        cls: Type[QAVST],
        qaDocuments: List[QaDocument],
        embedding: Embeddings,
        **kwargs: Any,
    ) -> QAVST:
        question_texts = [doc.question_content for doc in qaDocuments]
        answer_texts = [doc.answer_content for doc in qaDocuments]
        metadatas = [doc.metadata for doc in qaDocuments]
        return cls.from_QaTexts(question_texts,answer_texts, metadatas, **kwargs)
    
    @classmethod
    @abstractmethod
    def from_QaTexts(
        cls: Type[QAVST],
        question_texts: List[str],
        answer_texts: List[str],
        embedding: Embeddings,
        metadatas: Optional[List[dict]] = None,
        **kwargs: Any,
    ) -> QAVST:
        """Return VectorStore initialized from texts and embeddings."""
    
