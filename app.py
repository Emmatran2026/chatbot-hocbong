import streamlit as st

try:
    import chatbot_hocbong as logic
except KeyError:
    st.set_page_config(page_title="Tư Vấn Học Bổng", page_icon="🎓")
    st.error("Chưa tìm thấy GEMINI_API_KEY. Hãy thêm key trong Replit Secrets rồi chạy lại app.")
    st.stop()


st.set_page_config(
    page_title="Tư Vấn Học Bổng Người Trung Niên",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp {
        background: #ffffff;
    }
    [data-testid="stSidebar"] {
        background: #f0f4ff;
    }
    [data-testid="stSidebar"] * {
        color: #1a1a2e;
    }
    [data-testid="stSidebar"] .stCaption {
        color: #475569;
    }
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] textarea,
    [data-testid="stSidebar"] [data-baseweb="input"] > div,
    [data-testid="stSidebar"] [data-baseweb="textarea"] > div,
    [data-testid="stSidebar"] [data-baseweb="select"] > div,
    [data-testid="stSidebar"] [data-testid="stNumberInput"] input {
        background: #ffffff !important;
        color: #1a1a2e !important;
        border-color: #94a3b8 !important;
    }
    [data-testid="stSidebar"] input::placeholder,
    [data-testid="stSidebar"] textarea::placeholder {
        color: #64748b !important;
        opacity: 1 !important;
    }
    [data-testid="stSidebar"] [data-baseweb="select"] *,
    [data-testid="stSidebar"] [data-baseweb="input"] *,
    [data-testid="stSidebar"] [data-baseweb="textarea"] * {
        color: #1a1a2e !important;
    }
    [data-testid="stSidebar"] [data-testid="stSlider"] * {
        color: #1a1a2e !important;
    }
    [data-baseweb="popover"] *,
    [role="listbox"] *,
    [role="option"] {
        color: #1a1a2e !important;
        background-color: #ffffff;
    }
    .stApp input,
    .stApp textarea {
        color: #1a1a2e !important;
        caret-color: #1e3a8a;
    }
    .hero {
        padding: 1.4rem 1.6rem;
        border-radius: 20px;
        background: linear-gradient(135deg, #172554 0%, #2563eb 100%);
        color: white;
        margin-bottom: 1.2rem;
        box-shadow: 0 12px 30px rgba(30, 64, 175, .18);
    }
    .hero h1 {
        margin: 0;
        font-size: 2rem;
        letter-spacing: -.02em;
    }
    .hero p {
        margin: .45rem 0 0;
        color: #dbeafe;
    }
    .profile-card {
        padding: .75rem 1rem;
        border: 1px solid #dbeafe;
        border-radius: 12px;
        background: #eff6ff;
        color: #1e3a8a;
        margin-bottom: 1rem;
    }
    .empty-chat {
        padding: 3rem 1rem;
        text-align: center;
        border: 1px dashed #cbd5e1;
        border-radius: 16px;
        color: #64748b;
        background: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def khoi_tao_session():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Xin chào! Tôi có thể giúp bạn tìm học bổng, ước tính chi phí "
                    "gia đình và lập kế hoạch chuẩn bị hồ sơ. Bạn có thể nhập thông "
                    "tin bên trái hoặc bắt đầu bằng một câu hỏi."
                ),
            }
        ]
    if "chat_session" not in st.session_state:
        st.session_state.chat_session = logic.model.start_chat(history=[])


def them_tin_nhan(role, content):
    st.session_state.messages.append({"role": role, "content": content})


def gui_cau_hoi(cau_hoi):
    """Gửi câu hỏi qua Gemini và thực thi các tool mà model yêu cầu."""
    response = st.session_state.chat_session.send_message(cau_hoi)
    response = logic.xu_ly_tool_calls(
        response, chat_session=st.session_state.chat_session
    )
    return response.text


