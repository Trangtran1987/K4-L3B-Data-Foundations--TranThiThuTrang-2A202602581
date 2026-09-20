# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** Kling
**Thành viên:** Nguyễn Văn Bảo; Nguyễn Minh Ngọc, Nguyễn Đình Anh, Trần Thị Thu Trang
**Ngày:** 20/09

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng,  dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** chính sách đổi trả/bảo hành thương mại điện tử

**Tại sao nhóm chọn chủ đề này?**
 Theo yêu cầu của

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Long Châu — Chính sách đổi trả | https://nhathuoclongchau.com.vn/chinh-sach/chinh-sach-doi-tra | 2026-09-20 / không nêu phiên bản rõ ràng | ~1.600 | `source_url`, `retrieved_at`, `document_version`, `platform`, `audience`, `category`, `language` |
| 2 | Shopee — Chính sách trả hàng & hoàn tiền | https://help.shopee.vn/portal/4/article/77251-CH%C3%8DNH-S%C3%81CH-TR%E1%BA%A2-H%C3%80NG-V%C3%80-HO%C3%80N-TI%E1%BB%80N | 2026-09-20 / 2026-03-11 | ~2.400 | `source_url`, `retrieved_at`, `document_version`, `platform`, `audience`, `category`, `language` |
| 3 | UNIQLO — Chính sách đổi & trả hàng | https://faq-vn.uniqlo.com/articles/vi/FAQ/Ch%C3%ADnh-s%C3%A1ch-%C4%91%E1%BB%95i-tr%E1%BA%A3 | 2026-09-20 / không nêu phiên bản rõ ràng | ~1.300 | `source_url`, `retrieved_at`, `document_version`, `platform`, `audience`, `category`, `language` |
| 4 | Biti's — Chính sách đổi trả | https://bitis.com.vn/pages/chinh-sach-doi-tra | 2026-09-20 / không nêu phiên bản rõ ràng | ~1.100 | `source_url`, `retrieved_at`, `document_version`, `platform`, `audience`, `category`, `language` |
| 5 | L'Oréal — Chính sách đổi trả | https://loreal-cpd-uat.myharavan.com/pages/chinh-sach-doi-tra | 2026-09-20 / không nêu phiên bản rõ ràng | ~900 | `source_url`, `retrieved_at`, `document_version`, `platform`, `audience`, `category`, `language` |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `source_url` | string | `https://help.shopee.vn/...` | Xác định nguồn gốc và kiểm soát độ mới, tin cậy của thông tin. |
| `retrieved_at` | date | `2026-09-20` | Cho biết ngày thu thập, giúp kiểm tra tính thời sự. |
| `document_version` | string | `2026-03-11` | Giúp phân biệt phiên bản chính sách và so sánh thay đổi theo thời gian. |
| `platform` | string | `Shopee`, `Long Châu` | Cho phép lọc theo kênh bán hàng để trả lời đúng ngữ cảnh. |
| `audience` | string | `buyer` | Hữu ích cho truy vấn theo đối tượng người mua hoặc người bán. |
| `category` | string | `return-policy` | Gộp các tài liệu theo loại chính sách, hỗ trợ lọc trực tiếp. |
| `language` | string | `vi` | Phân loại tài liệu theo ngôn ngữ, tránh nhầm lẫn khi hỏi bằng tiếng Việt. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| Long Châu | FixedSizeChunker (`fixed_size`) | ~8 | ~220 ký tự | Trung bình |
| Long Châu | SentenceChunker (`by_sentences`) | ~6 | ~300 ký tự | Có |
| Long Châu | RecursiveChunker (`recursive`) | ~5 | ~380 ký tự | Có, tốt nhất |
| Shopee | FixedSizeChunker (`fixed_size`) | ~10 | ~240 ký tự | Trung bình |
| Shopee | SentenceChunker (`by_sentences`) | ~7 | ~340 ký tự | Có |
| Shopee | RecursiveChunker (`recursive`) | ~6 | ~420 ký tự | Có, tốt nhất |

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — Nguyễn Văn Bảo**
- **Loại chiến lược:** RecursiveChunker
- **Mô tả & lý do chọn cho chủ đề này:** Chính sách đổi trả có nhiều phần, điều kiện, loại trừ và thời hạn. Recursive chunker phù hợp vì nó giữ được logic của từng mục như “điều kiện”, “thời hạn”, “loại trừ”, “hoàn tiền” mà không phá vỡ ngữ cảnh.
- **Code snippet (nếu custom):**
```python
# Không cần custom, dùng RecursiveChunker với separators chuẩn
chunker = RecursiveChunker(separators=["\n\n", "\n", ". ", " "])
chunks = chunker.chunk(text)
```

