# PROMPT TẠO BÁO CÁO TIỂU LUẬN – `tieuluan_final_05_09_baong.docx`

## 1. Vai trò và mục tiêu

Bạn là trợ lý học thuật có kinh nghiệm biên soạn báo cáo chuyên ngành Trí tuệ nhân tạo, Machine Learning, Deep Learning, Knowledge Graph, RAG và hệ đa agent.

Hãy nghiên cứu **toàn bộ project hiện tại** cùng tất cả tài liệu, mã nguồn, hình ảnh, dữ liệu và thư mục nằm trong `final_tieuluan` (bao gồm thư mục con). Dựa trên những tài liệu thực tế đó, biên soạn lại thành một báo cáo tiểu luận hoàn chỉnh bằng tiếng Việt và xuất thành file Word có tên chính xác:

**`tieuluan_final_05_09_baong.docx`**

Báo cáo phải phản ánh đúng nội dung đã triển khai trong project. Không viết như thể các chức năng, mô hình, thí nghiệm hoặc kết quả đã được thực hiện nếu không có bằng chứng trong mã nguồn, dữ liệu, notebook, tài liệu hoặc kết quả chạy thực tế.

## 2. Quy trình bắt buộc trước khi viết

1. Khảo sát cấu trúc project và toàn bộ `final_tieuluan`, bao gồm thư mục con.
2. Đọc các tài liệu có liên quan: PDF, DOC/DOCX, PPT/PPTX, XLS/XLSX, Markdown, TXT, notebook, mã nguồn, cấu hình, dữ liệu và các báo cáo/kết quả thực nghiệm.
3. Lập bảng kiểm kê nội bộ gồm: tên file, loại file, nội dung chính, chương phù hợp và mức độ tin cậy/khả năng sử dụng.
4. Xác định kiến trúc thực tế của hệ thống, các thành phần đã triển khai, luồng dữ liệu, mô hình/thuật toán, cơ sở dữ liệu, công nghệ và kết quả thực nghiệm có thể kiểm chứng.
5. Đối chiếu thông tin giữa báo cáo cũ, tài liệu thiết kế và mã nguồn. Khi có mâu thuẫn, ưu tiên bằng chứng triển khai mới nhất trong project; ghi rõ điểm chưa thống nhất nếu không thể kết luận.
6. Xây dựng dàn ý chi tiết cho sáu chương bên dưới, sau đó mới biên soạn nội dung.
7. Không bỏ qua tài liệu chỉ vì tên file không rõ ràng. Không tự ý sửa, xóa hoặc di chuyển file nguồn.

Nếu không truy cập được một file hoặc định dạng nào, ghi nhận hạn chế đó và tiếp tục với các nguồn còn lại. Không được tuyên bố đã đọc file khi thực tế không đọc được.

## 3. Bố cục báo cáo bắt buộc

Báo cáo phải được tổ chức theo đúng sáu chương và đúng thứ tự sau:

### CHƯƠNG 1: LỊCH SỬ PHÁT TRIỂN TRÍ TUỆ NHÂN TẠO (AI)

Trình bày quá trình hình thành và phát triển của AI theo các giai đoạn lịch sử. Có thể bao gồm:
- Khái niệm, mục tiêu và phạm vi của trí tuệ nhân tạo.
- Những cột mốc, nhà khoa học và công trình quan trọng.
- Các giai đoạn phát triển, những thời kỳ AI Winter và nguyên nhân.
- Sự phát triển của Expert Systems, Machine Learning, Deep Learning và Generative AI.
- Xu hướng AI hiện đại và mối liên hệ với đề tài hệ thống dự đoán nguy cơ đái tháo đường.

Nội dung lịch sử cần có mốc thời gian và nguồn tham khảo đáng tin cậy; tránh liệt kê sự kiện thiếu kiểm chứng.

### CHƯƠNG 2: CÁC KỸ THUẬT MACHINE LEARNING CƠ BẢN

