import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY is missing. Add it to the .env file.")

loader = DirectoryLoader(
    path="./papers",
    glob="**/*.pdf",
    loader_cls=PyPDFLoader,
    show_progress=True,
    use_multithreading=True,
)
docs = loader.load()

MARKDOWN_SEPARATORS = [
    "\n#{1,6} ",
    "```\n",
    "\n\\*\\*\\*+\n",
    "\n---+\n",
    "\n___+\n",
    "\n\n",
    "\n",
    " ",
    "",
]

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1200,
    chunk_overlap=200,
    add_start_index=True,
    strip_whitespace=True,
    separators=MARKDOWN_SEPARATORS,
)
splits = text_splitter.split_documents(docs)

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vector_store = FAISS.from_documents(
    splits,
    embeddings,
    distance_strategy=DistanceStrategy.COSINE,
)
vector_store.save_local("faiss_index")

retriever = vector_store.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"score_threshold": 0.2, "k": 5},
)


def format_documents(documents):
    return "\n\n".join(
        f"[Source: {Path(doc.metadata['source']).name}, page {doc.metadata['page'] + 1}]\n"
        f"{doc.page_content}"
        for doc in documents
    )


prompt = ChatPromptTemplate.from_template(
    """You are a rigorous research analyst specializing in Brazilian Jiu-Jitsu.

Rules:
1. Answer using only the supplied context.
2. Do not invent facts or use outside knowledge.
3. If the context is insufficient, say: "Tôi không biết dựa trên tài liệu được cung cấp."
4. Put an exact [Source: filename, page N] citation after every factual sentence or bullet.
5. Answer in English when the question is English and in Vietnamese when the question is Vietnamese.

Context:
{context}

Question: {question}

Answer:"""
)

llm = ChatOpenAI(
    model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
    temperature=0,
)

rag_chain = (
    {
        "context": retriever | RunnableLambda(format_documents),
        "question": RunnablePassthrough(),
    }
    | prompt
    | llm
    | StrOutputParser()
)

print(f"Indexed {len(splits)} chunks from {len(docs)} PDF pages.")
question = input("Question: ").strip()
if not question:
    raise ValueError("Question cannot be empty.")

print(f"\nAnswer:\n{rag_chain.invoke(question)}")
