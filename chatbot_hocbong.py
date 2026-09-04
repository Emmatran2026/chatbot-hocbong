import google.generativeai as genai
import csv
import os
import io
import unicodedata
from collections import Counter

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

CSV_DATA = """ten,nuoc,loai,tuoi_min,tuoi_max,ho_tro_gia_dinh,muc_tro_cap_eur,han_nop,link
DAAD EPOS,Đức,Thạc sĩ/Tiến sĩ,30,55,conditional,992,varies,daad.de
DAAD Doctoral Programmes,Đức,Tiến sĩ,30,55,conditional,1400,varies,daad.de
Chevening,Anh,Thạc sĩ,30,55,conditional,2000,November,chevening.org
Australia Awards,Úc,Thạc sĩ,30,55,yes,1800,April,australiaawards.gov.au
JSPS Postdoctoral,Nhật Bản,Nghiên cứu,30,55,conditional,2400,varies,jsps.go.jp
MSCA Postdoctoral European,EU,Nghiên cứu,30,55,conditional,5680,varies,ec.europa.eu
MSCA Postdoctoral Global,EU,Nghiên cứu,30,55,conditional,5680,varies,ec.europa.eu
JICA SDGs Global Leadership,Nhật Bản,Thạc sĩ,30,55,conditional,1500,varies,jica.go.jp
JICA Knowledge Co-Creation,Nhật Bản,Thạc sĩ,30,55,conditional,1500,varies,jica.go.jp
NORPART,Na Uy,Trao đổi,30,55,conditional,1800,varies,norpart.no
Holland Scholarship,Hà Lan,Thạc sĩ,30,55,no,5000,January,studyinholland.nl
GKS Graduate,Hàn Quốc,Thạc sĩ/Tiến sĩ,30,55,conditional,1000,September,niied.go.kr
Commonwealth Masters,Anh/Khối,Thạc sĩ,30,55,conditional,1500,December,cscuk.fcdo.gov.uk
Endeavour,Úc,Thạc sĩ/Nghiên cứu,30,55,conditional,1800,April,internationaleducation.gov.au
NUS Research Scholarship,Singapore,Tiến sĩ,30,55,conditional,1700,varies,nus.edu.sg
Australia Awards Fellowships,Úc,Thạc sĩ/Nghiên cứu,30,55,yes,1800,April,australiaawards.gov.au
Endeavour Leadership Program,Úc,Thạc sĩ/Nghiên cứu,30,55,conditional,1800,April,internationaleducation.gov.au
Australian Government RTP,Úc,Thạc sĩ/Nghiên cứu,30,55,conditional,1500,varies,education.gov.au
Vanier Canada Graduate,Canada,Thạc sĩ/Nghiên cứu,30,55,conditional,2100,November,vanier.gc.ca
IDRC Research Awards,Canada,Thạc sĩ/Nghiên cứu,30,55,conditional,1600,varies,idrc-crdi.ca
Ontario Trillium,Canada,Thạc sĩ/Nghiên cứu,30,55,conditional,1400,November,ontario.ca
Orange Tulip Scholarship,Hà Lan,Thạc sĩ/Nghiên cứu,30,55,conditional,1000,varies,studyinholland.nl
NFP Netherlands Fellowship,Hà Lan,Thạc sĩ/Nghiên cứu,30,55,yes,1800,varies,studyinholland.nl
A*STAR Research,Singapore,Thạc sĩ/Nghiên cứu,30,55,conditional,1700,varies,astar.edu.sg
NTU Research Scholarship,Singapore,Thạc sĩ/Nghiên cứu,30,55,conditional,1600,varies,ntu.edu.sg
NZAS New Zealand ASEAN,New Zealand,Thạc sĩ/Nghiên cứu,30,55,yes,1900,March,mfat.govt.nz
SISGP Swedish Institute,Thụy Điển,Thạc sĩ/Nghiên cứu,30,55,conditional,1100,February,si.se
GKS Undergraduate adapted,Hàn Quốc,Thạc sĩ/Nghiên cứu,30,55,conditional,900,September,studyinkorea.go.kr
ARES Scholarships,Bỉ,Thạc sĩ/Nghiên cứu,30,55,yes,1200,March,ares-ac.be
Eiffel Excellence,Pháp,Thạc sĩ/Nghiên cứu,30,55,conditional,1400,January,campusfrance.org"""


def doc_csv():
    reader = csv.DictReader(io.StringIO(CSV_DATA))
    fieldnames = reader.fieldnames or []
    rows = list(reader)
    total_before = len(rows)

    ten_counts = Counter()
    ten_display = {}
    for row in rows:
        ten = row.get("ten", "").strip()
        if ten:
            ten_key = ten.casefold()
            ten_counts[ten_key] += 1
            ten_display.setdefault(ten_key, ten)
    duplicate_names = sorted(
        ten_display[ten]
        for ten, count in ten_counts.items()
        if count > 1
    )

    seen_rows = set()
    unique_rows = []
    duplicate_full_names = []
    for row in rows:
        row_key = tuple(row.get(column, "") for column in fieldnames)
        if row_key in seen_rows:
            duplicate_full_names.append(row.get("ten", "").strip())
            continue
        seen_rows.add(row_key)
        unique_rows.append(row)

    print("=== Kiểm tra duplicate CSV_DATA ===")
    print(f"Tổng số học bổng trước khi xóa: {total_before}")
    print(
        "Học bổng trùng tên: "
        + (", ".join(duplicate_names) if duplicate_names else "Không có")
    )
    print(
        "Các dòng trùng hoàn toàn tất cả cột: "
        + (
            ", ".join(duplicate_full_names)
            if duplicate_full_names
            else "Không có"
        )
    )
    print(
        "Danh sách học bổng bị duplicate: "
        + (
            ", ".join(sorted(set(duplicate_names + duplicate_full_names)))
            if duplicate_names or duplicate_full_names
            else "Không có"
        )
    )
    print(f"Tổng số học bổng sau khi xóa: {len(unique_rows)}")
    print(f"Số dòng duplicate đã xóa: {total_before - len(unique_rows)}")
    return unique_rows


hoc_bong_list = doc_csv()


def loc_hocbong(tuoi: int, nuoc: str = "") -> str:
    ket_qua = []
    for hb in hoc_bong_list:
        if int(hb["tuoi_min"]) <= tuoi <= int(hb["tuoi_max"]):
            if nuoc == "" or nuoc.lower() in hb["nuoc"].lower():
                ket_qua.append(
                    f"- {hb['ten']} ({hb['nuoc']}): {hb['muc_tro_cap_eur']} EUR/tháng, "
                    f"hỗ trợ gia đình: {hb['ho_tro_gia_dinh']}, hạn nộp: {hb['han_nop']}"
                )
    if not ket_qua:
        return "Không tìm thấy học bổng phù hợp."
    return f"Tìm thấy {len(ket_qua)} học bổng:\n" + "\n".join(ket_qua)


def tinh_chi_phi(muc_tro_cap: float, so_con: int) -> str:
    chi_phi_hoc_vien = 1300
    chi_phi_nguoi_lon = 800
    chi_phi_moi_con = 400
    tong_chi_phi = chi_phi_hoc_vien + chi_phi_nguoi_lon + (so_con * chi_phi_moi_con)
    can_them = max(0, tong_chi_phi - muc_tro_cap)
    return (
        f"Chi phí gia đình ước tính: {tong_chi_phi} EUR/tháng\n"
        f"Học bổng hỗ trợ: {muc_tro_cap} EUR/tháng\n"
        f"Cần bổ sung thêm: {can_them} EUR/tháng\n"
        f"(Gồm: học viên {chi_phi_hoc_vien} + vợ/chồng {chi_phi_nguoi_lon} + {so_con} con x {chi_phi_moi_con} EUR)"
    )


def viet_email_hoi_hocbong(ten_nguoi: str, hoc_bong: str, nghe_nghiep: str, so_con: int) -> str:
    return f"""Subject: Inquiry About Family Support Under the {hoc_bong} Scholarship

Dear {hoc_bong} Scholarship Team,

My name is {ten_nguoi}, and I am a {nghe_nghiep} interested in applying for the {hoc_bong} program.

I have {so_con} child(ren) who may accompany me during my studies. I would be grateful if you could clarify:

1. Eligibility for applicants with extensive professional experience
2. Dependent/family allowance for accompanying children
3. Health insurance coverage for family members
4. Support for accommodation and family-related expenses
5. Application procedure for family support

Thank you for your time.

Kind regards,
{ten_nguoi}"""


def _bo_dau(text: str) -> str:
    """Chuẩn hóa chuỗi tiếng Việt để so khớp từ khóa."""
    return "".join(
        char
        for char in unicodedata.normalize("NFD", str(text).lower().replace("đ", "d"))
        if unicodedata.category(char) != "Mn"
    )


def _diem_bang_cap(bang_cap: str, loai_hoc_bong: str) -> tuple[int, str]:
    bang_cap_chuan = _bo_dau(bang_cap)
    loai_chuan = _bo_dau(loai_hoc_bong)

    if any(tu_khoa in bang_cap_chuan for tu_khoa in ["tien si", "phd", "doctorate"]):
        if "nghien cuu" in loai_chuan or "tien si" in loai_chuan:
            return 30, "Bằng Tiến sĩ phù hợp với chương trình nghiên cứu/tiến sĩ."
        return 18, "Bằng Tiến sĩ cao hơn yêu cầu thông thường của chương trình."

    if any(tu_khoa in bang_cap_chuan for tu_khoa in ["thac si", "master", "mba"]):
        if "thac si" in loai_chuan:
            return 30, "Bằng Thạc sĩ phù hợp với chương trình."
        if "nghien cuu" in loai_chuan:
            return 12, "Có nền tảng sau đại học, nhưng chương trình nghiên cứu thường cần kiểm tra thêm yêu cầu Tiến sĩ."
        return 24, "Bằng Thạc sĩ là nền tảng tốt cho chương trình này."

    if any(tu_khoa in bang_cap_chuan for tu_khoa in ["cu nhan", "dai hoc", "bachelor", "ky su"]):
        if "thac si" in loai_chuan or "trao doi" in loai_chuan:
            return 30, "Bằng đại học phù hợp với chương trình Thạc sĩ/trao đổi."
        return 14, "Bằng đại học có thể phù hợp, nhưng cần kiểm tra điều kiện bằng cấp chuyên biệt."

    return 15, "Chưa đủ thông tin để xác định mức độ tương thích bằng cấp; cần kiểm tra điều kiện chính thức."


