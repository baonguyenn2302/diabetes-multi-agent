"""Sinh file kb/DB_diabet.cypher từ dữ liệu tri thức bên dưới.

Chạy:  python scripts/build_kb.py
Mở rộng KB: thêm Source / node / quan hệ vào các danh sách rồi chạy lại.
Script tự kiểm tra: id không trùng, quan hệ trỏ đúng node, mọi tri thức đều có nguồn.

Nội dung được diễn đạt lại từ các nguồn trong SOURCES (không chép nguyên văn).
Đây là KB phục vụ học tập – chưa được chuyên gia y tế thẩm định.
"""
import sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from app.text_utils import normalize_text

KB_VERSION = "kb_diabet_v1"
ACCESSED = "2026-11-12"

# ============================================================ NGUỒN
SOURCES = [
    ("src_ada2026", "ADA – Standards of Care in Diabetes—2026, mục 2: Diagnosis and Classification of Diabetes",
     "American Diabetes Association", "https://doi.org/10.2337/dc26-S002"),
    ("src_ada2023_t4", "Bảng tiêu chí chẩn đoán đái tháo đường (theo ADA, 2023)",
     "PubMed Central", "https://pmc.ncbi.nlm.nih.gov/articles/PMC10516260/table/T4"),
    ("src_ada2021_t2", "ADA 2021 – Criteria for the Screening and Diagnosis of Prediabetes and Diabetes",
     "PubMed Central", "https://pmc.ncbi.nlm.nih.gov/articles/PMC7839613/table/T2"),
    ("src_diabetesnet", "Diabetes Risk Factors and Diagnosis 2026 (tóm tắt ADA Standards 2026)",
     "DiabetesNet", "https://www.diabetesnet.com/about-diabetes/newly-diagnosed/risk-diagnosis-diabetes/"),
    ("src_who", "WHO – Diabetes (fact sheet)",
     "World Health Organization", "https://www.who.int/News-Room/Fact-Sheets/Detail/Diabetes"),
    ("src_who_afro", "WHO AFRO – Diabetes",
     "World Health Organization", "https://www.afro.who.int/fr/node/530"),
    ("src_vinmec_early", "Vinmec – Triệu chứng sớm của đái tháo đường type 2",
     "Vinmec", "https://www.vinmec.com/vi/tin-tuc/thong-tin-suc-khoe/dau-hieu-som-cua-tieu-duong-type-2/"),
    ("src_vinmec_t2", "Vinmec – Bệnh tiểu đường tuýp 2",
     "Vinmec", "https://www.vinmec.com/vi/benh/tieu-duong-tuyp-2-3042/?location=all"),
    ("src_vinmec_ckd", "Vinmec – Chủ đề Đái tháo đường loại 2",
     "Vinmec", "https://www.vinmec.com/vi/chu-de/dai-thao-duong-loai-2"),
    ("src_vnexpress", "VnExpress – Đái tháo đường",
     "VnExpress", "https://vnexpress.net/dai-thao-duong-4444964.html"),
    ("src_longchau_t2", "Nhà thuốc Long Châu – Tiểu đường tuýp 2",
     "Nhà thuốc Long Châu", "https://nhathuoclongchau.com.vn/benh/tieu-duong-tip-2.html"),
    ("src_longchau_t2b", "Nhà thuốc Long Châu – Tiểu đường tuýp 2 (triệu chứng muộn)",
     "Nhà thuốc Long Châu", "https://nhathuoclongchau.com.vn/benh/tieu-duong-tuyp-2.html"),
    ("src_longchau_comp", "Nhà thuốc Long Châu – Đái tháo đường: kiểm soát toàn diện biến chứng",
     "Nhà thuốc Long Châu",
     "https://nhathuoclongchau.com.vn/bai-viet/dai-thao-duong-kiem-soat-toan-dien-bien-chung-de-song-khoe-moi-ngay.html"),
    ("src_longchau_mech", "Nhà thuốc Long Châu – Cơ chế đái tháo đường type 2",
     "Nhà thuốc Long Châu",
     "https://nhathuoclongchau.com.vn/bai-viet/co-che-dai-thao-duong-type-2-la-gi-nguyen-nhan-do-dau.html"),
    ("src_pharmacity_danger", "Pharmacity – Bệnh tiểu đường có nguy hiểm không? Các biến chứng có thể gặp",
     "Pharmacity", "https://www.pharmacity.vn/benh-tieu-duong-co-nguy-hiem-khong.htm"),
    ("src_pharmacity_elderly", "Pharmacity – Biến chứng tiểu đường ở người già",
     "Pharmacity", "https://www.pharmacity.vn/bien-chung-tieu-duong-o-nguoi-gia.htm"),
    ("src_pharmacity_coma", "Pharmacity – Hôn mê tiểu đường là gì?",
     "Pharmacity", "https://www.pharmacity.vn/hon-me-tieu-duong.htm"),
    ("src_tamanh", "Bệnh viện Tâm Anh – Tiểu đường tuýp 2",
     "Bệnh viện Tâm Anh", "https://tamanhhospital.vn/tieu-duong-tuyp-2/"),
    ("src_project", "Project – ánh xạ cột dữ liệu ↔ tri thức và chính sách an toàn",
     "Nhóm sinh viên (tự xây dựng)", ""),
]