Trình bày nền tảng và các kỹ thuật ML có liên quan đến project:
- Khái niệm Machine Learning và quy trình xây dựng mô hình.
- Học có giám sát, không giám sát và các dạng học khác nếu phù hợp.
- Tiền xử lý dữ liệu, xử lý giá trị thiếu, mã hóa biến, chuẩn hóa/đưa dữ liệu về cùng thang đo.
- Phân chia tập train/validation/test và các vấn đề rò rỉ dữ liệu.
- Các thuật toán ML thực sự có trong project hoặc tài liệu học tập liên quan.
- Các chỉ số đánh giá phù hợp với bài toán phân loại nguy cơ: accuracy, precision, recall, F1-score, confusion matrix, ROC và AUC.
- Giải thích ý nghĩa, ưu điểm, hạn chế và cách lựa chọn mô hình.

Chỉ mô tả chi tiết thuật toán được sử dụng hoặc có căn cứ liên quan đến project. Có thể giới thiệu thuật toán nền tảng để tạo cơ sở lý thuyết, nhưng phải phân biệt rõ phần lý thuyết chung và phần triển khai thực tế.

### CHƯƠNG 3: MẠNG NƠ-RON TÍCH CHẬP (CNN) VÀ THỊ GIÁC MÁY TÍNH

Trình bày:
- Khái niệm mạng nơ-ron nhân tạo và Deep Learning ở mức cần thiết.
- Tổng quan Computer Vision và các bài toán xử lý ảnh.
- Cấu trúc CNN: convolution, kernel/filter, stride, padding, activation, pooling, flatten và fully connected layer.
- Vai trò của các thành phần, luồng dữ liệu qua CNN và các công thức toán học cần thiết.
- Các kỹ thuật huấn luyện, hàm mất mát và đánh giá nếu có liên quan.
- Liên hệ với project: xác định rõ project có hay không có mô-đun ảnh/CNN. Nếu không có, trình bày đây là kiến thức nền theo chủ đề chương, tuyệt đối không khẳng định CNN đã được tích hợp vào hệ thống.

Có thể dùng sơ đồ kiến trúc CNN hoặc hình minh họa luồng xử lý ảnh để tăng khả năng trực quan.

### CHƯƠNG 4: MẠNG NƠ-RON HỒI QUY (RNN) VÀ XỬ LÝ DỮ LIỆU CHUỖI THỜI GIAN

Trình bày:
- Khái niệm dữ liệu tuần tự và dữ liệu chuỗi thời gian.
- Kiến trúc RNN, trạng thái ẩn và cơ chế xử lý dữ liệu theo thời gian.
- Các vấn đề vanishing gradient/exploding gradient.
- LSTM và GRU: cấu trúc cổng, cơ chế hoạt động, ưu/nhược điểm.
- Tiền xử lý dữ liệu chuỗi, tạo cửa sổ thời gian và cách đánh giá mô hình chuỗi.
- Liên hệ với project: chỉ mô tả RNN/LSTM/GRU là thành phần đã triển khai nếu có bằng chứng trong mã nguồn hoặc kết quả. Nếu không, nêu vai trò tiềm năng của dữ liệu theo thời gian trong theo dõi chỉ số sức khỏe, không gán chức năng chưa tồn tại cho hệ thống.

### CHƯƠNG 5: KNOWLEDGE GRAPH VÀ RETRIEVAL-AUGMENTED GENERATION (RAG)

Trình bày hai công nghệ và cách phối hợp:
- Khái niệm tri thức, Knowledge Graph, node, edge, label, property và quan hệ.
- Cách biểu diễn tri thức, truy vấn và khai thác quan hệ.
- Khái niệm embedding, vector database, semantic search và truy xuất tài liệu.
- Kiến trúc RAG: tiếp nhận câu hỏi, truy xuất, xây dựng ngữ cảnh, sinh câu trả lời và kiểm soát chất lượng.
- So sánh truy xuất vector với truy vấn đồ thị; trường hợp sử dụng và giới hạn.
- Các vấn đề hallucination, chất lượng nguồn tri thức, cập nhật dữ liệu và truy vết nguồn.
- Phân tích đúng cách project sử dụng Neo4j/Knowledge Graph, ChromaDB/vector database, tài liệu tri thức hoặc LLM nếu những thành phần này thực sự có trong project.
- Mô tả luồng xử lý thực tế và vai trò từng thành phần; không tự đặt tên node, quan hệ, collection, schema hoặc pipeline nếu chưa tìm thấy bằng chứng.

