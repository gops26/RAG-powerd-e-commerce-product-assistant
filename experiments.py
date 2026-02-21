from sarvamai import SarvamAI
import os
import requests
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from dotenv import load_dotenv
from pydantic import BaseModel, Field, model_validator

load_dotenv()

api_key = os.environ["SARVAM"]

class Product(BaseModel):
    title:str = Field(description="a breif title for the product citing the name of the product")
    description:str = Field(description="a breif description about the product")
    price:str = Field(description="a reasonable price of the product")

    @model_validator(mode='before')
    @classmethod
    def unwrap_list(cls, v: object) -> object:
        if isinstance(v, list) and len(v) > 0:
            return v[0]
        return v


class Chunk(BaseModel):
    title: str = Field(description="A brief title for this chunk of product, typically 3,4 words that is most likely surfaced in a query")
    summary: str = Field(description="A few sentence summarizing the chunk about the product to answer questions")
    original_text: str = Field(description="The original text of this chunk from the provided document, exactly as is, not changed in any way")


class Chunks(BaseModel):
    chunks: list[Chunk]



messages = [
    
    {"role":"user", "content":"generate 1 product data"}
    ]


llm = ChatOpenAI(
    base_url = "https://api.sarvam.ai/v1",
    api_key=api_key,
    model="sarvam-m",
)

parser = PydanticOutputParser(pydantic_object=Chunks)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Respond only with valid JSON that matches the required format.\n{format_instructions}"),
])

chain = prompt | llm | parser

def get_response(messages):
    return chain.invoke(messages)