def _danh_gia_ho_so_legacy(
    tuoi: int,
    bang_cap: str,
    kinh_nghiem_nam: int,
    nghe_nghiep: str,
    so_con: int,
    ielts_score: float,
    so_cong_bo: int,
    co_supervisor: bool,
    ngon_ngu_nuoc_den: bool,
    tuoi_con_nho_nhat: int,
) -> str:
    """Đánh giá hồ sơ theo 5 nhóm điểm và trả về top 3 học bổng.

    tuoi_con_nho_nhat nên là -1 nếu hồ sơ không có con.
    Cam kết chiến lược được đánh giá thận trọng từ việc đã liên hệ supervisor;
    tool sẽ nêu rõ phần này trong điểm mạnh/yếu.
    """
    nghe_nghiep_chuan = _bo_dau(nghe_nghiep)
    tuoi = int(tuoi)
    kinh_nghiem_nam = max(0, int(kinh_nghiem_nam))
    so_con = max(0, int(so_con))
    ielts_score = max(0.0, min(9.0, float(ielts_score)))
    so_cong_bo = max(0, int(so_cong_bo))

    # Nhóm 1: Học thuật/chuyên môn (30 điểm). Điểm bằng cấp được tính
    # riêng theo loại chương trình của từng học bổng.
    diem_kinh_nghiem = round(min(8, kinh_nghiem_nam * 8 / 20), 1)
    diem_cong_bo = min(10, so_cong_bo * 2)

    # Nhóm 2: Ngôn ngữ (20 điểm).
    diem_ielts = round(min(15, max(0, (ielts_score - 3.0) * 2.5)), 1) if ielts_score else 0
    diem_ngon_ngu_nuoc_den = 5 if ngon_ngu_nuoc_den else 0
    diem_ngon_ngu = round(diem_ielts + diem_ngon_ngu_nuoc_den, 1)

    # Nhóm 3: Gia đình phù hợp (20 điểm).
    ho_tro_diem = {"yes": 10, "conditional": 6, "no": 0}

    if so_con == 0:
        diem_so_con = 5
        ly_do_so_con = "Không có con đi cùng nên gánh nặng phụ thuộc thấp."
    elif so_con <= 2:
        diem_so_con = 4
        ly_do_so_con = f"Có {so_con} con; quy mô gia đình vẫn tương đối dễ bố trí."
    elif so_con == 3:
        diem_so_con = 3
        ly_do_so_con = "Có 3 con; cần ưu tiên học bổng có chính sách dependent rõ ràng."
    else:
        diem_so_con = 2
        ly_do_so_con = f"Có {so_con} con; cần kế hoạch tài chính và dependent chi tiết."

    if so_con == 0 or tuoi_con_nho_nhat >= 12:
        diem_tuoi_con = 5
        ly_do_tuoi_con = "Con đã lớn hoặc không có con nhỏ, thuận lợi hơn cho việc di chuyển."
    elif tuoi_con_nho_nhat >= 6:
        diem_tuoi_con = 4
        ly_do_tuoi_con = f"Con nhỏ nhất {tuoi_con_nho_nhat} tuổi; nhu cầu chăm sóc ở mức vừa phải."
    elif tuoi_con_nho_nhat >= 3:
        diem_tuoi_con = 2
        ly_do_tuoi_con = f"Con nhỏ nhất {tuoi_con_nho_nhat} tuổi; cần dự trù chăm sóc và học tập."
    elif tuoi_con_nho_nhat >= 0:
        diem_tuoi_con = 1
        ly_do_tuoi_con = f"Con nhỏ nhất {tuoi_con_nho_nhat} tuổi; chi phí và nhu cầu chăm sóc có thể cao."
    else:
        diem_tuoi_con = 0
        ly_do_tuoi_con = "Chưa cung cấp tuổi con nhỏ nhất."

    # Nhóm 4: Tác động xã hội (15 điểm).
    la_nganh_y_te = any(
        tu_khoa in nghe_nghiep_chuan
        for tu_khoa in ["bac si", "y khoa", "duoc", "dieu duong", "suc khoe", "health", "medicine"]
    )
    la_nghien_cuu = any(
        tu_khoa in nghe_nghiep_chuan
        for tu_khoa in ["nghien cuu", "research", "giang vien", "giao duc", "khoa hoc"]
    )
    la_khu_vuc_cong = any(
        tu_khoa in nghe_nghiep_chuan
        for tu_khoa in ["khu vuc cong", "nha nuoc", "benh vien cong", "bo y te", "public", "chinh phu"]
    )
    la_khu_vuc_tu = any(
        tu_khoa in nghe_nghiep_chuan
        for tu_khoa in ["khu vuc tu", "tu nhan", "benh vien tu", "private", "doanh nghiep"]
    )
    if la_nganh_y_te or la_nghien_cuu:
        diem_nganh_nghe = 10
        ly_do_nganh_nghe = "Ngành nghề có liên quan trực tiếp đến y tế/nghiên cứu và tạo tác động xã hội."
    elif nghe_nghiep.strip():
        diem_nganh_nghe = 6
        ly_do_nganh_nghe = "Có kinh nghiệm nghề nghiệp, nhưng mức liên quan với tác động xã hội cần làm rõ."
    else:
        diem_nganh_nghe = 0
        ly_do_nganh_nghe = "Chưa cung cấp nghề nghiệp."

    if la_khu_vuc_cong:
        diem_khu_vuc = 5
        ly_do_khu_vuc = "Kinh nghiệm khu vực công củng cố yếu tố phục vụ cộng đồng."
    elif la_khu_vuc_tu:
        diem_khu_vuc = 3
        ly_do_khu_vuc = "Kinh nghiệm khu vực tư vẫn có giá trị, cần nêu rõ tác động xã hội."
    else:
        diem_khu_vuc = 2
        ly_do_khu_vuc = "Chưa xác định khu vực công/tư; nên bổ sung trong hồ sơ."
    diem_tac_dong = min(15, diem_nganh_nghe + diem_khu_vuc)

    # Nhóm 5: Chiến lược (15 điểm). Không có tham số cam kết riêng,
    # nên việc liên hệ supervisor được dùng làm tín hiệu cam kết thận trọng.
    diem_chien_luoc = 15 if co_supervisor else 0
    ly_do_chien_luoc = (
        "Đã liên hệ supervisor, thể hiện định hướng nghiên cứu và cam kết chiến lược rõ ràng."
        if co_supervisor
        else "Chưa liên hệ supervisor; cần xác định người hướng dẫn và kế hoạch học tập cụ thể."
    )

    diem_ngon_ngu = min(20, diem_ngon_ngu)
    ket_qua = []

    for hb in hoc_bong_list:
        tuoi_min = int(hb["tuoi_min"])
        tuoi_max = int(hb["tuoi_max"])
        loai_chuan = _bo_dau(hb["loai"])
        ho_tro = hb["ho_tro_gia_dinh"].lower()
        diem_bang_raw, ly_do_bang = _diem_bang_cap(bang_cap, hb["loai"])
        diem_bang = round(diem_bang_raw * 12 / 30, 1)
        diem_gia_dinh = min(20, ho_tro_diem.get(ho_tro, 0) + diem_so_con + diem_tuoi_con)
        ly_do_gia_dinh = (
            f"{'Có' if ho_tro == 'yes' else 'Có điều kiện' if ho_tro == 'conditional' else 'Không có'} "
            f"hỗ trợ dependent; {ly_do_so_con} {ly_do_tuoi_con}"
        )

        # Các chương trình nghiên cứu sau Tiến sĩ được ưu tiên nhẹ khi hồ sơ
        # có công bố quốc tế; điểm vẫn nằm trong đúng 5 nhóm/100 điểm.
        diem_hoc_thuat = round(diem_bang + diem_kinh_nghiem + diem_cong_bo, 1)
        if "nghien cuu" in loai_chuan and so_cong_bo:
            diem_hoc_thuat = min(30, round(diem_hoc_thuat + min(2, so_cong_bo * 0.4), 1))

        tong_diem = round(
            diem_hoc_thuat
            + diem_ngon_ngu
            + diem_gia_dinh
            + diem_tac_dong
            + diem_chien_luoc,
            1,
        )
        ket_qua.append(
            {
                "diem": tong_diem,
                "ten": hb["ten"],
                "nuoc": hb["nuoc"],
                "tro_cap": hb["muc_tro_cap_eur"],
                "diem_hoc_thuat": diem_hoc_thuat,
                "diem_bang": diem_bang,
                "diem_gia_dinh": diem_gia_dinh,
                "ly_do": (
                    f"Học thuật/chuyên môn {diem_hoc_thuat}/30; "
                    f"ngôn ngữ {diem_ngon_ngu}/20; gia đình {diem_gia_dinh}/20; "
                    f"tác động xã hội {diem_tac_dong}/15; chiến lược {diem_chien_luoc}/15. "
                    f"{ly_do_bang} {ly_do_gia_dinh}"
                ),
            }
        )

    ket_qua.sort(key=lambda item: item["diem"], reverse=True)
    top_3 = ket_qua[:3]
    diem_hoc_thuat_co_so = max(item["diem_hoc_thuat"] for item in ket_qua)
    diem_bang_hien_thi = top_3[0]["diem_bang"]
    diem_tong_co_so = round(
        diem_hoc_thuat_co_so
        + diem_ngon_ngu
        + min(20, 10 + diem_so_con + diem_tuoi_con)
        + diem_tac_dong
        + diem_chien_luoc,
        1,
    )
    diem_manh = []
    diem_yeu = []
    if diem_hoc_thuat_co_so >= 24:
        diem_manh.append(
            f"Nền tảng học thuật/chuyên môn tốt ({diem_hoc_thuat_co_so}/30), "
            f"gồm bằng cấp, {kinh_nghiem_nam} năm kinh nghiệm và {so_cong_bo} công bố."
        )
    if diem_ielts >= 12:
        diem_manh.append(f"IELTS {ielts_score} tạo lợi thế ngôn ngữ ({diem_ielts}/15).")
    elif ielts_score == 0:
        diem_yeu.append("Chưa có IELTS; nên thi và đặt mục tiêu tối thiểu 6.5-7.0.")
    if ngon_ngu_nuoc_den:
        diem_manh.append("Đã biết ngôn ngữ nước đến, đạt thêm 5/5 điểm ngôn ngữ.")
    else:
        diem_yeu.append("Chưa biết ngôn ngữ nước đến; nên học ngôn ngữ cơ bản trước khi đi.")
    if so_cong_bo >= 3:
        diem_manh.append(f"Có {so_cong_bo} công bố quốc tế, củng cố năng lực nghiên cứu.")
    elif so_cong_bo == 0:
        diem_yeu.append("Chưa có công bố quốc tế; nên bổ sung bài báo/công trình hoặc đề cương nghiên cứu.")
    if co_supervisor:
        diem_manh.append("Đã liên hệ supervisor, giúp hồ sơ có định hướng chiến lược rõ ràng.")
    else:
        diem_yeu.append("Chưa liên hệ supervisor; đây là ưu tiên cải thiện lớn nhất.")
    if la_khu_vuc_cong or la_khu_vuc_tu:
        diem_manh.append(
            f"Đã xác định kinh nghiệm thuộc {'khu vực công' if la_khu_vuc_cong else 'khu vực tư'}."
        )
    else:
        diem_yeu.append("Chưa nêu rõ khu vực công/tư và tác động xã hội trong nghề nghiệp.")
    if so_con > 0 and tuoi_con_nho_nhat < 6:
        diem_yeu.append("Có con nhỏ dưới 6 tuổi; cần lập kế hoạch chăm sóc, trường học và chi phí dependent.")

    phan_hoi = [
        f"Đánh giá hồ sơ {tuoi} tuổi, {nghe_nghiep}, {so_con} con:",
        f"Điểm tổng tham khảo theo hồ sơ cơ sở: {diem_tong_co_so}/100",
        "\nĐiểm từng nhóm:",
        f"- Học thuật/chuyên môn: tối đa {diem_hoc_thuat_co_so}/30 "
        f"(học bổng đứng đầu: bằng cấp {diem_bang_hien_thi}/12, "
        f"kinh nghiệm {diem_kinh_nghiem}/8, công bố {diem_cong_bo}/10)",
        f"- Ngôn ngữ: {diem_ngon_ngu}/20 (IELTS {diem_ielts}/15, ngôn ngữ nước đến {diem_ngon_ngu_nuoc_den}/5)",
        f"- Gia đình phù hợp: thay đổi theo từng học bổng, tối đa 20 điểm "
        f"(số con {diem_so_con}/5, tuổi con {diem_tuoi_con}/5, dependent tối đa 10)",
        f"- Tác động xã hội: {diem_tac_dong}/15 ({ly_do_nganh_nghe} {ly_do_khu_vuc})",
        f"- Chiến lược: {diem_chien_luoc}/15 ({ly_do_chien_luoc})",
        "\nĐiểm mạnh cụ thể:",
    ]
    phan_hoi.extend(f"- {diem}" for diem in (diem_manh or ["Chưa đủ dữ liệu để xác định điểm mạnh nổi bật."]))
    phan_hoi.append("\nĐiểm yếu cần cải thiện:")
    phan_hoi.extend(f"- {diem}" for diem in (diem_yeu or ["Không phát hiện điểm yếu lớn từ dữ liệu đã cung cấp."]))
    phan_hoi.append("\nTop 3 học bổng phù hợp nhất:")
    for thu_hang, hb in enumerate(top_3, start=1):
        phan_hoi.append(
            f"\n{thu_hang}. {hb['ten']} ({hb['nuoc']}) — {hb['diem']}/100"
            f"\n   Trợ cấp tham khảo: {hb['tro_cap']} EUR/tháng"
            f"\n   Lý do: {hb['ly_do']}"
        )
    phan_hoi.append(
        "\nLưu ý: Điểm tổng thay đổi theo chính sách dependent của từng học bổng; "
        "điểm số là đánh giá sơ bộ từ database hiện có, không thay thế điều kiện chính thức."
    )
    return "\n".join(phan_hoi)


