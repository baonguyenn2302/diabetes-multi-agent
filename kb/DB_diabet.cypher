// ============================================================
// DB_diabet.cypher – Knowledge Graph tiểu đường (kb_diabet_v1)
// File này được SINH TỰ ĐỘNG bởi scripts/build_kb.py – đừng sửa tay, hãy sửa build_kb.py rồi chạy lại.
// Nạp vào Neo4j:  python scripts/load_kb.py
// Nội dung diễn đạt lại từ các nguồn trong nút :Source; prototype học tập, chưa được chuyên gia y tế thẩm định.
// ============================================================

CREATE CONSTRAINT entity_id IF NOT EXISTS FOR (n:Entity) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT source_id IF NOT EXISTS FOR (s:Source) REQUIRE s.id IS UNIQUE;

// ---------- Nguồn ----------
MERGE (s:Source {id: 'src_ada2026'})
SET s.title = 'ADA – Standards of Care in Diabetes—2026, mục 2: Diagnosis and Classification of Diabetes',
    s.publisher = 'American Diabetes Association',
    s.url = 'https://doi.org/10.2337/dc26-S002',
    s.accessed = '2026-11-12';
MERGE (s:Source {id: 'src_ada2023_t4'})
SET s.title = 'Bảng tiêu chí chẩn đoán đái tháo đường (theo ADA, 2023)',
    s.publisher = 'PubMed Central',
    s.url = 'https://pmc.ncbi.nlm.nih.gov/articles/PMC10516260/table/T4',
    s.accessed = '2026-11-12';
MERGE (s:Source {id: 'src_ada2021_t2'})
SET s.title = 'ADA 2021 – Criteria for the Screening and Diagnosis of Prediabetes and Diabetes',
    s.publisher = 'PubMed Central',
    s.url = 'https://pmc.ncbi.nlm.nih.gov/articles/PMC7839613/table/T2',
    s.accessed = '2026-11-12';
MERGE (s:Source {id: 'src_diabetesnet'})
SET s.title = 'Diabetes Risk Factors and Diagnosis 2026 (tóm tắt ADA Standards 2026)',
    s.publisher = 'DiabetesNet',
    s.url = 'https://www.diabetesnet.com/about-diabetes/newly-diagnosed/risk-diagnosis-diabetes/',
    s.accessed = '2026-11-12';
MERGE (s:Source {id: 'src_who'})
SET s.title = 'WHO – Diabetes (fact sheet)',
    s.publisher = 'World Health Organization',
    s.url = 'https://www.who.int/News-Room/Fact-Sheets/Detail/Diabetes',
    s.accessed = '2026-11-12';
MERGE (s:Source {id: 'src_who_afro'})
SET s.title = 'WHO AFRO – Diabetes',
    s.publisher = 'World Health Organization',
    s.url = 'https://www.afro.who.int/fr/node/530',
    s.accessed = '2026-11-12';
MERGE (s:Source {id: 'src_vinmec_early'})
SET s.title = 'Vinmec – Triệu chứng sớm của đái tháo đường type 2',
    s.publisher = 'Vinmec',
    s.url = 'https://www.vinmec.com/vi/tin-tuc/thong-tin-suc-khoe/dau-hieu-som-cua-tieu-duong-type-2/',
    s.accessed = '2026-11-12';
MERGE (s:Source {id: 'src_vinmec_t2'})
SET s.title = 'Vinmec – Bệnh tiểu đường tuýp 2',
    s.publisher = 'Vinmec',
    s.url = 'https://www.vinmec.com/vi/benh/tieu-duong-tuyp-2-3042/?location=all',
    s.accessed = '2026-11-12';
MERGE (s:Source {id: 'src_vinmec_ckd'})
SET s.title = 'Vinmec – Chủ đề Đái tháo đường loại 2',
    s.publisher = 'Vinmec',
    s.url = 'https://www.vinmec.com/vi/chu-de/dai-thao-duong-loai-2',
    s.accessed = '2026-11-12';
MERGE (s:Source {id: 'src_vnexpress'})
SET s.title = 'VnExpress – Đái tháo đường',
    s.publisher = 'VnExpress',
    s.url = 'https://vnexpress.net/dai-thao-duong-4444964.html',
    s.accessed = '2026-11-12';
MERGE (s:Source {id: 'src_longchau_t2'})
SET s.title = 'Nhà thuốc Long Châu – Tiểu đường tuýp 2',
    s.publisher = 'Nhà thuốc Long Châu',
    s.url = 'https://nhathuoclongchau.com.vn/benh/tieu-duong-tip-2.html',
    s.accessed = '2026-11-12';
MERGE (s:Source {id: 'src_longchau_t2b'})
SET s.title = 'Nhà thuốc Long Châu – Tiểu đường tuýp 2 (triệu chứng muộn)',
    s.publisher = 'Nhà thuốc Long Châu',
    s.url = 'https://nhathuoclongchau.com.vn/benh/tieu-duong-tuyp-2.html',
    s.accessed = '2026-11-12';
MERGE (s:Source {id: 'src_longchau_comp'})
SET s.title = 'Nhà thuốc Long Châu – Đái tháo đường: kiểm soát toàn diện biến chứng',
    s.publisher = 'Nhà thuốc Long Châu',
    s.url = 'https://nhathuoclongchau.com.vn/bai-viet/dai-thao-duong-kiem-soat-toan-dien-bien-chung-de-song-khoe-moi-ngay.html',
    s.accessed = '2026-11-12';
MERGE (s:Source {id: 'src_longchau_mech'})
SET s.title = 'Nhà thuốc Long Châu – Cơ chế đái tháo đường type 2',
    s.publisher = 'Nhà thuốc Long Châu',
    s.url = 'https://nhathuoclongchau.com.vn/bai-viet/co-che-dai-thao-duong-type-2-la-gi-nguyen-nhan-do-dau.html',
    s.accessed = '2026-11-12';
MERGE (s:Source {id: 'src_pharmacity_danger'})
SET s.title = 'Pharmacity – Bệnh tiểu đường có nguy hiểm không? Các biến chứng có thể gặp',
    s.publisher = 'Pharmacity',
    s.url = 'https://www.pharmacity.vn/benh-tieu-duong-co-nguy-hiem-khong.htm',
    s.accessed = '2026-11-12';
MERGE (s:Source {id: 'src_pharmacity_elderly'})
SET s.title = 'Pharmacity – Biến chứng tiểu đường ở người già',
    s.publisher = 'Pharmacity',
    s.url = 'https://www.pharmacity.vn/bien-chung-tieu-duong-o-nguoi-gia.htm',
    s.accessed = '2026-11-12';
MERGE (s:Source {id: 'src_pharmacity_coma'})
SET s.title = 'Pharmacity – Hôn mê tiểu đường là gì?',
    s.publisher = 'Pharmacity',
    s.url = 'https://www.pharmacity.vn/hon-me-tieu-duong.htm',
    s.accessed = '2026-11-12';
MERGE (s:Source {id: 'src_tamanh'})
SET s.title = 'Bệnh viện Tâm Anh – Tiểu đường tuýp 2',
    s.publisher = 'Bệnh viện Tâm Anh',
    s.url = 'https://tamanhhospital.vn/tieu-duong-tuyp-2/',
    s.accessed = '2026-11-12';
MERGE (s:Source {id: 'src_project'})
SET s.title = 'Project – ánh xạ cột dữ liệu ↔ tri thức và chính sách an toàn',
    s.publisher = 'Nhóm sinh viên (tự xây dựng)',
    s.url = '',
    s.accessed = '2026-11-12';

