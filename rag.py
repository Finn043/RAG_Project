import os
from dataclasses import dataclass
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

EMBEDDING_MODEL = "text-embedding-3-small"
DEFAULT_CHAT_MODEL = "gpt-4o-mini"

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

PROMPT = ChatPromptTemplate.from_template(
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


@dataclass(frozen=True)
class RAGSystem:
    chain: object
    chunk_count: int
    page_count: int
    pdf_count: int
    chat_model: str


def format_documents(documents):
    return "\n\n".join(
        f"[Source: {Path(doc.metadata['source']).name}, page {doc.metadata['page'] + 1}]\n"
        f"{doc.page_content}"
        for doc in documents
    )


def cosine_relevance_score(squared_l2_distance: float) -> float:
    """Convert FAISS squared L2 distance for unit vectors to cosine similarity."""
    return 1.0 - (squared_l2_distance / 2.0)


def build_rag_system(
    papers_dir: str | Path = "papers",
    index_dir: str | Path = "faiss_index",
) -> RAGSystem:
    load_dotenv()

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is missing. Add it to the .env file.")

    papers_path = Path(papers_dir)
    pdf_files = sorted(papers_path.glob("**/*.pdf"))
    if not pdf_files:
        raise FileNotFoundError(f"No PDF files found in {papers_path.resolve()}.")

    loader = DirectoryLoader(
        path=str(papers_path),
        glob="**/*.pdf",
        loader_cls=PyPDFLoader,
        show_progress=True,
        use_multithreading=True,
    )
    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=200,
        add_start_index=True,
        strip_whitespace=True,
        separators=MARKDOWN_SEPARATORS,
    )
    splits = text_splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
    vector_store = FAISS.from_documents(
        splits,
        embeddings,
        distance_strategy=DistanceStrategy.COSINE,
        relevance_score_fn=cosine_relevance_score,
    )
    vector_store.save_local(str(index_dir))

    retriever = vector_store.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"score_threshold": 0.2, "k": 5},
    )

    chat_model = os.getenv("OPENAI_CHAT_MODEL", DEFAULT_CHAT_MODEL)
    llm = ChatOpenAI(model=chat_model, temperature=0)
    chain = (
        {
            "context": retriever | RunnableLambda(format_documents),
            "question": RunnablePassthrough(),
        }
        | PROMPT
        | llm
        | StrOutputParser()
    )

    return RAGSystem(
        chain=chain,
        chunk_count=len(splits),
        page_count=len(docs),
        pdf_count=len(pdf_files),
        chat_model=chat_model,
    )
