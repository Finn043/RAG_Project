# BJJ RAG

Ứng dụng Retrieval-Augmented Generation (RAG) dùng các bài nghiên cứu PDF về Brazilian Jiu-Jitsu làm nguồn dữ liệu. Giao diện production dùng React, TypeScript và Tailwind CSS; API chạy bằng Netlify Functions. Bản Python/Streamlit và CLI vẫn được giữ để học và thử nghiệm pipeline LangChain/FAISS.

Production: <https://bjj-research-assistant-finn043.netlify.app>

## Pipeline

```text
PDF → PDF.js → Text chunks → OpenAI Embeddings
    → Cosine retrieval → Prompt → Chat Completions → Answer
```

## Tính năng

- Đọc toàn bộ PDF trong `papers/`.
- Chia văn bản thành chunk 1.200 ký tự, overlap 200 ký tự.
- Tạo vector bằng `text-embedding-3-small`.
- Python pipeline lưu FAISS index vào `faiss_index/`; Netlify Function tính cosine retrieval trong bộ nhớ.
- Truy xuất tối đa 5 chunk bằng cosine similarity và ngưỡng 0,2.
- Chỉ trả lời từ context được truy xuất; nói không biết khi thiếu dữ liệu.
- Yêu cầu trích dẫn theo định dạng `[Source: filename, page N]`.
- Giao diện chat trên web, hỗ trợ lịch sử hiển thị và xóa cuộc trò chuyện.
- Cache corpus và embeddings trong mỗi Netlify Function instance để không embedding lại sau mỗi câu hỏi.
- Có script so sánh kích thước vector của hai embedding model.

## Cài đặt

Yêu cầu Python 3.12 trở lên.

```bash
git clone https://github.com/Finn043/RAG_Project.git
cd RAG_Project

npm install
```

Để dùng Python CLI hoặc Streamlit thử nghiệm:

```bash

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
npm install
npm run dev
```

Mở URL Vite in trong terminal. Để chạy cả API Netlify Functions local, cài Netlify CLI rồi dùng:

```bash
npm install -g netlify-cli
netlify dev
```

API key được đọc ở phía server từ biến môi trường `OPENAI_API_KEY`; không được đưa vào client hoặc commit.

## Deploy lên Netlify

1. Đăng nhập Netlify bằng GitHub và tạo site từ repository `Finn043/RAG_Project`, nhánh `main`.
2. Thêm biến môi trường `OPENAI_API_KEY` trong Netlify project settings. Không commit `.env` hay dán key vào source code.
3. Build command `npm run build`, publish directory `dist`; các giá trị này đã có trong `netlify.toml`.
4. Deploy production. Frontend gọi API tại `/api/chat`; key OpenAI và PDF corpus chỉ được đọc bởi Netlify Function.

API giới hạn mỗi địa chỉ IP tối đa 6 câu hỏi/phút. Function tạo chỉ mục embeddings khi khởi động instance và giữ cache trong thời gian instance còn ấm; các cold start sau đó có thể tạo embeddings lại và phát sinh phí. Vì site production có thể được truy cập công khai, hãy theo dõi Netlify function logs và OpenAI usage.

Hướng dẫn chính thức: [deploy từ Git](https://docs.netlify.com/deploy/create-deploys/), [Netlify Functions](https://docs.netlify.com/build/functions/get-started/), [rate limiting](https://docs.netlify.com/manage/security/secure-access-to-sites/rate-limiting/).

## Chạy bản dòng lệnh

```bash
python chatbot.py
```

Ví dụ:

```text
Question: What are the most common injuries in Brazilian Jiu-Jitsu?
```

Ứng dụng Python tạo lại FAISS index từ các PDF mỗi lần chạy, sau đó in câu trả lời và citation. Cả `.env` và `faiss_index/` đều không được đưa lên Git.

## Cấu trúc project

```text
.
├── chatbot.py          # RAG pipeline và CLI
├── app.py              # Giao diện Streamlit (bản học/thử nghiệm)
├── rag.py              # RAG pipeline LangChain/FAISS cho CLI và Streamlit
├── embedding_demo.py   # So sánh embedding dimensions
├── src/                # Frontend React + TypeScript + Tailwind
├── netlify/functions/  # API serverless + cosine retrieval
├── papers/             # PDF nguồn
├── .streamlit/         # Theme cho bản Streamlit thử nghiệm
├── requirements.txt    # Python dependencies của CLI/Streamlit
├── package.json        # Frontend dependencies và scripts
├── netlify.toml        # Netlify build, function bundle và headers
├── .env.example        # Mẫu biến môi trường
└── README.md
```

## Cách retrieval hoạt động

Hai runtime dùng cùng retrieval policy: cosine similarity, ngưỡng 0,2 và tối đa 5 chunks:

```python
{"score_threshold": 0.2, "k": 5}
```

Chỉ các chunk đạt ngưỡng mới được đưa vào prompt. Metadata tên file và số trang được gắn vào từng chunk trước khi gửi cho model. Pipeline Python dùng FAISS; function production tính cosine trực tiếp trên vector đã cache.

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