// ---------- Thực thể ----------
MERGE (n:Entity {id: 'diabetes'})
SET n:Disease,
    n.kind = 'Disease',
    n.name = 'Bệnh đái tháo đường (tiểu đường)',
    n.name_en = 'Diabetes mellitus',
    n.aliases = ['đái tháo đường', 'tiểu đường', 'bệnh tiểu đường', 'bệnh đái tháo đường', 'diabetes'],
    n.search_terms = ['dai thao duong', 'tieu duong', 'benh tieu duong', 'benh dai thao duong', 'diabetes', 'benh dai thao duong tieu duong', 'diabetes mellitus'],
    n.description = 'Bệnh mạn tính xảy ra khi tuyến tụy không tạo đủ insulin hoặc cơ thể không sử dụng insulin hiệu quả, khiến đường huyết tăng cao. Nếu kéo dài, tăng đường huyết có thể làm tổn thương tim, mạch máu, mắt, thận và thần kinh.',
    n.source_id = 'src_who';
MERGE (n:Entity {id: 'type1'})
SET n:Disease,
    n.kind = 'Disease',
    n.name = 'Tiểu đường type 1',
    n.name_en = 'Type 1 diabetes',
    n.aliases = ['tiểu đường type 1', 'tiểu đường tuýp 1', 'tiểu đường loại 1', 'đái tháo đường type 1', 'đái tháo đường tuýp 1', 'đái tháo đường loại 1', 'type 1', 't1d'],
    n.search_terms = ['tieu duong type 1', 'tieu duong tuyp 1', 'tieu duong loai 1', 'dai thao duong type 1', 'dai thao duong tuyp 1', 'dai thao duong loai 1', 'type 1', 't1d', 'type 1 diabetes'],
    n.description = 'Thể bệnh đặc trưng bởi việc cơ thể thiếu hụt khả năng sản xuất insulin nên người bệnh cần dùng insulin hằng ngày. Nguyên nhân chưa được biết rõ và hiện chưa có cách phòng ngừa.',
    n.source_id = 'src_who';
MERGE (n:Entity {id: 'type2'})
SET n:Disease,
    n.kind = 'Disease',
    n.name = 'Tiểu đường type 2',
    n.name_en = 'Type 2 diabetes',
    n.aliases = ['tiểu đường type 2', 'tiểu đường tuýp 2', 'tiểu đường loại 2', 'đái tháo đường type 2', 'đái tháo đường tuýp 2', 'đái tháo đường loại 2', 'type 2', 't2d'],
    n.search_terms = ['tieu duong type 2', 'tieu duong tuyp 2', 'tieu duong loai 2', 'dai thao duong type 2', 'dai thao duong tuyp 2', 'dai thao duong loai 2', 'type 2', 't2d', 'type 2 diabetes'],
    n.description = 'Dạng phổ biến nhất, chiếm khoảng 90–95% số ca. Cơ chế gồm đề kháng insulin cùng với suy giảm chức năng tế bào beta của tuyến tụy. Bệnh thường tiến triển âm thầm, triệu chứng nhẹ hoặc không rõ nên dễ được phát hiện muộn, khi đã có biến chứng.',
    n.source_id = 'src_vnexpress';
MERGE (n:Entity {id: 'gestational'})
SET n:Disease,
    n.kind = 'Disease',
    n.name = 'Tiểu đường thai kỳ',
    n.name_en = 'Gestational diabetes',
    n.aliases = ['tiểu đường thai kỳ', 'đái tháo đường thai kỳ', 'tiểu đường khi mang thai', 'gdm'],
    n.search_terms = ['tieu duong thai ky', 'dai thao duong thai ky', 'tieu duong khi mang thai', 'gdm', 'gestational diabetes'],
    n.description = 'Tình trạng tăng đường huyết xuất hiện trong thai kỳ, thường được phát hiện qua sàng lọc trước sinh. Người từng mắc có nguy cơ cao hơn bị tiểu đường type 2 về sau.',
    n.source_id = 'src_who';
MERGE (n:Entity {id: 'prediabetes'})
SET n:Disease,
    n.kind = 'Disease',
    n.name = 'Tiền tiểu đường',
    n.name_en = 'Prediabetes',
    n.aliases = ['tiền tiểu đường', 'tiền đái tháo đường', 'rối loạn dung nạp glucose', 'prediabetes', 'igt', 'ifg'],
    n.search_terms = ['tien tieu duong', 'tien dai thao duong', 'roi loan dung nap glucose', 'prediabetes', 'igt', 'ifg'],
    n.description = 'Giai đoạn đường huyết cao hơn bình thường nhưng chưa đạt ngưỡng chẩn đoán tiểu đường, thường không có triệu chứng rõ ràng. Đây là giai đoạn cảnh báo nguy cơ cao tiến triển thành tiểu đường type 2.',
    n.source_id = 'src_vinmec_early';
MERGE (n:Entity {id: 'sym_polyuria'})
SET n:Symptom,
    n.kind = 'Symptom',
    n.name = 'Đi tiểu nhiều',
    n.name_en = 'Polyuria',
    n.aliases = ['đi tiểu nhiều', 'tiểu nhiều', 'tiểu đêm', 'polyuria'],
    n.search_terms = ['di tieu nhieu', 'tieu nhieu', 'tieu dem', 'polyuria'],
    n.description = 'Đi tiểu thường xuyên hơn bình thường, một trong những dấu hiệu điển hình của tăng đường huyết.',
    n.source_id = 'src_longchau_t2';
MERGE (n:Entity {id: 'sym_polydipsia'})
SET n:Symptom,
    n.kind = 'Symptom',
    n.name = 'Khát nước, uống nhiều',
    n.name_en = 'Polydipsia',
    n.aliases = ['uống nhiều', 'khát nước', 'khát nhiều', 'rất khát', 'polydipsia'],
    n.search_terms = ['uong nhieu', 'khat nuoc', 'khat nhieu', 'rat khat', 'polydipsia', 'khat nuoc uong nhieu'],
    n.description = 'Cảm giác khát và uống nước nhiều hơn bình thường, dấu hiệu điển hình của tăng đường huyết.',
    n.source_id = 'src_longchau_t2';
MERGE (n:Entity {id: 'sym_polyphagia'})
SET n:Symptom,
    n.kind = 'Symptom',
    n.name = 'Ăn nhiều, hay đói',
    n.name_en = 'Polyphagia',
    n.aliases = ['ăn nhiều', 'hay đói', 'đói nhiều', 'polyphagia'],
    n.search_terms = ['an nhieu', 'hay doi', 'doi nhieu', 'polyphagia', 'an nhieu hay doi'],
    n.description = 'Thèm ăn, ăn nhiều hơn bình thường, một trong bốn dấu hiệu điển hình của tăng đường huyết.',
    n.source_id = 'src_longchau_t2';
MERGE (n:Entity {id: 'sym_weight_loss'})
SET n:Symptom,
    n.kind = 'Symptom',
    n.name = 'Sụt cân (gầy nhiều)',
    n.name_en = 'Weight loss',
    n.aliases = ['sụt cân', 'gầy nhiều', 'gầy sút', 'giảm cân không rõ nguyên nhân'],
    n.search_terms = ['sut can', 'gay nhieu', 'gay sut', 'giam can khong ro nguyen nhan', 'sut can gay nhieu', 'weight loss'],
    n.description = 'Giảm cân dù ăn nhiều, một trong bốn dấu hiệu điển hình của tăng đường huyết.',
    n.source_id = 'src_longchau_t2';
MERGE (n:Entity {id: 'sym_fatigue'})
SET n:Symptom,
    n.kind = 'Symptom',
    n.name = 'Mệt mỏi',
    n.name_en = 'Fatigue',
    n.aliases = ['mệt mỏi', 'mệt'],
    n.search_terms = ['met moi', 'met', 'fatigue'],
    n.description = 'Cảm giác mệt, thiếu năng lượng; có thể xuất hiện đột ngột ở người bị tăng đường huyết.',
    n.source_id = 'src_who_afro';
