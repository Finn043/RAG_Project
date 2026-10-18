# BJJ RAG

A Retrieval-Augmented Generation (RAG) assistant for research papers about Brazilian Jiu-Jitsu (BJJ). The production application answers questions from the included PDF corpus and cites the source file and page. The Python CLI and Streamlit app are retained as learning/demo implementations of the LangChain and FAISS pipeline.

Production: <https://bjj-research-assistant-finn043.netlify.app>

## AI pipeline

```text
PDF papers → page text → overlapping chunks → OpenAI embeddings
    → cosine-similarity retrieval → grounded prompt → gpt-4o-mini answer with citations
```

The project has two implementations of the retrieval stage:

- **Python CLI/Streamlit:** LangChain retriever backed by a local FAISS index.
- **Netlify production API:** embeds the PDF chunks and keeps vectors in a warm function instance; it computes cosine similarity directly and does not use a separate vector database.

Both use `text-embedding-3-small`, a 0.2 relevance threshold, and at most 5 chunks per question. Text is split into roughly 1,200-character chunks with 200 characters of overlap. Answers are instructed to use the retrieved context, avoid unsupported claims, and include source/page citations.

## Interview guide: AI and RAG

### Short project summary

> This is a RAG question-answering system over Brazilian Jiu-Jitsu research PDFs. I extract page text and source metadata, split the text into overlapping chunks, and embed each chunk with `text-embedding-3-small`. For a question, I embed the query, retrieve up to five chunks using cosine similarity with a 0.2 threshold, and pass the relevant text and citations to `gpt-4o-mini`. The prompt grounds the answer in those sources, and the model runs with temperature 0. The Python implementation uses LangChain LCEL and FAISS; the production function performs cosine retrieval directly over cached vectors.

### What is this project's RAG chain?

RAG stands for Retrieval-Augmented Generation. Rather than asking an LLM to answer only from its training, the application first retrieves relevant passages from its document collection and supplies them as context for the answer.

In `rag.py`, LangChain Expression Language (LCEL) connects the Python pipeline with `|`:

```python
chain = (
    {
        "context": retriever | RunnableLambda(format_documents),
        "question": RunnablePassthrough(),
    }
    | PROMPT
    | llm
    | StrOutputParser()
)
```

1. The retriever searches for documents relevant to the input question.
2. `format_documents` turns the retrieved chunks into context and adds each source filename and page number.
3. `RunnablePassthrough()` keeps the original question while the context is being retrieved.
4. The prompt template combines the context and question.
5. The LLM generates an answer, and `StrOutputParser()` returns it as plain text.

Calling `chain.invoke(question)` runs the sequence. The production API in `netlify/functions/answer.ts` follows the same conceptual flow but implements it directly in TypeScript rather than using LangChain.

### What is a prompt template, and how is it used here?

A prompt template is a reusable instruction with placeholders for request-specific data. The Python pipeline uses `ChatPromptTemplate.from_template(...)` with `{context}` and `{question}`. Production sends equivalent system and user messages.

The system prompt sets the role of a rigorous BJJ research analyst and instructs the model to:

- Answer only from the retrieved context; do not invent facts or use outside knowledge.
- Say, “I don't know based on the provided sources,” when the context is insufficient.
- Add an exact `[Source: filename, page N]` citation after every factual sentence or bullet.
- Always answer in English, even if the user submits a question in another language.

The context is retrieved for the current request; it is not model memory. Prompt rules reduce unsupported answers but cannot guarantee that the model will always follow them. Retrieval and citations still need evaluation.

### How are documents chunked and embedded?

The Python implementation loads PDFs by page with `DirectoryLoader` and `PyPDFLoader`. `RecursiveCharacterTextSplitter` creates chunks with `chunk_size=1200`, `chunk_overlap=200`, and start-index metadata. It prefers structural separators such as headings, horizontal rules, newlines, and spaces to avoid cutting text at arbitrary points where possible.

`OpenAIEmbeddings(model="text-embedding-3-small")` converts each chunk into a numerical vector that represents its semantic content. The user's question is embedded with the same model, so its vector can be compared with the chunk vectors. Source filename and page are retained as metadata for citations.

In production, PDF.js extracts text by page. The function chunks it at roughly 1,200 characters with 200 characters of overlap, requests embeddings for the chunks, and caches the resulting vectors in the running function instance. A warm instance can reuse that index for later questions; a cold start may need to rebuild it and incur embedding usage again.

### Which vector store does the project use?

The **Python pipeline uses FAISS**, through `langchain_community.vectorstores.FAISS`. `FAISS.from_documents(splits, embeddings, ...)` builds an index from the document chunks and their embeddings. `save_local()` writes the index to `faiss_index/`.