### CHƯƠNG 6: HỆ ĐA AGENT DỰ ĐOÁN NGUY CƠ ĐÁI THÁO ĐƯỜNG

Đây là chương trọng tâm, cần dành dung lượng và mức độ phân tích lớn nhất. Dựa trên project thực tế để trình bày:
- Bài toán, mục tiêu, phạm vi và đối tượng sử dụng của hệ thống.
- Kiến trúc tổng thể và lý do lựa chọn mô hình đa agent.
- Khái niệm agent, nhiệm vụ, công cụ, trạng thái, giao tiếp và phối hợp giữa các agent.
- Sơ đồ kiến trúc hệ thống, sơ đồ luồng xử lý và mô tả trách nhiệm từng agent.
- Quy trình tiếp nhận thông tin người dùng, phân tích ý định, trích xuất thực thể/chỉ số sức khỏe, dự đoán nguy cơ, truy xuất tri thức và tạo phản hồi (chỉ giữ những bước thực sự tồn tại).
- Vai trò của mô hình Machine Learning/Deep Learning, LLM, Knowledge Graph, RAG và các cơ sở dữ liệu trong hệ thống.
- Công nghệ và cấu trúc triển khai thực tế: backend, frontend, database, vector database, graph database, mô hình chạy cục bộ, thư viện và cách các thành phần kết nối.
- Mô tả các luồng chính bằng ví dụ minh họa phù hợp với chức năng đã có.
- Kết quả kiểm thử/thực nghiệm: dữ liệu, phương pháp, chỉ số, bảng kết quả và nhận xét. Chỉ đưa số liệu khi tìm thấy trong log, notebook, file kết quả hoặc có thể tái lập từ dữ liệu.
- Đánh giá ưu điểm, hạn chế, rủi ro, vấn đề bảo mật và giới hạn y tế.
- Hướng phát triển tiếp theo.

Đặc biệt lưu ý: đây là hệ thống hỗ trợ dự đoán/đánh giá nguy cơ, không được mô tả như công cụ chẩn đoán hoặc thay thế bác sĩ. Không đưa ra khuyến nghị điều trị cá nhân hóa vượt quá phạm vi bằng chứng của project.

## 4. Trang bìa

Trang đầu tiên phải là **trang bìa tiểu luận**, trình bày trang trọng, cân đối và phù hợp với báo cáo học thuật.

Thông tin bắt buộc:
- Giảng viên: **PGS. Trần Đình Quế**
- Sinh viên thực hiện: **Nguyễn Gia Bảo**
- Mã sinh viên: **B23DCCN075**
- Nhóm: **05**

Tên đề tài nên phản ánh đúng project, có thể dùng tiêu đề theo hướng: **HỆ ĐA AGENT ỨNG DỤNG TRÍ TUỆ NHÂN TẠO TRONG DỰ ĐOÁN NGUY CƠ ĐÁI THÁO ĐƯỜNG**. Điều chỉnh câu chữ nếu tên đề tài chính thức trong tài liệu của project khác.

Nếu tìm thấy tên trường, khoa, bộ môn, học phần hoặc logo chính thức trong tài liệu project thì sử dụng chính xác. Nếu không tìm thấy, không tự bịa; để chỗ trống hoặc dùng placeholder dễ nhận biết để người dùng bổ sung. Không tự đặt ngày nộp nếu chưa có thông tin.

Trang bìa không đánh số trang hiển thị. Sau trang bìa, bố trí mục lục tự động nếu công cụ tạo Word hỗ trợ; có thể thêm danh mục hình, danh mục bảng, danh mục từ viết tắt nếu nội dung đủ nhu cầu.

## 5. Quy chuẩn định dạng Word

Áp dụng thống nhất trên toàn bộ tài liệu:

