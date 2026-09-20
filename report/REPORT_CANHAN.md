# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Trần Thị Thu Trang
**Nhóm:** Kling
**Ngày:** 20/09/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
độ tương tự Cosine cao có nghĩa là chúng có hướng vector gần nhau trong không gian embedding, nội dung của hai câu/ đoạn này giống nhau về nghĩa, chủ đề hoặc ý tưởng

**Ví dụ có độ tương tự CAO:**
- Câu A: "Tôi muốn mua một chiếc laptop để học lập trình."
- Câu B: "Tôi cần máy tính xách tay cho việc học coding và phát triển phần mềm."

Hai câu này cùng nói về mục tiêu mua máy tính cho học lập trình, nên có ý nghĩa gần nhau và cosine similarity cao.

**Ví dụ có độ tương tự THẤP:**
- Câu A:"Tôi muốn mua giáo trình môn toán cao cấp"
- Câu B:"Trời hôm nay đã hết mưa rồi."
- Tại sao khác: Hai chủ đề của hai câu là khác nhau --> cosine similarity thấp

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
- Cosin similarity tập trung vào hướng của vecto, không quá nhạy với độ dài văn bản.
- Euclindean distance lại nhạy với kích thước vectow: một đoạn văn bản dài hơn dù cùng chủ đề có thể chám điểm thấp hơn.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:*
> *Đáp án:*
- số lượng Chunk = Cei((độ_dài_tài_liệu-overlap)/(chunk_size-overlap))
                 = Cei((10000-50)/(500-50))
                 = Cei(9950/450)
                 = 23

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> *Viết 1-2 câu:*
- số lượng chunk = Cei((10000-100)/(500-100))
                 = 25
Vậy nếu overlap tăng từ 50 lên 100, số chunk tăng lên từ 23 lên 25
- Người ta muốn tăng overlap lên vì
                - giữ ngữ cảnh ở ranh giới giữa các chunk
                - giảm nguy cơ mất thông tin khi một ý /câu quan trọng bị chia ở giữa hai chunk
                - hữu ích cho retrieval và RAG vì các chunk có thể chứa ngữ cánh liên quan hơn.
Tuy nhiên overlap lớn hơn đồng nghĩa với tần suất lặp lại dữ liệu nhiều hơn nên có thể tăng độ dư thừa và chi phí lưu trữ.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
Tôi chia văn bản thành các câu trước, sau đó gom từng nhóm theo số câu tối đa trong một chunk. Cách làm này giúp giữ được cấu trúc ngữ nghĩa của câu, vì các chunk thường chứa các ý hoàn chỉnh hơn. Tôi cũng xử lý các trường hợp rỗng, whitespace thừa và câu cuối cùng bằng cách bỏ các phần trống để đảm bảo đầu ra là list các string hợp lệ.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
Thuật toán hoạt động theo kiểu thử lần lượt các separator theo thứ tự ưu tiên: đoạn văn lớn, xuống dòng, dấu chấm, khoảng trắng, cuối cùng mới cắt theo kích thước cố định. Nếu một đoạn vẫn quá dài sau khi tách, tôi gọi lại phương thức đệ quy với danh sách separator còn lại. Base case là khi độ dài của đoạn đã nhỏ hơn hoặc bằng `chunk_size`, lúc đó trả về đoạn đó như một chunk.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
Tôi lưu dữ liệu dưới dạng record có `id`, `content`, `metadata` và `embedding`. Khi thêm tài liệu, tôi gọi embedder để tạo vector cho nội dung, sau đó lưu vào store. Với tìm kiếm, tôi nhúng query thành vector rồi tính tương đồng với từng embedding đã lưu bằng dot product; sau đó sắp xếp theo score giảm dần để lấy top-k phù hợp nhất.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
Phương pháp lọc metadata được thực hiện trước khi tính similarity để giảm tập hợp candidate. Sau đó tôi chỉ tìm kiếm trong các record thỏa mãn điều kiện metadata. Với xóa tài liệu, tôi xoá toàn bộ các chunks thuộc cùng `doc_id` để đảm bảo không còn dữ liệu dư thừa trong store.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
Tôi tạo luồng RAG theo đúng mô hình: retrieve top-k chunks từ vector store, nối chúng thành một đoạn ngữ cảnh, rồi đưa vào prompt cho LLM. Cách này giúp mô hình trả lời dựa trên thông tin có trong tài liệu thay vì đoán theo kiến thức chung. Prompt được thiết kế ngắn gọn, rõ ràng và tập trung vào câu hỏi của người dùng.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```bash
pytest tests/ -v
```

**Số lượng bài test vượt qua (pass):** 42 / 42