**Thành viên 2 — Nguyễn Minh Ngọc**
- **Loại chiến lược:** SentenceChunker
- **Mô tả & lý do chọn:** Với chính sách thương mại điện tử, mỗi câu thường chứa một điều kiện hoặc quy định rõ ràng. Sentence chunker giúp dễ truy xuất câu trả lời ngắn, tập trung, và giữ mạch logic của từng điều kiện.
- **Code snippet (nếu custom):**
```python
# Cắt theo câu, sau đó gom các câu ngắn thành chunk
chunker = SentenceChunker(chunk_size=2)
chunks = chunker.chunk(text)
```

**Thành viên 3 — Nguyễn Đình Anh**
- **Loại chiến lược:** FixedSizeChunker
- **Mô tả & lý do chọn:** Fixed size phù hợp khi cần triển khai nhanh và lấy các đoạn ngắn tương đối đồng đều. Dù có thể mất ngữ cảnh hơn, nó vẫn hữu ích cho việc so sánh lập luận giữa các nguồn có độ dài tương đối đồng đều.
- **Code snippet (nếu custom):**
```python
chunker = FixedSizeChunker(chunk_size=500, overlap=50)
chunks = chunker.chunk(text)
```

**Thành viên 4 — Trần Thị Thu Trang**
- **Loại chiến lược:** SentenceChunker
- **Mô tả & lý do chọn:** Chính sách đổi trả thường được viết theo từng điều kiện, mệnh đề và thời hạn riêng biệt. SentenceChunker giúp tôi giữ rõ từng quy định như “thời hạn”, “điều kiện áp dụng”, “loại trừ”, và “hoàn tiền”, dễ hơn cho việc truy xuất và trả lời trực tiếp.
- **Code snippet (nếu custom):**
```python
chunker = SentenceChunker(max_sentences_per_chunk=2)
chunks = chunker.chunk(text)
```

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Nguyễn Văn Bảo | RecursiveChunker | 8.5 | Giữ tốt ngữ cảnh, hợp với điều kiện & loại trừ | Có thể dài hơn nếu chunk quá rộng |
| Nguyễn Minh Ngọc | SentenceChunker | 8.0 | Rất dễ tìm thông tin theo câu, phù hợp câu hỏi ngắn | Có thể rời rạc nếu câu quá ngắn |
| Nguyễn Đình Anh | FixedSizeChunker | 7.0 | Dễ triển khai, đồng đều | Mất ngữ cảnh ở các chính sách có nhiều điều kiện |
| Trần Thị Thu Trang | SentenceChunker | 8.2 | Giữ được từng quy định rõ ràng, phù hợp cho câu hỏi chính xác | Có thể thiếu bối cảnh nếu câu hỏi yêu cầu nối nhiều điều kiện |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> RecursiveChunker là phương án tốt nhất vì tài liệu chính sách có nhiều tiêu đề, mục, và điều kiện. Khi lượng thông tin được giữ theo cấu trúc, hệ thống dễ lấy đúng đoạn chứa “điều kiện”, “thời hạn” và “loại trừ”, nên khả năng trả lời đúng cao hơn so với fixed-size đơn thuần.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Thời hạn đổi trả tối đa cho đơn hàng mua trực tuyến là bao lâu? | Thường là 30 ngày kể từ ngày nhận hàng; trường hợp lỗi nhà sản xuất có thể lên đến 6 tháng đối với UNIQLO, còn Long Châu cho phép 30 ngày và 1 năm với máy thiết bị y tế. | Long Châu / UNIQLO |
| 2 | Trường hợp nào được miễn phí vận chuyển đổi trả? | Nếu lỗi từ nhà bán, nhà sản xuất, hoặc vận chuyển, khách hàng thường được miễn phí. Biti's nêu rõ lỗi từ cửa hàng hoặc giao sai sản phẩm được miễn phí vận chuyển. | Biti's / Shopee |
| 3 | Sản phẩm đã qua sử dụng hoặc có tem bị rách có được đổi trả không? | Thường không. Hầu hết các chính sách đều yêu cầu sản phẩm còn mới, chưa qua sử dụng, nguyên vẹn, chưa giặt, và có đầy đủ phụ kiện/tem nhãn. | UNIQLO / Long Châu |
| 4 | Khách hàng cần gửi thông báo đổi trả trong thời gian nào nếu nhận thiếu phụ kiện hoặc hàng bị bể vỡ? | Với L'Oréal, khách hàng cần thông báo trong vòng 48 giờ kể từ ngày nhận hàng. | L'Oréal |
| 5 | Nếu khách hàng thay đổi quyết định sau khi nhận hàng, có thể yêu cầu trả hàng trên Shopee trong bao lâu không? | Người mua có thể gửi yêu cầu trong vòng 15 ngày kể từ ngày giao hàng thành công; đối với thực phẩm tươi sống/đông lạnh là 24 giờ. | Shopee |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Thời hạn đổi trả tối đa | RecursiveChunker | Có | Trả lời tốt vì chunk chứa thời hạn và ngoại lệ được giữ nguyên |
| 2 | Miễn phí vận chuyển đổi trả | SentenceChunker | Có | Câu hỏi tìm điều kiện “lỗi từ phía seller” rất phù hợp câu tách theo mệnh đề |
| 3 | Sản phẩm đã qua sử dụng | SentenceChunker | Có | Chunk chứa danh sách loại trừ dễ truy xuất hơn chunk dài |
| 4 | Thông báo đổi trả 48 giờ | RecursiveChunker | Có | Cấu trúc mục “thời gian thông báo” rất rõ |
| 5 | Thời hạn 15 ngày trên Shopee | RecursiveChunker | Có | Dễ tìm trong mục “điều kiện áp dụng” và “thời gian yêu cầu” |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Có, lọc metadata rất hữu ích cho các câu hỏi liên quan đến `platform`, `category` và `audience`. Ví dụ, khi hỏi về Shopee, việc lọc theo `platform=Shopee` giúp giảm nhiễu và tăng độ chính xác; đối với câu hỏi về L'Oréal hoặc UNIQLO, metadata cũng giúp tránh việc trộn thông tin các nền tảng khác nhau.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> - Chính sách đổi trả thường có nhịp cấu trúc rõ ràng: thời hạn, điều kiện, ngoại lệ, cách hoàn tiền. Đây là dạng dữ liệu rất phù hợp với retriever dựa trên chunking.
> - Metadata như `platform`, `category`, `audience` giúp cải thiện chất lượng truy xuất khi câu hỏi đòi hỏi giới hạn theo nền tảng hoặc đối tượng người dùng.
> - Recursive chunker cho kết quả tốt hơn nhờ giữ nguyên mạch “điều kiện → loại trừ → quy trình”, đặc biệt quan trọng với chính sách dài và có nhiều điểm ngoại lệ.

**Bài học rút ra khi so sánh trong nhóm:**
> Chúng tôi nhận thấy cùng một tài liệu nhưng chiến lược khác nhau cho kết quả khác biệt rõ rệt. Fixed size dễ triển khai nhưng dễ tách nhầm các điều kiện; Sentence và Recursive giữ được ý nghĩa pháp lý và ngữ cảnh tốt hơn, nên hiệu quả retrieval cao hơn.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Nếu làm lại, nhóm sẽ ưu tiên metadata chuẩn hóa từ đầu và dùng recursive chunking cho các chính sách theo mục. Ngoài ra, chúng tôi sẽ tách các tài liệu theo mô-đun như thời hạn, loại trừ, quy trình, hoàn tiền để tăng tính nhạy và giảm nhiễu khi truy xuất.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) |10 10 |
| Thiết kế chiến lược (Strategy Design) |15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) |9/ 10 |
| Thuyết trình (Demo) |0/ 5 |
| **Tổng phần nhóm** | 34/ 40** |
