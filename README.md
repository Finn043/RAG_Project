# BJJ RAG

Ứng dụng Retrieval-Augmented Generation (RAG) có giao diện web và dòng lệnh, dùng các bài nghiên cứu PDF về Brazilian Jiu-Jitsu làm nguồn dữ liệu. Ứng dụng tải PDF, chia nhỏ văn bản, tạo OpenAI embeddings, lưu vector bằng FAISS, truy xuất các đoạn liên quan và tạo câu trả lời có trích dẫn nguồn/trang.

## Pipeline

```text
PDF → PyPDFLoader → RecursiveCharacterTextSplitter
    → OpenAI Embeddings → FAISS → Retriever
    → Prompt → ChatOpenAI → Answer
```

## Tính năng

- Đọc toàn bộ PDF trong `papers/`.
- Chia văn bản thành chunk 1.200 ký tự, overlap 200 ký tự.
- Tạo vector bằng `text-embedding-3-small`.
- Lưu FAISS index vào `faiss_index/`.
- Truy xuất tối đa 5 chunk bằng cosine similarity và ngưỡng 0,2.
- Chỉ trả lời từ context được truy xuất; nói không biết khi thiếu dữ liệu.
- Yêu cầu trích dẫn theo định dạng `[Source: filename, page N]`.
- Giao diện chat trên web, hỗ trợ lịch sử hiển thị và xóa cuộc trò chuyện.
- Cache RAG pipeline trong tiến trình web để không embedding lại sau mỗi câu hỏi.
- Có script so sánh kích thước vector của hai embedding model.

## Cài đặt

Yêu cầu Python 3.12 trở lên.

```bash
git clone https://github.com/Finn043/RAG_Project.git
cd RAG_Project

python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Trên Windows PowerShell, kích hoạt môi trường bằng:

```powershell
.venv\Scripts\Activate.ps1
```

## Cấu hình

Tạo file `.env` từ mẫu:

```bash
cp .env.example .env
```

Mở `.env` và điền API key mới của bạn:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_CHAT_MODEL=gpt-4o-mini
```

Không commit hoặc chia sẻ `.env`. File này đã được khai báo trong `.gitignore`.

`gpt-4o-mini` được giữ làm mặc định để tương thích với bài thực hành và `temperature=0`. Có thể thay `OPENAI_CHAT_MODEL` trong `.env` khi muốn dùng model khác tương thích với `ChatOpenAI`.

## So sánh embedding model

```bash
python embedding_demo.py
```

Kết quả mặc định:

```text
text-embedding-3-small: 1536 dimensions
text-embedding-3-large: 3072 dimensions
```

Script này gọi API một lần cho mỗi model nên có phát sinh API usage.

## Chạy giao diện web

```bash
streamlit run app.py
```

Mở địa chỉ Streamlit in ra trong terminal, mặc định là <http://localhost:8501>. Lần đầu khởi động, ứng dụng đọc các PDF và tạo embeddings; các câu hỏi tiếp theo trong cùng tiến trình sẽ dùng lại pipeline đã cache.

API key chỉ được đọc từ `.env` ở phía server, không được gửi xuống mã nguồn chạy trong trình duyệt.

## Chạy bản dòng lệnh

```bash
python chatbot.py
```

Ví dụ:

```text
Question: What are the most common injuries in Brazilian Jiu-Jitsu?
```

Ứng dụng tạo lại FAISS index từ các PDF mỗi lần khởi động tiến trình, sau đó in câu trả lời và citation. Cả `.env` và `faiss_index/` đều không được đưa lên Git.

## Cấu trúc project

```text
.
├── chatbot.py          # RAG pipeline và CLI
├── app.py              # Giao diện chat Streamlit
├── rag.py              # RAG pipeline dùng chung cho CLI và web
├── embedding_demo.py   # So sánh embedding dimensions
├── papers/             # PDF nguồn
├── .streamlit/         # Theme và cấu hình Streamlit
├── requirements.txt    # Python dependencies
├── .env.example        # Mẫu biến môi trường
└── README.md
```

## Cách retrieval hoạt động

FAISS sử dụng chiến lược cosine distance. Retriever dùng `similarity_score_threshold` với:

```python
{"score_threshold": 0.2, "k": 5}
```

Chỉ các chunk đạt ngưỡng mới được đưa vào prompt, tối đa 5 chunk. Metadata tên file và số trang được gắn vào từng chunk trước khi gửi cho model.

## Bảo mật và chi phí

- Không đặt API key trực tiếp trong source code.
- Nếu key từng bị gửi qua chat hoặc commit lên Git, hãy revoke và tạo key mới.
- Mỗi lần chạy `chatbot.py` sẽ embedding lại tài liệu và gọi chat model, do đó có phát sinh API usage.
- `embedding_demo.py` gọi cả model small và large; chỉ chạy khi cần so sánh.

## Giới hạn hiện tại

- Lịch sử trên web chỉ dùng để hiển thị; mỗi câu hỏi được truy xuất độc lập, chưa hỗ trợ câu hỏi nối tiếp theo ngữ cảnh hội thoại.
- FAISS index được xây lại mỗi lần chạy thay vì tái sử dụng index cũ.
- Chất lượng câu trả lời phụ thuộc vào nội dung PDF, cách chunking và ngưỡng retrieval.
- `langchain-community` hiện phát cảnh báo deprecation nhưng vẫn hoạt động với phiên bản đã khóa trong `requirements.txt`.
