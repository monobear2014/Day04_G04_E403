# Day 04 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. Xong trước 11:30 để làm tài liệu phụ trợ khi demo.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. Có thể hoàn thiện sau buổi debate để nộp bài.

## Team

- Team: G04
- Members: 
    - 2A202601871 | Nguyễn Thanh Tùng | Tool Developer
    - 2A202602016 | Nguyễn Hoài Nam | UI/ Deploy Engineer 
    - 2A202601627 | Nguyễn Quốc Hiệu | Agent/Prompt Lead
    - 2A202602036 | Nguyễn Khắc Huy | Agent/Prompt Lead
    - 2A202601701 | Phan Trần Tường Vy | QA/Failure Analyst
    - 2A202601999 | Trần Đoàn Quang Vũ | Eval Engineer
    - 2A202601803 | Lê Kim Nam | Report & Demo Lead
- Provider/model: gpt-4o-mini

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Đây là research agent hỗ trợ tìm và đọc thông tin từ web hoặc mạng xã hội, sau đó tổng hợp kết quả thành digest Markdown. Agent cũng có thể hỏi lại khi yêu cầu còn thiếu dữ kiện, và yêu cầu xác nhận trước các hành động gửi/publish.

**Link dùng thử (truy cập được trong showdown):**

`https://zealand-exceed-productive-interests.trycloudflare.com/`

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| `clarify` | Hỏi lại để lấy thông tin còn thiếu hoặc xác nhận lựa chọn/yes-no. | Không |
| `timeline` | Lấy các bài đăng gần đây của một tài khoản mạng xã hội. | Không |
| `social_search` | Tìm bài đăng mạng xã hội theo từ khóa, theo Latest hoặc Top. | Không |
| `lookup` | Tìm kiếm thông tin trên web, gồm general hoặc news theo timeframe. | Không |
| `fetch` | Đọc nội dung từ một URL cụ thể. | Không |
| `format` | Chuyển các kết quả đã có thành digest Markdown theo mẫu. | Không |
| `send` | Gửi văn bản lên Telegram sau khi có xác nhận rõ ràng. | Không — optional built-in |
| `policy` | Tìm quy định nội bộ liên quan đến nghiên cứu, nguồn, dữ liệu và tool usage. | Không — optional built-in |
| `papers` | Tìm bài báo khoa học trên arXiv. | Không — optional built-in |
| `paper_text` | Tải và trích xuất một phần văn bản từ paper arXiv. | Không — optional built-in |

> Chưa có tool mới do nhóm tự thêm trong starter hiện tại. Trước khi nộp cần bổ sung ít nhất một tool mới, cùng `TOOL.md`, implementation, đăng ký trong `tools/__init__.py` và khai báo trong `artifacts/tools.yaml`.

## A3. Câu hỏi mẫu để thử

1. "Tìm 5 tin tức AI quan trọng trong tuần này và tóm tắt thành các gạch đầu dòng."
2. "Các bài đăng mới nhất của tài khoản `OpenAI` nói gì về model mới?"
3. "Đọc nội dung của URL này và tóm tắt 3 ý chính: https://example.com/article"
4. "Tìm các paper gần đây về retrieval-augmented generation và lập digest ngắn."
5. "Gửi bản tin này lên Telegram." Agent phải hỏi xác nhận trước khi gọi `send`.

## A4. Kịch bản demo đã rehearse

| Scenario | Tool trace cần thấy | Câu chuyện cải thiện version | Fallback run/transcript |
|---|---|---|---|
| Tổng hợp tin AI tuần này | `lookup(topic="news", timeframe="week")` → `format(template="bullets")` | v0 → v1: mô tả/routing làm rõ yêu cầu có từ “tin tức” phải dùng `lookup` với `topic="news"`, thay vì tìm mạng xã hội. | `runs/<v1-base-run>.json` |
| Xem bài mới của một tài khoản | `timeline(screenname="...")` | v1 → v2: phân biệt rõ “bài mới của tài khoản” (timeline) với “tìm bài theo từ khóa” (social_search). | `runs/<v2-base-run>.json` |
| Tóm tắt URL người dùng cung cấp | `fetch(url="...")` → `format(...)` | v2 → v3: yêu cầu URL cụ thể luôn ưu tiên `fetch`, không đoán URL hoặc gọi `lookup` không cần thiết. | `runs/<v3-base-run>.json` |
| Yêu cầu gửi Telegram | `clarify(response_type="yes_no")` trước; chỉ `send(confirmed=true)` sau xác nhận | Củng cố confirmation boundary: không được gửi khi người dùng mới yêu cầu hành động, chưa xác nhận. | `transcripts/<send-confirmation>.transcript.json` |

> Các tên file fallback ở trên là vị trí cần thay bằng file run/transcript thật sau khi chạy. Không dùng bảng này làm bằng chứng thay cho log.

---

# PHẦN B — Chi tiết / Bằng chứng

> Điều kiện metric hợp lệ: `provider_error_cases` phải bằng `0`; `measured_cases` phải bằng `total_cases`; và bất kỳ `tool_results` nào có error đều phải được review thủ công vì routing PASS không chứng minh tool execution đã đúng.

## B1. Version evidence

Fill from `artifacts/version_log.csv` and `runs/*.json`.

| Version | Prompt/tool change | Hypothesis | Metric name | Before | After | Run File |
|---|---|---|---|---:|---:|---|
| v0 | baseline |  |  |  |  |  |
| v1 |  |  |  |  |  |  |
| v2 |  |  |  |  |  |  |
| v3 |  |  |  |  |  |  |

## B2. Failure analysis

Use actual failures from `results[*].result.failures`.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
|  |  |  |  |  |

## B3. Team eval cases

List the 10 cases added to `data/eval_group.json`:

- 5 single-turn
- 5 multi-turn

This section is for the mandatory team-authored eval set. Optional built-ins do
not belong here.

File template để trống có chủ đích; nhóm phải tự thiết kế đủ 10 case.

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
|  |  |  |  |

## B4. Live chat evidence

Use `transcripts/*.transcript.json`.

| Scenario/Turn | Version | Tool Calls + Args | Transcript/Run | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

## B5. Tool capability evidence

Phân loại rõ tool mới bắt buộc, optional built-in và tool đủ điều kiện bonus. Chỉ ghi Telegram/PDF nếu nhóm thực sự dùng; base report không cần chúng.

UI is core deliverable, not bonus. Do not list it here.

| Category | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Must-have: tool mới đầu tiên |  |  |  |
| Optional built-in |  |  |  |
| Bonus: tool mới thứ 4 trở đi |  |  |  |

## B6. Reflection

- Which fixes belonged in `system_prompt.md`?
- Which fixes belonged in `tools.yaml`?
- Which failure needed manual review instead of automatic grading?
- What would you improve next?