def thong_tin_ho_so(
    ho_ten,
    tuoi,
    nghe_nghiep,
    bang_cap,
    so_con,
    tuoi_con_nho_nhat,
    nuoc,
    ngan_sach,
):
    ten_hien_thi = ho_ten.strip() or "Chưa nhập họ tên"
    nghe_hien_thi = nghe_nghiep.strip() or "Chưa nhập nghề nghiệp"
    bang_hien_thi = bang_cap.strip() or "Chưa nhập bằng cấp"
    tuoi_con = (
        f"{tuoi_con_nho_nhat} tuổi"
        if so_con > 0
        else "Không có con đi cùng"
    )
    return (
        f"**Hồ sơ đang tư vấn:** {ten_hien_thi} · {tuoi} tuổi · {nghe_hien_thi}  \n"
        f"**Học vấn:** {bang_hien_thi} · **Gia đình:** {so_con} con ({tuoi_con})  \n"
        f"**Nước dự kiến:** {nuoc} · **Ngân sách:** {ngan_sach:,} EUR/tháng"
    )


khoi_tao_session()

st.sidebar.markdown("## 🎓 Hồ sơ cá nhân")
st.sidebar.caption("Thông tin này được dùng để cá nhân hóa tư vấn trong phiên hiện tại.")

ho_ten = st.sidebar.text_input("Họ tên", placeholder="Ví dụ: Nguyễn Minh Anh")
tuoi = st.sidebar.slider("Tuổi", min_value=30, max_value=55, value=40)
nghe_nghiep = st.sidebar.text_input(
    "Nghề nghiệp",
    placeholder="Ví dụ: Bác sĩ, giảng viên, quản lý...",
)
bang_cap = st.sidebar.text_input(
    "Bằng cấp cao nhất",
    placeholder="Ví dụ: Thạc sĩ Y tế công cộng",
)
so_con = st.sidebar.slider("Số con đi cùng", min_value=0, max_value=5, value=1)
if so_con > 0:
    tuoi_con_nho_nhat = st.sidebar.slider(
        "Tuổi con nhỏ nhất",
        min_value=0,
        max_value=18,
        value=7,
    )
else:
    tuoi_con_nho_nhat = -1
    st.sidebar.caption("Không có con đi cùng — tuổi con nhỏ nhất được đặt là -1.")

nuoc = st.sidebar.selectbox(
    "Nước muốn học",
    ["Đức", "Anh", "Úc", "Nhật", "Hà Lan", "Na Uy", "Hàn Quốc", "Singapore", "Canada", "New Zealand"],
    index=0,
)
ngan_sach = st.sidebar.slider(
    "Ngân sách gia đình (EUR/tháng)",
    min_value=500,
    max_value=10000,
    value=2500,
    step=100,
)

with st.sidebar.expander("Thông tin bổ sung cho đánh giá hồ sơ"):
    kinh_nghiem_nam = st.number_input(
        "Số năm kinh nghiệm",
        min_value=0,
        max_value=50,
        value=10,
        step=1,
    )
    ielts_score = st.number_input(
        "Điểm IELTS (0 nếu chưa có)",
        min_value=0.0,
        max_value=9.0,
        value=0.0,
        step=0.5,
    )
    so_cong_bo = st.number_input(
        "Số công bố quốc tế",
        min_value=0,
        max_value=100,
        value=0,
        step=1,
    )
    co_supervisor = st.checkbox("Đã liên hệ supervisor", value=False)
    ngon_ngu_nuoc_den = st.checkbox("Đã biết ngôn ngữ nước đến", value=False)
    loai_to_chuc = st.selectbox(
        "Loại tổ chức đang làm việc",
        ["cong", "tu", "ngo"],
        format_func=lambda value: {
            "cong": "Khu vực công",
            "tu": "Khu vực tư",
            "ngo": "Tổ chức NGO",
        }[value],
    )
    co_thu_gioi_thieu_qt = st.checkbox("Có thư giới thiệu quốc tế", value=False)
    da_lien_he_alumni = st.checkbox("Đã liên hệ alumni", value=False)
    co_chung_minh_tai_chinh = st.checkbox("Có chứng minh tài chính bổ sung", value=False)
    tinh_trang_suc_khoe = st.selectbox(
        "Tình trạng sức khỏe",
        ["tot", "on_dinh", "co_benh_man_tinh"],
        format_func=lambda value: {
            "tot": "Tốt",
            "on_dinh": "Ổn định",
            "co_benh_man_tinh": "Có bệnh mạn tính",
        }[value],
    )

