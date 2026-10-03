# Kế hoạch xây dựng RetailMind

Hệ thống gợi ý sản phẩm và phân tích khách hàng cho portfolio AI và Data Science

Người thực hiện: Thái Trọng Đăng
Ngày lập kế hoạch: 03 tháng 10 năm 2026
Phiên bản kế hoạch: 1.2 bản Markdown bàn giao cho Codex, tích hợp GitHub xuyên suốt

RetailMind là ứng dụng phân tích giao dịch bán lẻ và gợi ý sản phẩm cho từng khách hàng. Project giúp bạn học và thực hành toàn bộ quy trình từ dữ liệu gốc, SQL, mô hình recommendation đến đánh giá, API và demo. Sản phẩm chính là một ứng dụng có thể chạy lại, cùng bằng chứng về chất lượng mô hình và cách bạn xử lý giới hạn dữ liệu.

Bài toán chính được chốt: tại một thời điểm t, sử dụng thông tin có trước t để xếp hạng tối đa 10 sản phẩm mà một khách hàng có thể mua trong 30 ngày tiếp theo. Danh sách có thể chứa sản phẩm từng mua vì đây là bài toán dự đoán mua lại và khám phá sản phẩm. Điểm xếp hạng của mô hình không phải xác suất mua hàng.

Kế hoạch dự kiến 12 tuần ở mức 10 đến 15 giờ mỗi tuần. Có thể hoàn thành khoảng 10 tuần nếu phần nền tảng đã vững. Nhịp học và kết quả kiểm tra quyết định tốc độ thực tế. Khi gặp phần mới, ưu tiên hiểu và hoàn thành tiêu chí của giai đoạn trước khi chuyển tiếp.

Thành phẩm gồm ứng dụng demo, mã nguồn có hướng dẫn chạy, ba mô hình so sánh, báo cáo đánh giá theo thời gian, model card, video giới thiệu và case study tiếng Anh. Mục tiêu là chứng minh năng lực giải quyết bài toán và giải thích lựa chọn kỹ thuật; kết quả mô hình sẽ được đo trong quá trình làm.

### Cách sử dụng kế hoạch

Đọc mục 1 đến 4 để hiểu sản phẩm và phạm vi. Dùng mục 5 đến 13 làm đặc tả kỹ thuật khi xây dựng. Mục 14 đến 18 hướng dẫn kiểm thử, triển khai, học tập và bàn giao. Mục 24 quy định quy trình GitHub từ tuần đầu. Các mục cuối giúp chuẩn bị portfolio và tra cứu nguồn.

Mỗi buổi làm việc sẽ đi theo trình tự: hiểu mục tiêu, học kiến thức cần dùng, giải một ví dụ nhỏ, tự triển khai, kiểm tra kết quả và ghi lại điều đã học. Kế hoạch này mô tả việc cần làm; các bài giảng và code sẽ được triển khai từng bước sau đó.

## 0 Hướng dẫn cho Codex khi nhận project

### 0.1 Mục tiêu của người học

Người học là Thái Trọng Đăng, đang xây portfolio để xin internship trong AI và Data Science. Trình độ lập trình đã khá ổn và sẵn sàng học công nghệ mới. Mục tiêu gồm sản phẩm hoạt động, kết quả có thể kiểm chứng và khả năng tự giải thích, sửa, mở rộng project.

Hãy làm việc như một người hướng dẫn kỹ thuật: giải thích bằng tiếng Việt, giữ thuật ngữ tiếng Anh kèm định nghĩa khi xuất hiện lần đầu. Code, tên biến, docstring, giao diện và README của sản phẩm dùng tiếng Anh. Giải thích trực quan trước, sau đó đi vào cơ chế, ví dụ, phần toán cần thiết và implementation.

### 0.2 Phạm vi của tài liệu và trạng thái khởi đầu

Đây là đặc tả sản phẩm và lộ trình học, không phải báo cáo một ứng dụng đã hoàn thành. Khi bắt đầu lần đầu, trạng thái chỉ là có kế hoạch; chưa có model được huấn luyện, metrics, API, UI hoặc hosting được xác nhận. Các CLI, routes, cấu trúc thư mục và ngân sách hiệu năng bên dưới là thiết kế cần triển khai và kiểm tra.

Nếu workspace đã có code, hãy đọc các chỉ dẫn áp dụng trong repository, kiểm tra cấu trúc, dependencies và phần thực sự đã hoàn thành. Tái sử dụng công việc phù hợp, không giả định repository trống hoặc đánh dấu một việc hoàn thành chỉ vì nó xuất hiện trong kế hoạch.

Khi người học yêu cầu bắt đầu mà chưa chỉ định giai đoạn, bắt đầu Tuần 1 Buổi 1. Nếu có tiến độ cũ, tiếp tục từ checkpoint thực tế gần nhất. Chỉ triển khai phần của buổi hoặc giai đoạn đang học, để người học có thể kiểm tra và tự làm; không tự hoàn thành toàn bộ 12 tuần trong một lượt.

### 0.3 Trình tự cho từng buổi học

1. Nêu mục tiêu, đầu vào, đầu ra và điều kiện hoàn thành của buổi.
2. Giải thích kiến thức cần dùng, lý do chọn cách làm và những lỗi có thể ảnh hưởng kết quả.
3. Dùng ví dụ nhỏ có thể tính bằng tay trước khi thao tác trên toàn bộ dataset.
4. Triển khai một phần đủ nhỏ để đọc hiểu; nêu file nào thay đổi và vai trò của chúng.
5. Chạy kiểm tra phù hợp và giải thích kết quả. Nếu chưa chạy được, ghi rõ nguyên nhân.
6. Giao một bài biến thể để người học tự làm, kèm tiêu chí kiểm tra.
7. Ghi checkpoint, kiến thức đã học, vấn đề còn mở và bước tiếp theo.

Không cần hỏi lại để quyết định những chi tiết kỹ thuật thông thường đã nằm trong phạm vi buổi học. Chỉ hỏi khi thông tin còn thiếu làm thay đổi đáng kể lựa chọn, chẳng hạn workspace thực tế, môi trường không tương thích hoặc thời gian học khác với giả định. Khi người học đưa bài làm hoặc lỗi, giải thích và sửa trong đúng giai đoạn đang thực hiện.

### 0.4 Những yêu cầu phải giữ xuyên suốt

- Bài toán chính là top 10 sản phẩm cho cửa sổ 30 ngày; mua lại được phép. Score của mô hình không được gọi là xác suất mua.
- Mọi model, mapping, feature, mô tả sản phẩm, RFM, popularity, candidate set và evidence phải phù hợp cutoff của snapshot.
- Tách nhãn tương lai khỏi service recommendation. Replay dùng bundle được build từ đúng phần lịch sử, không dùng model cuối kỳ để dự đoán quá khứ.
- Dùng cùng protocol khi so sánh mô hình. Chọn cấu hình bằng validation rồi khóa trước đánh giá test.
- Giữ đúng định nghĩa cohort và cách xử lý nhãn trống, sản phẩm mới, khách mới trong mục 10.
- Không tự điền CustomerID thiếu bằng một khách chung. Không dùng giao dịch hủy ở tương lai để sửa snapshot quá khứ.
- Phân biệt raw bất biến, dữ liệu analytics và tương tác dùng train. Quy tắc loại dòng phải có lý do và số đếm đối chiếu.
- Giữ scope V1. Chỉ thêm V2 khi người học yêu cầu hoặc khi đã hoàn thành V1 và thống nhất hướng tiếp theo.
- Chỉ ghi kết quả đo được. Không tạo metrics, benchmark, số tăng doanh thu, URL demo hoặc claim đã chạy tests khi chưa có bằng chứng.
- Pin dependencies sau khi kiểm tra môi trường và đọc API của phiên bản cài thực tế. Không coi một phiên bản xuất hiện trong ví dụ là mặc định mới nhất.

### 0.5 Theo dõi tiến độ trong repository

Khi bắt đầu triển khai, tạo hoặc cập nhật `docs/progress.md` và `docs/learning_log.md`. Đây là các file cần làm trong project tương lai, không phải những file đã có cùng bản kế hoạch này.

Mỗi checkpoint trong progress ghi ngày, tuần hoặc buổi, mục tiêu, việc đã làm, file thay đổi, lệnh thực sự đã chạy, kết quả kiểm tra, kiến thức cần ôn và nhiệm vụ tiếp theo. Thêm Issue, branch, commit và PR liên quan khi đã có; ghi riêng trạng thái commit local, push và merge. Phân biệt `planned`, `in_progress`, `done` và `blocked`.

Learning log ghi giải thích bằng lời của người học, bài tự làm, lỗi và cách sửa. Ghi quyết định quan trọng ở `docs/decisions.md`, kèm lý do, lựa chọn khác và bằng chứng validation nếu liên quan mô hình. Giữ code có thể chạy bằng pipeline, không phụ thuộc trạng thái notebook ngầm.

### 0.6 Công việc đầu tiên Codex cần thực hiện

- Đọc toàn bộ kế hoạch và kiểm tra workspace hiện có.
- Xác định hệ điều hành, Python, công cụ môi trường và tài nguyên thực tế nếu có thể kiểm tra trực tiếp; không đoán cấu hình máy từ lịch sử hội thoại.
- Tóm tắt bài toán 30 ngày, granularity của dữ liệu và đầu ra mà buổi đầu cần đạt.
- Hướng dẫn hoặc thiết lập môi trường riêng trong phạm vi project, kiểm tra import tối thiểu.
- Chuẩn bị cấu trúc ban đầu, problem statement và kế hoạch kiểm tra file nguồn.
- Kiểm tra Git repository và remote hiện có; hướng dẫn kết nối hoặc tạo repository GitHub cho RetailMind trong tuần đầu theo mục 24. Không khởi tạo repository lồng trong một repository đang có.
- Kết thúc buổi bằng bài tự giải thích về dòng giao dịch, hóa đơn, khách hàng và cutoff, cùng checkpoint rõ ràng.

Buổi đầu chưa yêu cầu huấn luyện ALS, tạo toàn bộ UI hoặc triển khai hosting. Công việc tiếp theo phụ thuộc kết quả thực tế của buổi đầu và mức hiểu của người học.

### 0.7 Yêu cầu GitHub bắt buộc

Người học yêu cầu làm project bằng GitHub. Dùng GitHub từ tuần 1 để lưu mã nguồn, theo dõi công việc và trình bày portfolio; học commit, push, branch, Issue, Pull Request và CI ngay khi có nhu cầu thực tế. Áp dụng quy trình ở mục 24 cho các giai đoạn sau.

Bản kế hoạch hiện tại chưa tạo repository GitHub và chưa có URL repository. Khi bắt đầu triển khai, kiểm tra thông tin thực tế; chỉ hỏi tài khoản hoặc repository đích nếu chưa xác định được từ yêu cầu và workspace. Không tự suy đoán username, URL hoặc trạng thái đăng nhập. Nếu chưa kết nối được, vẫn hoàn thành phần local của buổi học và ghi rõ bước GitHub còn thiếu.

Không gom toàn bộ project thành một lần upload cuối kỳ. Mỗi thay đổi có phạm vi rõ ràng, lời giải thích và kiểm tra tương ứng. Chỉ báo đã push, tạo Issue, mở PR, merge hoặc có CI thành công sau khi thực sự kiểm chứng hành động đó. Giải thích thao tác Git để người học có thể tự làm lại.


## 1 Mục tiêu và giới hạn của project

### 1.1 Người dùng và quyết định cần hỗ trợ

Người dùng chính là người phân tích dữ liệu hoặc quản lý một cửa hàng trực tuyến. Họ muốn hiểu khách hàng đã mua gì, sản phẩm nào nên xuất hiện trong danh sách gợi ý và hệ thống có hoạt động tốt khi kiểm tra trên dữ liệu tương lai hay không.

Người xem portfolio cần nhanh chóng thấy được sản phẩm hoạt động, sau đó có thể kiểm tra phương pháp, dữ liệu, kết quả và mã nguồn. Vì vậy, giao diện có đường dẫn xem kết quả đánh giá và các ví dụ sai ngay trong ứng dụng.