MERGE (n:Entity {id: 'sym_blurred_vision'})
SET n:Symptom,
    n.kind = 'Symptom',
    n.name = 'Nhìn mờ',
    n.name_en = 'Blurred vision',
    n.aliases = ['nhìn mờ', 'mờ mắt', 'thay đổi thị lực'],
    n.search_terms = ['nhin mo', 'mo mat', 'thay doi thi luc', 'blurred vision'],
    n.description = 'Thị lực thay đổi, nhìn mờ; có thể gặp khi đường huyết cao hoặc do biến chứng ở mắt.',
    n.source_id = 'src_who_afro';
MERGE (n:Entity {id: 'sym_numbness'})
SET n:Symptom,
    n.kind = 'Symptom',
    n.name = 'Tê bì tay chân',
    n.name_en = 'Numbness / tingling',
    n.aliases = ['tê bì', 'tê tay chân', 'tê bì tay chân', 'châm chích'],
    n.search_terms = ['te bi', 'te tay chan', 'te bi tay chan', 'cham chich', 'numbness tingling'],
    n.description = 'Tê, châm chích ở bàn tay hoặc bàn chân, thường là dấu hiệu muộn của tổn thương thần kinh do tiểu đường.',
    n.source_id = 'src_longchau_t2b';
MERGE (n:Entity {id: 'sym_dry_mouth'})
SET n:Symptom,
    n.kind = 'Symptom',
    n.name = 'Khô miệng',
    n.name_en = 'Dry mouth',
    n.aliases = ['khô miệng'],
    n.search_terms = ['kho mieng', 'dry mouth'],
    n.description = 'Cảm giác khô miệng, gặp trong các triệu chứng khởi phát của tiểu đường type 1.',
    n.source_id = 'src_vnexpress';
MERGE (n:Entity {id: 'sym_itchy_skin'})
SET n:Symptom,
    n.kind = 'Symptom',
    n.name = 'Ngứa da',
    n.name_en = 'Itchy skin',
    n.aliases = ['ngứa da'],
    n.search_terms = ['ngua da', 'itchy skin'],
    n.description = 'Ngứa da, gặp trong các triệu chứng khởi phát của tiểu đường type 1.',
    n.source_id = 'src_vnexpress';
MERGE (n:Entity {id: 'rf_overweight'})
SET n:RiskFactor,
    n.kind = 'RiskFactor',
    n.name = 'Thừa cân, béo phì',
    n.name_en = 'Overweight / obesity',
    n.aliases = ['thừa cân', 'béo phì', 'bmi', 'chỉ số khối cơ thể', 'bmi cao'],
    n.search_terms = ['thua can', 'beo phi', 'bmi', 'chi so khoi co the', 'bmi cao', 'thua can beo phi', 'overweight obesity'],
    n.description = 'Chỉ số BMI và vòng eo cao có liên quan đến nguy cơ mắc tiểu đường type 2 cao hơn. Thừa cân, béo phì là yếu tố nguy cơ quan trọng và có thể thay đổi được.',
    n.source_id = 'src_who';
MERGE (n:Entity {id: 'rf_age45'})
SET n:RiskFactor,
    n.kind = 'RiskFactor',
    n.name = 'Tuổi từ 45 trở lên',
    n.name_en = 'Age ≥ 45',
    n.aliases = ['tuổi cao', '45 tuổi', 'từ 45 tuổi', 'lớn tuổi', 'tuổi tác', 'người cao tuổi'],
    n.search_terms = ['tuoi cao', '45 tuoi', 'tu 45 tuoi', 'lon tuoi', 'tuoi tac', 'nguoi cao tuoi', 'tuoi tu 45 tro len', 'age 45'],
    n.description = 'Người từ khoảng 45 tuổi trở lên là nhóm dễ mắc tiểu đường type 2 hơn.',
    n.source_id = 'src_longchau_mech';
MERGE (n:Entity {id: 'rf_family'})
SET n:RiskFactor,
    n.kind = 'RiskFactor',
    n.name = 'Tiền sử gia đình mắc tiểu đường',
    n.name_en = 'Family history',
    n.aliases = ['tiền sử gia đình', 'di truyền', 'bố mẹ mắc', 'người thân mắc', 'gia đình có người'],
    n.search_terms = ['tien su gia dinh', 'di truyen', 'bo me mac', 'nguoi than mac', 'gia dinh co nguoi', 'tien su gia dinh mac tieu duong', 'family history'],
    n.description = 'Có cha mẹ hoặc anh chị em ruột mắc tiểu đường type 2 làm tăng nguy cơ mắc bệnh.',
    n.source_id = 'src_vinmec_early';
MERGE (n:Entity {id: 'rf_inactivity'})
SET n:RiskFactor,
    n.kind = 'RiskFactor',
    n.name = 'Ít vận động',
    n.name_en = 'Physical inactivity',
    n.aliases = ['ít vận động', 'lười vận động', 'thiếu vận động', 'ngồi nhiều'],
    n.search_terms = ['it van dong', 'luoi van dong', 'thieu van dong', 'ngoi nhieu', 'physical inactivity'],
    n.description = 'Thiếu vận động thể lực góp phần làm tăng nguy cơ mắc tiểu đường type 2.',
    n.source_id = 'src_who';
MERGE (n:Entity {id: 'rf_hypertension'})
SET n:RiskFactor,
    n.kind = 'RiskFactor',
    n.name = 'Tăng huyết áp',
    n.name_en = 'Hypertension',
    n.aliases = ['tăng huyết áp', 'huyết áp cao', 'cao huyết áp', 'hypertension'],
    n.search_terms = ['tang huyet ap', 'huyet ap cao', 'cao huyet ap', 'hypertension'],
    n.description = 'Tăng huyết áp nằm trong nhóm yếu tố nguy cơ của tiểu đường type 2.',
    n.source_id = 'src_vnexpress';
MERGE (n:Entity {id: 'rf_cvd'})
SET n:RiskFactor,
    n.kind = 'RiskFactor',
    n.name = 'Bệnh tim mạch (xơ vữa động mạch)',
    n.name_en = 'Cardiovascular disease',
    n.aliases = ['bệnh tim mạch', 'bệnh tim', 'heart disease', 'xơ vữa động mạch'],
    n.search_terms = ['benh tim mach', 'benh tim', 'heart disease', 'xo vua dong mach', 'benh tim mach xo vua dong mach', 'cardiovascular disease'],
    n.description = 'Tiền sử bệnh tim mạch do xơ vữa động mạch nằm trong nhóm yếu tố nguy cơ của tiểu đường type 2.',
    n.source_id = 'src_vnexpress';
MERGE (n:Entity {id: 'rf_dyslipidemia'})
SET n:RiskFactor,
    n.kind = 'RiskFactor',
    n.name = 'Rối loạn lipid máu (mỡ máu cao)',
    n.name_en = 'Dyslipidemia',
    n.aliases = ['rối loạn lipid', 'mỡ máu', 'mỡ máu cao', 'cholesterol cao'],
    n.search_terms = ['roi loan lipid', 'mo mau', 'mo mau cao', 'cholesterol cao', 'roi loan lipid mau mo mau cao', 'dyslipidemia'],
    n.description = 'Rối loạn lipid máu làm tăng đề kháng insulin, dễ dẫn đến tiểu đường type 2.',
    n.source_id = 'src_vinmec_early';
MERGE (n:Entity {id: 'rf_pcos'})
SET n:RiskFactor,
    n.kind = 'RiskFactor',
    n.name = 'Hội chứng buồng trứng đa nang (PCOS)',
    n.name_en = 'Polycystic ovary syndrome',
    n.aliases = ['pcos', 'buồng trứng đa nang'],
    n.search_terms = ['pcos', 'buong trung da nang', 'hoi chung buong trung da nang pcos', 'polycystic ovary syndrome'],
    n.description = 'Phụ nữ mắc hội chứng buồng trứng đa nang có nguy cơ cao hơn mắc tiểu đường type 2.',
    n.source_id = 'src_vinmec_early';