def danh_gia_ho_so(
    tuoi: int,
    bang_cap: str,
    kinh_nghiem_nam: int,
    nghe_nghiep: str,
    so_con: int,
    ielts_score: float,
    so_cong_bo: int,
    co_supervisor: bool,
    ngon_ngu_nuoc_den: bool,
    tuoi_con_nho_nhat: int,
    loai_to_chuc: str,
    co_thu_gioi_thieu_qt: bool,
    da_lien_he_alumni: bool,
    co_chung_minh_tai_chinh: bool,
    tinh_trang_suc_khoe: str,
) -> str:
    """Đánh giá hồ sơ theo 15 yếu tố và 6 nhóm điểm, tối đa 100 điểm.

    tuoi_con_nho_nhat nên là -1 nếu hồ sơ không có con. Bộ 15 yếu tố không
    có tham số cam_ket_tro_ve riêng, nên phần cam kết được ước lượng thận
    trọng từ loại tổ chức và được ghi rõ là proxy trong báo cáo.
    """
    nghe_nghiep_chuan = _bo_dau(nghe_nghiep)
    tuoi = int(tuoi)
    kinh_nghiem_nam = max(0, int(kinh_nghiem_nam))
    so_con = max(0, int(so_con))
    ielts_score = max(0.0, min(9.0, float(ielts_score)))
    so_cong_bo = max(0, int(so_cong_bo))
    loai_to_chuc_chuan = _bo_dau(loai_to_chuc).strip()
    if loai_to_chuc_chuan not in {"cong", "tu", "ngo"}:
        loai_to_chuc_chuan = "khac"

    tinh_trang_suc_khoe_chuan = _bo_dau(tinh_trang_suc_khoe).strip()
    diem_suc_khoe_map = {"tot": 5, "on dinh": 4, "co benh man tinh": 2}
    diem_suc_khoe = float(
        round(diem_suc_khoe_map.get(tinh_trang_suc_khoe_chuan, 0), 1)
    )
    ly_do_suc_khoe = {
        "tot": "Sức khỏe tốt, thuận lợi cho kế hoạch học tập dài hạn.",
        "on dinh": "Sức khỏe ổn định; nên chuẩn bị hồ sơ y tế và bảo hiểm phù hợp.",
        "co benh man tinh": "Có bệnh mạn tính; cần kế hoạch điều trị, bảo hiểm và thuốc men khi ở nước ngoài.",
    }.get(
        tinh_trang_suc_khoe_chuan,
        "Chưa xác định tình trạng sức khỏe theo ba mức được yêu cầu.",
    )

    # Nhóm 1: Học thuật/chuyên môn (25 điểm).
    diem_kinh_nghiem = float(
        round(min(8, kinh_nghiem_nam * 8 / 20), 1)
    )
    diem_cong_bo = float(round(min(7, so_cong_bo * 1.4), 1))

    # Nhóm 2: Ngôn ngữ (15 điểm).
    if ielts_score >= 8:
        diem_ielts = 10
    elif ielts_score >= 7:
        diem_ielts = 9
    elif ielts_score >= 6.5:
        diem_ielts = 8
    elif ielts_score >= 6:
        diem_ielts = 6
    elif ielts_score > 0:
        diem_ielts = 3
    else:
        diem_ielts = 0
    diem_ielts = float(round(diem_ielts, 1))
    diem_ngon_ngu_nuoc_den = float(
        round(5 if ngon_ngu_nuoc_den else 0, 1)
    )
    diem_ngon_ngu = float(
        round(diem_ielts + diem_ngon_ngu_nuoc_den, 1)
    )

    # Nhóm 3: Gia đình phù hợp (20 điểm).
    if so_con == 0:
        diem_so_con = 4
        ly_do_so_con = "Không có con đi cùng nên áp lực dependent thấp hơn."
    elif so_con <= 2:
        diem_so_con = 3
        ly_do_so_con = f"Có {so_con} con; quy mô gia đình vẫn tương đối dễ bố trí."
    elif so_con == 3:
        diem_so_con = 2
        ly_do_so_con = "Có 3 con; cần ưu tiên học bổng có chính sách dependent rõ ràng."
    else:
        diem_so_con = 1
        ly_do_so_con = f"Có {so_con} con; cần kế hoạch tài chính và dependent chi tiết."

    if so_con == 0 or tuoi_con_nho_nhat >= 12:
        diem_tuoi_con = 4
        ly_do_tuoi_con = "Con đã lớn hoặc không có con nhỏ."
    elif tuoi_con_nho_nhat >= 6:
        diem_tuoi_con = 3
        ly_do_tuoi_con = f"Con nhỏ nhất {tuoi_con_nho_nhat} tuổi; nhu cầu chăm sóc ở mức vừa phải."
    elif tuoi_con_nho_nhat >= 3:
        diem_tuoi_con = 2
        ly_do_tuoi_con = f"Con nhỏ nhất {tuoi_con_nho_nhat} tuổi; cần dự trù chăm sóc và học tập."
    elif tuoi_con_nho_nhat >= 0:
        diem_tuoi_con = 1
        ly_do_tuoi_con = f"Con nhỏ nhất {tuoi_con_nho_nhat} tuổi; chi phí chăm sóc có thể cao."
    else:
        diem_tuoi_con = 0
        ly_do_tuoi_con = "Chưa cung cấp tuổi con nhỏ nhất."
    diem_so_con = float(round(diem_so_con, 1))
    diem_tuoi_con = float(round(diem_tuoi_con, 1))
    diem_tai_chinh = float(round(6 if co_chung_minh_tai_chinh else 0, 1))

    # Nhóm 5: Tác động xã hội (15 điểm).
    la_nganh_uu_tien = (
        any(
            tu_khoa in nghe_nghiep_chuan
            for tu_khoa in [
                "bac si",
                "y khoa",
                "duoc",
                "dieu duong",
                "suc khoe",
                "health",
                "medicine",
                "nghien cuu",
                "research",
                "giang vien",
                "giao duc",
                "khoa hoc",
                "moi truong",
                "phat trien",
                "cong dong",
                "xa hoi",
                "giao vien",
            ]
        )
    )
    if la_nganh_uu_tien:
        diem_nganh_nghe = 8
        ly_do_nganh_nghe = "Ngành nghề thuộc nhóm ưu tiên y tế/nghiên cứu/phát triển xã hội."
    elif nghe_nghiep.strip():
        diem_nganh_nghe = 4
        ly_do_nganh_nghe = "Có nghề nghiệp rõ ràng nhưng cần làm nổi bật tác động xã hội."
    else:
        diem_nganh_nghe = 0
        ly_do_nganh_nghe = "Chưa cung cấp nghề nghiệp."
    diem_khu_vuc = {"cong": 7, "ngo": 7, "tu": 4, "khac": 1}[loai_to_chuc_chuan]
    ly_do_khu_vuc = {
        "cong": "Khu vực công tạo liên kết rõ với phục vụ cộng đồng.",
        "ngo": "Tổ chức NGO phù hợp với định hướng phát triển và tác động xã hội.",
        "tu": "Khu vực tư có giá trị thực tiễn; cần lượng hóa tác động cộng đồng.",
        "khac": "Loại tổ chức chưa thuộc ba nhóm công/tư/NGO.",
    }[loai_to_chuc_chuan]
    diem_nganh_nghe = float(round(diem_nganh_nghe, 1))
    diem_khu_vuc = float(round(diem_khu_vuc, 1))
    diem_tac_dong = float(
        round(min(15, diem_nganh_nghe + diem_khu_vuc), 1)
    )

    # Nhóm 6: Sức khỏe và cam kết (10 điểm). Do không có tham số cam kết
    # trở về riêng, loại tổ chức là tín hiệu proxy, không phải kết luận pháp lý.
    diem_cam_ket = float(
        round(
            {"cong": 5, "ngo": 4, "tu": 3, "khac": 1}[loai_to_chuc_chuan],
            1,
        )
    )
    ly_do_cam_ket = (
        f"Cam kết trở về tạm tính {diem_cam_ket}/5 theo loại tổ chức "
        f"'{loai_to_chuc_chuan}'; cần bổ sung kế hoạch trở về trong bài luận."
    )
    diem_suc_khoe_cam_ket = float(
        round(diem_suc_khoe + diem_cam_ket, 1)
    )

    ket_qua = []
    for hb in hoc_bong_list:
        tuoi_min = int(hb["tuoi_min"])
        tuoi_max = int(hb["tuoi_max"])
        if not (tuoi_min <= tuoi <= tuoi_max):
            continue

        diem_bang_raw, ly_do_bang = _diem_bang_cap(bang_cap, hb["loai"])
        diem_bang = float(round(diem_bang_raw * 10 / 30, 1))
        diem_hoc_thuat = float(
            round(
                min(25, diem_bang + diem_kinh_nghiem + diem_cong_bo),
                1,
            )
        )
        loai_hoc_bong_chuan = _bo_dau(hb["loai"])
        if "nghien cuu" in loai_hoc_bong_chuan and so_cong_bo:
            diem_hoc_thuat = float(
                round(
                    min(25, diem_hoc_thuat + min(2, so_cong_bo * 0.4)),
                    1,
                )
            )

        ho_tro = hb["ho_tro_gia_dinh"].lower()
        diem_dependent = float(
            round({"yes": 6, "conditional": 3, "no": 0}.get(ho_tro, 0), 1)
        )
        diem_gia_dinh = float(
            round(
                min(
                    20,
                    diem_so_con
                    + diem_tuoi_con
                    + diem_tai_chinh
                    + diem_dependent,
                ),
                1,
            )
        )
        ly_do_gia_dinh = (
            f"{'Có' if ho_tro == 'yes' else 'Có điều kiện' if ho_tro == 'conditional' else 'Không có'} "
            f"hỗ trợ dependent ({diem_dependent}/6); {ly_do_so_con} "
            f"{ly_do_tuoi_con} Chứng minh tài chính bổ sung: {diem_tai_chinh}/6."
        )

        diem_supervisor = float(round(7 if co_supervisor else 0, 1))
        diem_alumni = float(round(4 if da_lien_he_alumni else 0, 1))
        diem_thu_gioi_thieu_qt = float(
            round(4 if co_thu_gioi_thieu_qt else 0, 1)
        )
        diem_mang_luoi = float(
            round(
                diem_supervisor + diem_alumni + diem_thu_gioi_thieu_qt,
                1,
            )
        )
        tong_diem = float(
            round(
                diem_hoc_thuat
                + diem_ngon_ngu
                + diem_gia_dinh
                + diem_mang_luoi
                + diem_tac_dong
                + diem_suc_khoe_cam_ket,
                1,
            )
        )
        ket_qua.append(
            {
                "diem": tong_diem,
                "ten": hb["ten"],
                "nuoc": hb["nuoc"],
                "tro_cap": hb["muc_tro_cap_eur"],
                "diem_hoc_thuat": diem_hoc_thuat,
                "diem_ngon_ngu": diem_ngon_ngu,
                "diem_gia_dinh": diem_gia_dinh,
                "diem_mang_luoi": diem_mang_luoi,
                "diem_tac_dong": diem_tac_dong,
                "diem_suc_khoe_cam_ket": diem_suc_khoe_cam_ket,
                "diem_bang": diem_bang,
                "ly_do": (
                    f"Học thuật/chuyên môn {diem_hoc_thuat}/25; ngôn ngữ {diem_ngon_ngu}/15; "
                    f"gia đình {diem_gia_dinh}/20; mạng lưới quan hệ {diem_mang_luoi}/15; "
                    f"tác động xã hội {diem_tac_dong}/15; sức khỏe và cam kết "
                    f"{diem_suc_khoe_cam_ket}/10. {ly_do_bang} {ly_do_gia_dinh}"
                ),
                "nhan_xet": {
                    "hoc_thuat": f"{ly_do_bang} {kinh_nghiem_nam} năm kinh nghiệm và {so_cong_bo} công bố quốc tế.",
                    "ngon_ngu": f"IELTS {ielts_score} đạt {diem_ielts}/10; ngôn ngữ nước đến đạt {diem_ngon_ngu_nuoc_den}/5.",
                    "gia_dinh": ly_do_gia_dinh,
                    "mang_luoi": (
                        f"Supervisor {'đã liên hệ' if co_supervisor else 'chưa liên hệ'}, "
                        f"alumni {'đã liên hệ' if da_lien_he_alumni else 'chưa liên hệ'}, "
                        f"thư giới thiệu quốc tế {'đã có' if co_thu_gioi_thieu_qt else 'chưa có'}."
                    ),
                    "tac_dong": f"{ly_do_nganh_nghe} {ly_do_khu_vuc}",
                    "suc_khoe": f"{ly_do_suc_khoe} {ly_do_cam_ket}",
                },
            }
        )

    if not ket_qua:
        return (
            f"Không có học bổng trong database phù hợp với tuổi {tuoi}. "
            "Các chương trình hiện có yêu cầu độ tuổi trong khoảng 30-55."
        )

    ket_qua.sort(key=lambda item: (-item["diem"], -item["diem_gia_dinh"]))
    top_3 = ket_qua[:3]
    tot_nhat = top_3[0]
    diem_tong = tot_nhat["diem"]
    xep_loai = (
        "Xuất sắc"
        if diem_tong >= 85
        else "Tốt"
        if diem_tong >= 70
        else "Cần cải thiện"
        if diem_tong >= 50
        else "Chưa đủ"
    )

    diem_manh = [
        (
            tot_nhat["diem_hoc_thuat"],
            f"Học thuật/chuyên môn {tot_nhat['diem_hoc_thuat']}/25: bằng {bang_cap}, "
            f"{kinh_nghiem_nam} năm kinh nghiệm và {so_cong_bo} công bố quốc tế.",
        ),
        (
            diem_mang_luoi,
            f"Mạng lưới quan hệ {diem_mang_luoi}/15 với supervisor="
            f"{'có' if co_supervisor else 'chưa'}, alumni="
            f"{'có' if da_lien_he_alumni else 'chưa'} và thư giới thiệu quốc tế="
            f"{'có' if co_thu_gioi_thieu_qt else 'chưa'}.",
        ),
        (
            diem_tac_dong,
            f"Tác động xã hội {diem_tac_dong}/15: {ly_do_nganh_nghe} {ly_do_khu_vuc}",
        ),
        (
            diem_ngon_ngu,
            f"Ngôn ngữ {diem_ngon_ngu}/15 với IELTS {ielts_score} và "
            f"ngôn ngữ nước đến={'đã biết' if ngon_ngu_nuoc_den else 'chưa biết'}.",
        ),
    ]
    diem_manh = [item[1] for item in sorted(diem_manh, reverse=True)[:3]]

    diem_yeu = [
        (
            round(15 - diem_ngon_ngu, 1),
            f"Ngôn ngữ còn thiếu {round(15 - diem_ngon_ngu, 1)} điểm; ưu tiên IELTS và ngôn ngữ nước đến.",
        ),
        (
            round(15 - diem_mang_luoi, 1),
            f"Mạng lưới còn thiếu {round(15 - diem_mang_luoi, 1)} điểm; cần liên hệ supervisor/alumni "
            "và xin thư giới thiệu quốc tế.",
        ),
        (
            round(10 - diem_suc_khoe_cam_ket, 1),
            (
                f"Sức khỏe và cam kết còn thiếu {round(10 - diem_suc_khoe_cam_ket, 1)} điểm; "
                "cần bổ sung kế hoạch điều trị hoặc kế hoạch trở về cụ thể."
                if diem_suc_khoe_cam_ket < 10
                else "Sức khỏe đạt tối đa; vẫn cần chứng minh cam kết trở về bằng kế hoạch cụ thể."
            ),
        ),
        (
            round(20 - tot_nhat["diem_gia_dinh"], 1),
            f"Gia đình còn thiếu {round(20 - tot_nhat['diem_gia_dinh'], 1)} điểm; cần hoàn thiện "
            "chứng minh tài chính và xác minh chính sách dependent.",
        ),
        (
            round(25 - tot_nhat["diem_hoc_thuat"], 1),
            f"Học thuật còn thiếu {round(25 - tot_nhat['diem_hoc_thuat'], 1)} điểm; "
            "cần tăng công bố hoặc làm rõ sự phù hợp của bằng cấp.",
        ),
    ]
    diem_yeu = [item[1] for item in sorted(diem_yeu, reverse=True)[:3]]

    phan_hoi = [
        f"Đánh giá hồ sơ {tuoi} tuổi, {nghe_nghiep}, {so_con} con:",
        f"Điểm tổng: {diem_tong}/100 — Xếp loại: {xep_loai}",
        "(Điểm tổng lấy theo học bổng phù hợp nhất trong database; tuổi được dùng "
        "như điều kiện lọc 30-55, không cộng thêm vào 6 nhóm điểm.)",
        "\nĐiểm từng nhóm:",
        f"- Học thuật/chuyên môn: {tot_nhat['diem_hoc_thuat']}/25 "
        f"(bằng cấp {tot_nhat['diem_bang']}/10, kinh nghiệm {diem_kinh_nghiem}/8, "
        f"công bố {diem_cong_bo}/7).",
        f"- Ngôn ngữ: {diem_ngon_ngu}/15 (IELTS {diem_ielts}/10, "
        f"ngôn ngữ nước đến {diem_ngon_ngu_nuoc_den}/5).",
        f"- Gia đình phù hợp: {tot_nhat['diem_gia_dinh']}/20 "
        f"(số con {diem_so_con}/4, tuổi con {diem_tuoi_con}/4, "
        f"tài chính bổ sung {diem_tai_chinh}/6, dependent {tot_nhat['diem_gia_dinh'] - diem_so_con - diem_tuoi_con - diem_tai_chinh}/6).",
        f"- Mạng lưới quan hệ: {diem_mang_luoi}/15 (supervisor "
        f"{diem_supervisor}/7, alumni {diem_alumni}/4, "
        f"thư giới thiệu quốc tế {diem_thu_gioi_thieu_qt}/4).",
        f"- Tác động xã hội: {diem_tac_dong}/15 ({ly_do_nganh_nghe} {ly_do_khu_vuc})",
        f"- Sức khỏe và cam kết: {diem_suc_khoe_cam_ket}/10 "
        f"(sức khỏe {diem_suc_khoe}/5; cam kết proxy {diem_cam_ket}/5).",
        "\nTop 3 điểm mạnh cụ thể:",
    ]
    phan_hoi.extend(f"- {diem}" for diem in diem_manh)
    phan_hoi.append("\nTop 3 điểm yếu cần cải thiện ngay:")
    phan_hoi.extend(f"- {diem}" for diem in diem_yeu)
    phan_hoi.extend(
        [
            "\nKế hoạch cải thiện trong 3 tháng:",
            "1. Tháng 1: chốt 3 học bổng mục tiêu, kiểm tra điều kiện bằng cấp, lập danh sách supervisor/alumni và xác định giấy tờ dependent.",
            "2. Tháng 2: thi hoặc nâng IELTS, học ngôn ngữ nước đến, xin thư giới thiệu quốc tế, bổ sung công bố/đề cương nghiên cứu và hoàn thiện chứng minh tài chính.",
            "3. Tháng 3: gửi email cho supervisor/alumni, hoàn thiện bài luận tác động xã hội và cam kết trở về, kiểm tra hồ sơ sức khỏe-bảo hiểm rồi rà soát hồ sơ từng học bổng.",
            "\nTop 3 học bổng phù hợp nhất:",
        ]
    )
    for thu_hang, hb in enumerate(top_3, start=1):
        phan_hoi.append(
            f"\n{thu_hang}. {hb['ten']} ({hb['nuoc']}) — {hb['diem']}/100"
            f"\n   Trợ cấp tham khảo: {hb['tro_cap']} EUR/tháng"
            f"\n   Cơ cấu điểm: học thuật {hb['diem_hoc_thuat']}/25, ngôn ngữ "
            f"{hb['diem_ngon_ngu']}/15, gia đình {hb['diem_gia_dinh']}/20, "
            f"mạng lưới {hb['diem_mang_luoi']}/15, tác động {hb['diem_tac_dong']}/15, "
            f"sức khỏe & cam kết {hb['diem_suc_khoe_cam_ket']}/10."
            f"\n   Lý do: {hb['ly_do']}"
        )
    phan_hoi.append(
        "\nLưu ý: Điểm số là đánh giá sơ bộ từ database hiện có; cam kết trở về "
        "được dùng như proxy vì không có tham số riêng, và điểm số không thay thế "
        "điều kiện chính thức của từng chương trình."
    )
    return "\n".join(phan_hoi)


