import streamlit as st

from rag import EMBEDDING_MODEL, build_rag_system

st.set_page_config(
    page_title="BJJ Research Assistant",
    page_icon="🥋",
    layout="centered",
)

st.markdown(
    """
    <style>
    .stApp { background: linear-gradient(180deg, #f7f4ed 0%, #ffffff 35%); }
    [data-testid="stSidebar"] { background: #132238; }
    [data-testid="stSidebar"] * { color: #f7f4ed; }
    [data-testid="stChatMessage"] {
        border: 1px solid rgba(19, 34, 56, 0.10);
        border-radius: 16px;
        padding: 0.35rem 0.75rem;
        background: rgba(255, 255, 255, 0.72);
    }
    .hero-label {
        color: #9b6b28;
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner=False)
def load_rag_system():
    return build_rag_system()


st.markdown('<p class="hero-label">Evidence-based BJJ research</p>', unsafe_allow_html=True)
st.title("🥋 BJJ Research Assistant")
st.caption(
    "Hỏi bằng tiếng Việt hoặc English. Câu trả lời chỉ dựa trên các bài nghiên cứu "
    "trong thư mục `papers/` và kèm nguồn theo trang."
)

try:
    with st.spinner("Đang đọc tài liệu và xây dựng chỉ mục..."):
        rag = load_rag_system()
except Exception as error:
    st.error("Không thể khởi tạo hệ thống RAG.")
    st.caption(str(error))
    st.stop()

with st.sidebar:
    st.title("BJJ RAG")
    st.caption("Trạng thái dữ liệu")
    col1, col2 = st.columns(2)
    col1.metric("PDF", rag.pdf_count)
    col2.metric("Trang", rag.page_count)
    st.metric("Chunks", rag.chunk_count)
    st.divider()
    st.caption(f"Embedding: `{EMBEDDING_MODEL}`")
    st.caption(f"Chat model: `{rag.chat_model}`")
    st.caption("Retriever: cosine · top 5 · threshold 0.2")
    st.divider()
    if st.button("Xóa cuộc trò chuyện", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Chào bạn! Hãy hỏi mình về sinh lý học, chấn thương hoặc tác động "
                "tâm lý - xã hội của Brazilian Jiu-Jitsu trong bộ tài liệu hiện có."
            ),
        }
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input("Ví dụ: Những chấn thương nào thường gặp trong BJJ?")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Đang tìm bằng chứng trong tài liệu..."):
                answer = rag.chain.invoke(question)
        except Exception as error:
            answer = "Không thể tạo câu trả lời lúc này. Vui lòng kiểm tra API key và thử lại."
            st.error(answer)
            st.caption(str(error))
        else:
            st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