### 1.2 Mục tiêu học tập

- Giải thích được sự khác nhau giữa một dòng giao dịch, một hóa đơn, một khách hàng và một tương tác khách hàng với sản phẩm.
- Viết truy vấn SQL có JOIN, GROUP BY và hàm cửa sổ; chuyển logic xử lý từ notebook thành module có thể chạy lại.
- Hiểu dữ liệu phản hồi ngầm, ma trận thưa, cosine similarity và factorization trước khi dùng thư viện.
- Xây một quy trình đánh giá có mốc thời gian rõ ràng; phát hiện dữ liệu bị rò rỉ từ tương lai.
- Đọc chỉ số ranking, phân tích lỗi và chọn mô hình theo bằng chứng.
- Đưa mô hình vào API, xử lý đầu vào không hợp lệ, lưu metadata và đóng gói demo.

### 1.3 Những giới hạn cần trình bày khi phỏng vấn

Dữ liệu lịch sử mua hàng không cho biết tất cả sản phẩm khách hàng đã nhìn thấy. Không mua một món hàng chưa chứng minh khách hàng không thích món đó. Đánh giá offline chỉ đo mức độ khớp với các giao dịch quan sát được; muốn đo tác động tới doanh thu cần thử nghiệm với người dùng thực tế. [S8]

Danh mục đã xuất hiện trong dữ liệu chỉ là cách xấp xỉ sản phẩm biết được tại thời điểm dự đoán. Project không có bằng chứng về tồn kho, ngày ngừng bán hoặc khả năng giao hàng của cửa hàng. Giao diện phải dùng từ phù hợp, chẳng hạn danh mục đã biết, thay vì khẳng định còn hàng.

## 2 Phạm vi phát triển theo phiên bản

| Phiên bản | Phạm vi | Mốc dự kiến |
| --- | --- | --- |
| V0 | Dữ liệu sạch, phân tích SQL, dashboard cơ bản, gợi ý phổ biến và quy trình đánh giá | Cuối tuần 4 |
| V1 | Ba mô hình, fallback, giải thích, replay hai mốc, API, sáu trang demo, kiểm thử và tài liệu portfolio | Cuối tuần 12 |
| V2 | Chọn một hướng cải tiến có kiểm chứng như đặc trưng văn bản hoặc weighting theo thời gian | Sau V1 |

V1 là phạm vi dùng để nộp portfolio. V2 chỉ bắt đầu sau khi V1 chạy ổn định và có báo cáo kết quả. Không yêu cầu deep learning để đạt V1; việc lựa chọn mô hình dựa trên dữ liệu và mục tiêu ranking.

Phần chưa đưa vào V1 gồm thanh toán, quản lý kho, marketing tự động, dự báo churn, customer lifetime value, dự báo nhu cầu và chatbot. Những bài toán này có nhãn và tiêu chí đánh giá riêng. Giữ bài toán recommendation làm trọng tâm giúp bạn hoàn thành một sản phẩm có thể giải thích đầy đủ.

Project bắt đầu từ dữ liệu công khai, phục vụ demo chỉ đọc. Môi trường chạy dự kiến là máy cá nhân dùng CPU. Cấu hình máy, thời gian huấn luyện và chi phí hosting sẽ được đo hoặc xác minh tại giai đoạn triển khai.

## 3 Danh sách tính năng và tiêu chí hoàn thành

### F01 Nạp và kiểm tra dữ liệu gốc

Đọc tất cả sheet dữ liệu, chuẩn hóa tên cột, lưu hash của file và số dòng mỗi sheet. Đầu ra gồm manifest dữ liệu, bản Parquet và báo cáo kiểm tra schema. Lần chạy lại cùng file và cấu hình phải tạo ra cùng số dòng và cùng định danh nguồn.

Mỗi dòng có raw_row_id từ file, sheet và số dòng gốc. Không dùng InvoiceNo làm khóa dòng vì một hóa đơn có nhiều sản phẩm và có thể có nhiều dòng cùng sản phẩm.

### F02 Báo cáo chất lượng và quy tắc làm sạch

Đếm giá trị thiếu, bản ghi trùng đáng ngờ, ngày lỗi, số lượng âm, giá không hợp lệ, giao dịch hủy và dòng điều chỉnh. Mỗi dòng được gắn loại xử lý cùng lý do. Báo cáo thể hiện số lượng trước và sau từng bước, giữ được đường truy ngược về nguồn.

Hoàn thành khi tổng các nhóm xử lý đối chiếu được với dữ liệu đầu vào, cùng bộ ví dụ nhỏ chứng minh từng quy tắc. Quy tắc riêng cho dữ liệu phân tích và dữ liệu recommendation được ghi rõ.

### F03 Dashboard hoạt động bán lẻ

Hiển thị giá trị giao dịch bán dương, điều chỉnh đủ điều kiện ghi nhận, số hóa đơn bán, khách hàng định danh và sản phẩm. Có lọc theo khoảng thời gian và quốc gia trong phạm vi snapshot. Các biểu đồ chính gồm diễn biến theo thời gian, sản phẩm phổ biến và phân phối giá trị hóa đơn.

Hoàn thành khi các số tổng khớp truy vấn SQL, mỗi KPI có định nghĩa và đơn vị GBP. Giá trị giao dịch sau điều chỉnh không được mô tả là lợi nhuận hoặc doanh thu kế toán đã kiểm toán.

### F04 Hồ sơ khách hàng và phân nhóm RFM

Hiển thị lịch sử mua, ngày mua gần nhất, số hóa đơn và tổng giá trị mua dương trước cutoff. RFM là Recency, Frequency và Monetary, lần lượt mô tả độ gần của lần mua, tần suất mua và giá trị mua. Dùng phân nhóm theo quy tắc hoặc quantile có thể giải thích, chưa cần clustering.

Hoàn thành khi thay đổi snapshot không làm hồ sơ dùng dữ liệu tương lai. Tên nhóm phản ánh số đo; tránh gán nhãn giá trị đạo đức hoặc khẳng định khách sắp rời bỏ khi chưa có mô hình đó.

### F05 Gợi ý cá nhân hóa và so sánh mô hình

Chọn khách hàng và snapshot để nhận top 10 từ Popularity, ItemCF hoặc ALS. Hiển thị thứ hạng, mã sản phẩm, mô tả biết được trước cutoff và nhãn đã mua trước đó. Không lặp sản phẩm trong một danh sách. Nếu danh mục có ít hơn 10 sản phẩm hợp lệ, trả số lượng thực tế.

Hoàn thành khi danh sách tuân thủ candidate set, quy tắc mua lại và snapshot. Không so sánh trực tiếp score số học của các mô hình vì thang đo khác nhau; so sánh bằng thứ hạng và metrics.

### F06 Giải thích gợi ý bằng bằng chứng

Popularity hiển thị lý do từ mức phổ biến trong khoảng lịch sử đã cấu hình. ItemCF hiển thị sản phẩm khách đã mua có đóng góp vào điểm similarity. ALS dùng phép explain của thư viện hoặc một phân tích đóng góp được kiểm chứng. [S3]

Giải thích là thông tin về cơ chế mô hình, không khẳng định nguyên nhân tâm lý của khách hàng. Hoàn thành khi lý do truy được tới dữ liệu trước cutoff và không có câu giải thích tự tạo không có bằng chứng.

### F07 Gợi ý dự phòng cho khách hàng chưa có lịch sử

Một chế độ khách mới được hiển thị riêng. Khách mới hoặc lịch sử không đủ theo ngưỡng đã chọn trên validation sẽ nhận popularity fallback. Câu trả lời ghi rõ reason_code và loại mô hình thực sự phục vụ.

Hoàn thành khi ID nhập sai được phân biệt với chế độ khách mới. CustomerID không tồn tại trả lỗi tra cứu; ứng dụng không âm thầm coi lỗi gõ ID là khách mới.

### F08 Xem lại dự đoán theo thời gian

Người dùng chọn một trong hai mốc đã huấn luyện. Màn hình trước tiên chỉ hiện lịch sử trước cutoff và danh sách gợi ý. Nút xem kết quả mở những sản phẩm được mua trong 30 ngày tiếp theo cùng chỉ số cho ví dụ đó.

Hoàn thành khi danh sách gợi ý đã được tạo từ snapshot trước khi mở kết quả. Khóa cache gồm snapshot và model_version. V1 không cho chọn một ngày bất kỳ rồi sử dụng mô hình cuối kỳ để giả lập quá khứ.

### F09 So sánh mô hình và phân tích lỗi

Hiển thị Recall@10, NDCG@10, HitRate@10, độ phủ danh mục, số khách được đánh giá và thời gian phục vụ. Có kết quả riêng cho khách ít lịch sử, nhiều lịch sử và phân nhóm RFM trước cutoff.

Hoàn thành khi mọi mô hình dùng cùng user cohort, candidate set, nhãn và quy tắc mua lại. Giao diện phân biệt validation dùng chọn mô hình với test dùng báo cáo cuối.

### F10 Khám phá sản phẩm

Tra cứu theo mã hoặc từ khóa mô tả, xem lịch sử phổ biến và sản phẩm tương tự của ItemCF. Dữ liệu không có ảnh sản phẩm đáng tin cậy; giao diện dùng mã, tên và biểu đồ. Hoàn thành khi tên và số liệu phù hợp snapshot.

### F11 API và trạng thái dịch vụ

API cung cấp truy vấn hồ sơ, gợi ý, sản phẩm tương tự, danh sách snapshot và kết quả đánh giá. Có kiểm tra tham số, mã lỗi rõ ràng và endpoint health. Model được nạp khi dịch vụ khởi động, không huấn luyện trong mỗi request.

### F12 Xuất kết quả và quan sát hoạt động

Cho tải CSV danh sách gợi ý hoặc bảng metrics kèm snapshot, cutoff, model_version và quy tắc đánh giá. Log có request_id, chế độ phục vụ, latency, số kết quả và lỗi. Không tạo CTR hoặc conversion từ lượt bấm demo vì đây không phải cửa hàng thật.

### F13 Chạy lại và bàn giao portfolio

Có lệnh chuẩn bị dữ liệu, huấn luyện, đánh giá và khởi động ứng dụng. Manifest lưu version thư viện, cấu hình, seed, hash dữ liệu và mappings. Hoàn thành khi người khác có thể làm theo README trên môi trường sạch và nhận các chỉ số tương đương trong sai số số học được công bố.

## 4 Giao diện và hành trình sử dụng

### 4.1 Sáu trang trong ứng dụng

| Trang | Thành phần chính | Hành động người dùng |
| --- | --- | --- |
| Overview | KPI, biểu đồ thời gian, quốc gia và sản phẩm | Chọn snapshot và lọc dữ liệu |
| Customers | Tra cứu, RFM, lịch sử và top 10 | Xem khách hàng và so sánh gợi ý |
| Historical Replay | Lịch sử, dự đoán và kết quả tương lai | Chọn mốc rồi mở kết quả |
| Products | Tìm kiếm và sản phẩm tương tự | Khám phá một mã sản phẩm |
| Model Evaluation | Metrics, cohorts, cấu hình và lỗi | So sánh mô hình trên cùng split |
| Data Quality | Chất lượng, quy tắc và dòng loại bỏ | Kiểm tra nguồn gốc số liệu |

Thanh bên có snapshot selector. Mỗi trang ghi rõ thời điểm dữ liệu và phạm vi đang xem. Trang replay và evaluation dùng snapshot cố định; bộ lọc giao diện không được tự thay đổi dữ liệu huấn luyện. Giao diện chính dùng tiếng Anh để đưa vào portfolio; kế hoạch và các buổi học dùng tiếng Việt với thuật ngữ tiếng Anh đi kèm.

Các trạng thái cần thiết gồm đang tải, không có dữ liệu, khách không tồn tại, khách mới, API lỗi và model chưa sẵn sàng. Biểu đồ có nhãn trục, đơn vị và bảng số tương ứng. Không chỉ dùng màu để phân biệt đúng và sai.