# ============================================================ NODE
# (id, kind, name, name_en, aliases, description, source_id)
NODES = [
 # ---- Disease
 ("diabetes", "Disease", "Bệnh đái tháo đường (tiểu đường)", "Diabetes mellitus",
  ["đái tháo đường", "tiểu đường", "bệnh tiểu đường", "bệnh đái tháo đường", "diabetes"],
  "Bệnh mạn tính xảy ra khi tuyến tụy không tạo đủ insulin hoặc cơ thể không sử dụng insulin hiệu quả, khiến đường huyết tăng cao. Nếu kéo dài, tăng đường huyết có thể làm tổn thương tim, mạch máu, mắt, thận và thần kinh.",
  "src_who"),
 ("type1", "Disease", "Tiểu đường type 1", "Type 1 diabetes",
  ["tiểu đường type 1", "tiểu đường tuýp 1", "tiểu đường loại 1", "đái tháo đường type 1",
   "đái tháo đường tuýp 1", "đái tháo đường loại 1", "type 1", "t1d"],
  "Thể bệnh đặc trưng bởi việc cơ thể thiếu hụt khả năng sản xuất insulin nên người bệnh cần dùng insulin hằng ngày. Nguyên nhân chưa được biết rõ và hiện chưa có cách phòng ngừa.",
  "src_who"),
 ("type2", "Disease", "Tiểu đường type 2", "Type 2 diabetes",
  ["tiểu đường type 2", "tiểu đường tuýp 2", "tiểu đường loại 2", "đái tháo đường type 2",
   "đái tháo đường tuýp 2", "đái tháo đường loại 2", "type 2", "t2d"],
  "Dạng phổ biến nhất, chiếm khoảng 90–95% số ca. Cơ chế gồm đề kháng insulin cùng với suy giảm chức năng tế bào beta của tuyến tụy. Bệnh thường tiến triển âm thầm, triệu chứng nhẹ hoặc không rõ nên dễ được phát hiện muộn, khi đã có biến chứng.",
  "src_vnexpress"),
 ("gestational", "Disease", "Tiểu đường thai kỳ", "Gestational diabetes",
  ["tiểu đường thai kỳ", "đái tháo đường thai kỳ", "tiểu đường khi mang thai", "gdm"],
  "Tình trạng tăng đường huyết xuất hiện trong thai kỳ, thường được phát hiện qua sàng lọc trước sinh. Người từng mắc có nguy cơ cao hơn bị tiểu đường type 2 về sau.",
  "src_who"),
 ("prediabetes", "Disease", "Tiền tiểu đường", "Prediabetes",
  ["tiền tiểu đường", "tiền đái tháo đường", "rối loạn dung nạp glucose", "prediabetes", "igt", "ifg"],
  "Giai đoạn đường huyết cao hơn bình thường nhưng chưa đạt ngưỡng chẩn đoán tiểu đường, thường không có triệu chứng rõ ràng. Đây là giai đoạn cảnh báo nguy cơ cao tiến triển thành tiểu đường type 2.",
  "src_vinmec_early"),
 # ---- Symptom
 ("sym_polyuria", "Symptom", "Đi tiểu nhiều", "Polyuria",
  ["đi tiểu nhiều", "tiểu nhiều", "tiểu đêm", "polyuria"],
  "Đi tiểu thường xuyên hơn bình thường, một trong những dấu hiệu điển hình của tăng đường huyết.",
  "src_longchau_t2"),
 ("sym_polydipsia", "Symptom", "Khát nước, uống nhiều", "Polydipsia",
  ["uống nhiều", "khát nước", "khát nhiều", "rất khát", "polydipsia"],
  "Cảm giác khát và uống nước nhiều hơn bình thường, dấu hiệu điển hình của tăng đường huyết.",
  "src_longchau_t2"),
 ("sym_polyphagia", "Symptom", "Ăn nhiều, hay đói", "Polyphagia",
  ["ăn nhiều", "hay đói", "đói nhiều", "polyphagia"],
  "Thèm ăn, ăn nhiều hơn bình thường, một trong bốn dấu hiệu điển hình của tăng đường huyết.",
  "src_longchau_t2"),
 ("sym_weight_loss", "Symptom", "Sụt cân (gầy nhiều)", "Weight loss",
  ["sụt cân", "gầy nhiều", "gầy sút", "giảm cân không rõ nguyên nhân"],
  "Giảm cân dù ăn nhiều, một trong bốn dấu hiệu điển hình của tăng đường huyết.",
  "src_longchau_t2"),
 ("sym_fatigue", "Symptom", "Mệt mỏi", "Fatigue",
  ["mệt mỏi", "mệt"],
  "Cảm giác mệt, thiếu năng lượng; có thể xuất hiện đột ngột ở người bị tăng đường huyết.",
  "src_who_afro"),
 ("sym_blurred_vision", "Symptom", "Nhìn mờ", "Blurred vision",
  ["nhìn mờ", "mờ mắt", "thay đổi thị lực"],
  "Thị lực thay đổi, nhìn mờ; có thể gặp khi đường huyết cao hoặc do biến chứng ở mắt.",
  "src_who_afro"),
 ("sym_numbness", "Symptom", "Tê bì tay chân", "Numbness / tingling",
  ["tê bì", "tê tay chân", "tê bì tay chân", "châm chích"],
  "Tê, châm chích ở bàn tay hoặc bàn chân, thường là dấu hiệu muộn của tổn thương thần kinh do tiểu đường.",
  "src_longchau_t2b"),
 ("sym_dry_mouth", "Symptom", "Khô miệng", "Dry mouth",
  ["khô miệng"],
  "Cảm giác khô miệng, gặp trong các triệu chứng khởi phát của tiểu đường type 1.",
  "src_vnexpress"),
 ("sym_itchy_skin", "Symptom", "Ngứa da", "Itchy skin",
  ["ngứa da"],
  "Ngứa da, gặp trong các triệu chứng khởi phát của tiểu đường type 1.",
  "src_vnexpress"),
 # ---- RiskFactor
 ("rf_overweight", "RiskFactor", "Thừa cân, béo phì", "Overweight / obesity",
  ["thừa cân", "béo phì", "bmi", "chỉ số khối cơ thể", "bmi cao"],
  "Chỉ số BMI và vòng eo cao có liên quan đến nguy cơ mắc tiểu đường type 2 cao hơn. Thừa cân, béo phì là yếu tố nguy cơ quan trọng và có thể thay đổi được.",
  "src_who"),
 ("rf_age45", "RiskFactor", "Tuổi từ 45 trở lên", "Age ≥ 45",
  ["tuổi cao", "45 tuổi", "từ 45 tuổi", "lớn tuổi", "tuổi tác", "người cao tuổi"],
  "Người từ khoảng 45 tuổi trở lên là nhóm dễ mắc tiểu đường type 2 hơn.",
  "src_longchau_mech"),
 ("rf_family", "RiskFactor", "Tiền sử gia đình mắc tiểu đường", "Family history",
  ["tiền sử gia đình", "di truyền", "bố mẹ mắc", "người thân mắc", "gia đình có người"],
  "Có cha mẹ hoặc anh chị em ruột mắc tiểu đường type 2 làm tăng nguy cơ mắc bệnh.",
  "src_vinmec_early"),
 ("rf_inactivity", "RiskFactor", "Ít vận động", "Physical inactivity",
  ["ít vận động", "lười vận động", "thiếu vận động", "ngồi nhiều"],
  "Thiếu vận động thể lực góp phần làm tăng nguy cơ mắc tiểu đường type 2.",
  "src_who"),
 ("rf_hypertension", "RiskFactor", "Tăng huyết áp", "Hypertension",
  ["tăng huyết áp", "huyết áp cao", "cao huyết áp", "hypertension"],
  "Tăng huyết áp nằm trong nhóm yếu tố nguy cơ của tiểu đường type 2.",
  "src_vnexpress"),
 ("rf_cvd", "RiskFactor", "Bệnh tim mạch (xơ vữa động mạch)", "Cardiovascular disease",
  ["bệnh tim mạch", "bệnh tim", "heart disease", "xơ vữa động mạch"],
  "Tiền sử bệnh tim mạch do xơ vữa động mạch nằm trong nhóm yếu tố nguy cơ của tiểu đường type 2.",
  "src_vnexpress"),
 ("rf_dyslipidemia", "RiskFactor", "Rối loạn lipid máu (mỡ máu cao)", "Dyslipidemia",
  ["rối loạn lipid", "mỡ máu", "mỡ máu cao", "cholesterol cao"],
  "Rối loạn lipid máu làm tăng đề kháng insulin, dễ dẫn đến tiểu đường type 2.",
  "src_vinmec_early"),
 ("rf_pcos", "RiskFactor", "Hội chứng buồng trứng đa nang (PCOS)", "Polycystic ovary syndrome",
  ["pcos", "buồng trứng đa nang"],
  "Phụ nữ mắc hội chứng buồng trứng đa nang có nguy cơ cao hơn mắc tiểu đường type 2.",
  "src_vinmec_early"),
 ("rf_gdm_history", "RiskFactor", "Tiền sử tiểu đường thai kỳ", "History of gestational diabetes",
  ["tiền sử tiểu đường thai kỳ", "từng bị tiểu đường thai kỳ", "từng mắc tiểu đường thai kỳ"],
  "Phụ nữ từng bị tiểu đường thai kỳ có nguy cơ cao hơn mắc tiểu đường type 2 sau này.",
  "src_vnexpress"),
 # ---- Complication
 ("comp_retinopathy", "Complication", "Biến chứng mắt (võng mạc, đục thủy tinh thể, tăng nhãn áp)", "Eye complications",
  ["võng mạc", "biến chứng mắt", "đục thủy tinh thể", "tăng nhãn áp"],
  "Ngoài bệnh võng mạc, người mắc tiểu đường còn dễ gặp đục thủy tinh thể và tăng nhãn áp. Tổn thương thường tiến triển chậm và ít triệu chứng ở giai đoạn đầu.",
  "src_pharmacity_danger"),
 ("comp_nephropathy", "Complication", "Bệnh thận mạn do tiểu đường", "Diabetic kidney disease",
  ["bệnh thận", "suy thận", "thận mạn", "biến chứng thận", "tổn thương thận"],
  "Khoảng 40% người mắc đái tháo đường có thể phát triển bệnh thận mạn, thường không có triệu chứng rõ ở giai đoạn đầu; nếu không theo dõi có thể tiến triển thành suy thận mạn.",
  "src_longchau_comp"),
 ("comp_neuropathy", "Complication", "Biến chứng thần kinh", "Diabetic neuropathy",
  ["thần kinh", "tổn thương thần kinh", "biến chứng thần kinh"],
  "Thường gặp ở người bệnh lâu năm, biểu hiện như tê bì, châm chích, đau rát hoặc giảm cảm giác ở tay và chân.",
  "src_pharmacity_danger"),
 ("comp_cvd", "Complication", "Biến chứng tim mạch (nhồi máu cơ tim, đột quỵ)", "Cardiovascular complications",
  ["nhồi máu cơ tim", "đột quỵ", "biến chứng tim mạch"],
  "Người mắc tiểu đường type 2 có nguy cơ cao hơn bị tăng huyết áp, rối loạn lipid máu, đột quỵ, nhồi máu cơ tim và các bệnh mạch máu khác.",
  "src_longchau_t2"),
 ("comp_foot", "Complication", "Loét bàn chân tiểu đường", "Diabetic foot ulcer",
  ["loét bàn chân", "bàn chân tiểu đường", "cắt cụt chi", "cắt cụt", "biến chứng chân", "biến chứng ở chân"],
  "Tổn thương thần kinh và lưu thông máu kém khiến vết loét ở bàn chân dễ nhiễm trùng, khó lành; nếu không điều trị kịp thời có thể phải cắt cụt chi.",
  "src_pharmacity_elderly"),
 ("comp_coma", "Complication", "Hôn mê tiểu đường (hạ đường huyết nặng, nhiễm toan ceton, tăng áp lực thẩm thấu)", "Diabetic coma",
  ["hôn mê", "hôn mê tiểu đường", "nhiễm toan ceton", "hạ đường huyết nặng", "biến chứng cấp"],
  "Biến chứng cấp tính, có thể tiến triển rất nhanh và đe dọa tính mạng. Các nguyên nhân phổ biến gồm hạ đường huyết nặng, nhiễm toan ceton và tăng áp lực thẩm thấu.",
  "src_pharmacity_coma"),
 # ---- Test
 ("test_hba1c", "Test", "Xét nghiệm HbA1c", "Hemoglobin A1c",
  ["hba1c", "a1c", "xét nghiệm hba1c"],
  "Xét nghiệm phản ánh mức kiểm soát đường huyết trong thời gian dài. Ngưỡng ≥ 6.5% dùng để chẩn đoán tiểu đường, 5.7–6.4% gợi ý tiền tiểu đường. Cần làm ở phòng xét nghiệm đạt chuẩn; không dùng máy đo tại chỗ để chẩn đoán.",
  "src_ada2023_t4"),
 ("test_fpg", "Test", "Đường huyết lúc đói (FPG)", "Fasting plasma glucose",
  ["đường huyết lúc đói", "đường huyết đói", "glucose lúc đói", "fpg"],
  "Đường huyết đo sau khi nhịn ăn (không nạp calo) ít nhất 8 giờ. Ngưỡng ≥ 126 mg/dL (7.0 mmol/L) dùng để chẩn đoán tiểu đường; 100–125 mg/dL gợi ý tiền tiểu đường.",
  "src_ada2023_t4"),
 ("test_ogtt", "Test", "Nghiệm pháp dung nạp glucose đường uống (OGTT)", "Oral glucose tolerance test",
  ["ogtt", "nghiệm pháp dung nạp glucose", "dung nạp glucose đường uống"],
  "Đo đường huyết sau 2 giờ uống 75 g glucose. Mức ≥ 200 mg/dL (11.1 mmol/L) là tiểu đường; 140–199 mg/dL gợi ý tiền tiểu đường.",
  "src_ada2021_t2"),
 ("test_rpg", "Test", "Đường huyết ngẫu nhiên (bất kỳ thời điểm)", "Random plasma glucose",
  ["đường huyết ngẫu nhiên", "đường huyết bất kỳ", "random glucose"],
  "Ở người có triệu chứng điển hình của tăng đường huyết, mức ≥ 200 mg/dL (11.1 mmol/L) đo vào bất kỳ thời điểm nào đủ để chẩn đoán tiểu đường.",
  "src_ada2023_t4"),
 # ---- Advice
 ("adv_confirm", "Advice", "Xác nhận chẩn đoán bằng xét nghiệm lặp lại", "Confirm diagnosis",
  ["xác nhận chẩn đoán", "xét nghiệm lại"],
  "Khi chưa có tăng đường huyết rõ rệt, việc chẩn đoán cần kết quả bất thường ở hai xét nghiệm khác nhau cùng ngày hoặc ở hai mẫu lấy vào hai ngày khác nhau.",
  "src_ada2023_t4"),
 ("adv_not_diagnosis", "Advice", "Kết quả hệ thống chỉ mang tính tham khảo", "Not a diagnosis",
  ["thay thế bác sĩ", "chẩn đoán xác định"],
  "Kết quả dự đoán của mô hình và gợi ý của hệ thống chỉ mang tính tham khảo, không thay thế chẩn đoán của bác sĩ; cần xét nghiệm xác nhận và tư vấn chuyên môn.",
  "src_project"),
 ("adv_see_doctor", "Advice", "Đến gặp bác sĩ khi có nguy cơ hoặc triệu chứng", "See a doctor",
  ["gặp bác sĩ", "đi khám", "khám bác sĩ"],
  "Nếu có yếu tố nguy cơ hoặc xuất hiện các triệu chứng nghi ngờ, nên liên hệ bác sĩ để được kiểm tra và tư vấn.",
  "src_longchau_t2"),
 ("adv_checkup", "Advice", "Khám và xét nghiệm đường huyết định kỳ", "Regular check-ups",
  ["khám định kỳ", "tầm soát", "sàng lọc", "xét nghiệm định kỳ"],
  "Cách tốt nhất để phát hiện sớm là khám sức khỏe và xét nghiệm đường huyết định kỳ với cán bộ y tế.",
  "src_who"),
 ("adv_screen_35", "Advice", "Bắt đầu sàng lọc từ 35 tuổi", "Screening from age 35",
  ["sàng lọc từ 35 tuổi", "35 tuổi"],
  "Theo tóm tắt khuyến cáo ADA 2026, người trưởng thành nên bắt đầu sàng lọc tiểu đường từ 35 tuổi; sớm hơn nếu thừa cân hoặc béo phì và có thêm yếu tố nguy cơ.",
  "src_diabetesnet"),
 ("adv_prediabetes_followup", "Advice", "Theo dõi người tiền tiểu đường ít nhất mỗi năm", "Annual follow-up for prediabetes",
  ["theo dõi tiền tiểu đường"],
  "Người tiền tiểu đường nên được theo dõi khả năng tiến triển thành tiểu đường ít nhất mỗi năm, hoặc thường xuyên hơn tùy mức nguy cơ.",
  "src_diabetesnet"),
 ("adv_diet", "Advice", "Ăn uống lành mạnh", "Healthy diet",
  ["ăn uống", "chế độ ăn", "thực đơn", "hạn chế đường", "ăn gì"],
  "Ăn uống lành mạnh, hạn chế đường và chất béo bão hòa giúp phòng ngừa hoặc làm chậm tiểu đường type 2.",
  "src_who_afro"),
 ("adv_activity", "Advice", "Vận động thể lực đều đặn", "Regular physical activity",
  ["vận động", "tập thể dục", "thể dục", "hoạt động thể lực", "tập luyện"],
  "Duy trì hoạt động thể lực cường độ vừa, ít nhất 150 phút mỗi tuần (khoảng 30 phút vào hầu hết các ngày).",
  "src_who"),
 ("adv_weight", "Advice", "Duy trì cân nặng hợp lý", "Healthy weight",
  ["giảm cân", "cân nặng hợp lý", "kiểm soát cân nặng"],
  "Đạt và duy trì cân nặng hợp lý là một trong các biện pháp phòng ngừa hoặc làm chậm tiểu đường type 2.",
  "src_who_afro"),
 ("adv_no_tobacco", "Advice", "Không hút thuốc lá", "Avoid tobacco",
  ["hút thuốc", "thuốc lá", "bỏ thuốc"],
  "Tránh sử dụng thuốc lá giúp phòng ngừa tiểu đường type 2; bỏ thuốc cũng quan trọng để tránh biến chứng ở người đã mắc bệnh.",
  "src_who_afro"),
 ("adv_bp_lipid", "Advice", "Kiểm soát huyết áp và mỡ máu", "Control blood pressure and lipids",
  ["kiểm soát huyết áp", "kiểm soát mỡ máu"],
  "Kiểm soát đồng thời huyết áp và mỡ máu, kết hợp thăm khám định kỳ, giúp giảm nguy cơ biến chứng của tiểu đường.",
  "src_pharmacity_danger"),
 ("adv_foot_care", "Advice", "Chăm sóc bàn chân", "Foot care",
  ["chăm sóc chân", "chăm sóc bàn chân"],
  "Chăm sóc bàn chân là một phần quan trọng trong quản lý tiểu đường.",
  "src_who_afro"),
 # ---- Feature (cột của dataset; chỉ khớp theo đúng tên cột để tránh nhập nhằng)
 ("feat_age", "Feature", "age (cột dữ liệu)", "dataset column: age", [],
  "Cột `age` trong dataset: tuổi của bệnh nhân.", "src_project"),
 ("feat_hypertension", "Feature", "hypertension (cột dữ liệu)", "dataset column: hypertension", [],
  "Cột `hypertension` trong dataset: 1 nếu bệnh nhân có tăng huyết áp, 0 nếu không.", "src_project"),
 ("feat_heart_disease", "Feature", "heart_disease (cột dữ liệu)", "dataset column: heart_disease", [],
  "Cột `heart_disease` trong dataset: 1 nếu bệnh nhân có bệnh tim, 0 nếu không.", "src_project"),
 ("feat_bmi", "Feature", "bmi (cột dữ liệu)", "dataset column: bmi", [],
  "Cột `bmi` trong dataset: chỉ số khối cơ thể.", "src_project"),
 ("feat_smoking_history", "Feature", "smoking_history (cột dữ liệu)", "dataset column: smoking_history",
  ["smoking history"],
  "Cột `smoking_history` trong dataset: tiền sử hút thuốc (never, former, current, ever, not current, No Info).",
  "src_project"),
 ("feat_hba1c_level", "Feature", "HbA1c_level (cột dữ liệu)", "dataset column: HbA1c_level",
  ["hba1c level"],
  "Cột `HbA1c_level` trong dataset: mức HbA1c (%) của bệnh nhân.", "src_project"),
 ("feat_blood_glucose_level", "Feature", "blood_glucose_level (cột dữ liệu)", "dataset column: blood_glucose_level",
  ["blood glucose level"],
  "Cột `blood_glucose_level` trong dataset: mức đường huyết (giả định đơn vị mg/dL). Dataset không nêu rõ đo lúc đói hay ngẫu nhiên.",
  "src_project"),
]

