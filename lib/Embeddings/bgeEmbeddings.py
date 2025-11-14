
from typing import List
from langchain_core.embeddings import Embeddings
import requests
class bgeEmbeddings(Embeddings):

    url = "http://10.10.109.2:8001/v1/getembedding"

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embeddings=[]
        for text in texts:
            data = {
                "text":text
            }
            response = requests.post(url=self.url,json=data)
            if(response.status_code!=200) : raise Exception(f"get embedding faied with {response.status_code}")
            response_data = response.json()

            # 检查响应的内容是否是一个列表
            if not isinstance(response_data, list):
                raise Exception("Unexpected response format")
            float_list = [float(item) for item in response_data]
            embeddings.append(float_list)
        return  embeddings

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]

    def __init__(
        self,
    )->None:
        pass