### 4.2 Luồng demo dành cho người xem portfolio

1. Mở Overview để hiểu dữ liệu, phạm vi thời gian và bài toán.
2. Chọn một khách hàng trong Customers để xem lịch sử và gợi ý.
3. Chuyển mô hình để thấy danh sách khác nhau và bằng chứng đi kèm.
4. Mở Historical Replay, tạo danh sách rồi xem các giao dịch tương lai.
5. Mở Model Evaluation để kiểm tra kết quả tổng thể, cohort và ví dụ sai.
6. Mở Data Quality để thấy quy tắc xử lý và đường truy nguyên dữ liệu.

Chọn ba ví dụ trình bày gồm khách có lịch sử phong phú, khách ít dữ liệu và chế độ khách mới. Chọn ví dụ dựa trên các nhóm đã định nghĩa, ghi rõ cách chọn; bảng kết quả tổng thể giúp tránh chỉ trình bày ví dụ đẹp.

## 5 Dữ liệu và quy tắc nghiệp vụ

### 5.1 Nguồn và các trường gốc

Nguồn là Online Retail II của UCI, gồm 1.067.371 dòng trong giai đoạn 01 tháng 12 năm 2009 đến 09 tháng 12 năm 2011. Dữ liệu thuộc nhà bán lẻ trực tuyến tại Anh, có nhiều khách mua sỉ, có giá trị thiếu và được cấp phép CC BY 4.0. [S1]

| Trường | Ý nghĩa | Kiểu lưu đề xuất |
| --- | --- | --- |
| InvoiceNo | Mã hóa đơn | VARCHAR |
| StockCode | Mã sản phẩm | VARCHAR |
| Description | Mô tả | VARCHAR |
| Quantity | Số lượng | BIGINT |
| InvoiceDate | Thời điểm giao dịch | TIMESTAMP |
| UnitPrice | Giá đơn vị GBP | DECIMAL |
| CustomerID | Mã khách hàng | VARCHAR nullable |
| Country | Quốc gia | VARCHAR |

Tên cột thực tế của từng sheet sẽ được kiểm tra rồi ánh xạ về schema trên. Giữ ID dạng chuỗi, tránh biến mã sản phẩm thành số hoặc giữ hậu tố .0 do Excel. Dữ liệu nguồn không công bố múi giờ trong schema; dùng thời gian gốc và ghi rõ timezone chưa xác định, không tự gán UTC.

### 5.2 Tách dữ liệu bán và điều chỉnh

Định nghĩa sale hợp lệ cho recommendation: có customer_id, mã sản phẩm hợp lệ, thời gian parse được, số lượng dương, giá dương và không thuộc hóa đơn hủy. Mã hóa đơn bắt đầu bằng C hoặc c là dấu hiệu cancellation theo tài liệu UCI. [S1]

Dữ liệu điều chỉnh và số lượng âm được lưu riêng. Với dashboard, tính tổng giá trị bán dương và tổng giá trị điều chỉnh đủ điều kiện, rồi trình bày cả hai thành phần. Không tự nối một giao dịch hủy tới một dòng bán nếu không có khóa liên kết đáng tin cậy.

Dữ liệu sale thiếu CustomerID vẫn có thể dùng cho thống kê giao dịch, nhưng không đưa vào recommendation cá nhân hóa. Thiếu ID không được thay bằng một ID chung, vì sẽ trộn hành vi nhiều người thành một người.

### 5.3 Các trường hợp cần xử lý riêng

- Giá bằng không hoặc âm: tách nhóm kiểm tra; không đưa vào tín hiệu mua hàng trả tiền của V1.
- Mã phí, điều chỉnh hoặc phi hàng hóa: xác định bằng quy tắc minh bạch từ dữ liệu huấn luyện và schema; giữ trong raw để đối chiếu.
- Mô tả thiếu: lấy mô tả gần nhất biết được trước cutoff của cùng mã; nếu không có thì hiển thị mã. Không điền mô tả từ tương lai.
- Dòng giống nhau: phân biệt nạp trùng file với dòng lặp trong nguồn. Loại nạp trùng bằng raw_row_id; dòng nguồn lặp chưa rõ giữ trong raw, đánh dấu và phân tích độ nhạy trước khi quyết định.
- Khách mua lượng rất lớn: giữ đặc điểm mua sỉ; giảm ảnh hưởng lượng hàng trong weighting thay vì xóa outlier chỉ vì số lớn.
- Giao dịch hủy ở tương lai: không dùng để sửa lại tín hiệu đã có ở snapshot quá khứ. V1 học từ sale dương quan sát được, ghi rõ giới hạn chưa mô hình hóa hoàn trả.

Các tham số, whitelist hoặc ngưỡng học từ dữ liệu phải chỉ dùng phần lịch sử tại cutoff. Quy tắc schema cố định có thể áp dụng cho toàn bộ nguồn, nhưng kiểm thử và điều chỉnh mô hình không dùng nhãn test.

## 6 Kiến trúc và công nghệ

### 6.1 Quy trình xử lý offline

File gốc được kiểm tra và chuyển sang Parquet. DuckDB truy vấn dữ liệu để tạo snapshot khách hàng, sản phẩm và tương tác. Từ snapshot, pipeline huấn luyện tạo model bundle. Evaluator độc lập sử dụng model bundle và dữ liệu 30 ngày tiếp theo để tạo báo cáo.

Model bundle chứa model, mapping ID, cấu hình, thời điểm cutoff, version preprocessing và metadata nguồn. Các bundle validation và test được lưu riêng để historical replay dùng đúng mô hình.

### 6.2 Quy trình phục vụ ứng dụng

Streamlit gọi FastAPI. API đọc model bundle và snapshot chỉ đọc, tạo danh sách, áp dụng chính sách fallback, ghi log rồi trả dữ liệu. UI hiển thị kết quả và bằng chứng. Outcome của replay nằm ở evaluator hoặc endpoint outcome riêng, không được đưa vào service tạo gợi ý.

Giai đoạn V0 có thể gọi trực tiếp Python service để học nhanh. V1 chuyển cùng logic sang API, không viết hai bản thuật toán khác nhau. Công nghệ và vai trò được đề xuất như sau.

| Công nghệ | Vai trò | Thời điểm học |
| --- | --- | --- |
| Python và môi trường riêng | Logic, cấu hình và pipeline | Tuần 1 |
| Git và GitHub | Lịch sử thay đổi, Issues, branches, PR và portfolio | Từ tuần 1, dùng xuyên suốt |
| Pandas và NumPy | Làm sạch, biến đổi và ví dụ ma trận | Tuần 2 |
| Parquet và DuckDB | Lưu dữ liệu và phân tích SQL | Tuần 2 đến 3 |
| SciPy sparse | Ma trận user item thưa | Tuần 4 đến 5 |
| implicit | ItemCF hoặc ALS và serving | Tuần 5 đến 6 |
| Plotly và Streamlit | Dashboard, replay và bảng kết quả | V0 tuần 4 rồi hoàn thiện tuần 9 đến 10 |
| FastAPI và Pydantic | API, validation và schema | Tuần 8 |
| pytest và GitHub Actions | Kiểm thử có ý nghĩa và CI | Bắt đầu tuần 3 |
| Docker | Môi trường demo có thể chạy lại | Tuần 11 |

Chốt phiên bản thư viện sau khi thử cài trên máy bạn và lưu lockfile. Không chọn số version chỉ vì xuất hiện trong một ví dụ. implicit có các mô hình phản hồi ngầm và hỗ trợ xử lý CPU; FastAPI cung cấp hướng dẫn API theo từng bước. [S2] [S4]

### 6.3 Phạm vi hạ tầng

V1 dùng Parquet cùng DuckDB cho dữ liệu và truy vấn chỉ đọc. Log có thể ghi JSONL; không cần triển khai database server từ đầu. Khởi đầu trên mẫu nhỏ để debug, sau đó chạy đủ dữ liệu trước báo cáo cuối. Tránh tạo ma trận user item dense.

Mục tiêu tài nguyên ban đầu là môi trường CPU, tham khảo máy có 8 GB RAM trở lên; đây là giả định cần kiểm tra, không phải cấu hình đã benchmark. Nếu thiếu RAM, giảm cột đọc, chuyển Excel một lần sang Parquet và xử lý theo partition.

## 7 Thiết kế bảng và artifact

| Bảng hoặc artifact | Khóa đề xuất | Nội dung chính |
| --- | --- | --- |
| raw_transactions | raw_row_id | Giá trị gốc, file hash, sheet, row index |
| sales | raw_row_id | Sale hợp lệ, line_value, customer nullable cho analytics |
| adjustments | raw_row_id | Cancellation và điều chỉnh kèm reason_code |
| customer_snapshot | snapshot_id và customer_id | RFM, quốc gia đã biết, lịch sử tóm tắt |
| product_snapshot | snapshot_id và stock_code | Mô tả đã biết, first_seen, độ phổ biến |
| interaction_snapshot | snapshot_id và customer_id và stock_code | Số hóa đơn, last_purchase, weight |
| recommendation_requests | request_id | Model, snapshot, chế độ, latency và lỗi |
| recommendation_items | request_id và rank | Sản phẩm, score, evidence và fallback |
| evaluation_runs | run_id và model_name và cohort | Split, metrics, số khách và cấu hình |

sales và adjustments truy ngược về raw_transactions. interaction_snapshot tham chiếu hai bảng snapshot bằng khóa ghép để tránh trộn thời điểm. recommendation_items tham chiếu request; model artifact chứa mappings riêng cho từng snapshot.

Nhãn đánh giá được lưu ở artifact riêng với cutoff và cửa sổ outcome. Service recommendation không tải nhãn này. Snapshot không phải một bảng được sửa tại chỗ: mỗi snapshot có ID và manifest bất biến.

Metadata tối thiểu của model gồm snapshot_id, train_cutoff, label_horizon_days, candidate_policy, repeat_purchase_policy, preprocessing_version, source_hash, user_mapping_hash, item_mapping_hash, params, seed và package_versions. Ghi cả dataset time và thời gian model thực sự được build.

## 8 Phân tích dữ liệu và tạo đặc trưng

### 8.1 Những câu hỏi phải trả lời bằng dữ liệu

- Bao nhiêu dòng dùng được cho thống kê và bao nhiêu dòng dùng được cho recommendation?
- Tần suất mua, số sản phẩm mỗi khách và giá trị hóa đơn phân bố như thế nào?
- Một nhóm nhỏ khách mua sỉ có chi phối lượng hàng hoặc giá trị giao dịch không?
- Tỷ lệ mua lại sản phẩm so với mua sản phẩm mới là bao nhiêu theo từng giai đoạn?
- Mức phổ biến thay đổi theo tháng và quốc gia thế nào?
- Có bao nhiêu sản phẩm và khách lần đầu xuất hiện trong mỗi cửa sổ tương lai?
- Ma trận tương tác thưa đến mức nào và có bao nhiêu khách chỉ mua một lần?

Mỗi kết luận EDA phải có truy vấn hoặc code tạo được bảng số và biểu đồ. Phân tích trên training hoặc validation để thiết kế mô hình; test chỉ dùng ở đánh giá cuối. Khi trình bày toàn bộ dữ liệu để mô tả nguồn, ghi rõ đó là mô tả tổng quan và không dùng để học ngưỡng.

### 8.2 Đặc trưng khách hàng

Recency là số ngày từ lần mua dương gần nhất đến cutoff. Frequency là số hóa đơn bán khác nhau trước cutoff, không phải số dòng. Monetary là tổng giá trị mua dương theo định nghĩa phân tích; giá trị sau điều chỉnh được hiển thị riêng nếu dùng.

Tạo thêm số sản phẩm khác nhau, số ngày hoạt động và average order value. Quantile RFM được fit trên khách trước cutoff; ngưỡng của snapshot được lưu để tái hiện. RFM phục vụ dashboard và cohort, không mặc định đưa toàn bộ vào ALS.