MERGE (n:Entity {id: 'rf_gdm_history'})
SET n:RiskFactor,
    n.kind = 'RiskFactor',
    n.name = 'Tiền sử tiểu đường thai kỳ',
    n.name_en = 'History of gestational diabetes',
    n.aliases = ['tiền sử tiểu đường thai kỳ', 'từng bị tiểu đường thai kỳ', 'từng mắc tiểu đường thai kỳ'],
    n.search_terms = ['tien su tieu duong thai ky', 'tung bi tieu duong thai ky', 'tung mac tieu duong thai ky', 'history of gestational diabetes'],
    n.description = 'Phụ nữ từng bị tiểu đường thai kỳ có nguy cơ cao hơn mắc tiểu đường type 2 sau này.',
    n.source_id = 'src_vnexpress';
MERGE (n:Entity {id: 'comp_retinopathy'})
SET n:Complication,
    n.kind = 'Complication',
    n.name = 'Biến chứng mắt (võng mạc, đục thủy tinh thể, tăng nhãn áp)',
    n.name_en = 'Eye complications',
    n.aliases = ['võng mạc', 'biến chứng mắt', 'đục thủy tinh thể', 'tăng nhãn áp'],
    n.search_terms = ['vong mac', 'bien chung mat', 'duc thuy tinh the', 'tang nhan ap', 'bien chung mat vong mac duc thuy tinh the tang nhan ap', 'eye complications'],
    n.description = 'Ngoài bệnh võng mạc, người mắc tiểu đường còn dễ gặp đục thủy tinh thể và tăng nhãn áp. Tổn thương thường tiến triển chậm và ít triệu chứng ở giai đoạn đầu.',
    n.source_id = 'src_pharmacity_danger';
MERGE (n:Entity {id: 'comp_nephropathy'})
SET n:Complication,
    n.kind = 'Complication',
    n.name = 'Bệnh thận mạn do tiểu đường',
    n.name_en = 'Diabetic kidney disease',
    n.aliases = ['bệnh thận', 'suy thận', 'thận mạn', 'biến chứng thận', 'tổn thương thận'],
    n.search_terms = ['benh than', 'suy than', 'than man', 'bien chung than', 'ton thuong than', 'benh than man do tieu duong', 'diabetic kidney disease'],
    n.description = 'Khoảng 40% người mắc đái tháo đường có thể phát triển bệnh thận mạn, thường không có triệu chứng rõ ở giai đoạn đầu; nếu không theo dõi có thể tiến triển thành suy thận mạn.',
    n.source_id = 'src_longchau_comp';
MERGE (n:Entity {id: 'comp_neuropathy'})
SET n:Complication,
    n.kind = 'Complication',
    n.name = 'Biến chứng thần kinh',
    n.name_en = 'Diabetic neuropathy',
    n.aliases = ['thần kinh', 'tổn thương thần kinh', 'biến chứng thần kinh'],
    n.search_terms = ['than kinh', 'ton thuong than kinh', 'bien chung than kinh', 'diabetic neuropathy'],
    n.description = 'Thường gặp ở người bệnh lâu năm, biểu hiện như tê bì, châm chích, đau rát hoặc giảm cảm giác ở tay và chân.',
    n.source_id = 'src_pharmacity_danger';
MERGE (n:Entity {id: 'comp_cvd'})
SET n:Complication,
    n.kind = 'Complication',
    n.name = 'Biến chứng tim mạch (nhồi máu cơ tim, đột quỵ)',
    n.name_en = 'Cardiovascular complications',
    n.aliases = ['nhồi máu cơ tim', 'đột quỵ', 'biến chứng tim mạch'],
    n.search_terms = ['nhoi mau co tim', 'dot quy', 'bien chung tim mach', 'bien chung tim mach nhoi mau co tim dot quy', 'cardiovascular complications'],
    n.description = 'Người mắc tiểu đường type 2 có nguy cơ cao hơn bị tăng huyết áp, rối loạn lipid máu, đột quỵ, nhồi máu cơ tim và các bệnh mạch máu khác.',
    n.source_id = 'src_longchau_t2';
MERGE (n:Entity {id: 'comp_foot'})
SET n:Complication,
    n.kind = 'Complication',
    n.name = 'Loét bàn chân tiểu đường',
    n.name_en = 'Diabetic foot ulcer',
    n.aliases = ['loét bàn chân', 'bàn chân tiểu đường', 'cắt cụt chi', 'cắt cụt', 'biến chứng chân', 'biến chứng ở chân'],
    n.search_terms = ['loet ban chan', 'ban chan tieu duong', 'cat cut chi', 'cat cut', 'bien chung chan', 'bien chung o chan', 'loet ban chan tieu duong', 'diabetic foot ulcer'],
    n.description = 'Tổn thương thần kinh và lưu thông máu kém khiến vết loét ở bàn chân dễ nhiễm trùng, khó lành; nếu không điều trị kịp thời có thể phải cắt cụt chi.',
    n.source_id = 'src_pharmacity_elderly';
MERGE (n:Entity {id: 'comp_coma'})
SET n:Complication,
    n.kind = 'Complication',
    n.name = 'Hôn mê tiểu đường (hạ đường huyết nặng, nhiễm toan ceton, tăng áp lực thẩm thấu)',
    n.name_en = 'Diabetic coma',
    n.aliases = ['hôn mê', 'hôn mê tiểu đường', 'nhiễm toan ceton', 'hạ đường huyết nặng', 'biến chứng cấp'],
    n.search_terms = ['hon me', 'hon me tieu duong', 'nhiem toan ceton', 'ha duong huyet nang', 'bien chung cap', 'hon me tieu duong ha duong huyet nang nhiem toan ceton tang ap luc tham thau', 'diabetic coma'],
    n.description = 'Biến chứng cấp tính, có thể tiến triển rất nhanh và đe dọa tính mạng. Các nguyên nhân phổ biến gồm hạ đường huyết nặng, nhiễm toan ceton và tăng áp lực thẩm thấu.',
    n.source_id = 'src_pharmacity_coma';
MERGE (n:Entity {id: 'test_hba1c'})
SET n:Test,
    n.kind = 'Test',
    n.name = 'Xét nghiệm HbA1c',
    n.name_en = 'Hemoglobin A1c',
    n.aliases = ['hba1c', 'a1c', 'xét nghiệm hba1c'],
    n.search_terms = ['hba1c', 'a1c', 'xet nghiem hba1c', 'hemoglobin a1c'],
    n.description = 'Xét nghiệm phản ánh mức kiểm soát đường huyết trong thời gian dài. Ngưỡng ≥ 6.5% dùng để chẩn đoán tiểu đường, 5.7–6.4% gợi ý tiền tiểu đường. Cần làm ở phòng xét nghiệm đạt chuẩn; không dùng máy đo tại chỗ để chẩn đoán.',
    n.source_id = 'src_ada2023_t4';
MERGE (n:Entity {id: 'test_fpg'})
SET n:Test,
    n.kind = 'Test',
    n.name = 'Đường huyết lúc đói (FPG)',
    n.name_en = 'Fasting plasma glucose',
    n.aliases = ['đường huyết lúc đói', 'đường huyết đói', 'glucose lúc đói', 'fpg'],
    n.search_terms = ['duong huyet luc doi', 'duong huyet doi', 'glucose luc doi', 'fpg', 'duong huyet luc doi fpg', 'fasting plasma glucose'],
    n.description = 'Đường huyết đo sau khi nhịn ăn (không nạp calo) ít nhất 8 giờ. Ngưỡng ≥ 126 mg/dL (7.0 mmol/L) dùng để chẩn đoán tiểu đường; 100–125 mg/dL gợi ý tiền tiểu đường.',
    n.source_id = 'src_ada2023_t4';