# ============================================================ QUAN HỆ
# (from, type, to, source_id, {props})
RELS = []
def R(a, t, b, src, **props): RELS.append((a, t, b, src, props))

for sub in ("type1", "type2", "gestational"):
    R(sub, "SUBTYPE_OF", "diabetes", "src_who")

# Triệu chứng
for s in ("sym_polyuria", "sym_polydipsia", "sym_polyphagia", "sym_weight_loss"):
    R(s, "SYMPTOM_OF", "diabetes", "src_longchau_t2", note="Một trong bốn dấu hiệu điển hình của tăng đường huyết")
R("sym_fatigue", "SYMPTOM_OF", "diabetes", "src_who_afro")
R("sym_blurred_vision", "SYMPTOM_OF", "diabetes", "src_who_afro")
for s in ("sym_polyuria", "sym_polydipsia", "sym_polyphagia", "sym_weight_loss", "sym_fatigue",
          "sym_dry_mouth", "sym_itchy_skin"):
    R(s, "SYMPTOM_OF", "type1", "src_vnexpress", note="Thường khởi phát nhanh trong vài ngày đến vài tuần")
for s in ("sym_polydipsia", "sym_polyuria", "sym_blurred_vision"):
    R(s, "SYMPTOM_OF", "type2", "src_tamanh", note="Ở type 2 triệu chứng thường nhẹ, dễ bị bỏ qua")