- Khổ giấy A4, hướng dọc; căn lề cân đối theo chuẩn báo cáo học thuật. Ưu tiên lề trái 3 cm, phải 2 cm, trên 2 cm, dưới 2 cm nếu không có quy định khác trong tài liệu hướng dẫn.
- Font chữ toàn bộ tài liệu: **Times New Roman**.
- Cỡ chữ nội dung thông thường: **13 pt**.
- Hệ thống tiêu đề phân cấp, mỗi cấp chênh nhau 2 pt; tiêu đề nhỏ nhất không được dưới 15 pt. Đề xuất:
  - Tên chương / Heading 1: 21 pt, in hoa, đậm.
  - Heading 2: 19 pt, đậm.
  - Heading 3: 17 pt, đậm.
  - Heading 4: 15 pt, đậm hoặc đậm nghiêng.
- Không dùng cỡ chữ tiêu đề nhỏ hơn 15 pt.
- Nội dung căn đều hai lề (Justify), giãn dòng khoảng 1.3–1.5; khoảng cách đoạn hợp lý, không tạo khoảng trắng quá lớn.
- Dùng Styles của Microsoft Word cho Heading 1–4, Normal, Caption và các thành phần tương ứng; không định dạng tiêu đề chỉ bằng cách bôi đậm thủ công.
- Tiêu đề chương nên bắt đầu ở trang mới. Không để tiêu đề đứng đơn độc ở cuối trang.
- Header/footer gọn gàng; số trang đặt thống nhất, bắt đầu từ phần nội dung sau bìa theo cách trình bày học thuật.
- Bảng có tiêu đề phía trên; hình có chú thích phía dưới. Đánh số hình/bảng theo chương nếu phù hợp (Hình 3.1, Bảng 2.1...). Có dẫn chiếu trong nội dung trước hoặc sau hình/bảng.
- Không để hình, bảng bị vỡ, mờ, méo tỷ lệ hoặc tràn lề.
- Các đoạn mã nguồn nếu cần đưa vào báo cáo phải ngắn, có mục đích giải thích, dùng kiểu trình bày dễ đọc; không chèn tràn lan toàn bộ source code.

## 6. Công thức và phương trình

Đây là yêu cầu bắt buộc:

- Mọi công thức toán học, hàm mất mát, phương trình, biểu thức đánh giá và phép tính quan trọng phải được trình bày dưới dạng **Equation thực sự của Microsoft Word (Office Math / OMML)**, không chỉ gõ công thức dưới dạng văn bản thường hoặc ảnh chụp.
- Công thức phải rõ ràng, đúng ký hiệu, đúng chỉ số trên/dưới, phân số, căn, tổng, tích phân, vector và ma trận khi cần.
- Ưu tiên công thức dạng hiển thị riêng giữa dòng (display equation), căn giữa; đánh số công thức theo chương nếu có nhiều công thức.
- Giải thích các ký hiệu ngay sau công thức.
- Kiểm tra công thức sau khi mở file bằng Microsoft Word hoặc trình đọc tương thích. Nếu công cụ tạo DOCX không tạo được OMML cho một biểu thức, phải ghi nhận và chọn cách chuyển đổi đáng tin cậy; không giả vờ rằng văn bản LaTeX thuần là Word Equation.
- Không đưa công thức sai chỉ để làm báo cáo có vẻ chuyên sâu. Chỉ sử dụng công thức đúng với thuật toán và ngữ cảnh đang mô tả.

## 7. Hình ảnh, sơ đồ và bảng biểu

Có thể và nên sử dụng hình ảnh để làm báo cáo trực quan hơn, nhưng phải bảo đảm:
- Ưu tiên hình/sơ đồ có sẵn trong project, tài liệu `final_tieuluan`, notebook hoặc kết quả chạy thực tế.
- Có thể tự tạo sơ đồ kiến trúc, flowchart, biểu đồ và hình minh họa mới dựa trên thông tin đã xác minh.
- Có thể dùng hình minh họa lý thuyết từ nguồn có uy tín nếu được phép sử dụng và có trích dẫn rõ ràng.
- Không sử dụng ảnh trang trí không liên quan, ảnh chất lượng thấp hoặc ảnh không rõ nguồn.
- Không tạo hình giả lập rồi chú thích như kết quả thực nghiệm thật.
- Mọi hình đều phải có số thứ tự, chú thích, nguồn (nếu lấy từ bên ngoài) và được nhắc đến trong phần nội dung.
- Với sơ đồ hệ thống, tên thành phần và mũi tên phải khớp với kiến trúc triển khai thực tế.
- Với biểu đồ kết quả, ghi rõ nguồn dữ liệu, đơn vị và cách tính.