### 8.3 Đặc trưng tương tác

Baseline dùng số hóa đơn khác nhau mà khách mua một sản phẩm. Số lượng mua rất lớn trong một hóa đơn không được coi tương đương rất nhiều lần thể hiện sở thích. So sánh binary interaction với log weighting của số hóa đơn trên validation.

Theo thư viện được chọn, chuyển weighting sang confidence đúng một lần và ghi rõ công thức. Không nhân alpha đồng thời trong tiền xử lý và trong model nếu mục tiêu chỉ là một lần scale. Đây là chi tiết sẽ được kiểm tra bằng ma trận nhỏ. [S3]

## 9 Các mô hình sẽ xây dựng

### 9.1 Popularity làm mốc so sánh

Xếp hạng theo số khách định danh khác nhau đã mua sản phẩm trong khoảng lịch sử. Khởi đầu dùng 90 ngày trước cutoff, rồi chỉ điều chỉnh cửa sổ trên validation. Ràng buộc cùng candidate set với các mô hình khác. Dùng StockCode làm tie breaker để chạy lại có thứ tự ổn định.

Bạn sẽ tự viết thuật toán này để hiểu baseline, độ phổ biến và sự khác biệt giữa số đơn, số khách, số lượng và giá trị bán. Một baseline tốt là điều kiện cần để biết mô hình phức tạp có đem lại cải thiện hay không.

### 9.2 Item based collaborative filtering

Xây ma trận tương tác khách hàng với sản phẩm, tìm similarity giữa cột sản phẩm và lấy tổng đóng góp từ các món khách đã mua. Bắt đầu cosine similarity trên ví dụ nhỏ, sau đó dùng ma trận thưa và giữ top neighbors để tiết kiệm bộ nhớ.

Để bài toán cho phép mua lại có ý nghĩa, không xóa sản phẩm từng mua khỏi danh sách. Khi tính similarity, loại tự tương đồng của sản phẩm để tránh score bị thống trị bởi đường chéo. So sánh thêm một baseline mua lại đơn giản nếu tỷ lệ mua lại cao; giữ nó trong báo cáo để hiểu ALS có tốt hơn việc chỉ lặp lịch sử không.

Tham số thử ban đầu gồm số hàng xóm 20 hoặc 50 và binary hoặc log weighting. Mỗi thay đổi phải được ghi lại, không mở một search quá lớn trước khi kiểm tra quy trình.

### 9.3 ALS cho phản hồi ngầm

ALS học vector khách hàng và vector sản phẩm sao cho tích vô hướng phản ánh mức phù hợp theo tín hiệu và confidence đã định nghĩa. Bạn sẽ học vector, tích vô hướng, regularization, hàm mục tiêu và cách cập nhật luân phiên trên một ví dụ nhỏ trước khi dùng thư viện. [S2] [S3]

Search khởi đầu được giới hạn ở khoảng 6 cấu hình, chẳng hạn factors 32 hoặc 64 cùng vài giá trị regularization. Cố định seed và ngân sách iterations ban đầu; chỉ mở rộng sau khi biết model có học tín hiệu hữu ích. Giá trị cụ thể sẽ điều chỉnh theo thời gian huấn luyện đo trên máy.

Với nhiệm vụ mua lại, đặt filter_already_liked_items=False khi dùng API tương ứng của implicit. Candidate set được giới hạn theo snapshot. Kiểm tra mapping và thứ tự trục: hàng là khách, cột là sản phẩm theo API hiện hành của thư viện đã pin. [S3]

### 9.4 Chọn mô hình phục vụ và fallback

Chọn mô hình chính bằng NDCG@10 trên validation, đồng thời xem Recall@10, cohort ít lịch sử, độ phủ và latency. Nếu các mô hình gần tương đương, ưu tiên phương án đơn giản và dễ giải thích hơn. Không đặt điều kiện bắt buộc ALS phải thắng.

Routing dùng mô hình đã chọn cho khách có lịch sử phù hợp, popularity cho khách mới hoặc trường hợp score không tạo đủ danh sách. Ngưỡng ít lịch sử được chọn trên validation. Với phần còn thiếu, bổ sung popularity đã loại các món đang có trong danh sách. Ghi rõ từng món được tạo bởi mô hình hay fallback.

## 10 Quy trình đánh giá theo thời gian

### 10.1 Hai mốc đầu tiên

| Mốc | Lịch sử được dùng | Cửa sổ nhãn |
| --- | --- | --- |
| Validation | Trước 2011 09 01 00 00 | Từ 2011 09 01 đến trước 2011 10 01 |
| Test | Trước 2011 11 01 00 00 | Từ 2011 11 01 đến trước 2011 12 01 |

Đây là hai mốc dự kiến sau khi kiểm tra file gốc. Mỗi cửa sổ có 30 ngày. Dữ liệu cuối nguồn phải đủ để quan sát trọn cửa sổ nhãn. Các cửa sổ dùng quy ước đóng đầu, mở cuối. Thời gian là thời gian gốc của dataset.

Fit mô hình validation bằng dữ liệu trước mốc validation, chọn tham số và chính sách tại đó. Sau khi khóa lựa chọn, fit mô hình test bằng toàn bộ dữ liệu trước mốc test, kể cả dữ liệu từng thuộc validation. Sau đó đánh giá test một lần. Không tiếp tục tune theo kết quả test; nếu làm phiên bản tiếp theo, ghi rõ test cũ đã được xem và thiết kế kiểm tra mới.

V1 replay chỉ hỗ trợ các mốc có model bundle tương ứng. Một mô hình huấn luyện tới tháng 11 không được dùng để dự đoán lại tháng 9. Điều này áp dụng cả với popularity, similarity, mô tả sản phẩm, mapping và ngưỡng RFM. [S7]

### 10.2 Định nghĩa người dùng và sản phẩm đánh giá

Candidate set của cutoff là các sản phẩm hàng hóa hợp lệ có sale định danh trước cutoff, vì V1 chỉ có dữ liệu giao dịch để suy ra danh mục. Mọi mô hình xếp hạng trên cùng tập này, gồm sản phẩm khách từng mua. Không dùng việc sản phẩm có bán trong tương lai để quyết định được đưa vào danh sách ở quá khứ.

Tập khách nhận gợi ý là tất cả khách có lịch sử hợp lệ trước cutoff. Tập tính ranking metrics gồm khách trong tập trên có ít nhất một sale dương trong 30 ngày tới; đây là cohort có quay lại mua trong dữ liệu. Báo rõ số khách không quay lại và không gán recall bằng 0 cho trường hợp nhãn trống.

Nhãn chính của mỗi khách là tập mã sản phẩm khác nhau đã mua trong cửa sổ tương lai, kể cả sản phẩm chưa nằm trong candidate set. Recall chính dùng toàn bộ tập này làm mẫu số để không che giấu nhu cầu với sản phẩm mới. Báo thêm recall trên phần nhãn thuộc candidate set và tỷ lệ nhãn có thể được gợi ý. Người chỉ mua sản phẩm chưa biết vẫn được tính ở metric chính với hit bằng 0.

Khách lần đầu xuất hiện trong cửa sổ tương lai được báo riêng về số lượng và giới hạn dữ liệu. Không biến mốc xuất hiện đầu tiên thành bằng chứng rằng ta đã biết họ ở cutoff. Chế độ khách mới trong demo là một chức năng fallback; chưa có đủ dữ liệu để kiểm chứng tác động thực tế khi họ ghé cửa hàng lần đầu.

### 10.3 Chỉ số và cách tổng hợp

| Chỉ số | Định nghĩa dùng trong project |
| --- | --- |
| Recall@10 | Số sản phẩm gợi ý đúng chia số sản phẩm khác nhau trong nhãn |
| NDCG@10 | Chất lượng thứ tự top 10 với relevance nhị phân và giảm trọng số theo vị trí |
| HitRate@10 | Tỷ lệ khách có ít nhất một món gợi ý xuất hiện trong nhãn |
| Catalog coverage | Số sản phẩm khác nhau được gợi ý chia kích thước candidate set |
| Label availability | Tỷ lệ sản phẩm trong nhãn đã biết trước cutoff |
| Serving coverage | Tỷ lệ khách yêu cầu hợp lệ nhận được danh sách hợp lệ |
| Fallback rate | Tỷ lệ request phải dùng fallback toàn phần hoặc bổ sung |
| Latency p50 và p95 | Thời gian phục vụ giữa và gần cuối phân phối request |

Recall và NDCG tính theo từng khách rồi lấy trung bình, để khách nhiều giao dịch không chi phối hoàn toàn. Với relevance nhị phân, IDCG của NDCG dùng số positive tương ứng với định nghĩa metric chính hoặc metric có thể gợi ý; không dùng lẫn hai định nghĩa. Tự tính metric trên ví dụ nhỏ rồi đối chiếu implementation phù hợp. [S6]

V1 xếp hạng trên toàn bộ candidate set, không dùng sampled negatives để làm metric trông tốt hơn. Nếu tương lai cần sampling để tiết kiệm tính toán, phải báo riêng protocol và không so trực tiếp với bảng V1.

### 10.4 Cohort và độ chắc chắn của kết quả

Phân nhóm theo số hóa đơn trước cutoff: một hóa đơn, hai đến năm hóa đơn và trên năm hóa đơn. Ngưỡng này là mô tả cohort ban đầu; ngưỡng routing có thể khác và phải chọn bằng validation. Phân tích thêm nhóm RFM và tỷ lệ mua lại.

Nếu thời gian cho phép, bootstrap theo khách để ước lượng khoảng tin cậy và dùng chênh lệch theo cặp giữa hai mô hình trên cùng khách. Không tuyên bố cải thiện mạnh khi chênh lệch nhỏ và không ổn định. V1 chỉ có hai mốc; muốn kết luận độ bền qua mùa cần thêm các mốc lịch sử độc lập.

## 11 API và hợp đồng đầu ra

| Endpoint đề xuất | Vai trò | Kiểm tra quan trọng |
| --- | --- | --- |
| GET /health | Kiểm tra dịch vụ và model đã nạp | Model thiếu trả 503 |
| GET /snapshots | Liệt kê mốc được hỗ trợ | Chỉ bundle đã build thành công |
| GET /customers/{id} | Hồ sơ và lịch sử tại snapshot | ID không tồn tại trả 404 |
| GET /recommendations | Top k cho khách có lịch sử | k từ 1 đến 20 và snapshot hợp lệ |
| GET /recommendations/new | Popularity cho khách mới | Chế độ fallback được ghi rõ |
| GET /products/{id}/similar | Sản phẩm tương tự | ID sản phẩm và snapshot hợp lệ |
| GET /evaluations | Metrics đã tính offline | Split và model_version rõ ràng |
| GET /replay/outcomes | Nhãn tương lai cho replay | Endpoint tách khỏi recommendation |

Response recommendation có request_id, snapshot_id, train_cutoff, model_name, model_version, k_requested, k_returned, mode, reason_code và danh sách items. Mỗi item có stock_code, rank, score, description_as_of_cutoff, repeat_item, source_model và evidence. Score chỉ là điểm ranking, không đặt tên purchase_probability.

Tham số không hợp lệ trả lỗi validation 422; snapshot không tồn tại trả 404. Sự cố model hoặc dữ liệu trả 503 cùng request_id để tra log. /health có thể kết hợp readiness cho V1; nếu triển khai lớn mới tách liveness và readiness.

Không cho người xem tải model pickle hoặc nạp file tùy ý vào dịch vụ public. File dữ liệu do pipeline quản lý offline. Health response không tiết lộ đường dẫn máy hoặc secret. FastAPI và Pydantic dùng schema thống nhất để UI xử lý đúng. [S4]

## 12 Cấu trúc mã nguồn và lệnh chạy