def cai_thien_ho_so(
    diem_yeu_list: list[str],
    thoi_gian_chuan_bi_thang: int,
) -> str:
    """Tạo lịch cải thiện theo tuần dựa trên các điểm yếu của hồ sơ."""
    if isinstance(diem_yeu_list, str):
        diem_yeu_list = [diem_yeu_list]
    diem_yeu_list = [str(diem).strip() for diem in diem_yeu_list if str(diem).strip()]
    so_thang = max(1, min(12, int(thoi_gian_chuan_bi_thang)))
    van_de = _bo_dau(" ".join(diem_yeu_list))

    tracks = []
    if any(tu_khoa in van_de for tu_khoa in ["ielts", "ngoai ngu", "ngon ngu"]):
        tracks.append(
            (
                "IELTS/ngôn ngữ",
                [
                    "Tuần 1: làm bài kiểm tra đầu vào miễn phí, đặt mục tiêu IELTS 6.5 và lập lịch học 45-60 phút/ngày.",
                    "Tuần 2: luyện Reading/Listening theo dạng bài, ghi lại lỗi và học 20 từ mới mỗi ngày.",
                    "Tuần 3: luyện Writing/Speaking với bạn học hoặc cộng đồng trao đổi ngôn ngữ.",
                    "Tuần 4: làm một đề thi thử, chấm theo band descriptor và điều chỉnh kế hoạch.",
                ],
                "British Council IELTS Ready, IDP IELTS sample tests, Cambridge English sample tests, BBC Learning English.",
            )
        )
    if any(tu_khoa in van_de for tu_khoa in ["cong bo", "bai bao", "hoi thao", "nghien cuu"]):
        tracks.append(
            (
                "Công bố/hội thảo quốc tế",
                [
                    "Tuần 1: chọn một đề tài hẹp, lập danh sách 3-5 hội thảo có hạn nộp phù hợp và kiểm tra uy tín/indexing.",
                    "Tuần 2: viết abstract 250-300 từ, tìm đồng tác giả/mentor và hoàn thiện câu hỏi nghiên cứu.",
                    "Tuần 3: viết bản thảo hoặc poster, xin phản biện nội bộ và chuẩn hóa trích dẫn.",
                    "Tuần 4: nộp đúng kênh chính thức, lưu biên nhận và kiểm tra điều khoản proceedings; tránh hội thảo thu phí bất thường.",
                ],
                "Google Scholar, DOAJ, OpenAlex, Think.Check.Submit và kho mẫu bài của các hội chuyên ngành.",
            )
        )
    if any(tu_khoa in van_de for tu_khoa in ["supervisor", "professor", "giao su", "nguoi huong dan"]):
        tracks.append(
            (
                "Tiếp cận supervisor",
                [
                    "Tuần 1: lập danh sách 10 giáo sư phù hợp, đọc một bài gần đây của mỗi người và ghi rõ điểm giao với đề tài.",
                    "Tuần 2: cá nhân hóa và gửi 3-5 email đầu tiên, kèm CV 2 trang và research concept một trang.",
                    "Tuần 3: gửi nhóm tiếp theo, theo dõi phản hồi và chuẩn bị câu trả lời cho câu hỏi về phương pháp.",
                    "Tuần 4: follow-up lịch sự sau 7-10 ngày và đặt lịch trao đổi nếu có phản hồi.",
                ],
                "Google Scholar, ORCID, trang khoa của đại học, OpenAlex và Google Docs để quản lý danh sách liên hệ.",
            )
        )
    if any(tu_khoa in van_de for tu_khoa in ["alumni", "mang luoi", "quan he"]):
        tracks.append(
            (
                "Mạng lưới/alumni",
                [
                    "Tuần 1: tìm 5 alumni qua trang chương trình, LinkedIn hoặc hội cựu sinh viên.",
                    "Tuần 2: gửi tin nhắn ngắn, nêu rõ câu hỏi về chương trình và kinh nghiệm đi cùng gia đình.",
                    "Tuần 3: thực hiện 2 cuộc trao đổi 15-20 phút và ghi lại thông tin có thể kiểm chứng.",
                    "Tuần 4: cảm ơn, xin phép giữ liên lạc và xác minh lại các yêu cầu quan trọng từ website chính thức.",
                ],
                "LinkedIn, trang alumni chính thức, Google Meet và các webinar công khai của trường/chương trình.",
            )
        )
    if any(tu_khoa in van_de for tu_khoa in ["thu gioi thieu", "gioi thieu"]):
        tracks.append(
            (
                "Thư giới thiệu",
                [
                    "Tuần 1: chọn 2-3 người có thể đánh giá trực tiếp năng lực, xin lịch trao đổi và gửi CV.",
                    "Tuần 2: chuẩn bị bảng thành tích, đề cương mục tiêu và hướng dẫn nộp thư.",
                    "Tuần 3: nhắc hạn nộp trước ít nhất 7 ngày, kiểm tra đúng email/hệ thống.",
                    "Tuần 4: cảm ơn và lưu bản xác nhận đã nộp.",
                ],
                "Google Drive, ORCID, mẫu CV Europass và hướng dẫn hồ sơ trên website chính thức của học bổng.",
            )
        )
    if any(tu_khoa in van_de for tu_khoa in ["tai chinh", "dependent", "gia dinh", "con nho", "hoc phi"]):
        tracks.append(
            (
                "Tài chính/dependent",
                [
                    "Tuần 1: lập ngân sách theo tháng cho cả gia đình, tách học phí, nhà ở, bảo hiểm, trường học và dự phòng.",
                    "Tuần 2: gom giấy khai sinh, giấy đăng ký kết hôn, hộ chiếu và bản dịch công chứng.",
                    "Tuần 3: hỏi trường và cơ quan di trú về quyền học trường công, lệ phí và yêu cầu visa của dependent.",
                    "Tuần 4: hoàn thiện sao kê/thư ngân hàng và bảng giải trình nguồn tiền.",
                ],
                "Google Sheets, website cơ quan di trú/trường công địa phương, UNICEF education resources và các trang đại sứ quán.",
            )
        )
    if any(tu_khoa in van_de for tu_khoa in ["suc khoe", "benh man tinh", "bao hiem"]):
        tracks.append(
            (
                "Sức khỏe/bảo hiểm",
                [
                    "Tuần 1: khám tổng quát, lập danh sách thuốc và xin bản tóm tắt bệnh án bằng tiếng Anh.",
                    "Tuần 2: so sánh yêu cầu bảo hiểm của visa và quyền lợi cho từng thành viên.",
                    "Tuần 3: chuẩn bị thuốc theo quy định nhập cảnh và danh sách cơ sở y tế tại nơi đến.",
                    "Tuần 4: lập lịch theo dõi sức khỏe và quỹ dự phòng y tế.",
                ],
                "Website cơ quan y tế/di trú chính thức, WHO health information và tờ hướng dẫn bảo hiểm của trường.",
            )
        )
    if any(tu_khoa in van_de for tu_khoa in ["cam ket", "tro ve", "tac dong xa hoi"]):
        tracks.append(
            (
                "Cam kết trở về/tác động xã hội",
                [
                    "Tuần 1: viết bản đồ mục tiêu 3 năm và xác định vấn đề tại Việt Nam muốn giải quyết.",
                    "Tuần 2: định lượng tác động dự kiến bằng 2-3 chỉ số cụ thể.",
                    "Tuần 3: xin góp ý từ quản lý/đồng nghiệp và sửa bài luận cá nhân.",
                    "Tuần 4: hoàn thiện kế hoạch trở về, vị trí công việc dự kiến và cách chuyển giao kiến thức.",
                ],
                "UN Sustainable Development Goals, UNDP country reports, Google Docs và các bài luận mẫu công khai.",
            )
        )

    if not tracks:
        tracks.append(
            (
                "Rà soát hồ sơ tổng thể",
                [
                    "Tuần 1: lập checklist điều kiện từng học bổng và xác định 3 khoảng trống lớn nhất.",
                    "Tuần 2: cập nhật CV, research concept và bộ hồ sơ giấy tờ.",
                    "Tuần 3: xin một người có kinh nghiệm phản biện hồ sơ.",
                    "Tuần 4: rà soát bản cuối, đặt lịch thi/nộp và lưu bản sao an toàn.",
                ],
                "Google Sheets, Google Scholar, mẫu CV Europass và website chính thức của từng chương trình.",
            )
        )

    phan_hoi = [
        f"Kế hoạch cải thiện hồ sơ trong {so_thang} tháng dựa trên {len(diem_yeu_list)} điểm yếu:",
        "Mỗi tháng gồm 4 tuần; nếu thời gian dài hơn 1 tháng, lặp chu kỳ với mục tiêu nâng chất lượng và đo lại kết quả.",
    ]
    for thang in range(1, so_thang + 1):
        phan_hoi.append(f"\nTháng {thang}:")
        for ten_track, hanh_dong, _ in tracks:
            if thang == 1:
                viec = hanh_dong
            elif thang == 2:
                viec = [
                    hanh_dong[0].replace("Tuần 1:", "Tuần 1: tiếp tục -"),
                    hanh_dong[1].replace("Tuần 2:", "Tuần 2: tiếp tục -"),
                    hanh_dong[2].replace("Tuần 3:", "Tuần 3: tiếp tục -"),
                    hanh_dong[3].replace("Tuần 4:", "Tuần 4: tiếp tục -"),
                ]
            elif thang == 3:
                viec = [
                    "Tuần 1: kiểm tra tiến độ bằng một kết quả đo được và sửa phần còn yếu.",
                    "Tuần 2: hoàn thiện phiên bản nộp chính thức hoặc thực hiện bước tiếp cận tiếp theo.",
                    "Tuần 3: xin phản biện lần cuối từ mentor/alumni và cập nhật hồ sơ.",
                    "Tuần 4: chốt deadline, nộp hồ sơ và lưu bằng chứng.",
                ]
            else:
                viec = [
                    "Tuần 1: đo lại kết quả và nâng mục tiêu thêm một bậc.",
                    "Tuần 2: duy trì luyện tập/tiếp cận tối thiểu 5 giờ.",
                    "Tuần 3: cập nhật tài liệu theo phản hồi mới nhất.",
                    "Tuần 4: rà soát deadline và loại bỏ tài nguyên/hội thảo không đáng tin.",
                ]
            phan_hoi.append(f"- {ten_track}:")
            phan_hoi.extend(f"  {hanh_dong_tuan}" for hanh_dong_tuan in viec)

    phan_hoi.append("\nNguồn tài nguyên miễn phí ưu tiên:")
    tai_nguyen = []
    for _, _, nguon in tracks:
        if nguon not in tai_nguyen:
            tai_nguyen.append(nguon)
    phan_hoi.extend(f"- {nguon}" for nguon in tai_nguyen)
    if any(ten_track == "Tiếp cận supervisor" for ten_track, _, _ in tracks):
        phan_hoi.extend(
            [
                "\nMẫu email tiếp cận professor:",
                "Subject: Prospective applicant interested in your research on [topic]",
                "Dear Professor [Last name],",
                "My name is [Name], a [current role] with [X] years of experience in [field]. "
                "I recently read your work on [specific paper/topic] and would like to explore "
                "a research proposal on [one-sentence topic].",
                "I am preparing an application for [scholarship/program] and would be grateful "
                "to know whether you are accepting doctoral/postdoctoral students for [period]. "
                "My CV and one-page research concept are attached.",
                "Would you be available for a brief meeting? Thank you for your time.",
                "Kind regards,\n[Name] | [Email] | [ORCID/Google Scholar]",
            ]
        )
    phan_hoi.append(
        "\nCách theo dõi: mỗi Chủ nhật ghi 3 cột 'đã làm - bằng chứng - bước tiếp theo'; "
        "không trả phí cho hội thảo hoặc dịch vụ hứa hẹn xuất bản nhanh nếu chưa kiểm tra uy tín."
    )
    return "\n".join(phan_hoi)