MERGE (n:Entity {id: 'test_ogtt'})
SET n:Test,
    n.kind = 'Test',
    n.name = 'Nghiệm pháp dung nạp glucose đường uống (OGTT)',
    n.name_en = 'Oral glucose tolerance test',
    n.aliases = ['ogtt', 'nghiệm pháp dung nạp glucose', 'dung nạp glucose đường uống'],
    n.search_terms = ['ogtt', 'nghiem phap dung nap glucose', 'dung nap glucose duong uong', 'nghiem phap dung nap glucose duong uong ogtt', 'oral glucose tolerance test'],
    n.description = 'Đo đường huyết sau 2 giờ uống 75 g glucose. Mức ≥ 200 mg/dL (11.1 mmol/L) là tiểu đường; 140–199 mg/dL gợi ý tiền tiểu đường.',
    n.source_id = 'src_ada2021_t2';
MERGE (n:Entity {id: 'test_rpg'})
SET n:Test,
    n.kind = 'Test',
    n.name = 'Đường huyết ngẫu nhiên (bất kỳ thời điểm)',
    n.name_en = 'Random plasma glucose',
    n.aliases = ['đường huyết ngẫu nhiên', 'đường huyết bất kỳ', 'random glucose'],
    n.search_terms = ['duong huyet ngau nhien', 'duong huyet bat ky', 'random glucose', 'duong huyet ngau nhien bat ky thoi diem', 'random plasma glucose'],
    n.description = 'Ở người có triệu chứng điển hình của tăng đường huyết, mức ≥ 200 mg/dL (11.1 mmol/L) đo vào bất kỳ thời điểm nào đủ để chẩn đoán tiểu đường.',
    n.source_id = 'src_ada2023_t4';
MERGE (n:Entity {id: 'adv_confirm'})
SET n:Advice,
    n.kind = 'Advice',
    n.name = 'Xác nhận chẩn đoán bằng xét nghiệm lặp lại',
    n.name_en = 'Confirm diagnosis',
    n.aliases = ['xác nhận chẩn đoán', 'xét nghiệm lại'],
    n.search_terms = ['xac nhan chan doan', 'xet nghiem lai', 'xac nhan chan doan bang xet nghiem lap lai', 'confirm diagnosis'],
    n.description = 'Khi chưa có tăng đường huyết rõ rệt, việc chẩn đoán cần kết quả bất thường ở hai xét nghiệm khác nhau cùng ngày hoặc ở hai mẫu lấy vào hai ngày khác nhau.',
    n.source_id = 'src_ada2023_t4';
MERGE (n:Entity {id: 'adv_not_diagnosis'})
SET n:Advice,
    n.kind = 'Advice',
    n.name = 'Kết quả hệ thống chỉ mang tính tham khảo',
    n.name_en = 'Not a diagnosis',
    n.aliases = ['thay thế bác sĩ', 'chẩn đoán xác định'],
    n.search_terms = ['thay the bac si', 'chan doan xac dinh', 'ket qua he thong chi mang tinh tham khao', 'not a diagnosis'],
    n.description = 'Kết quả dự đoán của mô hình và gợi ý của hệ thống chỉ mang tính tham khảo, không thay thế chẩn đoán của bác sĩ; cần xét nghiệm xác nhận và tư vấn chuyên môn.',
    n.source_id = 'src_project';
MERGE (n:Entity {id: 'adv_see_doctor'})
SET n:Advice,
    n.kind = 'Advice',
    n.name = 'Đến gặp bác sĩ khi có nguy cơ hoặc triệu chứng',
    n.name_en = 'See a doctor',
    n.aliases = ['gặp bác sĩ', 'đi khám', 'khám bác sĩ'],
    n.search_terms = ['gap bac si', 'di kham', 'kham bac si', 'den gap bac si khi co nguy co hoac trieu chung', 'see a doctor'],
    n.description = 'Nếu có yếu tố nguy cơ hoặc xuất hiện các triệu chứng nghi ngờ, nên liên hệ bác sĩ để được kiểm tra và tư vấn.',
    n.source_id = 'src_longchau_t2';
MERGE (n:Entity {id: 'adv_checkup'})
SET n:Advice,
    n.kind = 'Advice',
    n.name = 'Khám và xét nghiệm đường huyết định kỳ',
    n.name_en = 'Regular check-ups',
    n.aliases = ['khám định kỳ', 'tầm soát', 'sàng lọc', 'xét nghiệm định kỳ'],
    n.search_terms = ['kham dinh ky', 'tam soat', 'sang loc', 'xet nghiem dinh ky', 'kham va xet nghiem duong huyet dinh ky', 'regular check ups'],
    n.description = 'Cách tốt nhất để phát hiện sớm là khám sức khỏe và xét nghiệm đường huyết định kỳ với cán bộ y tế.',
    n.source_id = 'src_who';
MERGE (n:Entity {id: 'adv_screen_35'})
SET n:Advice,
    n.kind = 'Advice',
    n.name = 'Bắt đầu sàng lọc từ 35 tuổi',
    n.name_en = 'Screening from age 35',
    n.aliases = ['sàng lọc từ 35 tuổi', '35 tuổi'],
    n.search_terms = ['sang loc tu 35 tuoi', '35 tuoi', 'bat dau sang loc tu 35 tuoi', 'screening from age 35'],
    n.description = 'Theo tóm tắt khuyến cáo ADA 2026, người trưởng thành nên bắt đầu sàng lọc tiểu đường từ 35 tuổi; sớm hơn nếu thừa cân hoặc béo phì và có thêm yếu tố nguy cơ.',
    n.source_id = 'src_diabetesnet';
MERGE (n:Entity {id: 'adv_prediabetes_followup'})
SET n:Advice,
    n.kind = 'Advice',
    n.name = 'Theo dõi người tiền tiểu đường ít nhất mỗi năm',
    n.name_en = 'Annual follow-up for prediabetes',
    n.aliases = ['theo dõi tiền tiểu đường'],
    n.search_terms = ['theo doi tien tieu duong', 'theo doi nguoi tien tieu duong it nhat moi nam', 'annual follow up for prediabetes'],
    n.description = 'Người tiền tiểu đường nên được theo dõi khả năng tiến triển thành tiểu đường ít nhất mỗi năm, hoặc thường xuyên hơn tùy mức nguy cơ.',
    n.source_id = 'src_diabetesnet';
MERGE (n:Entity {id: 'adv_diet'})
SET n:Advice,
    n.kind = 'Advice',
    n.name = 'Ăn uống lành mạnh',
    n.name_en = 'Healthy diet',
    n.aliases = ['ăn uống', 'chế độ ăn', 'thực đơn', 'hạn chế đường', 'ăn gì'],
    n.search_terms = ['an uong', 'che do an', 'thuc don', 'han che duong', 'an gi', 'an uong lanh manh', 'healthy diet'],
    n.description = 'Ăn uống lành mạnh, hạn chế đường và chất béo bão hòa giúp phòng ngừa hoặc làm chậm tiểu đường type 2.',
    n.source_id = 'src_who_afro';
MERGE (n:Entity {id: 'adv_activity'})
SET n:Advice,
    n.kind = 'Advice',
    n.name = 'Vận động thể lực đều đặn',
    n.name_en = 'Regular physical activity',
    n.aliases = ['vận động', 'tập thể dục', 'thể dục', 'hoạt động thể lực', 'tập luyện'],
    n.search_terms = ['van dong', 'tap the duc', 'the duc', 'hoat dong the luc', 'tap luyen', 'van dong the luc deu dan', 'regular physical activity'],
    n.description = 'Duy trì hoạt động thể lực cường độ vừa, ít nhất 150 phút mỗi tuần (khoảng 30 phút vào hầu hết các ngày).',
    n.source_id = 'src_who';
