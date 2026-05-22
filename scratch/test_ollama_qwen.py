from langchain_ollama import ChatOllama
from pydantic import BaseModel

class Person(BaseModel):
    name: str
    age: int

try:
    llm = ChatOllama(model="qwen2.5:latest", temperature=0)
    structured_llm = llm.with_structured_output(Person)
    res = structured_llm.invoke("My name is John and I am 30 years old")
    print(res)
except Exception as e:
    print("FAILED:", e)