HOCPHI_CON_DB = {
    "duc": {
        "ten": "Đức",
        "truong_cong": "Trường công lập thường miễn học phí ở bậc mầm non phổ thông tùy bang/thành phố và miễn học phí tiểu học, trung học; vẫn có thể có phí ăn, sách, hoạt động hoặc giữ trẻ.",
        "dieu_kien": "Con cần đăng ký cư trú và phụ thuộc vào loại visa/quyền cư trú của cha mẹ; trường và địa phương quyết định việc xếp lớp, ngôn ngữ hỗ trợ.",
        "ho_tro": "Có thể hỏi Bildung und Teilhabe, trợ cấp địa phương và miễn/giảm phí Kita; hỗ trợ phụ thuộc thu nhập và tình trạng cư trú.",
        "quoc_te": "Khoảng 8.000-25.000 EUR/năm, tùy trường và thành phố.",
        "cong_dong": "Tìm Hội người Việt tại Đức và nhóm phụ huynh Việt theo thành phố như Berlin, München, Frankfurt; nên hỏi cả kinh nghiệm đăng ký trường công.",
    },
    "anh": {
        "ten": "Anh",
        "truong_cong": "Trường state school miễn học phí cho trẻ đủ điều kiện domestic; nursery/childcare và một số khoản ăn, đồng phục, hoạt động thường tính riêng.",
        "dieu_kien": "Phụ thuộc visa của cha mẹ, thời hạn cư trú và quy định của local authority; cần kiểm tra quyền học trường công trước khi đưa con sang.",
        "ho_tro": "Có thể có free school meals, bursary hoặc hỗ trợ childcare theo địa phương, nhưng không mặc nhiên áp dụng cho mọi dependent.",
        "quoc_te": "Khoảng 15.000-35.000 GBP/năm.",
        "cong_dong": "Tìm Hội người Việt tại Vương quốc Anh và nhóm phụ huynh Việt tại London, Manchester, Birmingham để hỏi catchment area và thủ tục nhập học.",
    },
    "uc": {
        "ten": "Úc",
        "truong_cong": "Trường công thường thu phí với gia đình giữ visa tạm trú; một số bang hoặc loại visa có miễn/giảm phí, còn phí sách, đồng phục và hoạt động vẫn có thể phát sinh.",
        "dieu_kien": "Quyền học và mức phí phụ thuộc visa của cha mẹ, bang và loại trường; cần liên hệ Department of Education của bang.",
        "ho_tro": "Có thể hỏi fee remission, hardship assistance hoặc hỗ trợ tại trường/bang; học bổng cho dependent không phổ biến và thường xét riêng.",
        "quoc_te": "Khoảng 15.000-35.000 AUD/năm.",
        "cong_dong": "Tìm Hội người Việt tại Úc và nhóm phụ huynh Việt theo bang như NSW, Victoria, Queensland; hỏi kinh nghiệm visa và trường công địa phương.",
    },
    "nhat": {
        "ten": "Nhật",
        "truong_cong": "Tiểu học và trung học cơ sở công lập thường không thu học phí với trẻ cư trú; tiền ăn trưa, đồng phục, đồ dùng và hoạt động vẫn cần dự trù. Trung học phổ thông có chính sách hỗ trợ riêng.",
        "dieu_kien": "Cần đăng ký địa chỉ cư trú và làm thủ tục với hội đồng giáo dục địa phương; trường có thể hỗ trợ tiếng Nhật tùy khu vực.",
        "ho_tro": "Có thể hỏi miễn/giảm tiền ăn học, hỗ trợ học tập và các chương trình cho gia đình có trẻ em tại thành phố; điều kiện khác nhau theo địa phương.",
        "quoc_te": "Khoảng 1.000.000-3.000.000 JPY/năm.",
        "cong_dong": "Tìm Hội người Việt tại Nhật và nhóm phụ huynh Việt theo tỉnh/thành; hỏi thêm về lớp tiếng Nhật, trường địa phương và chi phí thực tế.",
    },
    "ha lan": {
        "ten": "Hà Lan",
        "truong_cong": "Tiểu học công lập không thu học phí cơ bản; trung học thường có khoản đóng góp tự nguyện, sách, máy tính, đi lại hoặc hoạt động.",
        "dieu_kien": "Con cần đăng ký cư trú và làm thủ tục với trường/municipality; trẻ mới đến có thể học lớp chuyển tiếp ngôn ngữ.",
        "ho_tro": "Có thể kiểm tra kinderopvangtoeslag, kindgebonden budget và hỗ trợ của municipality; không phải khoản nào cũng áp dụng cho visa tạm thời.",
        "quoc_te": "Khoảng 6.000-25.000 EUR/năm.",
        "cong_dong": "Tìm Hội người Việt tại Hà Lan và nhóm phụ huynh Việt theo Amsterdam, Rotterdam, Eindhoven để hỏi trường và hỗ trợ ngôn ngữ.",
    },
    "na uy": {
        "ten": "Na Uy",
        "truong_cong": "Trường công tiểu học và trung học cơ sở thường miễn học phí; vẫn có chi phí đồ dùng, hoạt động, đi lại và chăm sóc ngoài giờ.",
        "dieu_kien": "Quyền học thường gắn với cư trú hợp pháp và đăng ký với municipality; trẻ mới đến có thể được đánh giá nhu cầu tiếng Na Uy.",
        "ho_tro": "Có thể hỏi hỗ trợ municipality, giảm phí kindergarten/SFO và các chương trình hòa nhập; điều kiện phụ thuộc cư trú và thu nhập.",
        "quoc_te": "Khoảng 100.000-250.000 NOK/năm.",
        "cong_dong": "Tìm Hội người Việt tại Na Uy và nhóm phụ huynh Việt ở Oslo, Bergen, Trondheim để hỏi về municipality và trường địa phương.",
    },
    "han quoc": {
        "ten": "Hàn Quốc",
        "truong_cong": "Tiểu học công lập thường miễn học phí cơ bản; tiền ăn, đồng phục, sách và hoạt động có thể tính riêng. Trung học có chính sách hỗ trợ theo cấp.",
        "dieu_kien": "Cần cư trú và đăng ký với văn phòng giáo dục địa phương; hỗ trợ tiếng Hàn cho trẻ quốc tế tùy trường.",
        "ho_tro": "Có thể hỏi 다문화가족지원센터, hỗ trợ giáo dục địa phương và miễn/giảm một số khoản; điều kiện phụ thuộc visa và gia đình.",
        "quoc_te": "Khoảng 10.000.000-30.000.000 KRW/năm.",
        "cong_dong": "Tìm Hội người Việt tại Hàn Quốc và nhóm phụ huynh Việt ở Seoul, Busan, Incheon để hỏi trường, tiếng Hàn và giấy tờ.",
    },
    "singapore": {
        "ten": "Singapore",
        "truong_cong": "Government/government-aided school không hoàn toàn miễn phí cho học sinh quốc tế; có học phí theo tháng, lệ phí và thường phải qua quy trình xét tuyển/AEIS.",
        "dieu_kien": "Phụ thuộc Student Pass/Dependent Pass, chỗ trống và kết quả xét tuyển; cần kiểm tra quy định MOE cho đúng cấp học.",
        "ho_tro": "Financial Assistance Scheme chủ yếu dành cho công dân/PR; học sinh quốc tế nên hỏi trường về bursary hoặc hỗ trợ riêng.",
        "quoc_te": "Khoảng 20.000-45.000 SGD/năm.",
        "cong_dong": "Tìm Cộng đồng người Việt tại Singapore và nhóm phụ huynh Việt; hỏi thực tế về AEIS, trường công và lựa chọn quốc tế.",
    },
    "canada": {
        "ten": "Canada",
        "truong_cong": "Trường công miễn học phí cho citizen/PR; dependent của người có study permit có thể được học miễn hoặc phải đóng học phí tùy province và tình trạng học tập của cha mẹ.",
        "dieu_kien": "Quy định khác nhau theo tỉnh bang, tuổi và study permit; cần xác nhận với school board trước khi nộp visa.",
        "ho_tro": "Có thể hỏi school board về fee waiver, newcomer support, ESL và hỗ trợ bữa ăn; học bổng dependent không có một chính sách toàn quốc.",
        "quoc_te": "Khoảng 12.000-30.000 CAD/năm.",
        "cong_dong": "Tìm Hội người Việt tại Canada và nhóm phụ huynh Việt theo Toronto, Vancouver, Calgary, Montreal để hỏi tỉnh bang và school board.",
    },
    "new zealand": {
        "ten": "New Zealand",
        "truong_cong": "State school miễn học phí cho domestic student; dependent có thể được xem là domestic hoặc international tùy visa của cha mẹ và loại chương trình.",
        "dieu_kien": "Cần kiểm tra Dependent Child Student Visa và điều kiện domestic student với Immigration New Zealand/nhà trường.",
        "ho_tro": "Có thể hỏi school donation relief, hardship support và hỗ trợ học tiếng Anh; học bổng riêng cho dependent khá hạn chế.",
        "quoc_te": "Khoảng 15.000-35.000 NZD/năm.",
        "cong_dong": "Tìm Hội người Việt tại New Zealand và nhóm phụ huynh Việt ở Auckland, Wellington, Christchurch để hỏi zone trường và visa.",
    },
}