MERGE (n:Entity {id: 'adv_weight'})
SET n:Advice,
    n.kind = 'Advice',
    n.name = 'Duy trì cân nặng hợp lý',
    n.name_en = 'Healthy weight',
    n.aliases = ['giảm cân', 'cân nặng hợp lý', 'kiểm soát cân nặng'],
    n.search_terms = ['giam can', 'can nang hop ly', 'kiem soat can nang', 'duy tri can nang hop ly', 'healthy weight'],
    n.description = 'Đạt và duy trì cân nặng hợp lý là một trong các biện pháp phòng ngừa hoặc làm chậm tiểu đường type 2.',
    n.source_id = 'src_who_afro';
MERGE (n:Entity {id: 'adv_no_tobacco'})
SET n:Advice,
    n.kind = 'Advice',
    n.name = 'Không hút thuốc lá',
    n.name_en = 'Avoid tobacco',
    n.aliases = ['hút thuốc', 'thuốc lá', 'bỏ thuốc'],
    n.search_terms = ['hut thuoc', 'thuoc la', 'bo thuoc', 'khong hut thuoc la', 'avoid tobacco'],
    n.description = 'Tránh sử dụng thuốc lá giúp phòng ngừa tiểu đường type 2; bỏ thuốc cũng quan trọng để tránh biến chứng ở người đã mắc bệnh.',
    n.source_id = 'src_who_afro';
MERGE (n:Entity {id: 'adv_bp_lipid'})
SET n:Advice,
    n.kind = 'Advice',
    n.name = 'Kiểm soát huyết áp và mỡ máu',
    n.name_en = 'Control blood pressure and lipids',
    n.aliases = ['kiểm soát huyết áp', 'kiểm soát mỡ máu'],
    n.search_terms = ['kiem soat huyet ap', 'kiem soat mo mau', 'kiem soat huyet ap va mo mau', 'control blood pressure and lipids'],
    n.description = 'Kiểm soát đồng thời huyết áp và mỡ máu, kết hợp thăm khám định kỳ, giúp giảm nguy cơ biến chứng của tiểu đường.',
    n.source_id = 'src_pharmacity_danger';
MERGE (n:Entity {id: 'adv_foot_care'})
SET n:Advice,
    n.kind = 'Advice',
    n.name = 'Chăm sóc bàn chân',
    n.name_en = 'Foot care',
    n.aliases = ['chăm sóc chân', 'chăm sóc bàn chân'],
    n.search_terms = ['cham soc chan', 'cham soc ban chan', 'foot care'],
    n.description = 'Chăm sóc bàn chân là một phần quan trọng trong quản lý tiểu đường.',
    n.source_id = 'src_who_afro';
MERGE (n:Entity {id: 'feat_age'})
SET n:Feature,
    n.kind = 'Feature',
    n.name = 'age (cột dữ liệu)',
    n.name_en = 'dataset column: age',
    n.aliases = [],
    n.search_terms = [],
    n.description = 'Cột `age` trong dataset: tuổi của bệnh nhân.',
    n.source_id = 'src_project';
MERGE (n:Entity {id: 'feat_hypertension'})
SET n:Feature,
    n.kind = 'Feature',
    n.name = 'hypertension (cột dữ liệu)',
    n.name_en = 'dataset column: hypertension',
    n.aliases = [],
    n.search_terms = [],
    n.description = 'Cột `hypertension` trong dataset: 1 nếu bệnh nhân có tăng huyết áp, 0 nếu không.',
    n.source_id = 'src_project';
MERGE (n:Entity {id: 'feat_heart_disease'})
SET n:Feature,
    n.kind = 'Feature',
    n.name = 'heart_disease (cột dữ liệu)',
    n.name_en = 'dataset column: heart_disease',
    n.aliases = [],
    n.search_terms = [],
    n.description = 'Cột `heart_disease` trong dataset: 1 nếu bệnh nhân có bệnh tim, 0 nếu không.',
    n.source_id = 'src_project';
MERGE (n:Entity {id: 'feat_bmi'})
SET n:Feature,
    n.kind = 'Feature',
    n.name = 'bmi (cột dữ liệu)',
    n.name_en = 'dataset column: bmi',
    n.aliases = [],
    n.search_terms = [],
    n.description = 'Cột `bmi` trong dataset: chỉ số khối cơ thể.',
    n.source_id = 'src_project';
MERGE (n:Entity {id: 'feat_smoking_history'})
SET n:Feature,
    n.kind = 'Feature',
    n.name = 'smoking_history (cột dữ liệu)',
    n.name_en = 'dataset column: smoking_history',
    n.aliases = ['smoking history'],
    n.search_terms = ['smoking history'],
    n.description = 'Cột `smoking_history` trong dataset: tiền sử hút thuốc (never, former, current, ever, not current, No Info).',
    n.source_id = 'src_project';
MERGE (n:Entity {id: 'feat_hba1c_level'})
SET n:Feature,
    n.kind = 'Feature',
    n.name = 'HbA1c_level (cột dữ liệu)',
    n.name_en = 'dataset column: HbA1c_level',
    n.aliases = ['hba1c level'],
    n.search_terms = ['hba1c level'],
    n.description = 'Cột `HbA1c_level` trong dataset: mức HbA1c (%) của bệnh nhân.',
    n.source_id = 'src_project';
MERGE (n:Entity {id: 'feat_blood_glucose_level'})
SET n:Feature,
    n.kind = 'Feature',
    n.name = 'blood_glucose_level (cột dữ liệu)',
    n.name_en = 'dataset column: blood_glucose_level',
    n.aliases = ['blood glucose level'],
    n.search_terms = ['blood glucose level'],
    n.description = 'Cột `blood_glucose_level` trong dataset: mức đường huyết (giả định đơn vị mg/dL). Dataset không nêu rõ đo lúc đói hay ngẫu nhiên.',
    n.source_id = 'src_project';

// ---------- Quan hệ ----------
MATCH (a:Entity {id: 'type1'}), (b:Entity {id: 'diabetes'})
MERGE (a)-[r:SUBTYPE_OF]->(b)
SET r.source_id = 'src_who';
MATCH (a:Entity {id: 'type2'}), (b:Entity {id: 'diabetes'})
MERGE (a)-[r:SUBTYPE_OF]->(b)
SET r.source_id = 'src_who';
MATCH (a:Entity {id: 'gestational'}), (b:Entity {id: 'diabetes'})
MERGE (a)-[r:SUBTYPE_OF]->(b)
SET r.source_id = 'src_who';
MATCH (a:Entity {id: 'sym_polyuria'}), (b:Entity {id: 'diabetes'})
MERGE (a)-[r:SYMPTOM_OF]->(b)
SET r.source_id = 'src_longchau_t2',
    r.note = 'Một trong bốn dấu hiệu điển hình của tăng đường huyết';
MATCH (a:Entity {id: 'sym_polydipsia'}), (b:Entity {id: 'diabetes'})
MERGE (a)-[r:SYMPTOM_OF]->(b)
SET r.source_id = 'src_longchau_t2',
    r.note = 'Một trong bốn dấu hiệu điển hình của tăng đường huyết';
MATCH (a:Entity {id: 'sym_polyphagia'}), (b:Entity {id: 'diabetes'})
MERGE (a)-[r:SYMPTOM_OF]->(b)
SET r.source_id = 'src_longchau_t2',
    r.note = 'Một trong bốn dấu hiệu điển hình của tăng đường huyết';
MATCH (a:Entity {id: 'sym_weight_loss'}), (b:Entity {id: 'diabetes'})
MERGE (a)-[r:SYMPTOM_OF]->(b)
SET r.source_id = 'src_longchau_t2',
    r.note = 'Một trong bốn dấu hiệu điển hình của tăng đường huyết';