st.sidebar.markdown("---")
danh_gia_clicked = st.sidebar.button(
    "📊 Đánh giá hồ sơ ngay",
    use_container_width=True,
    type="primary",
)
tim_hoc_bong_clicked = st.sidebar.button(
    "🔎 Tìm học bổng phù hợp",
    use_container_width=True,
)

st.markdown(
    """
    <div class="hero">
        <h1>🎓 Tư Vấn Học Bổng Người Trung Niên</h1>
        <p>Tìm cơ hội học tập phù hợp với sự nghiệp, gia đình và ngân sách của bạn.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    thong_tin_ho_so(
        ho_ten,
        tuoi,
        nghe_nghiep,
        bang_cap,
        so_con,
        tuoi_con_nho_nhat,
        nuoc,
        ngan_sach,
    ),
    unsafe_allow_html=False,
)

if danh_gia_clicked:
    with st.spinner("Đang đánh giá hồ sơ..."):
        ket_qua = logic.danh_gia_ho_so(
            tuoi=tuoi,
            bang_cap=bang_cap,
            kinh_nghiem_nam=kinh_nghiem_nam,
            nghe_nghiep=nghe_nghiep,
            so_con=so_con,
            ielts_score=ielts_score,
            so_cong_bo=so_cong_bo,
            co_supervisor=co_supervisor,
            ngon_ngu_nuoc_den=ngon_ngu_nuoc_den,
            tuoi_con_nho_nhat=tuoi_con_nho_nhat,
            loai_to_chuc=loai_to_chuc,
            co_thu_gioi_thieu_qt=co_thu_gioi_thieu_qt,
            da_lien_he_alumni=da_lien_he_alumni,
            co_chung_minh_tai_chinh=co_chung_minh_tai_chinh,
            tinh_trang_suc_khoe=tinh_trang_suc_khoe,
        )
    them_tin_nhan("user", "📊 Đánh giá hồ sơ hiện tại")
    them_tin_nhan(
        "assistant",
        f"{ket_qua}\n\nNgân sách tham khảo bạn đã nhập: {ngan_sach:,} EUR/tháng.",
    )

if tim_hoc_bong_clicked:
    with st.spinner("Đang tìm học bổng phù hợp..."):
        ket_qua = logic.loc_hocbong(tuoi=tuoi, nuoc=nuoc)
    them_tin_nhan("user", "🔎 Tìm học bổng phù hợp")
    them_tin_nhan("assistant", ket_qua)

st.subheader("💬 Trò chuyện cùng chuyên gia")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

with st.form("chat_form", clear_on_submit=True):
    cau_hoi = st.text_area(
        "Câu hỏi của bạn",
        placeholder="Ví dụ: Con tôi 7 tuổi, tôi muốn học ở Đức. Chi phí học cho con thế nào?",
        height=90,
        label_visibility="collapsed",
    )
    gui_clicked = st.form_submit_button("Gửi câu hỏi ➜", use_container_width=True)

if gui_clicked and cau_hoi.strip():
    cau_hoi = cau_hoi.strip()
    them_tin_nhan("user", cau_hoi)
    try:
        with st.spinner("Đang suy nghĩ..."):
            cau_tra_loi = gui_cau_hoi(cau_hoi)
        them_tin_nhan("assistant", cau_tra_loi)
    except Exception as error:
        them_tin_nhan(
            "assistant",
            f"Xin lỗi, tôi chưa thể xử lý câu hỏi này. Chi tiết kỹ thuật: {error}",
        )
    st.rerun()
elif gui_clicked:
    st.warning("Hãy nhập câu hỏi trước khi gửi.")