R("sym_numbness", "SYMPTOM_OF", "type2", "src_longchau_t2b", note="Thường là triệu chứng muộn do biến chứng thần kinh")

# Yếu tố nguy cơ
R("rf_overweight", "RISK_FACTOR_FOR", "type2", "src_who")
R("rf_age45", "RISK_FACTOR_FOR", "type2", "src_longchau_mech")
R("rf_family", "RISK_FACTOR_FOR", "type2", "src_vinmec_early")
R("rf_inactivity", "RISK_FACTOR_FOR", "type2", "src_who")
R("rf_hypertension", "RISK_FACTOR_FOR", "type2", "src_vnexpress")
R("rf_cvd", "RISK_FACTOR_FOR", "type2", "src_vnexpress")
R("rf_dyslipidemia", "RISK_FACTOR_FOR", "type2", "src_vinmec_early")
R("rf_pcos", "RISK_FACTOR_FOR", "type2", "src_vinmec_early")
R("rf_gdm_history", "RISK_FACTOR_FOR", "type2", "src_vnexpress")
R("gestational", "INCREASES_RISK_OF", "type2", "src_who")
R("prediabetes", "MAY_PROGRESS_TO", "type2", "src_vinmec_early",
  note="Theo Vinmec, nếu không kiểm soát kịp thời thì hơn 50% người tiền tiểu đường tiến triển thành type 2 sau 5–10 năm")

