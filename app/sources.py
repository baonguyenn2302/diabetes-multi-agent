"""Tên và URL của nguồn, sinh từ SOURCES trong scripts/build_kb.py (không sửa tay).
Explanation Agent dùng bảng này để gắn nguồn cho cờ luật, vì cờ chỉ mang source_id."""

SOURCE_TITLES = {
    'src_ada2026': ('ADA – Standards of Care in Diabetes—2026, mục 2: Diagnosis and Classification of Diabetes', 'https://doi.org/10.2337/dc26-S002'),
    'src_ada2023_t4': ('Bảng tiêu chí chẩn đoán đái tháo đường (theo ADA, 2023)', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC10516260/table/T4'),
    'src_ada2021_t2': ('ADA 2021 – Criteria for the Screening and Diagnosis of Prediabetes and Diabetes', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC7839613/table/T2'),
    'src_diabetesnet': ('Diabetes Risk Factors and Diagnosis 2026 (tóm tắt ADA Standards 2026)', 'https://www.diabetesnet.com/about-diabetes/newly-diagnosed/risk-diagnosis-diabetes/'),
    'src_who': ('WHO – Diabetes (fact sheet)', 'https://www.who.int/News-Room/Fact-Sheets/Detail/Diabetes'),
    'src_who_afro': ('WHO AFRO – Diabetes', 'https://www.afro.who.int/fr/node/530'),
    'src_vinmec_early': ('Vinmec – Triệu chứng sớm của đái tháo đường type 2', 'https://www.vinmec.com/vi/tin-tuc/thong-tin-suc-khoe/dau-hieu-som-cua-tieu-duong-type-2/'),
    'src_vinmec_t2': ('Vinmec – Bệnh tiểu đường tuýp 2', 'https://www.vinmec.com/vi/benh/tieu-duong-tuyp-2-3042/?location=all'),
    'src_vinmec_ckd': ('Vinmec – Chủ đề Đái tháo đường loại 2', 'https://www.vinmec.com/vi/chu-de/dai-thao-duong-loai-2'),
    'src_vnexpress': ('VnExpress – Đái tháo đường', 'https://vnexpress.net/dai-thao-duong-4444964.html'),
    'src_longchau_t2': ('Nhà thuốc Long Châu – Tiểu đường tuýp 2', 'https://nhathuoclongchau.com.vn/benh/tieu-duong-tip-2.html'),
    'src_longchau_t2b': ('Nhà thuốc Long Châu – Tiểu đường tuýp 2 (triệu chứng muộn)', 'https://nhathuoclongchau.com.vn/benh/tieu-duong-tuyp-2.html'),
    'src_longchau_comp': ('Nhà thuốc Long Châu – Đái tháo đường: kiểm soát toàn diện biến chứng', 'https://nhathuoclongchau.com.vn/bai-viet/dai-thao-duong-kiem-soat-toan-dien-bien-chung-de-song-khoe-moi-ngay.html'),
    'src_longchau_mech': ('Nhà thuốc Long Châu – Cơ chế đái tháo đường type 2', 'https://nhathuoclongchau.com.vn/bai-viet/co-che-dai-thao-duong-type-2-la-gi-nguyen-nhan-do-dau.html'),
    'src_pharmacity_danger': ('Pharmacity – Bệnh tiểu đường có nguy hiểm không? Các biến chứng có thể gặp', 'https://www.pharmacity.vn/benh-tieu-duong-co-nguy-hiem-khong.htm'),
    'src_pharmacity_elderly': ('Pharmacity – Biến chứng tiểu đường ở người già', 'https://www.pharmacity.vn/bien-chung-tieu-duong-o-nguoi-gia.htm'),
    'src_pharmacity_coma': ('Pharmacity – Hôn mê tiểu đường là gì?', 'https://www.pharmacity.vn/hon-me-tieu-duong.htm'),
    'src_tamanh': ('Bệnh viện Tâm Anh – Tiểu đường tuýp 2', 'https://tamanhhospital.vn/tieu-duong-tuyp-2/'),
    'src_project': ('Project – ánh xạ cột dữ liệu ↔ tri thức và chính sách an toàn', ''),
}


def get_source(source_id):
    """Trả về (tiêu đề, url); id không rõ thì trả về placeholder."""
    return SOURCE_TITLES.get(source_id or "", ("Không rõ nguồn", ""))