THANH_PHO_HOCPHI_DB = {
    "duc": {
        "berlin": {
            "ten": "Berlin",
            "thue_nha_3_phong_eur": "2.000-3.000",
            "truong_cong": "Miễn học phí phổ thông; Kita/mầm non và phí giữ trẻ phụ thuộc bang, quận và thu nhập. Cần đăng ký cư trú để làm thủ tục với Jugendamt hoặc trường.",
            "truong_tu": "Khoảng 8.000-22.000 EUR/năm; có trường song ngữ Đức-Anh và trường quốc tế, thường có danh sách chờ.",
            "truong_tieng_anh": "Có, nhiều trường quốc tế và song ngữ; chỗ học và học phí cần xác nhận trực tiếp từng trường.",
            "cong_dong_viet": "Lớn",
            "diem_phu_hop": 5,
        },
        "frankfurt": {
            "ten": "Frankfurt",
            "thue_nha_3_phong_eur": "2.100-3.100",
            "truong_cong": "Miễn học phí phổ thông; Kita có thể thu phí tùy thành phố và tình trạng cư trú. Trẻ mới đến được phân trường theo nơi ở và cần hỗ trợ tiếng Đức.",
            "truong_tu": "Khoảng 10.000-25.000 EUR/năm; có trường quốc tế Đức-Anh và một số trường quốc tế dạy bằng tiếng Anh.",
            "truong_tieng_anh": "Có, lựa chọn tốt nhờ cộng đồng quốc tế và các trường quốc tế quanh Frankfurt.",
            "cong_dong_viet": "Lớn",
            "diem_phu_hop": 5,
        },
        "hamburg": {
            "ten": "Hamburg",
            "thue_nha_3_phong_eur": "1.800-2.700",
            "truong_cong": "Miễn học phí phổ thông; Kita và giữ trẻ có thể được trợ cấp hoặc tính phí theo độ tuổi, thu nhập và số giờ chăm sóc.",
            "truong_tu": "Khoảng 8.000-23.000 EUR/năm; có trường tư, song ngữ và quốc tế, nhưng số lựa chọn ít hơn Berlin.",
            "truong_tieng_anh": "Có, chủ yếu ở nhóm trường quốc tế/song ngữ; nên kiểm tra khu vực tuyển sinh và danh sách chờ.",
            "cong_dong_viet": "Lớn",
            "diem_phu_hop": 4,
        },
    },
    "anh": {
        "london": {
            "ten": "London",
            "thue_nha_3_phong_eur": "3.200-4.800",
            "truong_cong": "State school miễn học phí cho trẻ đủ điều kiện domestic; dependent của visa tạm thời phải kiểm tra quyền học và catchment area với local authority.",
            "truong_tu": "Khoảng 18.000-40.000 GBP/năm; có nhiều private school và international school, nhưng học phí và chi phí đi lại rất cao.",
            "truong_tieng_anh": "Có rất nhiều; tiếng Anh là ngôn ngữ chính của state school và phần lớn trường tư.",
            "cong_dong_viet": "Lớn",
            "diem_phu_hop": 4,
        },
        "manchester": {
            "ten": "Manchester",
            "thue_nha_3_phong_eur": "1.600-2.400",
            "truong_cong": "State school miễn học phí cho trẻ đủ điều kiện domestic; cần kiểm tra visa, địa chỉ cư trú và quy định của local authority.",
            "truong_tu": "Khoảng 12.000-28.000 GBP/năm; có private school và một số trường quốc tế với chi phí thấp hơn London.",
            "truong_tieng_anh": "Có; hệ state school dạy bằng tiếng Anh, ngoài ra có các trường tư và trường quốc tế trong vùng Greater Manchester.",
            "cong_dong_viet": "Lớn",
            "diem_phu_hop": 5,
        },
        "birmingham": {
            "ten": "Birmingham",
            "thue_nha_3_phong_eur": "1.500-2.300",
            "truong_cong": "State school miễn học phí cho trẻ đủ điều kiện domestic; cần xin school place theo địa chỉ và xác minh quyền học của dependent.",
            "truong_tu": "Khoảng 12.000-27.000 GBP/năm; có private school và lựa chọn quốc tế, thường dễ cân đối hơn London.",
            "truong_tieng_anh": "Có; nhiều state school dạy bằng tiếng Anh và có hỗ trợ English as an Additional Language.",
            "cong_dong_viet": "Lớn",
            "diem_phu_hop": 5,
        },
    },
    "uc": {
        "melbourne": {
            "ten": "Melbourne",
            "thue_nha_3_phong_eur": "1.600-2.500",
            "truong_cong": "Trường công thường thu phí với visa tạm trú; Victoria có thể có miễn/giảm cho một số loại visa hoặc hoàn cảnh. Phải xác nhận với Department of Education Victoria.",
            "truong_tu": "Khoảng 15.000-35.000 AUD/năm; có nhiều trường tư, Catholic và international, học phí thay đổi theo cấp.",
            "truong_tieng_anh": "Có; trường công và phần lớn trường tư dạy bằng tiếng Anh, thường có English language support cho học sinh mới đến.",
            "cong_dong_viet": "Lớn",
            "diem_phu_hop": 5,
        },
        "brisbane": {
            "ten": "Brisbane",
            "thue_nha_3_phong_eur": "1.300-2.000",
            "truong_cong": "Gia đình giữ visa tạm trú thường phải đóng phí; Queensland có chính sách riêng theo visa và chương trình học, cần hỏi Department of Education Queensland.",
            "truong_tu": "Khoảng 14.000-32.000 AUD/năm; có trường tư và Catholic với nhiều mức học phí hơn Sydney.",
            "truong_tieng_anh": "Có; trường công dạy bằng tiếng Anh và có chương trình hỗ trợ học sinh có ngôn ngữ khác tiếng Anh.",
            "cong_dong_viet": "Lớn",
            "diem_phu_hop": 5,
        },
        "sydney": {
            "ten": "Sydney",
            "thue_nha_3_phong_eur": "1.900-3.000",
            "truong_cong": "Visa tạm trú thường phải đóng phí trường công ở NSW, trừ một số diện được miễn/giảm; cần kiểm tra chính sách NSW Department of Education.",
            "truong_tu": "Khoảng 16.000-38.000 AUD/năm; có nhiều trường tư và quốc tế nhưng cạnh tranh và chi phí tổng thể cao.",
            "truong_tieng_anh": "Có; hệ trường công/tư chủ yếu dạy bằng tiếng Anh và có hỗ trợ English as an Additional Language.",
            "cong_dong_viet": "Lớn",
            "diem_phu_hop": 4,
        },
    },
    "nhat": {
        "tokyo": {
            "ten": "Tokyo",
            "thue_nha_3_phong_eur": "1.700-2.700",
            "truong_cong": "Tiểu học và trung học cơ sở công lập thường không thu học phí với trẻ cư trú; vẫn có tiền ăn, đồng phục, đồ dùng và hoạt động. Trường mầm non có thể thu phí theo thu nhập.",
            "truong_tu": "Khoảng 1.000.000-3.500.000 JPY/năm; có nhiều trường tư, international school và trường song ngữ nhưng chi phí cao.",
            "truong_tieng_anh": "Có nhiều international school dạy bằng tiếng Anh; trường công chủ yếu dạy bằng tiếng Nhật và hỗ trợ tiếng Nhật tùy quận.",
            "cong_dong_viet": "Lớn",
            "diem_phu_hop": 4,
        },
        "osaka": {
            "ten": "Osaka",
            "thue_nha_3_phong_eur": "1.000-1.700",
            "truong_cong": "Tiểu học và trung học cơ sở công lập thường không thu học phí với trẻ cư trú; tiền ăn, đồng phục, đồ dùng và chăm sóc ngoài giờ vẫn cần dự trù.",
            "truong_tu": "Khoảng 800.000-2.800.000 JPY/năm; có trường tư và international school, thường thấp hơn Tokyo.",
            "truong_tieng_anh": "Có một số trường quốc tế dạy bằng tiếng Anh; trẻ học trường công thường cần chuẩn bị tiếng Nhật và hỏi chương trình hỗ trợ của thành phố.",
            "cong_dong_viet": "Lớn",
            "diem_phu_hop": 5,
        },
        "nagoya": {
            "ten": "Nagoya",
            "thue_nha_3_phong_eur": "850-1.400",
            "truong_cong": "Tiểu học và trung học cơ sở công lập thường không thu học phí với trẻ cư trú; phụ huynh cần dự trù tiền ăn, đồ dùng và hoạt động.",
            "truong_tu": "Khoảng 800.000-2.500.000 JPY/năm; có trường tư và một số lựa chọn quốc tế, số lượng ít hơn Tokyo/Osaka.",
            "truong_tieng_anh": "Có nhưng ít hơn Tokyo và Osaka; trường công chủ yếu dùng tiếng Nhật, cần hỏi city board of education về hỗ trợ ngôn ngữ.",
            "cong_dong_viet": "Lớn",
            "diem_phu_hop": 5,
        },
    },
}