# Biến chứng
R("diabetes", "MAY_LEAD_TO", "comp_retinopathy", "src_pharmacity_danger")
R("diabetes", "MAY_LEAD_TO", "comp_nephropathy", "src_longchau_comp")
R("type2", "MAY_LEAD_TO", "comp_nephropathy", "src_vinmec_ckd",
  note="Tiểu đường type 2 là nguyên nhân chính dẫn tới bệnh thận mạn giai đoạn cuối")
R("diabetes", "MAY_LEAD_TO", "comp_neuropathy", "src_pharmacity_danger")
R("diabetes", "MAY_LEAD_TO", "comp_cvd", "src_who", note="Đường huyết cao kéo dài có thể tổn thương tim và mạch máu")
R("type2", "MAY_LEAD_TO", "comp_cvd", "src_longchau_t2")
R("diabetes", "MAY_LEAD_TO", "comp_foot", "src_pharmacity_elderly")
R("diabetes", "MAY_LEAD_TO", "comp_coma", "src_pharmacity_coma", acute="true")

# Chẩn đoán (ngưỡng có cấu trúc để Rule Agent có thể dùng sau này)
R("test_hba1c", "DIAGNOSES", "diabetes", "src_ada2026", criterion="≥ 6.5%", min_value=6.5, unit="%")
R("test_fpg", "DIAGNOSES", "diabetes", "src_ada2026", criterion="≥ 126 mg/dL (7.0 mmol/L), nhịn ăn ≥ 8 giờ", min_value=126.0, unit="mg/dL")
R("test_ogtt", "DIAGNOSES", "diabetes", "src_ada2026", criterion="≥ 200 mg/dL (11.1 mmol/L) sau 2 giờ, tải 75 g glucose", min_value=200.0, unit="mg/dL")
R("test_rpg", "DIAGNOSES", "diabetes", "src_ada2026", criterion="≥ 200 mg/dL (11.1 mmol/L) kèm triệu chứng điển hình", min_value=200.0, unit="mg/dL")
R("test_hba1c", "INDICATES", "prediabetes", "src_ada2021_t2", criterion="5.7–6.4%", min_value=5.7, max_value=6.4, unit="%")
R("test_fpg", "INDICATES", "prediabetes", "src_ada2021_t2", criterion="100–125 mg/dL (5.6–6.9 mmol/L)", min_value=100.0, max_value=125.0, unit="mg/dL")
R("test_ogtt", "INDICATES", "prediabetes", "src_ada2021_t2", criterion="140–199 mg/dL (7.8–11.0 mmol/L) sau 2 giờ", min_value=140.0, max_value=199.0, unit="mg/dL")