MATCH (a:Entity {id: 'sym_fatigue'}), (b:Entity {id: 'diabetes'})
MERGE (a)-[r:SYMPTOM_OF]->(b)
SET r.source_id = 'src_who_afro';
MATCH (a:Entity {id: 'sym_blurred_vision'}), (b:Entity {id: 'diabetes'})
MERGE (a)-[r:SYMPTOM_OF]->(b)
SET r.source_id = 'src_who_afro';
MATCH (a:Entity {id: 'sym_polyuria'}), (b:Entity {id: 'type1'})
MERGE (a)-[r:SYMPTOM_OF]->(b)
SET r.source_id = 'src_vnexpress',
    r.note = 'Thường khởi phát nhanh trong vài ngày đến vài tuần';
MATCH (a:Entity {id: 'sym_polydipsia'}), (b:Entity {id: 'type1'})
MERGE (a)-[r:SYMPTOM_OF]->(b)
SET r.source_id = 'src_vnexpress',
    r.note = 'Thường khởi phát nhanh trong vài ngày đến vài tuần';
MATCH (a:Entity {id: 'sym_polyphagia'}), (b:Entity {id: 'type1'})
MERGE (a)-[r:SYMPTOM_OF]->(b)
SET r.source_id = 'src_vnexpress',
    r.note = 'Thường khởi phát nhanh trong vài ngày đến vài tuần';
MATCH (a:Entity {id: 'sym_weight_loss'}), (b:Entity {id: 'type1'})
MERGE (a)-[r:SYMPTOM_OF]->(b)
SET r.source_id = 'src_vnexpress',
    r.note = 'Thường khởi phát nhanh trong vài ngày đến vài tuần';
MATCH (a:Entity {id: 'sym_fatigue'}), (b:Entity {id: 'type1'})
MERGE (a)-[r:SYMPTOM_OF]->(b)
SET r.source_id = 'src_vnexpress',
    r.note = 'Thường khởi phát nhanh trong vài ngày đến vài tuần';
MATCH (a:Entity {id: 'sym_dry_mouth'}), (b:Entity {id: 'type1'})
MERGE (a)-[r:SYMPTOM_OF]->(b)
SET r.source_id = 'src_vnexpress',
    r.note = 'Thường khởi phát nhanh trong vài ngày đến vài tuần';
MATCH (a:Entity {id: 'sym_itchy_skin'}), (b:Entity {id: 'type1'})
MERGE (a)-[r:SYMPTOM_OF]->(b)
SET r.source_id = 'src_vnexpress',
    r.note = 'Thường khởi phát nhanh trong vài ngày đến vài tuần';
MATCH (a:Entity {id: 'sym_polydipsia'}), (b:Entity {id: 'type2'})
MERGE (a)-[r:SYMPTOM_OF]->(b)
SET r.source_id = 'src_tamanh',
    r.note = 'Ở type 2 triệu chứng thường nhẹ, dễ bị bỏ qua';
MATCH (a:Entity {id: 'sym_polyuria'}), (b:Entity {id: 'type2'})
MERGE (a)-[r:SYMPTOM_OF]->(b)
SET r.source_id = 'src_tamanh',
    r.note = 'Ở type 2 triệu chứng thường nhẹ, dễ bị bỏ qua';
MATCH (a:Entity {id: 'sym_blurred_vision'}), (b:Entity {id: 'type2'})
MERGE (a)-[r:SYMPTOM_OF]->(b)
SET r.source_id = 'src_tamanh',
    r.note = 'Ở type 2 triệu chứng thường nhẹ, dễ bị bỏ qua';
MATCH (a:Entity {id: 'sym_numbness'}), (b:Entity {id: 'type2'})
MERGE (a)-[r:SYMPTOM_OF]->(b)
SET r.source_id = 'src_longchau_t2b',
    r.note = 'Thường là triệu chứng muộn do biến chứng thần kinh';
MATCH (a:Entity {id: 'rf_overweight'}), (b:Entity {id: 'type2'})
MERGE (a)-[r:RISK_FACTOR_FOR]->(b)
SET r.source_id = 'src_who';
MATCH (a:Entity {id: 'rf_age45'}), (b:Entity {id: 'type2'})
MERGE (a)-[r:RISK_FACTOR_FOR]->(b)
SET r.source_id = 'src_longchau_mech';
MATCH (a:Entity {id: 'rf_family'}), (b:Entity {id: 'type2'})
MERGE (a)-[r:RISK_FACTOR_FOR]->(b)
SET r.source_id = 'src_vinmec_early';
MATCH (a:Entity {id: 'rf_inactivity'}), (b:Entity {id: 'type2'})
MERGE (a)-[r:RISK_FACTOR_FOR]->(b)
SET r.source_id = 'src_who';
MATCH (a:Entity {id: 'rf_hypertension'}), (b:Entity {id: 'type2'})
MERGE (a)-[r:RISK_FACTOR_FOR]->(b)
SET r.source_id = 'src_vnexpress';
MATCH (a:Entity {id: 'rf_cvd'}), (b:Entity {id: 'type2'})
MERGE (a)-[r:RISK_FACTOR_FOR]->(b)
SET r.source_id = 'src_vnexpress';
MATCH (a:Entity {id: 'rf_dyslipidemia'}), (b:Entity {id: 'type2'})
MERGE (a)-[r:RISK_FACTOR_FOR]->(b)
SET r.source_id = 'src_vinmec_early';
MATCH (a:Entity {id: 'rf_pcos'}), (b:Entity {id: 'type2'})
MERGE (a)-[r:RISK_FACTOR_FOR]->(b)
SET r.source_id = 'src_vinmec_early';
MATCH (a:Entity {id: 'rf_gdm_history'}), (b:Entity {id: 'type2'})
MERGE (a)-[r:RISK_FACTOR_FOR]->(b)
SET r.source_id = 'src_vnexpress';
MATCH (a:Entity {id: 'gestational'}), (b:Entity {id: 'type2'})
MERGE (a)-[r:INCREASES_RISK_OF]->(b)
SET r.source_id = 'src_who';
MATCH (a:Entity {id: 'prediabetes'}), (b:Entity {id: 'type2'})
MERGE (a)-[r:MAY_PROGRESS_TO]->(b)
SET r.source_id = 'src_vinmec_early',
    r.note = 'Theo Vinmec, nếu không kiểm soát kịp thời thì hơn 50% người tiền tiểu đường tiến triển thành type 2 sau 5–10 năm';
MATCH (a:Entity {id: 'diabetes'}), (b:Entity {id: 'comp_retinopathy'})
MERGE (a)-[r:MAY_LEAD_TO]->(b)
SET r.source_id = 'src_pharmacity_danger';
MATCH (a:Entity {id: 'diabetes'}), (b:Entity {id: 'comp_nephropathy'})
MERGE (a)-[r:MAY_LEAD_TO]->(b)
SET r.source_id = 'src_longchau_comp';
MATCH (a:Entity {id: 'type2'}), (b:Entity {id: 'comp_nephropathy'})
MERGE (a)-[r:MAY_LEAD_TO]->(b)
SET r.source_id = 'src_vinmec_ckd',
    r.note = 'Tiểu đường type 2 là nguyên nhân chính dẫn tới bệnh thận mạn giai đoạn cuối';
MATCH (a:Entity {id: 'diabetes'}), (b:Entity {id: 'comp_neuropathy'})
MERGE (a)-[r:MAY_LEAD_TO]->(b)
SET r.source_id = 'src_pharmacity_danger';
MATCH (a:Entity {id: 'diabetes'}), (b:Entity {id: 'comp_cvd'})
MERGE (a)-[r:MAY_LEAD_TO]->(b)
SET r.source_id = 'src_who',
    r.note = 'Đường huyết cao kéo dài có thể tổn thương tim và mạch máu';
MATCH (a:Entity {id: 'type2'}), (b:Entity {id: 'comp_cvd'})
MERGE (a)-[r:MAY_LEAD_TO]->(b)
SET r.source_id = 'src_longchau_t2';
MATCH (a:Entity {id: 'diabetes'}), (b:Entity {id: 'comp_foot'})
MERGE (a)-[r:MAY_LEAD_TO]->(b)
SET r.source_id = 'src_pharmacity_elderly';
MATCH (a:Entity {id: 'diabetes'}), (b:Entity {id: 'comp_coma'})
MERGE (a)-[r:MAY_LEAD_TO]->(b)
SET r.source_id = 'src_pharmacity_coma',
    r.acute = 'true';