THANH_PHO_ALIASES = {
    "duc": {
        "berlin": "berlin",
        "frankfurt": "frankfurt",
        "frankfurt am main": "frankfurt",
        "hamburg": "hamburg",
    },
    "anh": {
        "london": "london",
        "manchester": "manchester",
        "birmingham": "birmingham",
    },
    "uc": {
        "melbourne": "melbourne",
        "brisbane": "brisbane",
        "sydney": "sydney",
    },
    "nhat": {
        "tokyo": "tokyo",
        "osaka": "osaka",
        "nagoya": "nagoya",
    },
}


def tim_hoc_phi_con(
    nuoc: str, tuoi_con: int, cap_hoc: str, thanh_pho: str = ""
) -> str:
    """Tra cứu học phí trẻ theo nước và tùy chọn thành phố."""
    cap_hoc_chuan = _bo_dau(cap_hoc).strip()
    cap_hoc_alias = {
        "mam non": "mam_non",
        "mam_non": "mam_non",
        "tieu hoc": "tieu_hoc",
        "tieu_hoc": "tieu_hoc",
        "trung hoc": "trung_hoc",
        "trung_hoc": "trung_hoc",
    }
    cap_hoc_hien_thi = cap_hoc_alias.get(cap_hoc_chuan)
    if not cap_hoc_hien_thi:
        return "cap_hoc phải là 'mam_non', 'tieu_hoc' hoặc 'trung_hoc'."

    nuoc_chuan = _bo_dau(nuoc).strip()
    aliases = {
        "duc": "duc",
        "germany": "duc",
        "anh": "anh",
        "uk": "anh",
        "united kingdom": "anh",
        "uc": "uc",
        "australia": "uc",
        "nhat": "nhat",
        "japan": "nhat",
        "ha lan": "ha lan",
        "netherlands": "ha lan",
        "na uy": "na uy",
        "norway": "na uy",
        "han quoc": "han quoc",
        "south korea": "han quoc",
        "singapore": "singapore",
        "canada": "canada",
        "new zealand": "new zealand",
        "newzealand": "new zealand",
    }
    khoa_quoc_gia = aliases.get(nuoc_chuan)
    if not khoa_quoc_gia:
        return (
            "Chưa có dữ liệu nội bộ cho nước này. Hiện hỗ trợ: Đức, Anh, Úc, Nhật, "
            "Hà Lan, Na Uy, Hàn Quốc, Singapore, Canada và New Zealand."
        )
    thong_tin = HOCPHI_CON_DB[khoa_quoc_gia]
    cap_hoc_text = {
        "mam_non": "mầm non",
        "tieu_hoc": "tiểu học",
        "trung_hoc": "trung học",
    }[cap_hoc_hien_thi]
    phan_hoi = [
        f"Tra cứu nội bộ: {thong_tin['ten']} — con {int(tuoi_con)} tuổi, cấp {cap_hoc_text}.",
        f"- Tổng quan trường công lập: {thong_tin['truong_cong']}",
        f"- Điều kiện dependent/visa: {thong_tin['dieu_kien']}",
        f"- Học bổng/hỗ trợ học phí: {thong_tin['ho_tro']}",
        f"- Trường quốc tế để tham chiếu: {thong_tin['quoc_te']}",
        f"- Cộng đồng phụ huynh Việt: {thong_tin['cong_dong']}",
    ]

    thanh_pho_chuan = _bo_dau(thanh_pho).strip()
    if thanh_pho_chuan:
        khoa_thanh_pho = THANH_PHO_ALIASES.get(khoa_quoc_gia, {}).get(
            thanh_pho_chuan
        )
        if not khoa_thanh_pho:
            if khoa_quoc_gia not in THANH_PHO_HOCPHI_DB:
                return "\n".join(
                    phan_hoi
                    + [
                        f"- Chưa có database thành phố cho {thong_tin['ten']}. "
                        "Hiện có dữ liệu thành phố chi tiết cho Đức, Anh, Úc và Nhật.",
                    ]
                )
            danh_sach = ", ".join(
                city["ten"]
                for city in THANH_PHO_HOCPHI_DB[khoa_quoc_gia].values()
            )
            return "\n".join(
                phan_hoi
                + [
                    f"- Chưa có dữ liệu cho thành phố '{thanh_pho}'. "
                    f"Hiện có: {danh_sach}.",
                ]
            )

        city = THANH_PHO_HOCPHI_DB[khoa_quoc_gia][khoa_thanh_pho]
        phan_hoi.extend(
            [
                f"\nChi tiết thành phố: {city['ten']}",
                f"- Thuê nhà 3 phòng: khoảng {city['thue_nha_3_phong_eur']} EUR/tháng "
                "(ước tính quy đổi để so sánh).",
                f"- Trường công miễn phí/điều kiện: {city['truong_cong']}",
                f"- Trường tư và học phí tham khảo: {city['truong_tu']}",
                f"- Có trường dạy tiếng Anh: {city['truong_tieng_anh']}",
                f"- Cộng đồng người Việt: {city['cong_dong_viet']}",
            ]
        )
    elif khoa_quoc_gia in THANH_PHO_HOCPHI_DB:
        top_3 = sorted(
            THANH_PHO_HOCPHI_DB[khoa_quoc_gia].values(),
            key=lambda city: city["diem_phu_hop"],
            reverse=True,
        )[:3]
        phan_hoi.append(
            "\nTop 3 thành phố phù hợp gia đình có con nhỏ "
            "(cân bằng trường tốt, cộng đồng châu Á/người Việt và chi phí sống):"
        )
        for vi_tri, city in enumerate(top_3, start=1):
            phan_hoi.extend(
                [
                    f"{vi_tri}. {city['ten']} — thuê nhà 3 phòng khoảng "
                    f"{city['thue_nha_3_phong_eur']} EUR/tháng.",
                    f"   Trường công: {city['truong_cong']}",
                    f"   Trường tiếng Anh: {city['truong_tieng_anh']}",
                    f"   Cộng đồng người Việt: {city['cong_dong_viet']}.",
                ]
            )
    else:
        phan_hoi.append(
            f"\nChưa có database thành phố chi tiết cho {thong_tin['ten']}; "
            "hiện có dữ liệu thành phố cho Đức, Anh, Úc và Nhật."
        )

    phan_hoi.append(
        "\nLưu ý: đây là dữ liệu tham khảo nội bộ; học phí và quyền học phụ thuộc visa, "
        "municipality/province/state, khu vực tuyển sinh và năm tuyển sinh. Hãy xác nhận "
        "với trường và cơ quan giáo dục/di trú chính thức trước khi lập ngân sách."
    )
    return "\n".join(phan_hoi)