# Lời khuyên
R("adv_diet", "HELPS_PREVENT", "type2", "src_who_afro")
R("adv_activity", "HELPS_PREVENT", "type2", "src_who")
R("adv_weight", "HELPS_PREVENT", "type2", "src_who_afro")
R("adv_no_tobacco", "HELPS_PREVENT", "type2", "src_who_afro")
R("adv_bp_lipid", "HELPS_PREVENT", "comp_cvd", "src_pharmacity_danger")
R("adv_bp_lipid", "HELPS_PREVENT", "comp_nephropathy", "src_pharmacity_danger")
R("adv_foot_care", "HELPS_PREVENT", "comp_foot", "src_who_afro")
R("adv_checkup", "HELPS_DETECT_EARLY", "diabetes", "src_who")
R("adv_screen_35", "HELPS_DETECT_EARLY", "type2", "src_diabetesnet")
R("adv_confirm", "APPLIES_TO", "diabetes", "src_ada2023_t4")
R("adv_not_diagnosis", "APPLIES_TO", "diabetes", "src_project")
R("adv_see_doctor", "APPLIES_TO", "type2", "src_longchau_t2")
R("adv_prediabetes_followup", "APPLIES_TO", "prediabetes", "src_diabetesnet")

# Ánh xạ cột dataset ↔ tri thức
R("feat_age", "RELATES_TO", "rf_age45", "src_project")
R("feat_hypertension", "RELATES_TO", "rf_hypertension", "src_project")
R("feat_heart_disease", "RELATES_TO", "rf_cvd", "src_project")
R("feat_bmi", "RELATES_TO", "rf_overweight", "src_project")
R("feat_smoking_history", "RELATES_TO", "adv_no_tobacco", "src_project")
R("feat_hba1c_level", "MEASURES", "test_hba1c", "src_project")
R("feat_blood_glucose_level", "RELATES_TO", "test_fpg", "src_project",
  note="Dataset không nêu rõ đo lúc đói hay ngẫu nhiên nên không so trực tiếp với ngưỡng chẩn đoán được")
