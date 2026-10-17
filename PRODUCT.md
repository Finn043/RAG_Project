# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Người học và người nghiên cứu Brazilian Jiu-Jitsu cần tra cứu nhanh nội dung trong một bộ tài liệu PDF có giới hạn, bằng tiếng Việt hoặc tiếng Anh.

## Product Purpose

BJJ Research Assistant biến các bài nghiên cứu PDF thành trải nghiệm hỏi đáp có căn cứ. Thành công nghĩa là người dùng nhận được câu trả lời dễ đọc, biết chính xác tài liệu và trang nào hỗ trợ từng thông tin, và nhận được câu trả lời “không biết” khi dữ liệu không đủ.

## Positioning

Sản phẩm không đóng vai một chatbot kiến thức BJJ tổng quát. Nó chỉ trả lời từ corpus nghiên cứu đã nạp, truy xuất tối đa năm chunks liên quan và gắn citation tên file cùng số trang để người dùng kiểm chứng.

## Operating Context

Người dùng mở giao diện web, đọc trạng thái corpus, đặt câu hỏi bằng tiếng Việt hoặc tiếng Anh, xem câu trả lời có citation và có thể xóa lịch sử hiển thị. Tài liệu nguồn nằm trong `papers/`; API key chỉ tồn tại ở server trong `.env`.

## Capabilities and Constraints

- Giữ nguyên RAG backend hiện tại: PyPDFLoader, chunk 1.200 ký tự với overlap 200, OpenAI embeddings, FAISS cosine retrieval và ChatOpenAI.
- Corpus hiện có 2 PDF, 8 trang và 34 chunks; con số thực tế được lấy từ pipeline khi khởi động.
- Citation dùng định dạng `[Source: filename, page N]`.
- Lịch sử hội thoại hiện chỉ phục vụ hiển thị; mỗi câu hỏi được truy xuất độc lập.
- Frontend dùng Streamlit và phải hoạt động tốt trên desktop lẫn mobile web.

## Evidence on Hand

- Hai bài nghiên cứu BJJ thật trong `papers/`.
- Metadata tên file và số trang từ PDF loader.
- Kết quả retrieval và câu trả lời có citation do pipeline hiện tại tạo ra.
- Không có logo, ảnh thương hiệu, testimonial hoặc tuyên bố thương mại; không được tự tạo các bằng chứng này.

## Product Principles

1. Nguồn và khả năng kiểm chứng quan trọng hơn vẻ thông minh của câu trả lời.
2. Trạng thái hệ thống phải rõ nhưng không lấn át tác vụ đặt câu hỏi.
3. Ngôn ngữ và affordance phải dễ hiểu với người đang học, không đòi hỏi kiến thức về RAG.
4. Giao diện có cá tính BJJ nhưng không biến nghiên cứu thành trò chơi hoặc võ đài giả lập.
5. API key và chi tiết lỗi nhạy cảm không được đưa xuống client.

## Accessibility & Inclusion

Hỗ trợ nội dung tiếng Việt và tiếng Anh, tương phản đủ cao, focus rõ ràng, kích thước chạm phù hợp và không phụ thuộc vào màu sắc để truyền đạt trạng thái.