MATCH (a:Entity {id: 'test_hba1c'}), (b:Entity {id: 'diabetes'})
MERGE (a)-[r:DIAGNOSES]->(b)
SET r.source_id = 'src_ada2026',
    r.criterion = '≥ 6.5%',
    r.min_value = 6.5,
    r.unit = '%';
MATCH (a:Entity {id: 'test_fpg'}), (b:Entity {id: 'diabetes'})
MERGE (a)-[r:DIAGNOSES]->(b)
SET r.source_id = 'src_ada2026',
    r.criterion = '≥ 126 mg/dL (7.0 mmol/L), nhịn ăn ≥ 8 giờ',
    r.min_value = 126.0,
    r.unit = 'mg/dL';
MATCH (a:Entity {id: 'test_ogtt'}), (b:Entity {id: 'diabetes'})
MERGE (a)-[r:DIAGNOSES]->(b)
SET r.source_id = 'src_ada2026',
    r.criterion = '≥ 200 mg/dL (11.1 mmol/L) sau 2 giờ, tải 75 g glucose',
    r.min_value = 200.0,
    r.unit = 'mg/dL';
MATCH (a:Entity {id: 'test_rpg'}), (b:Entity {id: 'diabetes'})
MERGE (a)-[r:DIAGNOSES]->(b)
SET r.source_id = 'src_ada2026',
    r.criterion = '≥ 200 mg/dL (11.1 mmol/L) kèm triệu chứng điển hình',
    r.min_value = 200.0,
    r.unit = 'mg/dL';
MATCH (a:Entity {id: 'test_hba1c'}), (b:Entity {id: 'prediabetes'})
MERGE (a)-[r:INDICATES]->(b)
SET r.source_id = 'src_ada2021_t2',
    r.criterion = '5.7–6.4%',
    r.max_value = 6.4,
    r.min_value = 5.7,
    r.unit = '%';
MATCH (a:Entity {id: 'test_fpg'}), (b:Entity {id: 'prediabetes'})
MERGE (a)-[r:INDICATES]->(b)
SET r.source_id = 'src_ada2021_t2',
    r.criterion = '100–125 mg/dL (5.6–6.9 mmol/L)',
    r.max_value = 125.0,
    r.min_value = 100.0,
    r.unit = 'mg/dL';
MATCH (a:Entity {id: 'test_ogtt'}), (b:Entity {id: 'prediabetes'})
MERGE (a)-[r:INDICATES]->(b)
SET r.source_id = 'src_ada2021_t2',
    r.criterion = '140–199 mg/dL (7.8–11.0 mmol/L) sau 2 giờ',
    r.max_value = 199.0,
    r.min_value = 140.0,
    r.unit = 'mg/dL';
MATCH (a:Entity {id: 'adv_diet'}), (b:Entity {id: 'type2'})
MERGE (a)-[r:HELPS_PREVENT]->(b)
SET r.source_id = 'src_who_afro';
MATCH (a:Entity {id: 'adv_activity'}), (b:Entity {id: 'type2'})
MERGE (a)-[r:HELPS_PREVENT]->(b)
SET r.source_id = 'src_who';
MATCH (a:Entity {id: 'adv_weight'}), (b:Entity {id: 'type2'})
MERGE (a)-[r:HELPS_PREVENT]->(b)
SET r.source_id = 'src_who_afro';
MATCH (a:Entity {id: 'adv_no_tobacco'}), (b:Entity {id: 'type2'})
MERGE (a)-[r:HELPS_PREVENT]->(b)
SET r.source_id = 'src_who_afro';
MATCH (a:Entity {id: 'adv_bp_lipid'}), (b:Entity {id: 'comp_cvd'})
MERGE (a)-[r:HELPS_PREVENT]->(b)
SET r.source_id = 'src_pharmacity_danger';
MATCH (a:Entity {id: 'adv_bp_lipid'}), (b:Entity {id: 'comp_nephropathy'})
MERGE (a)-[r:HELPS_PREVENT]->(b)
SET r.source_id = 'src_pharmacity_danger';
MATCH (a:Entity {id: 'adv_foot_care'}), (b:Entity {id: 'comp_foot'})
MERGE (a)-[r:HELPS_PREVENT]->(b)
SET r.source_id = 'src_who_afro';
MATCH (a:Entity {id: 'adv_checkup'}), (b:Entity {id: 'diabetes'})
MERGE (a)-[r:HELPS_DETECT_EARLY]->(b)
SET r.source_id = 'src_who';
MATCH (a:Entity {id: 'adv_screen_35'}), (b:Entity {id: 'type2'})
MERGE (a)-[r:HELPS_DETECT_EARLY]->(b)
SET r.source_id = 'src_diabetesnet';
MATCH (a:Entity {id: 'adv_confirm'}), (b:Entity {id: 'diabetes'})
MERGE (a)-[r:APPLIES_TO]->(b)
SET r.source_id = 'src_ada2023_t4';
MATCH (a:Entity {id: 'adv_not_diagnosis'}), (b:Entity {id: 'diabetes'})
MERGE (a)-[r:APPLIES_TO]->(b)
SET r.source_id = 'src_project';
MATCH (a:Entity {id: 'adv_see_doctor'}), (b:Entity {id: 'type2'})
MERGE (a)-[r:APPLIES_TO]->(b)
SET r.source_id = 'src_longchau_t2';
MATCH (a:Entity {id: 'adv_prediabetes_followup'}), (b:Entity {id: 'prediabetes'})
MERGE (a)-[r:APPLIES_TO]->(b)
SET r.source_id = 'src_diabetesnet';
MATCH (a:Entity {id: 'feat_age'}), (b:Entity {id: 'rf_age45'})
MERGE (a)-[r:RELATES_TO]->(b)
SET r.source_id = 'src_project';
MATCH (a:Entity {id: 'feat_hypertension'}), (b:Entity {id: 'rf_hypertension'})
MERGE (a)-[r:RELATES_TO]->(b)
SET r.source_id = 'src_project';
MATCH (a:Entity {id: 'feat_heart_disease'}), (b:Entity {id: 'rf_cvd'})
MERGE (a)-[r:RELATES_TO]->(b)
SET r.source_id = 'src_project';
MATCH (a:Entity {id: 'feat_bmi'}), (b:Entity {id: 'rf_overweight'})
MERGE (a)-[r:RELATES_TO]->(b)
SET r.source_id = 'src_project';
MATCH (a:Entity {id: 'feat_smoking_history'}), (b:Entity {id: 'adv_no_tobacco'})
MERGE (a)-[r:RELATES_TO]->(b)
SET r.source_id = 'src_project';
MATCH (a:Entity {id: 'feat_hba1c_level'}), (b:Entity {id: 'test_hba1c'})
MERGE (a)-[r:MEASURES]->(b)
SET r.source_id = 'src_project';
MATCH (a:Entity {id: 'feat_blood_glucose_level'}), (b:Entity {id: 'test_fpg'})
MERGE (a)-[r:RELATES_TO]->(b)
SET r.source_id = 'src_project',
    r.note = 'Dataset không nêu rõ đo lúc đói hay ngẫu nhiên nên không so trực tiếp với ngưỡng chẩn đoán được';
MATCH (a:Entity {id: 'feat_blood_glucose_level'}), (b:Entity {id: 'test_rpg'})
MERGE (a)-[r:RELATES_TO]->(b)
SET r.source_id = 'src_project',
    r.note = 'Dataset không nêu rõ đo lúc đói hay ngẫu nhiên nên không so trực tiếp với ngưỡng chẩn đoán được';