R("feat_blood_glucose_level", "RELATES_TO", "test_rpg", "src_project",
  note="Dataset không nêu rõ đo lúc đói hay ngẫu nhiên nên không so trực tiếp với ngưỡng chẩn đoán được")


# ============================================================ KIỂM TRA TOÀN VẸN
def terms_of(node):
    _id, kind, name, name_en, aliases = node[:5]
    raw = list(aliases)
    if kind != "Feature":
        raw += [name, name_en]
    out = []
    for r in raw:
        t = normalize_text(r)
        if t and t not in out:
            out.append(t)
    return out

def validate():
    src_ids = [s[0] for s in SOURCES]
    node_ids = [n[0] for n in NODES]
    assert len(set(src_ids)) == len(src_ids), "Source id trùng"
    assert len(set(node_ids)) == len(node_ids), "Node id trùng"
    kinds = {"Disease", "Symptom", "RiskFactor", "Complication", "Test", "Advice", "Feature"}
    for n in NODES:
        assert n[1] in kinds, f"kind lạ: {n[0]}"
        assert n[6] in src_ids, f"Node {n[0]} thiếu nguồn hợp lệ: {n[6]}"
        assert "\n" not in n[5] and not n[5].rstrip().endswith(";"), f"description lỗi: {n[0]}"
    seen = set()
    for a, t, b, s, p in RELS:
        assert a in node_ids and b in node_ids, f"Quan hệ trỏ node không tồn tại: {a}-{t}->{b}"
        assert s in src_ids, f"Quan hệ {a}-{t}->{b} thiếu nguồn: {s}"
        assert (a, t, b) not in seen, f"Quan hệ trùng: {a}-{t}->{b}"
        seen.add((a, t, b))
    # cảnh báo alias trùng giữa các entity
    owner = {}
    for n in NODES:
        for t in terms_of(n):
            if t in owner and owner[t] != n[0]:
                print(f"[CẢNH BÁO] cụm '{t}' trùng giữa {owner[t]} và {n[0]}")
            owner.setdefault(t, n[0])