The **production API does not currently use FAISS or a managed vector database**. It keeps chunk vectors in memory and computes cosine similarity directly in `server/rag-core.ts`. This is a simple fit for the project's small, fixed corpus, but the index is not persisted or shared across function instances. A cold start can rebuild it.

### What is the distance strategy?

A distance strategy defines how the system compares the query vector with document vectors. The Python FAISS store is configured with `distance_strategy=DistanceStrategy.COSINE`. Cosine similarity compares vector direction: a higher score means the vectors are more similar. Unlike raw Euclidean distance, it is not directly driven by vector magnitude.

The Python code supplies `relevance_score_fn=cosine_relevance_score`, which converts FAISS squared L2 distance into a cosine-like relevance score using `1 - (squared_l2_distance / 2)`. This conversion is equivalent to cosine similarity when both vectors are normalized to unit length. Production calculates cosine similarity directly. Be clear about the distinction: higher similarity/relevance is better, while lower distance is better.

### How does the retriever work? What are `search_type` and `search_kwargs`?

A LangChain retriever provides a common interface for looking up documents relevant to a query. Here it embeds the query, searches the FAISS index, applies the selected search policy, and returns matching documents to the context-formatting step.

```python
retriever = vector_store.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"score_threshold": 0.2, "k": 5},
)
```

- **`search_type`** selects the retrieval method. `similarity_score_threshold` ranks by relevance and filters out documents whose score is below the threshold. Unlike plain `similarity`, it can return fewer than `k` documents—or none—when the matches are too weak.
- **`search_kwargs`** passes options to that method. `score_threshold=0.2` is the minimum relevance score; `k=5` sets the maximum number of chunks to return.
- **The threshold is 0.2.** It is a relevance/similarity score threshold, not a distance of 0.2. In Python it is applied to the score from `cosine_relevance_score`; in production, `selectRelevant()` keeps chunks whose direct cosine similarity is at least 0.2.
- **`k=5` is a maximum, not a guarantee.** The threshold can reduce the number of returned chunks.

The 0.2 threshold is the project's current setting, not a universally optimal value. A threshold that is too low may admit weak context; one that is too high may discard useful evidence. A representative evaluation set can be used to tune threshold and top-k and measure retrieval precision, recall, and ranking quality.

### Which LLM and temperature does it use?

The chat model is **`gpt-4o-mini`**. The Python implementation allows `OPENAI_CHAT_MODEL` to override the default. The production function currently sets `gpt-4o-mini` directly.

The **temperature is `0`** in both implementations. This reduces randomness and tends to make answers more consistent. Temperature alone does not prevent hallucinations; good retrieval, grounded instructions, and citation checks are still necessary.

### End-to-end flow

```text
Indexing:
PDF pages → text chunks (1,200 chars; 200 overlap) → chunk embeddings
          → local FAISS index (Python) / in-memory vectors (production)

Question answering:
question → query embedding → cosine retrieval (threshold 0.2; max 5 chunks)
         → source/page context → grounded prompt → gpt-4o-mini (temperature 0)
         → English answer with citations
```

### Why use RAG instead of asking an LLM directly?

The answers should be based on a specific collection of research papers. RAG supplies evidence from those papers and provides page-level citations that a reader can verify. It also allows the source collection to be updated without fine-tuning the model. RAG does not train the LLM: embeddings and retrieval find relevant context, and the LLM synthesizes an answer from that context.

### Current limitations and honest interview talking points

- Chat history is only displayed in the web app. Each question is retrieved independently; there is no conversational memory or query rewriting.
- The production corpus is small and fixed, so direct in-memory retrieval keeps the implementation simple. A larger corpus or higher traffic would call for a persistent vector database, a separate indexing pipeline, and an index shared across instances.
- Chunking is character-based rather than token- or section-aware. It could be improved with heading-aware/token-aware splitting and richer metadata.
- The threshold and top-k have not been tuned against a formal evaluation set. Build representative queries with expected source passages, then measure retrieval quality and answer/citation quality.
- The model is asked to produce citations, but the application does not independently prove that every citation supports its claim. Citation correctness should be evaluated against the original PDF pages.
- Python and production share the same retrieval policy but have different implementations: LangChain + FAISS in Python, PDF.js + direct cosine similarity in production. Changes should be tested in both paths.
- RAG reduces the risk of unsupported answers but does not eliminate hallucinations; retrieval can miss evidence and the model can misinterpret it.

### Common follow-up questions

**What happens if no chunks meet the threshold?** The retriever may return no documents. The prompt tells the model to say it does not know when the context is insufficient; production supplies an explicit “No relevant context was found” message in that case.

**Does `k=5` mean the system always returns five chunks?** No. It is an upper limit. The score threshold may leave fewer than five results.

**Are embeddings the answer?** No. Embeddings are vectors used to find semantically relevant passages. The LLM generates the answer after those passages are added to the context.

