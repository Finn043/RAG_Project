import os

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY is missing. Add it to the .env file.")

query = "What are the common injuries in Brazilian Jiu-Jitsu?"

for model in ("text-embedding-3-small", "text-embedding-3-large"):
    vector = OpenAIEmbeddings(model=model).embed_query(query)
    print(f"{model}: {len(vector)} dimensions")