# ============================================================ SINH CYPHER
def q(s): return "'" + str(s).replace("\\", "\\\\").replace("'", "\\'") + "'"
def ql(xs): return "[" + ", ".join(q(x) for x in xs) + "]"
def qv(v): return repr(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else q(v)

def generate() -> str:
    validate()
    L = [
        f"// ============================================================",
        f"// DB_diabet.cypher – Knowledge Graph tiểu đường ({KB_VERSION})",
        f"// File này được SINH TỰ ĐỘNG bởi scripts/build_kb.py – đừng sửa tay, hãy sửa build_kb.py rồi chạy lại.",
        f"// Nạp vào Neo4j:  python scripts/load_kb.py",
        f"// Nội dung diễn đạt lại từ các nguồn trong nút :Source; prototype học tập, chưa được chuyên gia y tế thẩm định.",
        f"// ============================================================",
        "",
        "CREATE CONSTRAINT entity_id IF NOT EXISTS FOR (n:Entity) REQUIRE n.id IS UNIQUE;",
        "CREATE CONSTRAINT source_id IF NOT EXISTS FOR (s:Source) REQUIRE s.id IS UNIQUE;",
        "",
        "// ---------- Nguồn ----------",
    ]
    for sid, title, pub, url in SOURCES:
        L += [f"MERGE (s:Source {{id: {q(sid)}}})",
              f"SET s.title = {q(title)},",
              f"    s.publisher = {q(pub)},",
              f"    s.url = {q(url)},",
              f"    s.accessed = {q(ACCESSED)};"]
    L += ["", "// ---------- Thực thể ----------"]
    for n in NODES:
        _id, kind, name, name_en, aliases, desc, src = n
        L += [f"MERGE (n:Entity {{id: {q(_id)}}})",
              f"SET n:{kind},",
              f"    n.kind = {q(kind)},",
              f"    n.name = {q(name)},",
              f"    n.name_en = {q(name_en)},",
              f"    n.aliases = {ql(aliases)},",
              f"    n.search_terms = {ql(terms_of(n))},",
              f"    n.description = {q(desc)},",
              f"    n.source_id = {q(src)};"]
    L += ["", "// ---------- Quan hệ ----------"]
    for a, t, b, s, p in RELS:
        sets = [f"r.source_id = {q(s)}"] + [f"r.{k} = {qv(v)}" for k, v in sorted(p.items())]
        L += [f"MATCH (a:Entity {{id: {q(a)}}}), (b:Entity {{id: {q(b)}}})",
              f"MERGE (a)-[r:{t}]->(b)",
              "SET " + ",\n    ".join(sets) + ";"]
    return "\n".join(L) + "\n"

if __name__ == "__main__":
    out = ROOT / "kb" / "DB_diabet.cypher"
    out.parent.mkdir(exist_ok=True)
    text = generate()
    out.write_text(text, encoding="utf-8")
    from app.kb_utils import parse_statements
    n = len(parse_statements(text))
    print(f"Đã sinh {out}: {len(SOURCES)} nguồn, {len(NODES)} thực thể, {len(RELS)} quan hệ, {n} câu lệnh Cypher.")