> Kết quả đã được xác thực bằng lệnh `pytest tests/ -v`: 42 tests passed in 0.08s.

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | "Tôi muốn mua máy tính để lập trình." | "Tôi cần laptop cho học coding." | Cao | -0.040272 | Không |
| 2 | "Trời hôm nay nắng đẹp." | "Hôm nay thời tiết rất đẹp." | Cao | -0.150239 | Không |
| 3 | "Lập trình Python." | "Chủ đề về marketing online." | Thấp | 0.115053 | Có |
| 4 | "Máy tính xách tay" | "Điện thoại di động" | Thấp | 0.193679 | Không |
| 5 | "Học AI và machine learning" | "Nghiên cứu mô hình học máy" | Cao | 0.195659 | Có |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
Điều bất ngờ nhất là các giá trị thực tế không theo kỳ vọng ban đầu: nhiều cặp được dự đoán là “cao” lại có điểm thấp hoặc thậm chí âm, trong khi một số cặp không liên quan vẫn có giá trị dương nhỏ. Điều này cho thấy với MockEmbedder, các vector không mô hình hóa nghĩa văn bản theo kiểu embedding thực tế một cách mạnh mẽ; chúng phụ thuộc vào cách mã hóa ngẫu nhiên của bộ giả lập. Từ đó, tôi học được rằng cosine similarity chỉ thật sự đáng tin cậy khi embeddings được tạo ra từ mô hình ngữ nghĩa phù hợp.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Thời hạn đổi trả tối đa cho đơn hàng mua trực tuyến là bao lâu? | Long Châu: “sản phẩm có lỗi nhà sản xuất đổi trả trong vòng 30 ngày, máy thiết bị y tế lên đến 1 năm”; UNIQLO: “đơn hàng online đổi hàng trong vòng 30 ngày”. | 0.90 | Có | Agent trả lời: “Đối với đơn hàng online, thường là 30 ngày kể từ khi nhận hàng; riêng một số trường hợp có thể lên đến 6 tháng hoặc 1 năm.” |
| 2 | Trường hợp nào được miễn phí vận chuyển khi đổi trả? | Biti's: “nếu lỗi từ Biti's, giao sai sản phẩm hoặc do nhà sản xuất thì miễn phí vận chuyển đổi hàng”. | 0.88 | Có | Agent trả lời: “Khách hàng được miễn phí vận chuyển đổi trả khi lỗi thuộc về nhà bán, vận chuyển hoặc nhà sản xuất.” |
| 3 | Sản phẩm đã qua sử dụng hoặc có tem bị rách có được đổi trả không? | UNIQLO / Long Châu: “sản phẩm phải còn mới, chưa qua sử dụng, nguyên tem nhãn, đầy đủ phụ kiện”. | 0.92 | Có | Agent trả lời: “Thường không được đổi trả nếu sản phẩm đã qua sử dụng, bị dơ, hư hỏng hoặc thiếu phụ kiện/tem nhãn.” |
| 4 | Khách hàng cần gửi thông báo đổi trả trong thời gian nào nếu nhận thiếu phụ kiện hoặc hàng bị bể vỡ? | L'Oréal: “thông báo trong vòng 48 giờ kể từ khi nhận sản phẩm, nếu thiếu phụ kiện, quà tặng hoặc bể vỡ”. | 0.94 | Có | Agent trả lời: “Khách hàng cần thông báo trong vòng 48 giờ và gửi hàng trả trong vòng 14 ngày.” |
| 5 | Nếu khách hàng thay đổi quyết định sau khi nhận hàng, có thể yêu cầu trả hàng trên Shopee trong bao lâu không? | Shopee: “người mua có thể gửi yêu cầu trong vòng 15 ngày kể từ ngày giao hàng thành công; thực phẩm tươi sống/đông lạnh là 24 giờ”. | 0.89 | Có | Agent trả lời: “Trên Shopee, thường là 15 ngày kể từ khi giao hàng thành công; với thực phẩm tươi sống/đông lạnh thì 24 giờ.” |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
Qua demo nhóm, tôi nhận ra rằng chiến lược chunking có tác động lớn đến hiệu suất retrieval. Một số câu hỏi tốt hơn với chunk nhỏ và rõ ngữ cảnh, trong khi một số câu hỏi khác lại cần chunk lớn hơn để giữ đủ bối cảnh. Điều này cho thấy việc chọn phương án chia nhỏ phù hợp không chỉ là kỹ thuật mà còn ảnh hưởng trực tiếp đến chất lượng trả lời của hệ thống RAG.

**Nhận xét cá nhân:**
Tôi thấy rằng retrieval hoạt động tốt nhất khi chunk giữ nguyên các “mục” quan trọng như thời hạn, điều kiện, loại trừ và quy định hoàn tiền. Nếu chunk bị cắt quá nhỏ hoặc bị mất ngữ cảnh, hệ thống dễ trả lời thiếu chính xác. Vì vậy, với tài liệu về chính sách đổi trả, `RecursiveChunker` và `SentenceChunker` cho hiệu quả tốt hơn so với `FixedSizeChunker` khi cần hiểu điều kiện và ngoại lệ.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) |5/ 5 |
| Hướng tiếp cận của tôi (My Approach) |7/ 10 |
| Hoàn thiện code (Core Implementation — tests) |25 30 |
| Dự đoán độ tương tự (Similarity Predictions) |5/ 5 |
| Kết quả truy xuất của tôi (Competition Results) |5/ 10 |
| **Tổng phần cá nhân** | 47/ 60** |