| Đường dẫn dự kiến | Trách nhiệm |
| --- | --- |
| README.md | Bài toán, demo, kết quả và cách chạy |
| RetailMind_Codex_Plan.md | Kế hoạch sản phẩm và hướng dẫn học từng bước |
| .gitignore | Quy tắc loại dữ liệu gốc, secrets, môi trường và artifact lớn |
| .github/ISSUE_TEMPLATE/ | Mẫu công việc và báo lỗi có tiêu chí hoàn thành |
| .github/pull_request_template.md | Bài toán, thay đổi, kiểm tra và Issue liên quan |
| .github/workflows/ci.yml | Lint và test fixture trên Pull Request và main |
| pyproject.toml và lockfile | Dependencies và phiên bản môi trường |
| configs/project.yaml | Quy tắc dữ liệu, split và model |
| notebooks/ | Khảo sát và ví dụ học có ghi chú |
| src/retailmind/data/ | Nạp nguồn, schema và làm sạch |
| src/retailmind/features/ | RFM, snapshots và interactions |
| src/retailmind/models/ | Popularity, ItemCF, ALS và routing |
| src/retailmind/evaluation/ | Labels, ranking metrics và cohorts |
| src/retailmind/api/ | Routes, schema và model loader |
| app/ | Streamlit pages và API client |
| tests/ | Fixtures nhỏ, invariants và API checks |
| reports/ | Metrics, model card và data quality |
| artifacts/ | Bundle build được và manifest |
| docs/ | Architecture, data dictionary và decision log |

Notebook phục vụ khám phá và học tập. Pipeline cuối không phụ thuộc việc chạy cell thủ công theo một thứ tự ngầm. Code từ notebook được chuyển sang module, có đầu vào, đầu ra và cấu hình rõ ràng.

Các lệnh CLI mục tiêu gồm prepare, build-snapshot, train, evaluate và serve. Đây là đặc tả sẽ triển khai, chưa phải các lệnh đã có. Ví dụ giao diện lệnh dự kiến là retailmind train --snapshot validation --model als. README sẽ ghi lệnh thực tế sau khi project được xây.

Git lưu code, configs, báo cáo tổng hợp và một fixture nhỏ. Dữ liệu gốc, môi trường, cache và model lớn được đưa vào ignore. Công bố cách tải nguồn, hash file và cách build artifact; không bắt người khác nhận một file notebook đã chạy sẵn mà không có pipeline. Repository local được kết nối GitHub ngay từ tuần 1; các file GitHub được thêm theo nhu cầu ở mục 24, workflow CI bắt đầu tuần 3.

## 13 Kiểm thử và tiêu chí chất lượng kỹ thuật

### 13.1 Các kiểm thử cần thiết

- Ranh giới thời gian: dòng ở cutoff không vào training; dòng đúng cuối cửa sổ không vào nhãn.
- Snapshot: thêm một sale tương lai không thay đổi features, candidate set hoặc recommendations của snapshot cũ.
- Cancellation: hủy xảy ra sau cutoff không sửa tín hiệu của quá khứ; dòng điều chỉnh không bị biến thành sở thích âm tùy tiện.
- Mapping: chuyển ID sang index rồi ngược lại phải khớp, đúng kích thước ma trận và bundle.
- Metric: một danh sách hoàn hảo, một danh sách sai, một danh sách đảo thứ tự và nhãn trống được xử lý đúng.
- Recommendation: không trùng sản phẩm, không ngoài candidate set, repeat policy thống nhất và fallback không lặp.
- API: tham số sai, ID thiếu, chế độ khách mới và model thiếu đều có response đúng hợp đồng.
- Pipeline: nạp lại cùng file không tăng số dòng; chạy end to end trên fixture cho kết quả ổn định.

Các test kiểm chứng sai sót có thể làm hỏng kết luận hoặc demo. Không đặt mục tiêu coverage phần trăm tùy ý làm thay tiêu chí đúng. CI chạy lint và test fixture; huấn luyện đầy đủ chạy riêng để tránh chi phí không cần thiết.

### 13.2 Hiệu năng và khả năng phục vụ

Ngân sách ban đầu đề xuất là p95 dưới một giây cho request top 10 sau khi model đã nạp, trên máy và tải đo được công bố. Đây là mục tiêu thiết kế cần benchmark, chưa phải kết quả. Mốc kiểm tra ban đầu gồm 200 request đại diện sau warmup; ghi riêng thời gian API, UI và khởi động lạnh.

Nếu chưa đạt, kiểm tra nạp model lặp, truy vấn không cần thiết, cache và matrix operations trước khi thêm hạ tầng. Lưu RAM, CPU, phiên bản, số khách và số sản phẩm cùng báo cáo. Demo phải có thông báo khi đang khởi động hoặc gặp lỗi mạng.

Cache key phải chứa snapshot_id, model_version, preprocessing_version, khách và k; không cache chung giữa các mốc. Streamlit có các cơ chế caching khác nhau cho dữ liệu và tài nguyên; cách dùng sẽ được kiểm tra theo tài liệu hiện hành. [S5]

## 14 Triển khai và vận hành demo

### 14.1 Các bước triển khai

Chạy được local trước, rồi đóng gói bằng Docker. Có thể dùng hai service UI và API trong cùng cấu hình compose. Snapshot và model được mount chỉ đọc; log ghi tới nơi có quyền ghi. Một gói model bundle gọn giúp người xem khởi động nhanh.

Public demo chỉ đọc và có danh sách khách mẫu cùng chế độ khách mới. Không cho thao tác làm thay đổi dữ liệu nguồn hoặc huấn luyện lại. Thiết lập giới hạn request đơn giản nếu hosting cần, và chỉ cho CORS từ UI thực tế.

Chọn nơi hosting khi biết dung lượng artifact, RAM và cold start. Xác minh giá và chính sách tại thời điểm deploy. Dùng local miễn phí để phát triển; chi phí hosting là hạng mục tùy chọn, chưa đưa ra con số cố định. Có video demo và hướng dẫn local để portfolio vẫn xem được khi hosting ngủ hoặc hết hạn.

### 14.2 Nhật ký và tái huấn luyện

V1 log thời gian, lỗi, model version và tỷ lệ fallback để mô tả hoạt động phần mềm. Vì nguồn là dữ liệu lịch sử cố định, nhật ký không được mô tả như drift hoặc hành vi khách hàng thực tế đang thay đổi.

Huấn luyện lại bằng lệnh offline có cấu hình. Bundle mới chỉ được đưa vào phục vụ sau kiểm tra schema, mapping, smoke test và báo cáo validation. Bundle cũ giữ lại để quay về khi cần. Không cập nhật model trong một request người xem gửi.

### 14.3 Quyền riêng tư và nguồn dữ liệu

Demo dùng CustomerID công khai của dataset hoặc alias nhất quán, không gán tên, số điện thoại hay email. Ghi nguồn và giấy phép dữ liệu trong README. Không dùng dữ liệu cá nhân thật nếu chưa có quyền sử dụng; phần này sẽ được xem lại nếu mở rộng sang cửa hàng thực tế.

## 15 Lộ trình học và xây dựng trong 12 tuần

### Tuần 1 Chốt bài toán và môi trường

Học: môi trường Python riêng, dependencies, Git và GitHub, working tree, staging, commit, remote, branch và Pull Request; cấu trúc package, config và sự khác nhau giữa classification với ranking. Ôn những phần bạn đã biết bằng bài ngắn thay vì học lại toàn bộ.

Làm: tạo hoặc dùng repository GitHub của RetailMind, kết nối workspace, chuẩn bị README và .gitignore, đưa bản kế hoạch vào repo rồi commit/push phần khởi tạo. Tạo Issue cho problem statement và thử một branch, PR nhỏ. Chuẩn bị môi trường, tải nguồn đúng phiên bản, kiểm tra schema và viết problem statement một trang. Xác định cutoff, cửa sổ 30 ngày, mua lại, candidate set và giới hạn dữ liệu.

Bài tự làm: giải thích vì sao một dòng Excel không đồng nghĩa một đơn hàng; mô tả bằng lời đầu vào và đầu ra tại một cutoff. Tự sửa một đoạn README qua branch và PR, rồi giải thích commit khác push ở đâu.

Đầu ra: môi trường cài được, data manifest đầu tiên, project skeleton và mục tiêu rõ ràng; có URL repository GitHub, code đã push và một PR nhỏ đã tự review/merge. Chuyển bước khi bạn có thể giải thích bài toán và tự lặp lại workflow GitHub. Nếu remote đang bị chặn, ghi rõ checkpoint local và việc kết nối còn thiếu.

### Tuần 2 Nạp và làm sạch dữ liệu

Học: DataFrame, dtypes, missing values, datetime, khóa dòng, Decimal, Parquet và khác biệt giữa dữ liệu raw với dữ liệu dùng phân tích.

Làm: đọc các sheet, chuẩn hóa schema, lưu raw Parquet, viết các bộ lọc và bảng đối chiếu số dòng. Tạo fixture gồm sale, hủy, thiếu ID, giá lỗi và dòng lặp để kiểm chứng quy tắc.

Bài tự làm: xử lý 15 đến 20 dòng ví dụ bằng tay, rồi so sánh với pipeline. Giải thích vì sao dùng ID chung cho khách thiếu định danh gây sai.

Đầu ra: module prepare, data quality report và tests quy tắc. Chuyển bước khi mỗi dòng bị loại có lý do và pipeline chạy lại không nhân đôi dữ liệu.

### Tuần 3 SQL và phân tích khách hàng

Học: SELECT, GROUP BY, JOIN, CTE, window functions, granularity, average order value, RFM và quantile.

Làm: viết truy vấn KPI, bảng theo tháng, hồ sơ khách, độ phổ biến sản phẩm và tỷ lệ mua lại. Fit các ngưỡng RFM trên snapshot. Viết năm nhận xét có bảng hoặc biểu đồ hỗ trợ. Thêm GitHub Actions chạy lint và các tests fixture đã có trên PR và main; hiểu log và sửa lỗi CI trước khi merge.

Bài tự làm: tính frequency từ số hóa đơn rồi so với đếm dòng; chỉ ra khi nào hai số khác nhau. Giải thích average của dòng sản phẩm khác average của hóa đơn.

Đầu ra: SQL queries, EDA notebook có kết luận, customer_snapshot và workflow CI đầu tiên chạy thành công. Chuyển bước khi KPI đối chiếu được, bạn có thể giải thích từng mẫu số và tìm được nguyên nhân một lỗi CI.

### Tuần 4 Labels và baseline

Học: phản hồi ngầm, mốc dự đoán, data leakage, baseline, top k, relevance, recall và NDCG.

Làm: build snapshot validation, labels 30 ngày, candidate set và popularity. Viết evaluator dùng full candidate set. Tính chỉ số trên ví dụ nhỏ trước khi chạy dữ liệu thật. Tạo dashboard V0 một trang với KPI và bảng gợi ý phổ biến, gọi Python service trực tiếp; học Streamlit tối thiểu ở bước này.

Bài tự làm: lấy ba khách và khoảng mười sản phẩm, tự tạo top 5 rồi tính recall và thứ tự đúng. Thêm giao dịch tương lai và chứng minh snapshot cũ không đổi.

Đầu ra: V0 có baseline, metrics đầu tiên và báo cáo cohort; tạo GitHub Release v0.1.0 từ commit đã kiểm tra, kèm cách chạy và giới hạn V0. Chuyển bước khi protocol có thể chạy lại và không đọc tương lai khi tạo gợi ý.

### Tuần 5 ItemCF và ma trận thưa

Học: vector, dot product, chuẩn vector, cosine similarity, CSR matrix, sparsity và nearest neighbors.

Làm: tự triển khai similarity trên ma trận nhỏ, rồi chuyển sang sparse implementation. Lưu top neighbors, viết recommendation và evidence. Kiểm tra repeat policy cùng diagonal similarity.

Bài tự làm: tính cosine giữa hai sản phẩm bằng tay; giải thích vì sao sản phẩm phổ biến dễ được gợi ý. Ước lượng RAM cho ma trận dense và sparse.

Đầu ra: ItemCF có bảng so sánh validation và ví dụ giải thích. Chuyển bước khi bạn truy được đóng góp từ lịch sử tới điểm sản phẩm.