TOOL_FUNCTIONS = {
    "loc_hocbong": loc_hocbong,
    "tinh_chi_phi": tinh_chi_phi,
    "viet_email_hoi_hocbong": viet_email_hoi_hocbong,
    "danh_gia_ho_so": danh_gia_ho_so,
    "cai_thien_ho_so": cai_thien_ho_so,
    "tim_hoc_phi_con": tim_hoc_phi_con,
}


SYSTEM = f"""Bạn là chuyên gia tư vấn học bổng cho người trung niên (30–55 tuổi) đi du học cùng gia đình.
Trả lời bằng tiếng Việt, ngắn gọn và thực tế.
Dữ liệu có {len(hoc_bong_list)} học bổng. Luôn hỏi thêm nếu thiếu thông tin.
Bạn có 6 công cụ:
1. loc_hocbong: lọc học bổng theo tuổi và quốc gia.
2. tinh_chi_phi: ước tính chi phí gia đình theo tháng.
3. viet_email_hoi_hocbong: viết email hỏi về hỗ trợ gia đình.
4. danh_gia_ho_so: đánh giá hồ sơ theo 15 yếu tố và 6 nhóm điểm:
   học thuật/chuyên môn (25), ngôn ngữ (15), gia đình phù hợp (20),
   mạng lưới quan hệ (15), tác động xã hội (15), sức khỏe và cam kết (10).
5. cai_thien_ho_so: tạo kế hoạch cải thiện theo tuần/tháng từ danh sách điểm yếu,
   gồm lộ trình IELTS, công bố, supervisor và nguồn tài nguyên miễn phí.
6. tim_hoc_phi_con: tra cứu nội bộ về trường công, trường tư, visa dependent,
   hỗ trợ học phí và cộng đồng phụ huynh Việt theo nước, tuổi con, cấp học
   và thành phố tùy chọn. Nếu có thành phố thì trả về chi tiết thành phố đó;
   nếu không có thì trả về tổng quan theo nước và top 3 thành phố phù hợp.

Khi người dùng muốn đánh giá hồ sơ, hãy thực hiện quy trình nhập liệu từng bước:
không gọi danh_gia_ho_so cho đến khi đã có đủ cả 15 giá trị sau.
Chỉ hỏi MỘT câu hỏi ở mỗi lượt, ghi nhận các câu người dùng đã trả lời,
rồi hỏi câu còn thiếu tiếp theo:
1. Tuổi (tuoi).
2. Bằng cấp cao nhất (bang_cap).
3. Số năm kinh nghiệm (kinh_nghiem_nam).
4. Nghề nghiệp hiện tại và nếu có, mô tả ngắn tác động xã hội (nghe_nghiep).
5. Số con đi cùng (so_con).
6. Điểm IELTS; dùng 0 nếu chưa có (ielts_score).
7. Số bài báo/công trình quốc tế; dùng 0 nếu chưa có (so_cong_bo).
8. Đã liên hệ supervisor chưa, trả lời có/không (co_supervisor).
9. Đã biết ngôn ngữ nước đến chưa, trả lời có/không (ngon_ngu_nuoc_den).
10. Tuổi con nhỏ nhất; dùng -1 nếu không có con (tuoi_con_nho_nhat).
11. Loại tổ chức đang làm việc: cong, tu hoặc ngo (loai_to_chuc).
12. Có thư giới thiệu quốc tế chưa, trả lời có/không (co_thu_gioi_thieu_qt).
13. Đã liên hệ alumni chưa, trả lời có/không (da_lien_he_alumni).
14. Có chứng minh tài chính bổ sung chưa, trả lời có/không (co_chung_minh_tai_chinh).
15. Tình trạng sức khỏe: tot, on_dinh hoặc co_benh_man_tinh (tinh_trang_suc_khoe).
Chuẩn hóa câu trả lời có/không thành bool và các lựa chọn đúng như trên.
Sau câu 15 mới gọi danh_gia_ho_so. Khi trả kết quả, phải giữ đầy đủ điểm tổng,
xếp loại, điểm từng nhóm kèm nhận xét, top 3 điểm mạnh, top 3 điểm yếu,
kế hoạch 3 tháng và top 3 học bổng với điểm số/lý do.
Nếu người dùng muốn xử lý các điểm yếu hoặc lập kế hoạch chuẩn bị, hãy dùng
cai_thien_ho_so với danh sách điểm yếu và số tháng họ còn chuẩn bị; không chỉ
 đưa lời khuyên chung chung. Nếu người dùng hỏi về học phí/trường học cho con,
hãy hỏi lần lượt nước, tuổi con và cấp học; chỉ hỏi thêm thành phố nếu người dùng
muốn xem một thành phố cụ thể. Sau đó dùng tim_hoc_phi_con với thanh_pho mặc định
là chuỗi rỗng nếu không nêu thành phố. Chỉ nhận cap_hoc là mam_non, tieu_hoc hoặc
trung_hoc; nếu thiếu thông tin thì hỏi tiếp trước khi gọi tool. Chủ động gợi ý hai
tool này khi báo cáo hồ sơ cho thấy điểm yếu cần hành động hoặc người dùng có con
đi cùng."""


model = genai.GenerativeModel(
    "gemini-2.5-flash",
    system_instruction=SYSTEM,
    tools=list(TOOL_FUNCTIONS.values()),
)
chat = model.start_chat(history=[])


def xu_ly_tool_calls(response, chat_session=None):
    """Thực thi các tool Gemini yêu cầu rồi gửi kết quả lại cho model."""
    chat_session = chat_session or chat
    while True:
        function_calls = [
            part.function_call
            for part in response.parts
            if getattr(part, "function_call", None) and part.function_call.name
        ]
        if not function_calls:
            return response

        tool_parts = []
        for function_call in function_calls:
            ten_tool = function_call.name
            tool = TOOL_FUNCTIONS.get(ten_tool)
            if tool is None:
                ket_qua = f"Không tìm thấy tool: {ten_tool}"
            else:
                try:
                    ket_qua = tool(**dict(function_call.args))
                except Exception as error:
                    ket_qua = f"Tool {ten_tool} gặp lỗi: {error}"
            tool_parts.append(
                genai.protos.Part(
                    function_response=genai.protos.FunctionResponse(
                        name=ten_tool,
                        response={"result": ket_qua},
                    )
                )
            )
        response = chat_session.send_message(genai.protos.Content(parts=tool_parts))

def main():
    """Chạy phiên bản dòng lệnh của chatbot."""
    print("=" * 50)
    print("  CHATBOT HỌC BỔNG NGƯỜI TRUNG NIÊN")
    print(f"  Database: {len(hoc_bong_list)} học bổng")
    print("  Gõ 'thoat' để kết thúc")
    print("=" * 50)

    while True:
        cau_hoi = input("\nBạn: ").strip()
        if cau_hoi.lower() in ["thoat", "exit", "quit"]:
            print("Tạm biệt!")
            break
        if not cau_hoi:
            continue
        try:
            response = chat.send_message(cau_hoi)
            response = xu_ly_tool_calls(response)
            print(f"\nAgent: {response.text}")
        except Exception as e:
            print(f"Lỗi: {e}")


if __name__ == "__main__":
    main()