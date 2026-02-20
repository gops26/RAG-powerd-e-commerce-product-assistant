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


def get_response(messages) -> Chunks:
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "anthropic/claude-instant-1.1",
            "messages":messages,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "Chunks",
                    "strict": True,
                    "schema": Chunks.model_json_schema()
                }
            }
        }
    )

    data = response.json()
    if "error" in data:
        raise RuntimeError(f"API error: {data['error']}")
    raw = data["choices"][0]["message"]["content"]
    return Chunks.model_validate_json(raw)



# client = SarvamAI(api_subscription_key=api_key)

messages = [
    
    {"role":"user", "content":"generate 1 product data"}
    ]
# response = client.chat.completions( messages =messages)

# print(response)
# print()
# print()
# print(response["choices"][0]["message"]["content"])

llm = ChatOpenAI(
    base_url = "https://api.sarvam.ai/v1",
    api_key=api_key,
    model="sarvam-m",
)

parser = PydanticOutputParser(pydantic_object=Product)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Respond only with valid JSON that matches the required format.\n{format_instructions}"),
    ("human", "{input}"),
])

chain = prompt | llm | parser

res = chain.invoke({
    "input": "generate 1 product data",
    "format_instructions": parser.get_format_instructions(),
})

res1 = chain.invoke({
    "input": "generate 1 product data",
    "format_instructions": parser.get_format_instructions(),
})

class ProductLoader:

    def __init__(self, llm:ChatOpenAI, parser:PydanticOutputParser):
        self.n_products = 30
        self.llm = llm
        self.parser= parser
        self.message_store: list[Product] = []
        self._prompt = self.load_prompt().partial(
            format_instructions=self.parser.get_format_instructions()
        )
        self._chain = self._prompt | self.llm | self.parser

    @staticmethod
    def load_prompt():
        return ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant creating products to the customer.You are needed to create ```products``` on user's request. Do Not Create Same products repeatedly.  Respond only with valid JSON that matches the required format.\n{format_instructions}"),
            ("human", "{input}"),
        ])
    
    def generate_products(self, llm_input:str):
        try:
            for i in range(self.n_products):
                product_response = self._chain.invoke({"input":llm_input})
                self.message_store.append(product_response)
                print("product - {} created ".format(i))
            print( f"Total of {self.n_products} Products created successfully")
            self.create_products_jsonl_file()
            return "created file"
        except Exception as e: print(e)

    def create_products_jsonl_file(self, filepath: str = "products.jsonl"):
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                for product in self.message_store:
                    f.write(product.model_dump_json() + "\n")

        except Exception as e:
            print(e)

if __name__ == "__main__":
    product_loader = ProductLoader(llm=llm, parser=parser)
    product_loader.generate_products("create diverse products")