**Does RAG eliminate hallucinations?** No. It grounds answers in retrieved sources and asks for citations, but retrieval can be wrong or incomplete and the model can still misstate evidence.

**How would you improve the system?** Create a labeled evaluation set with questions, expected passages, and expected answers. Measure retrieval before changing the prompt or model; test chunking, top-k, threshold, and hybrid search; persist the index; and monitor latency, token usage, failures, and citation quality.

### Adding a new research paper

1. Add the PDF to the repository's `papers/` directory. Use a text-searchable PDF; scanned/image-only papers need OCR before this pipeline can retrieve their contents.
2. Check that the PDF opens, pages contain extractable text, and the filename is descriptive. Preserve the original page order because citations use PDF page numbers.
3. Run the Python CLI (`python chatbot.py`) or the Streamlit app to rebuild and inspect the local FAISS index. The Python pipeline reads all PDFs and recreates the index when it starts; check that the new paper contributes pages/chunks and that test questions retrieve the expected pages.
4. Commit and push the PDF to the production branch, then deploy the site. The PDF is included in the Netlify Function bundle. Production rebuilds the corpus embeddings when a function instance initializes; a warm instance reuses its cache, while a cold start can embed again.
5. Test several questions whose answers are present in the new paper, verify each citation against the original PDF page, and also test an unsupported question to check that the system abstains. Monitor function logs and OpenAI usage after deployment.

Adding a PDF does not require fine-tuning the LLM. It does require rebuilding/redeploying so production receives the new file, and embedding calls may incur API usage when the production index is rebuilt. The current corpus is small enough for this approach; for a growing corpus, move indexing to a persistent vector database and avoid rebuilding all embeddings on each cold start.

## Setup

Requirements: Node.js 24 (see `.nvmrc`) and Python 3.12 or later for the optional Python tools.

```bash
git clone https://github.com/Finn043/RAG_Project.git
cd RAG_Project
npm install
```

For the Python CLI or demo app:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

## Configuration

Create a local environment file from the template:

```bash
cp .env.example .env
```

Set your API key and, optionally, a chat model:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_CHAT_MODEL=gpt-4o-mini
```

Never commit or share `.env`; it is listed in `.gitignore`. The API key is read on the server and must not be exposed in client code.

## Embedding model comparison

```bash
python embedding_demo.py
```

The script compares the output dimensions of `text-embedding-3-small` (1,536) and `text-embedding-3-large` (3,072). It makes one API call per model and may incur usage charges.

## Run locally

For the web app:

```bash
npm run dev
```

To run the Netlify Function locally as well, install the Netlify CLI and use:

```bash
npm install -g netlify-cli
netlify dev
```

To run the Python CLI:

```bash
python chatbot.py
```

The Python application rebuilds and saves the FAISS index from the PDFs at startup, then prompts for a question. The local `.env` and `faiss_index/` are not committed.

## Deploy to Netlify

1. Connect the `Finn043/RAG_Project` GitHub repository and `main` branch to a Netlify site.
2. Add `OPENAI_API_KEY` to the Netlify site's environment variables. Do not commit the key or paste it into source code.
3. Use build command `npm run build` and publish directory `dist`; these are configured in `netlify.toml`.
4. Deploy. The app calls `/api/chat`; the OpenAI key and PDF corpus are used by the Netlify Function.

The API is public and rate-limited to 6 requests per IP per minute. The function caches the corpus and embeddings in a warm instance; a cold start may rebuild the embeddings and incur usage. Monitor Netlify function logs and OpenAI usage.

References: [Netlify Git deploys](https://docs.netlify.com/deploy/create-deploys/), [Netlify Functions](https://docs.netlify.com/build/functions/get-started/), [Netlify rate limiting](https://docs.netlify.com/manage/security/secure-access-to-sites/rate-limiting/).

## Repository structure

```text
.
├── chatbot.py          # Python RAG CLI
├── app.py              # Streamlit learning/demo app
├── rag.py              # LangChain + FAISS pipeline
├── embedding_demo.py   # Compare embedding dimensions
├── src/                # Web client
├── netlify/functions/  # Serverless API and retrieval
├── server/             # Chunking and cosine similarity helpers
├── papers/             # Source research PDFs
├── requirements.txt    # Python dependencies
├── package.json        # Node dependencies and scripts
├── netlify.toml        # Netlify build and function configuration
└── .env.example        # Environment variable template
```

## Security and cost notes

- Never hard-code API keys in source code. Revoke and replace any key that has been exposed in chat or committed to Git.
- Running `chatbot.py` rebuilds the document embeddings and calls the chat model, which may incur API usage.
- `embedding_demo.py` calls both embedding models; run it only when you need the comparison.
- The production site is public. An IP rate limit is not a global spending cap; monitor usage and configure provider-side budget alerts/limits.
