# Chatbot học bổng người trung niên

Ứng dụng Streamlit tư vấn học bổng cho người học 30–55 tuổi đi cùng gia đình.
Ứng dụng sử dụng Gemini, database học bổng nội bộ và các công cụ tư vấn chi phí
cho con, đánh giá hồ sơ, cải thiện hồ sơ và tìm học bổng.

## Chạy tại máy

```bash
streamlit run app.py
```

## Deploy trên Streamlit Community Cloud

1. Truy cập [share.streamlit.io](https://share.streamlit.io/) và đăng nhập bằng GitHub.
2. Chọn **Create app**.
3. Chọn repository `chatbot-hocbong`, branch `main`, file chính `app.py`.
4. Trong **Advanced settings**, chọn Python **3.13** vì project yêu cầu Python `>=3.13`.
   Tại mục **Secrets**, thêm:

```toml
GEMINI_API_KEY = "dán-Gemini-key-của-bạn-vào-đây"
```

5. Chọn **Deploy**.

Không đưa `GEMINI_API_KEY` vào source code hoặc commit lên GitHub. Nếu repository
để private, tài khoản GitHub dùng trong Streamlit Community Cloud cần có quyền
truy cập repository đó.