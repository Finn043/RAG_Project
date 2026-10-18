import logging
import os

import streamlit as st

from rag import EMBEDDING_MODEL, build_rag_system

LOGGER = logging.getLogger(__name__)

st.set_page_config(
    page_title="BJJ Research Assistant",
    layout="wide",
    initial_sidebar_state="auto",
)

st.markdown(
    """<!--
THESIS: Evidence is inspected on a research film desk, refusing the generic AI chat-card layout.
OWN-WORLD: Deep ink, backlit film, mint registration lines, safety orange, square archival controls.
STORY: See the corpus state, ask one precise question, read an answer whose citations remain inspectable.
FIRST VIEWPORT: A narrow corpus rail anchors a broad illuminated conversation plate and bottom query field.
FORM: Sports-science microfilm archive, seventh grounded direction, seed 015d3476.
FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
-->""",
    unsafe_allow_html=True,
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&family=Barlow+Condensed:wght@500;600;700&display=swap');

    :root {
        --ink-950: #06171d;
        --ink-900: #09232b;
        --ink-800: #10343d;
        --film: #e8f2ef;
        --film-strong: #f4faf7;
        --film-dim: #b9ccc8;
        --mint: #42e8c8;
        --orange: #ff6b35;
        --line: rgba(66, 232, 200, 0.28);
        --line-quiet: rgba(232, 242, 239, 0.13);
        --shadow: 0 22px 54px rgba(0, 8, 10, 0.32);
    }

    html, body, [class*="css"] { font-family: "Atkinson Hyperlegible", sans-serif; }

    .stApp {
        color: var(--film);
        background: var(--ink-950);
    }

    .stApp::before {
        content: "";
        position: fixed;
        inset: 0;
        pointer-events: none;
        background: linear-gradient(180deg, transparent 0%, rgba(66, 232, 200, 0.06) 48%, transparent 52%);
        background-size: 100% 220%;
        animation: film-scan 8s cubic-bezier(.16, 1, .3, 1) 1;
        z-index: 999;
    }

    @keyframes film-scan {
        from { background-position: 0 -120%; }
        to { background-position: 0 120%; }
    }

    ::selection { background: var(--orange); color: var(--ink-950); }
    * { scrollbar-width: thin; scrollbar-color: var(--mint) var(--ink-900); }
    *::-webkit-scrollbar { width: 10px; height: 10px; }
    *::-webkit-scrollbar-track { background: var(--ink-900); }
    *::-webkit-scrollbar-thumb { background: var(--mint); border: 3px solid var(--ink-900); }

    h1, h2, h3, [data-testid="stMetricValue"] {
        font-family: "Barlow Condensed", sans-serif !important;
        letter-spacing: -0.02em !important;
    }

    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stToolbar"] { color: var(--film); }
    [data-testid="stAppViewContainer"] > .main { background: transparent; }
    .main .block-container { max-width: 1100px; padding: 2.3rem 3.5rem 7.5rem; }

    .masthead {
        display: grid;
        grid-template-columns: minmax(0, 1fr) auto;
        gap: 2rem;
        align-items: end;
        padding: 0.8rem 0 1.4rem;
        border-bottom: 1px solid var(--line);
        margin-bottom: 1.6rem;
    }

    .masthead h1 {
        margin: 0;
        max-width: 9ch;
        color: var(--film-strong);
        font-family: "Barlow Condensed", sans-serif;
        font-size: clamp(3.25rem, 7vw, 5.8rem);
        line-height: 0.82;
        font-weight: 600;
        letter-spacing: -0.035em;
        text-wrap: balance;
    }

    .masthead h1 span { color: var(--mint); }

    .masthead-copy {
        max-width: 35rem;
        color: var(--film-dim);
        font-size: 1rem;
        line-height: 1.55;
        padding-bottom: 0.2rem;
    }

    .plate-label {
        display: flex;
        justify-content: space-between;
        gap: 1rem;
        color: var(--film-dim);
        font-family: "Barlow Condensed", sans-serif;
        font-size: 0.78rem;
        letter-spacing: 0.11em;
        text-transform: uppercase;
        margin-bottom: 0.6rem;
    }

    .plate-label strong { color: var(--mint); font-weight: 600; }

    [data-testid="stChatMessage"] {
        position: relative;
        align-items: flex-start;
        gap: 0.8rem;
        padding: 1.25rem 1.35rem;
        margin: 0 0 0.75rem;
        border: 0;
        border-radius: 0;
        background: rgba(232, 242, 239, 0.055);
        box-shadow: inset 0 1px 0 var(--line-quiet);
    }

    [data-testid="stChatMessage"]::after {
        content: "";
        position: absolute;
        right: 0.6rem;
        top: 0.6rem;
        width: 0.45rem;
        height: 0.45rem;
        border-top: 1px solid var(--mint);
        border-right: 1px solid var(--mint);
    }

    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        margin-left: 10%;
        background: rgba(66, 232, 200, 0.1);
    }

    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) { margin-right: 4%; }

    [data-testid="stChatMessageAvatarUser"],
    [data-testid="stChatMessageAvatarAssistant"] {
        position: relative;
        border-radius: 0 !important;
        background: var(--ink-800) !important;
        border: 1px solid var(--line);
    }

    [data-testid="stChatMessageAvatarUser"] svg,
    [data-testid="stChatMessageAvatarAssistant"] svg { display: none; }

    [data-testid="stChatMessageAvatarUser"]::after,
    [data-testid="stChatMessageAvatarAssistant"]::after {
        content: "";
        position: absolute;
        inset: 25%;
        background:
            linear-gradient(var(--mint), var(--mint)) center / 1px 100% no-repeat,
            linear-gradient(var(--mint), var(--mint)) center / 100% 1px no-repeat;
    }

    [data-testid="stChatMessageAvatarUser"]::after { background-color: transparent; }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageAvatarUser"]::after {
        background:
            linear-gradient(var(--orange), var(--orange)) center / 1px 100% no-repeat,
            linear-gradient(var(--orange), var(--orange)) center / 100% 1px no-repeat;
    }

    [data-testid="stChatMessageContent"] {
        max-width: 72ch;
        color: var(--film);
        line-height: 1.65;
    }

    [data-testid="stChatMessageContent"] p { margin-bottom: 0.75rem; }
    [data-testid="stChatMessageContent"] strong { color: var(--film-strong); }

    [data-testid="stChatInput"] {
        border: 1px solid var(--mint);
        border-radius: 0;
        background: var(--ink-900);
        box-shadow: var(--shadow);
    }

    [data-testid="stChatInput"] textarea {
        color: var(--film-strong) !important;
        caret-color: var(--orange);
        min-height: 3.4rem;
    }

    [data-testid="stChatInput"] textarea::placeholder { color: #9db6b1; opacity: 1; }
    [data-testid="stChatInput"] button { color: var(--ink-950); background: var(--mint); border-radius: 0; }

    .stButton > button {
        min-height: 2.7rem;
        border: 1px solid var(--line);
        border-radius: 0;
        color: var(--film);
        background: transparent;
        font-family: "Atkinson Hyperlegible", sans-serif;
        text-align: left;
        transition: background-color 180ms ease-out, border-color 180ms ease-out, color 180ms ease-out;
    }

    .stButton > button:hover { border-color: var(--mint); color: var(--ink-950); background: var(--mint); }

    .stButton > button:focus-visible,
    [data-testid="stChatInput"]:focus-within { outline: 3px solid var(--orange); outline-offset: 3px; }

    [data-testid="stSidebar"] {
        min-width: 18.5rem;
        background: var(--ink-900);
        border-right: 1px solid var(--line);
    }

    [data-testid="stSidebar"] > div:first-child { padding: 1.7rem 1.25rem; }
    [data-testid="stSidebar"] * { color: var(--film); }
    [data-testid="stSidebar"] hr { border-color: var(--line-quiet); }

    .archive-mark {
        display: grid;
        grid-template-columns: 2.4rem 1fr;
        gap: 0.85rem;
        align-items: center;
        margin-bottom: 2.5rem;
    }

    .archive-symbol { position: relative; width: 2.25rem; height: 2.25rem; border: 1px solid var(--mint); }
    .archive-symbol::before, .archive-symbol::after { content: ""; position: absolute; background: var(--mint); }
    .archive-symbol::before { width: 1px; height: 70%; left: 50%; top: 15%; }
    .archive-symbol::after { height: 1px; width: 70%; top: 50%; left: 15%; }

    .archive-mark strong {
        display: block;
        font-family: "Barlow Condensed", sans-serif;
        font-size: 1.25rem;
        line-height: 1;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }

    .archive-mark span { color: var(--film-dim) !important; font-size: 0.72rem; letter-spacing: 0.12em; text-transform: uppercase; }
    .rail-title { color: var(--mint) !important; font-family: "Barlow Condensed", sans-serif; font-size: 0.78rem; letter-spacing: 0.13em; text-transform: uppercase; margin-bottom: 0.8rem; }

    .corpus-readout {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        border-top: 1px solid var(--line);
        border-bottom: 1px solid var(--line);
        margin-bottom: 1.4rem;
    }

    .readout-cell { padding: 0.85rem 0.25rem 0.8rem 0; }
    .readout-cell + .readout-cell { border-left: 1px solid var(--line-quiet); padding-left: 0.65rem; }
    .readout-cell strong { display: block; color: var(--film-strong) !important; font-family: "Barlow Condensed", sans-serif; font-size: 1.75rem; font-variant-numeric: tabular-nums; line-height: 1; }
    .readout-cell span { color: var(--film-dim) !important; font-size: 0.68rem; text-transform: uppercase; }

    .system-line {
        display: grid;
        grid-template-columns: 0.5rem 1fr;
        gap: 0.65rem;
        padding: 0.55rem 0;
        color: var(--film-dim) !important;
        font-size: 0.78rem;
        border-bottom: 1px solid var(--line-quiet);
    }

    .system-line::before { content: ""; width: 1px; height: 1.1rem; background: var(--mint); justify-self: center; }
    [data-testid="stAlert"] { border-radius: 0; border: 1px solid var(--orange); background: rgba(255, 107, 53, 0.1); }
    [data-testid="stSpinner"] { color: var(--mint); }

    @media (max-width: 800px) {
        .main .block-container { padding: 4.5rem 1rem 7rem; }
        .masthead { grid-template-columns: 1fr; gap: 1rem; align-items: start; }
        .masthead h1 { max-width: 8ch; font-size: clamp(3rem, 16vw, 4.6rem); }
        .masthead-copy { max-width: 65ch; }
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) { margin-left: 4%; }
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) { margin-right: 0; }
        .plate-label { font-size: 0.68rem; }
    }

    @media (prefers-reduced-motion: reduce) {
        .stApp::before { animation: none; display: none; }
        *, *::before, *::after { scroll-behavior: auto !important; transition-duration: 0.01ms !important; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner=False)
def load_rag_system():
    if not os.getenv("OPENAI_API_KEY"):
        try:
            os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
            if st.secrets.get("OPENAI_CHAT_MODEL"):
                os.environ["OPENAI_CHAT_MODEL"] = st.secrets["OPENAI_CHAT_MODEL"]
        except (KeyError, FileNotFoundError):
            pass
    return build_rag_system()


st.markdown(
    """
    <header class="masthead">
        <div>
            <h1>BJJ<br><span>Research</span><br>Assistant</h1>
        </div>
        <p class="masthead-copy">
            Đặt câu hỏi bằng tiếng Việt hoặc English. Mỗi câu trả lời được giới hạn
            trong corpus nghiên cứu hiện có và phải để lại dấu vết nguồn theo trang.
        </p>
    </header>
    """,
    unsafe_allow_html=True,
)

try:
    with st.spinner("Đang hiệu chỉnh corpus và dựng chỉ mục bằng chứng..."):
        rag = load_rag_system()
except Exception:
    LOGGER.exception("Failed to initialize the RAG system")
    st.error("Không thể mở corpus. Hãy kiểm tra `OPENAI_API_KEY`, thư mục `papers/`, rồi tải lại trang.")
    st.stop()

with st.sidebar:
    st.markdown(
        """
        <div class="archive-mark">
            <div class="archive-symbol" aria-hidden="true"></div>
            <div><strong>BJJ RAG</strong><span>Evidence archive</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="rail-title">Corpus readout</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="corpus-readout">
            <div class="readout-cell"><strong>{rag.pdf_count}</strong><span>PDF</span></div>
            <div class="readout-cell"><strong>{rag.page_count}</strong><span>Trang</span></div>
            <div class="readout-cell"><strong>{rag.chunk_count}</strong><span>Chunks</span></div>
        </div>
        <div class="system-line">Embedding · {EMBEDDING_MODEL}</div>
        <div class="system-line">Chat · {rag.chat_model}</div>
        <div class="system-line">Cosine · top 5 · threshold 0.2</div>
        <div class="system-line">Mỗi câu hỏi truy xuất độc lập</div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    if st.button("Xóa cuộc trò chuyện", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Corpus đã sẵn sàng. Bạn có thể hỏi về **sinh lý học**, "
                "**chấn thương** hoặc **tác động tâm lý – xã hội** của Brazilian Jiu-Jitsu."
            ),
        }
    ]

st.markdown(
    '<div class="plate-label"><span>Conversation plate</span><strong>Source-locked output</strong></div>',
    unsafe_allow_html=True,
)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = None
typed_question = st.chat_input("Nhập câu hỏi để quét corpus nghiên cứu...")
if typed_question:
    question = typed_question

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Đang đối chiếu các trang liên quan..."):
                answer = rag.chain.invoke(question)
        except Exception:
            LOGGER.exception("Failed to answer a RAG query")
            answer = "Không thể tạo câu trả lời. Hãy kiểm tra kết nối API và thử lại."
            st.error(answer)
        else:
            st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()