### Tuần 6 ALS và lựa chọn tham số

Học: latent factors, factorization, confidence, regularization, overfitting, validation và hyperparameters.

Làm: dùng implicit sau khi hiểu ví dụ nhỏ, thử số cấu hình giới hạn, lưu seed và kết quả. Kiểm tra shape, mapping, alpha và filtering theo API đã pin. So sánh theo cùng protocol với Popularity và ItemCF.

Bài tự làm: giải thích tại sao score ALS không phải xác suất; phân biệt khách chưa mua với khách không thích. Mô tả vai trò regularization bằng một ví dụ dữ liệu ít.

Đầu ra: ba mô hình, bảng experiment và lựa chọn tạm thời trên validation. Chuyển bước khi bạn giải thích được lựa chọn và không đòi mô hình phức tạp phải thắng.

### Tuần 7 Phân tích lỗi và khóa mô hình

Học: cohort analysis, selection bias, cold start, paired comparison và khoảng tin cậy cơ bản.

Làm: phân tích theo lịch sử và RFM, chọn routing/fallback, kiểm tra các ví dụ sai. Khóa cấu hình rồi fit snapshot test và chạy đánh giá cuối. Lưu bundle của cả validation và test.

Bài tự làm: viết năm lỗi với nguyên nhân có thể kiểm tra; xác định một giới hạn do thiếu dữ liệu và một giới hạn có thể sửa bằng mô hình.

Đầu ra: final evaluation, error analysis và model card bản đầu. Chuyển bước khi bảng metrics kèm cohort size, nhãn và candidate policy đủ rõ để người khác kiểm tra.

### Tuần 8 API và service

Học: HTTP, JSON, REST, type hints, Pydantic, dependency loading, error handling và cách tách inference với evaluation.

Làm: model loader, endpoints, response schemas, fallback và logs. Nạp bundle một lần, thêm API tests và đo thời gian phục vụ thử.

Bài tự làm: giải thích request và response của một gợi ý; thử ID sai, k sai và snapshot chưa có. Chứng minh service recommendation không tải nhãn tương lai.

Đầu ra: API local ổn định với tài liệu tự sinh. Chuyển bước khi lỗi dự kiến có phản hồi đúng và model không bị fit lại trong request.

### Tuần 9 Dashboard và hồ sơ khách

Học: Streamlit state, API client, caching, biểu đồ và thiết kế thông tin.

Làm: Overview, Customers, Products và Data Quality. Có snapshot selector, KPI definitions, bảng lịch sử, gợi ý cùng evidence và chế độ khách mới.

Bài tự làm: đổi snapshot liên tục để thử cache; kiểm tra trường hợp empty và network error. Giải thích từng KPI bằng một câu.

Đầu ra: bốn trang kết nối API với dữ liệu thật. Chuyển bước khi UI không hiển thị số từ các snapshot khác nhau trong một màn hình.

### Tuần 10 Replay và trình bày kết quả

Học: đánh giá offline trong sản phẩm, so sánh ranking và cách chọn ví dụ đại diện.

Làm: Historical Replay và Model Evaluation. Thêm mở outcome, đánh dấu đúng/sai, phân tích cohort và tải CSV. Đối chiếu metric hiển thị với artifact evaluator.

Bài tự làm: kể lại một ví dụ dự đoán sai từ lịch sử tới kết quả; chỉ ra vì sao việc nhìn outcome trước không được làm thay đổi danh sách.

Đầu ra: đầy đủ sáu trang và luồng demo có thể trình bày. Chuyển bước khi một người khác sử dụng được ứng dụng mà không cần bạn sửa dữ liệu thủ công.

### Tuần 11 Kiểm thử và đóng gói

Học: integration tests, CI, Docker, cấu hình môi trường, model versioning và latency.

Làm: hoàn thành invariants, mở rộng CI fixture đã có từ tuần 3, Docker compose và benchmark. Thử khởi động từ môi trường sạch, kiểm tra bundle thiếu và timeout. Kiểm tra phiên bản Actions và dependencies đang dùng. Chọn hosting sau khi đo tài nguyên; triển khai nếu điều kiện phù hợp.

Bài tự làm: xóa cache và chạy lại theo README; chỉ ra những file cần để khôi phục một snapshot.

Đầu ra: ứng dụng chạy bằng quy trình được ghi rõ, benchmark có môi trường và video dự phòng. Chuyển bước khi người khác tái hiện được mà không cần notebook state của bạn.

### Tuần 12 Hoàn thiện portfolio và luyện phỏng vấn

Học: viết case study kỹ thuật, model card và trình bày tradeoff có bằng chứng.

Làm: README tiếng Anh, hình giao diện, architecture, data dictionary, final report, video hai đến ba phút và mô tả CV dùng số đo thực tế. Hoàn tất Issues của V1, tạo Release v1.0.0 và chuẩn bị link repository để đưa vào CV/GitHub profile.

Bài tự làm: trình bày project trong ba phút, rồi trả lời các câu hỏi về leakage, baseline, cold start, metrics và serving. Thực hiện một thay đổi nhỏ khi không có hướng dẫn từng dòng.

Đầu ra: V1 dùng được trong portfolio. Chuyển bước khi mọi claim trên README và CV truy được tới code hoặc báo cáo, không có số thành tích minh họa bị ghi như kết quả thật.

## 16 Cách hướng dẫn bạn trong từng buổi học

Mỗi tuần dự kiến hai buổi học chính và thời gian tự triển khai. Một buổi khoảng 60 đến 90 phút cho kiến thức và ví dụ; thời gian code tự làm phụ thuộc bài. Nội dung có thể chia nhỏ thêm nếu một khái niệm cần đào sâu.

Trình tự mỗi buổi gồm mục tiêu đầu ra, giải thích trực quan, thuật ngữ và cơ chế, ví dụ nhỏ tính được bằng tay, code tối thiểu, bài tự làm, kiểm tra, rồi nối lại vào RetailMind. Sau đó bạn ghi learning log với điều hiểu được, lỗi gặp, cách sửa và một câu hỏi còn mở.

Mức độ kiến thức có ba tầng. Tầng một là hiểu bằng lời và ví dụ. Tầng hai là tự viết hoặc thay đổi code. Tầng ba là phân tích toán, đánh đổi và giới hạn. Với các khái niệm cốt lõi như leakage, metric và confidence, cần đạt cả ba tầng trước khi hoàn tất V1.

Một bài được xem là hiểu khi bạn giải thích được vì sao làm như vậy, tự giải một ví dụ mới và sửa được một biến thể. Việc chạy code mẫu thành công chỉ là bước đầu. Nếu chưa đạt, dùng ví dụ nhỏ hơn rồi kiểm tra lại.

Ba phiên đầu tiên dự kiến là chốt bài toán và môi trường, khám phá cấu trúc dữ liệu, rồi xây pipeline raw đầu tiên. Chưa cần cài mọi công nghệ từ ngày đầu; dependencies được thêm khi có nhiệm vụ cụ thể.

## 17 Các mốc kiểm tra và quản lý thời gian

| Mốc | Bằng chứng cần có | Khi chưa đạt |
| --- | --- | --- |
| Sau tuần 2 | Data quality đối chiếu được, pipeline idempotent | Sửa dữ liệu trước khi học model |
| Sau tuần 4 | Baseline và evaluator đúng trên fixture | Thu hẹp UI, hoàn thiện protocol |
| Sau tuần 6 | Ba mô hình so cùng split và search có log | Giảm search, kiểm tra confidence |
| Sau tuần 7 | Cấu hình khóa và final test report | Sửa lỗi protocol, ghi rõ rerun nếu cần |
| Sau tuần 10 | Sáu trang và replay không đọc tương lai | Giảm trang trí, sửa luồng dữ liệu |
| Sau tuần 12 | Môi trường sạch chạy được, portfolio có evidence | Hoàn thiện tái hiện trước V2 |

Dự phòng một phần thời gian mỗi tuần cho debug và học bù. Khi chậm, ưu tiên giữ pipeline, baseline, evaluation, customer recommendations và replay. Có thể giảm biểu đồ phụ, export chi tiết hoặc trang Products. Các phần optional như bootstrap nhiều lần hoặc baseline mua lại bổ sung có thể làm sau khi V1 ổn định, nhưng giới hạn phải được ghi rõ.

Nếu mô hình không hơn popularity, kiểm tra protocol, tín hiệu và cohort trước. Kết quả đó vẫn có giá trị nếu bạn giải thích được bằng dữ liệu, phục vụ phương án phù hợp và trình bày giới hạn trung thực. Không thay split hoặc chọn vài khách đẹp để tạo một thành tích giả.

## 18 Rủi ro và cách xử lý

| Rủi ro | Dấu hiệu | Cách xử lý |
| --- | --- | --- |
| Thiếu nền toán recommendation | Dùng thư viện nhưng không hiểu score | Ví dụ vector và ma trận nhỏ trước ALS |
| Dữ liệu bẩn | KPI thay đổi bất thường sau lọc | Raw bất biến, bảng đối chiếu và fixtures |
| Leakage | Mô hình dùng item xuất hiện sau cutoff | Snapshot bất biến và future invariance test |
| Sai chính sách mua lại | Thư viện loại seen items ngoài ý muốn | Pin API, test flag và candidate set |
| Cold start | Không có vector cho khách mới | Popularity route và reason_code |
| Bias khách quay lại | Chỉ báo metric đẹp cho cohort nhỏ | Báo cohort size và khách không quay lại |
| Hosting chậm hoặc ngủ | Demo không phản hồi lần đầu | Loading state, bundle gọn và video |
| Project quá rộng | Thêm churn, chatbot hoặc kho trước V1 | Theo backlog, khóa bài toán chính |
| Chưa tự làm được | Code chạy nhưng không giải thích được | Bài biến thể và sửa lỗi có chủ đích |

## 19 Tiêu chí hoàn thành V1

- Dữ liệu gốc có nguồn, giấy phép, hash và manifest; pipeline có thể chạy lại.
- Các quy tắc làm sạch, KPI, CustomerID thiếu và cancellation được giải thích rõ.
- Popularity, ItemCF và ALS được so sánh trên cùng protocol; mô hình phục vụ được chọn bằng validation.
- Cấu hình đã khóa trước test; báo cáo kèm cohort size, candidate set, repeat policy và giới hạn.
- Nhãn tương lai không đi vào features, model, evidence hoặc cache của snapshot cũ.
- Gợi ý có fallback, không trùng mã, không ngoài candidate set và không gán score thành xác suất.
- Sáu trang demo, API và historical replay hoạt động trên các mốc được hỗ trợ.
- Kiểm thử dữ liệu, metric, leakage, mapping và API chạy thành công.
- Metadata model đủ để tái hiện; môi trường mới chạy được theo README.
- Báo cáo hiệu năng ghi rõ phần cứng, tải đo và cold start.
- Portfolio có README tiếng Anh, hình demo, video, model card, case study và mô tả CV dùng kết quả thật.
- Repository GitHub có lịch sử commit theo giai đoạn, Issues và PR có bằng chứng kiểm tra, CI thành công trên commit của release V1, cùng Release v1.0.0 có hướng dẫn tái hiện.
- Bạn tự giải thích được project và hoàn thành một bài thay đổi nhỏ mà không cần hướng dẫn từng dòng.

## 20 Hồ sơ portfolio và câu chuyện phỏng vấn

### 20.1 Các tài liệu cuối cùng

README mở đầu bằng bài toán, demo và các kết quả đã đo, rồi giải thích cách chạy. Model card nêu intended use, dữ liệu, preprocessing, phương pháp chọn mô hình, metrics và giới hạn. Data dictionary mô tả granularity, khóa và định nghĩa trường. Case study trình bày quyết định và bằng chứng theo thứ tự dễ kiểm tra.

Video hai đến ba phút đi qua hồ sơ khách, gợi ý, replay và bảng so sánh. Giữ thêm một bản video hoặc ảnh khi public demo không sẵn sàng. Architecture thể hiện đường offline, đường serving và chỗ nhãn tương lai được tách.