## 8. Trích dẫn và tài liệu tham khảo

- Trích dẫn các nguồn học thuật, sách, bài báo, tài liệu kỹ thuật và tài liệu chính thức được sử dụng.
- Ưu tiên bài báo khoa học, sách chuyên ngành, tài liệu chính thức của framework/thư viện và nguồn học thuật đáng tin cậy.
- Thông tin lịch sử, thuật toán, công thức và số liệu phải có nguồn phù hợp.
- Dùng một chuẩn trích dẫn nhất quán (ưu tiên IEEE nếu không có yêu cầu khác).
- Mọi tài liệu được trích dẫn trong nội dung phải xuất hiện ở danh mục tài liệu tham khảo và ngược lại.
- Không tạo DOI, tác giả, tên bài báo, URL hoặc thông tin xuất bản giả.
- Nếu tài liệu trong project có trích dẫn sẵn, kiểm tra và chuẩn hóa thay vì sao chép máy móc.
- Phân biệt tài liệu tham khảo học thuật với tài liệu nội bộ/mã nguồn của project.

## 9. Yêu cầu về văn phong và chất lượng học thuật

- Viết bằng tiếng Việt học thuật, rõ ràng, tự nhiên, mạch lạc.
- Giải thích thuật ngữ tiếng Anh ở lần xuất hiện đầu tiên; có thể ghi thuật ngữ tiếng Anh trong ngoặc.
- Không viết kiểu ghi chú rời rạc, không lặp ý để kéo dài báo cáo.
- Mỗi chương có phần dẫn nhập, nội dung được chia mục logic và phần tiểu kết.
- Có sự liên kết giữa lý thuyết ở Chương 1–5 và ứng dụng trong Chương 6.
- Phân biệt rõ: (1) kiến thức nền tảng, (2) thiết kế đề xuất, (3) phần đã triển khai, (4) kết quả đã kiểm chứng.
- Không phóng đại độ chính xác, hiệu quả hoặc mức độ hoàn thiện của hệ thống.
- Không sao chép nguyên văn dài từ nguồn. Diễn giải bằng lời của mình và trích dẫn nguồn.
- Không tự thêm nội dung ngoài phạm vi chỉ để tăng số trang. Ưu tiên chiều sâu, độ chính xác và tính nhất quán.

## 10. Kiểm tra trước khi bàn giao

Trước khi xuất file cuối cùng, tự kiểm tra:

1. Đúng tên file `tieuluan_final_05_09_baong.docx`.
2. Có trang bìa và đủ sáu chương theo đúng tên, thứ tự yêu cầu.
3. Nội dung bám sát project và các file trong `final_tieuluan`.
4. Không có chức năng, mô hình, số liệu, kết quả hoặc nguồn tham khảo bị bịa.
5. Font Times New Roman được áp dụng nhất quán; nội dung 13 pt; tiêu đề theo thang 21/19/17/15 pt.
6. Công thức quan trọng là Word Equation/OMML, hiển thị đúng.
7. Hình/bảng có chú thích, đánh số và nguồn phù hợp.
8. Mục lục, số trang, tiêu đề, bảng biểu và tham chiếu không bị lỗi.
9. Không có trang trắng bất thường, dòng chữ tràn lề, hình bị méo, tiêu đề mồ côi hoặc bảng bị cắt khó đọc.
10. Mở thử DOCX sau khi tạo và kiểm tra các trang đầu, trang có công thức, trang có hình/bảng và trang cuối.

Sau khi hoàn tất, chỉ bàn giao file DOCX cuối cùng cùng một bản tóm tắt ngắn về:
- Các nguồn chính đã sử dụng.
- Những nội dung được lấy từ triển khai thực tế.
- Những phần còn thiếu dữ liệu hoặc phải để placeholder.
- Các kiểm tra định dạng đã thực hiện.

**Không thay thế yêu cầu tạo file Word bằng cách chỉ trả về nội dung văn bản trong cuộc trò chuyện.**