Mô tả CV sẽ viết sau khi có kết quả. Nội dung dự kiến bằng tiếng Anh: xây hệ thống gợi ý từ giao dịch thực, đánh giá theo thời gian, triển khai API và demo; điền số dòng sau xử lý, metric và latency thực tế. Không thêm mức tăng doanh thu nếu chưa có thử nghiệm.

### 20.2 Câu hỏi bạn cần trả lời được

- Vì sao chọn recommendation và vì sao chấp nhận sản phẩm đã mua?
- Vì sao chọn 30 ngày, và thay cửa sổ sẽ làm thay đổi điều gì?
- Một dòng hóa đơn khác một tương tác như thế nào?
- Tại sao không chia random hoặc dùng leave last one out riêng từng khách mà bỏ qua timeline chung?
- Candidate set được xác định bằng gì và có biết tồn kho không?
- Score ALS là gì, confidence là gì và khách không mua có nghĩa gì?
- Vì sao chọn mô hình phục vụ đó khi so với popularity?
- Khách nào được tính trong Recall@10, ai bị loại và vì sao?
- Xử lý khách mới, sản phẩm mới và giá trị thiếu như thế nào?
- Vì sao một mô hình tốt offline chưa chứng minh tăng doanh thu?
- Replay dùng đúng model của thời điểm nào và làm sao kiểm tra không leakage?
- Làm cách nào tái hiện một model version và cải thiện thời gian phục vụ?

## 21 Hướng mở rộng sau V1

Chọn một hướng dựa trên lỗi quan sát được. Nếu khách ít lịch sử hoạt động kém, thử đặc trưng văn bản từ mô tả sản phẩm để bổ sung similarity. Mô tả vẫn phải lấy trước cutoff và cách fit vocabulary phải tuân thủ thời gian.

Nếu nhu cầu thay đổi theo thời gian, thử time decay trong interaction weights và thêm nhiều mốc validation. Nếu muốn học deep learning, có thể thử một mô hình chuỗi sau khi xử lý đúng các sản phẩm trong cùng hóa đơn, vốn không có thứ tự click đáng tin cậy.

Nếu muốn hiểu phần vận hành, thêm MLflow hoặc một registry đơn giản để theo dõi experiment. Nếu có dữ liệu cửa hàng thực với exposure và quyền sử dụng, thiết kế đánh giá online hoặc A B test riêng trước khi đưa ra claim doanh thu.

Mỗi cải tiến phải có giả thuyết, baseline, protocol và tiêu chí thành công được đặt trước. Kết quả không tốt cũng được ghi lại để giải thích điều đã học. Không cần làm mọi hướng V2 để portfolio đầu tiên hoàn thành.

## 22 Thuật ngữ cần học

| Thuật ngữ | Giải thích ngắn |
| --- | --- |
| Implicit feedback | Tín hiệu hành vi như mua hàng, không phải đánh giá sao |
| Candidate set | Tập sản phẩm được phép xếp hạng tại một thời điểm |
| Snapshot | Trạng thái dữ liệu và model tại cutoff đã xác định |
| Data leakage | Dùng thông tin chưa thể biết khi dự đoán |
| Sparse matrix | Ma trận lưu hiệu quả khi đa số ô không có tương tác |
| Embedding hoặc latent factor | Vector được học để biểu diễn khách hoặc sản phẩm |
| Regularization | Ràng buộc giúp giảm việc fit quá mức dữ liệu |
| Cold start | Khách hoặc sản phẩm có ít hoặc chưa có lịch sử |
| Fallback | Phương án gợi ý dự phòng khi mô hình chính không phù hợp |
| Cohort | Nhóm khách được định nghĩa theo tiêu chí rõ ràng |
| Model artifact | File model cùng mapping, config và metadata |
| Idempotent pipeline | Chạy lại cùng đầu vào không nhân đôi hoặc làm lệch kết quả |

## 23 Nguồn tham khảo

Nguồn dưới đây là tài liệu chính thức hoặc nghiên cứu gốc đã kiểm tra khi lập kế hoạch. Chúng hỗ trợ dữ liệu, cơ chế thư viện và đánh giá; timeline, features, API và các mục tiêu kỹ thuật là thiết kế đề xuất cho RetailMind.

[S1] Chen D. Online Retail II. UCI Machine Learning Repository. DOI 10.24432/C5CG6D. https://archive.ics.uci.edu/dataset/502/online+retail+ii

[S2] implicit. Documentation and source repository. Các mô hình phản hồi ngầm và cách dùng cơ bản. https://benfred.github.io/implicit/ và https://github.com/benfred/implicit

[S3] implicit. CPU AlternatingLeastSquares API. fit, recommend, filtering, explain và lưu model. https://benfred.github.io/implicit/api/models/cpu/als.html

[S4] FastAPI. Tutorial User Guide. API, validation, xử lý lỗi và kiểm thử. https://fastapi.tiangolo.com/tutorial/

[S5] Streamlit. Caching overview. Cache dữ liệu và tài nguyên. https://docs.streamlit.io/develop/concepts/architecture/caching

[S6] scikit learn. ndcg_score documentation. Tham khảo định nghĩa NDCG và cách kiểm tra metric. https://scikit-learn.org/stable/modules/generated/sklearn.metrics.ndcg_score.html

[S7] A Critical Study on Data Leakage in Recommender System Offline Evaluation. Nghiên cứu về timeline chung và rò rỉ thông tin. https://arxiv.org/abs/2010.11060

[S8] Shani G. và Gunawardana A. Evaluating Recommender Systems. Microsoft Research. Phân biệt offline evaluation, user study và online experiments. https://www.microsoft.com/en-us/research/publication/evaluating-recommender-systems/

[S9] GitHub Docs. GitHub flow. Tham khảo quy trình branch, commit, Pull Request và merge. https://docs.github.com/en/get-started/using-github/github-flow

[S10] GitHub Docs. Building and testing Python. Tham khảo workflow CI cho Python. https://docs.github.com/en/actions/tutorials/build-and-test-code/python

[S11] GitHub Docs. Creating an issue. Tham khảo tạo và quản lý đầu việc. https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/creating-an-issue

Ngày truy cập nguồn: 03 tháng 10 năm 2026. Khi bắt đầu từng phần, kiểm tra lại tài liệu của phiên bản thư viện được cài; không mặc định ví dụ của một phiên bản khác sẽ chạy giống nhau.

## 24 Quy trình làm project trên GitHub

### 24.1 Mục tiêu và thiết lập từ tuần 1

Git lưu lịch sử thay đổi trên máy; GitHub lưu repository từ xa và cung cấp công cụ cộng tác. Portfolio cần cả sản phẩm và bằng chứng về cách bạn xây dựng, kiểm tra, sửa lỗi và giải thích quyết định. Các quy tắc bên dưới là thiết kế cho RetailMind, có thể điều chỉnh nhịp làm theo từng buổi học.

Tên repository đề xuất: `retailmind`; nhánh chính: `main`. Chưa xác định tài khoản, repository URL hay repository thực tế. Có thể dùng repo private trong quá trình học; khi đưa vào portfolio, ưu tiên repo public để người tuyển dụng xem code, hoặc bảo đảm người nhận có quyền truy cập. Không cần chọn hosting ứng dụng trong buổi đầu.

Thực hiện lần lượt ở buổi khởi tạo:

1. Kiểm tra workspace có Git hay chưa, branch hiện tại, remote và thay đổi chưa commit. Giữ nguyên công việc đã có.
2. Nếu đã có repo đúng project, dùng repo đó. Nếu tạo mới, tạo repository GitHub trống rồi clone, hoặc kết nối repository local với remote; chọn một cách để tránh hai lịch sử khởi tạo khác nhau.
3. Xác nhận danh tính commit và cách đăng nhập GitHub phù hợp trên máy. Không đưa token vào file project, URL remote hoặc nội dung hướng dẫn công khai.
4. Tạo README ngắn, .gitignore, cấu trúc tối thiểu và đưa `RetailMind_Codex_Plan.md` vào repo. Commit phần khởi tạo, push và kiểm tra các file hiện trên GitHub.
5. Tạo Issue đầu tiên cho problem statement; làm một thay đổi nhỏ bằng branch, PR và tự review trước khi merge. Ghi URL repo và checkpoint thật trong `docs/progress.md`.

Sau buổi này, người học cần phân biệt working tree, staging area, commit local và remote; biết thay đổi đã lên GitHub hay vẫn chỉ nằm trên máy.

### 24.2 Chia công việc bằng Issues và milestones

Issue mô tả một kết quả cần làm; không thay thế bài giảng. Tạo Issue theo phần sắp triển khai, đủ nhỏ để kiểm tra và giải thích. Có thể chia một feature F01 đến F13 thành nhiều Issue. Dùng checklist để thể hiện các bước của Issue. [S11]

| Milestone | Công việc gợi ý | Bằng chứng hoàn thành |
| --- | --- | --- |
| Setup, tuần 1 | Khởi tạo repo, môi trường, problem statement | Repo có code, README và PR đầu tiên |
| V0, tuần 2 đến 4 | F01/F02, SQL, labels, Popularity, evaluator, dashboard nhỏ | Pipeline và test chạy; báo cáo baseline; release v0.1.0 |
| Models, tuần 5 đến 7 | ItemCF, ALS, giải thích, phân tích lỗi | Báo cáo validation; cấu hình khóa; kết quả test có metadata |
| Application, tuần 8 đến 10 | API, dashboard, replay, xuất CSV | Demo sáu trang và API có kiểm tra |
| V1, tuần 11 đến 12 | Đóng gói, benchmark, README, model card | Chạy từ môi trường sạch; CI thành công; release v1.0.0 |

Mẫu Issue cần có: mục tiêu, feature liên quan, kiến thức cần học, phạm vi, tiêu chí nghiệm thu, cách kiểm tra và phụ thuộc. Ví dụ: `F02: validate cancellation and missing CustomerID`; tiêu chí gồm fixture có dòng hủy/thiếu ID và báo cáo phân biệt sales với adjustments. Các tiêu chí kỹ thuật phải khớp mục 3 và 13.

Labels gợi ý: `data`, `model`, `api`, `ui`, `docs`, `testing`, `bug`. Dùng GitHub Projects nếu cần bảng Todo/In progress/Done; đây là phần tùy chọn. Issue hoàn tất sau khi phần triển khai và kiểm tra đã được merge; learning log ghi riêng phần người học còn cần ôn.

### 24.3 Branch, commit và Pull Request cho từng thay đổi

GitHub flow dùng branch cho thay đổi, commit/push để lưu tiến độ, Pull Request để xem xét và merge vào nhánh chính. RetailMind áp dụng quy trình này cho cả project cá nhân. [S9]

Một vòng làm việc dự kiến:

1. Chọn Issue và nêu kết quả của buổi học.
2. Đồng bộ `main` sau khi kiểm tra trạng thái local, rồi tạo branch như `feat/transaction-validation`, `feat/itemcf-baseline` hoặc `docs/model-card`.
3. Học và triển khai phạm vi nhỏ; chạy kiểm tra phù hợp, xem diff và chọn đúng file đưa vào commit.
4. Commit với nội dung rõ ràng, ví dụ `feat: validate cancellation transactions` hoặc `test: verify cutoff boundary`.
5. Push branch và mở PR. Mô tả vấn đề, thay đổi, cách kiểm tra, kết quả và Issue liên quan.
6. Tự review diff, giải thích được lựa chọn kỹ thuật, xử lý lỗi CI nếu đã có workflow, rồi merge khi đạt tiêu chí. Sau merge, đồng bộ local và cập nhật checkpoint.

Lệnh học thực hành: `git status`, `git diff`, `git add <file>`, `git commit`, `git remote -v`, `git switch`, `git pull --ff-only`, `git push`. Codex giải thích các lệnh khi dùng, kiểm tra branch/remote thực tế và xử lý thay đổi local trước khi đồng bộ. Không chạy nguyên một chuỗi mẫu mà chưa kiểm tra trạng thái repo.

Làm solo có thể tự review và merge PR; không bắt buộc tìm một người khác để approve. Dùng PR để tập đọc diff và mô tả bằng chứng. Khi có xung đột, học cách hiểu và giải quyết nội dung xung đột. Không dùng force push hay reset mất dữ liệu như thao tác đồng bộ mặc định.

Không cần commit mỗi ngày hoặc đặt chỉ tiêu số commit. Một commit nên thể hiện một thay đổi hợp lý; PR có thể gồm nhiều commit. Không viết lại lịch sử để tạo cảm giác project đã có tiến độ từ trước.

### 24.4 Quy tắc lưu file trong repository

| Nên track bằng Git | Giữ ngoài Git, tái tạo hoặc tải riêng |
| --- | --- |
| Source code, SQL, tests và fixture nhỏ | Excel nguồn và toàn bộ dữ liệu raw/processed |
| Config và lockfile | Môi trường Python, cache và file tạm |
| Kế hoạch, README, docs và notebook gọn | Model bundle lớn và ma trận tương tác đầy đủ |
| Báo cáo metrics tổng hợp, manifest/hash | Request logs, bảng dự đoán từng khách đầy đủ |
| Ảnh demo vừa phải và workflow CI | Secrets, token và file .env |

Thêm `.env.example` nếu cần, chỉ chứa tên biến và giá trị mẫu không nhạy cảm. Manifest công khai ghi nguồn, hash, schema và quy tắc build; không chứa đường dẫn riêng của máy. Xóa output notebook quá lớn trước khi commit. README ghi nguồn và giấy phép dataset; lựa chọn giấy phép code riêng không thay thế giấy phép dữ liệu.

README phải hướng dẫn tải dữ liệu, prepare, build snapshot, train và evaluate bằng các lệnh thực tế. Bundle phục vụ demo có thể build local hoặc phân phối bằng cách phù hợp sau khi biết dung lượng; không cần thêm Git LFS ngay từ đầu. Nếu cung cấp bundle ngoài repo, ghi nơi tải, checksum, version và commit/config tương ứng.

### 24.5 GitHub Actions từ tuần 3

Đặt workflow ở `.github/workflows/ci.yml`. CI tự chạy khi có Pull Request và khi code được push vào `main`; dùng cùng phiên bản Python và dependencies đã kiểm tra local. Workflow thiết lập Python, cài dependencies và chạy các kiểm tra. [S10]

Phạm vi RetailMind: lint bằng công cụ đã chọn, tests cho dữ liệu/metric/leakage/mapping, và smoke pipeline trên fixture nhỏ. Thêm API tests từ tuần 8. Không tải dataset đầy đủ, huấn luyện ALS hoặc chạy benchmark đầy đủ trong mỗi PR. CI cơ bản không cần secrets hoặc dịch vụ trả phí. Chốt phiên bản Actions tương thích khi triển khai, kiểm tra tài liệu hiện hành thay vì chép version từ ví dụ cũ.

PR ghi lệnh local đã chạy và link kết quả CI thực tế. Test fail thì đọc log, tái hiện trên fixture và sửa nguyên nhân; không tắt test để làm CI xanh. Khi workflow chưa có hoặc chưa chạy, ghi rõ trạng thái đó. Tuần 11 mở rộng kiểm tra đóng gói và khởi động từ môi trường sạch.

### 24.6 README, releases và bằng chứng portfolio

README tiếng Anh sẽ hoàn thiện dần, gồm:

- Bài toán, người dùng, ảnh hoặc video demo và link ứng dụng nếu đã triển khai.
- Nguồn dữ liệu, giấy phép, quy tắc làm sạch và cách tái tạo dữ liệu.
- Kiến trúc, cấu trúc repo, thiết lập môi trường và lệnh chạy.
- Popularity/ItemCF/ALS, protocol theo thời gian, repeat policy và candidate set.
- Bảng kết quả thực tế, cohort size, giới hạn, model card và link báo cáo.
- Cách chạy tests, trạng thái CI và hướng phát triển tiếp theo.

Tạo release V0 `v0.1.0` cuối tuần 4 và V1 `v1.0.0` cuối tuần 12, gắn với commit đã kiểm tra. Release notes mô tả tính năng có thể dùng, cách chạy, giới hạn và thay đổi quan trọng. Báo cáo mô hình ghi commit dùng để chạy, config, dataset hash và model/snapshot ID; không chỉ ghi tên release vì báo cáo có thể được commit sau lần chạy.

Trước khi đưa link lên CV, thử theo README trong môi trường sạch và kiểm tra quyền truy cập repo, links, ảnh, video và CI trên commit release. Có thể pin repository trên GitHub profile và thêm topics phù hợp như `data-science` và `recommender-system`. GitHub là nơi lưu code và bằng chứng; việc chạy Streamlit/FastAPI và chọn hosting vẫn theo mục 14.

### 24.7 Tiêu chí GitHub tại mỗi checkpoint

- Code và tài liệu của giai đoạn đã commit; nếu đã push thì link/commit phải kiểm chứng được.
- Issue và PR mô tả kết quả cùng kiểm tra thực tế; không ghi kết quả chưa chạy.
- CI thành công khi giai đoạn đã yêu cầu CI; có lý do rõ ràng nếu một phần đang blocked.
- Người học tự giải thích được diff, commit, push và cách quay lại xem một thay đổi.
- `docs/progress.md` chỉ rõ phần đã merge, bài tự làm, kiến thức cần ôn và bước tiếp theo.

Checklist này bổ sung tiêu chí học và chất lượng trong kế hoạch; CI xanh hoặc có nhiều commit không tự chứng minh mô hình đúng hay người học đã hiểu project.

## Phụ lục A Cấu hình đề xuất để triển khai

Ví dụ YAML dưới đây là hợp đồng cấu hình dự kiến, không phải code đã hoạt động. Tên khóa có thể điều chỉnh khi triển khai nếu giữ nguyên ý nghĩa và cập nhật tài liệu. Cutoff phải được xác nhận bằng kiểm tra file gốc; thời gian giữ theo dataset, chưa tự gán múi giờ.

```yaml
project:
  name: retailmind
  default_language_ui: en
  teaching_language: vi

data:
  source: uci_online_retail_ii
  source_dataset_id: 502
  currency: GBP
  timezone_policy: preserve_source_time_unknown_timezone
  keep_raw_immutable: true
  missing_customer_id_policy: analytics_only
  source_duplicate_policy: flag_and_review

evaluation:
  horizon_days: 30
  k: 10
  validation_cutoff: "2011-09-01T00:00:00"
  test_cutoff: "2011-11-01T00:00:00"
  train_boundary: timestamp_lt_cutoff
  label_boundary: cutoff_lte_timestamp_lt_cutoff_plus_horizon
  candidate_policy: valid_items_with_identified_sales_before_cutoff
  allow_repeat_purchase: true
  ranking_policy: full_candidate_set
  user_aggregation: macro_average
  main_recall_labels: all_distinct_valid_future_purchases
  empty_label_policy: exclude_from_ranking_metrics_and_report_count
  model_selection_metric: ndcg_at_10_validation

models:
  compare: [popularity, itemcf, als]
  popularity:
    history_days_initial: 90
    popularity_unit: distinct_identified_customers
  itemcf:
    similarity_initial: cosine
    remove_self_similarity: true
  als:
    use_gpu_initial: false
    filter_already_liked_items: false
    seed_initial: 42
  confidence_scaling:
    policy: define_and_apply_once

serving:
  default_k: 10
  max_k: 20
  load_models_at_startup: true
  fallback: popularity
  replay_snapshots_v1: [validation, test]
  unknown_customer_id: return_404
  explicit_new_customer_mode: true
  p95_latency_budget_ms_initial: 1000
```

`p95_latency_budget_ms_initial` là mục tiêu cần đo trên môi trường công bố, chưa phải thành tích. Tham số model và ngưỡng routing chỉ được chọn bằng validation. Search space, weighting và confidence cần được ghi cụ thể khi đến giai đoạn huấn luyện.

## Phụ lục B Checklist bàn giao cho Codex

### B.1 Tính năng V1

- [ ] F01 Nạp nguồn và manifest có thể chạy lại.
- [ ] F02 Báo cáo chất lượng và lý do xử lý từng loại dòng.
- [ ] F03 Dashboard với KPI được định nghĩa và đối chiếu SQL.
- [ ] F04 Hồ sơ khách và RFM theo snapshot.
- [ ] F05 Top k từ Popularity, ItemCF và ALS theo cùng chính sách.
- [ ] F06 Giải thích dựa trên bằng chứng trước cutoff.
- [ ] F07 Fallback và chế độ khách mới rõ ràng.
- [ ] F08 Historical Replay ở các mốc có bundle đúng thời gian.
- [ ] F09 So sánh metrics và phân tích lỗi theo cohort.
- [ ] F10 Tìm sản phẩm và sản phẩm tương tự.
- [ ] F11 API có schema, validation, mã lỗi và health.
- [ ] F12 Xuất CSV có metadata và log hoạt động.
- [ ] F13 Môi trường sạch chạy lại được và hồ sơ portfolio đầy đủ.

### B.2 Giai đoạn học và triển khai

- [ ] Tuần 1 Bài toán và môi trường.
- [ ] Tuần 1 Repository GitHub, README, .gitignore, commit/push và PR đầu tiên.
- [ ] Tuần 2 Nạp nguồn và làm sạch.
- [ ] Tuần 3 SQL và phân tích khách hàng.
- [ ] Tuần 3 GitHub Actions chạy lint và fixture tests trên PR/main.
- [ ] Tuần 4 Labels, evaluator, Popularity và V0.
- [ ] Tuần 5 ItemCF và giải thích.
- [ ] Tuần 6 ALS và experiment validation.
- [ ] Tuần 7 Phân tích lỗi, khóa cấu hình và final test.
- [ ] Tuần 8 API và service.
- [ ] Tuần 9 Bốn trang dashboard đầu tiên.
- [ ] Tuần 10 Replay và Model Evaluation.
- [ ] Tuần 11 Tests, CI, Docker và benchmark.
- [ ] Tuần 12 Portfolio và luyện phỏng vấn.
- [ ] V0 Release v0.1.0; V1 Release v1.0.0 từ commit đã kiểm tra.
- [ ] README và CV liên kết repository, báo cáo và demo thực tế nếu có.

Chỉ đánh dấu hoàn thành khi có bằng chứng và người học đã đạt tiêu chí của giai đoạn. Số tuần là nhịp dự kiến; không dùng deadline để bỏ qua kiến thức chưa hiểu hoặc kiểm tra chưa đạt.

## Phụ lục C Prompt để bắt đầu với Codex

```text
Hãy đọc toàn bộ RetailMind_Codex_Plan.md và kiểm tra workspace hiện tại.
Hãy hướng dẫn tôi triển khai RetailMind từng bước theo kế hoạch, đồng thời
dạy kiến thức để tôi hiểu rõ và có thể tự làm. Giải thích bằng tiếng Việt;
code, UI và README dùng tiếng Anh.

Bắt đầu với Tuần 1 Buổi 1, hoặc tiếp tục từ checkpoint đã có nếu workspace
đã có tiến độ. Chỉ triển khai phần của buổi đang học. Nêu mục tiêu, giải thích
cơ chế, làm ví dụ nhỏ, triển khai, kiểm tra, giao bài tự làm và cập nhật tiến độ.
Giữ nguyên protocol đánh giá theo thời gian, chính sách mua lại và phạm vi V1.
GitHub là yêu cầu bắt buộc: làm theo mục 24 từ tuần đầu, gồm repository,
Issues, branch, commit/push, Pull Request, CI và release theo từng giai đoạn.
Kiểm tra repo/remote hiện có trước; chỉ hỏi tài khoản hoặc repo đích khi thiếu.
Chỉ ghi hoàn thành thao tác GitHub khi đã thực hiện và kiểm chứng.
```
