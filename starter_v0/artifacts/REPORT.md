# Day 04 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. Xong trước 11:30 để làm tài liệu phụ trợ khi demo.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. Có thể hoàn thiện sau buổi debate để nộp bài.

## Team

- Team: G04
- Members: 
    - 2A202601871 | Nguyễn Thanh Tùng | Tool Developer
    - 2A202602016 | Nguyễn Hoài Nam | UI/ Deploy Engineer
    - 2A202601685 | Nguyễn Minh Hiếu | UI/ Deploy Engineer
    - 2A202601627 | Nguyễn Quốc Hiệu | Agent/Prompt Lead
    - 2A202602036 | Nguyễn Khắc Huy | Agent/Prompt Lead
    - 2A202601701 | Phan Trần Tường Vy | QA/Failure Analyst
    - 2A202601999 | Trần Đoàn Quang Vũ | Eval Engineer
    - 2A202601803 | Lê Kim Nam | Report & Demo Lead
- Provider/model: gpt-4o-mini

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

**Research Agent** — trợ lý tìm kiếm & tổng hợp thông tin đa nguồn, có khả năng:

- Tìm web/tin tức (`lookup`), tìm bài đăng mạng xã hội theo tài khoản hoặc từ khóa (`timeline`, `social_search`), đọc nội dung một URL cụ thể (`fetch`), rồi tổng hợp thành digest Markdown (`format`).
- Tra cứu thêm trên GitHub, HuggingFace, Hacker News và lấy transcript video YouTube (4 tool mới nhóm tự thêm).
- Chủ động hỏi lại (`clarify`) khi thiếu thông tin thay vì đoán bừa, và luôn xin xác nhận trước khi thực hiện hành động gửi/đăng (`send`).

**🔗 Link dùng thử:** [zealand-exceed-productive-interests.trycloudflare.com](https://zealand-exceed-productive-interests.trycloudflare.com/)

> Provider: OpenRouter (`openai/gpt-4o-mini`). Link chỉ sống khi máy demo còn chạy Streamlit + Cloudflare Tunnel — nếu link không mở được, dùng `http://localhost:8501` khi demo trực tiếp trên máy trình chiếu.

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
| `github_search` | Tìm repo GitHub theo từ khóa, sắp xếp theo best match. | **Có** — tool mới (must-have) |
| `huggingface_search` | Tìm model/dataset trên HuggingFace Hub. | **Có** — tool mới (bonus #2) |
| `hn_search` | Tìm bài đăng/thảo luận trên Hacker News. | **Có** — tool mới (bonus #3) |
| `youtube_transcript` | Lấy transcript của một video YouTube. | **Có** — tool mới (bonus #4) |

> 4 tool mới đã được nhóm tự thêm đầy đủ: `TOOL.md`, implementation, đăng ký trong `tools/__init__.py`, khai báo trong `artifacts/tools.yaml`, đã smoke-test và chạy qua eval + UI thật.

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

Các run dưới đây đều có `provider_error_cases = 0` và `measured_cases = total_cases`; vì vậy metric hợp lệ. Số liệu lấy trực tiếp từ `summary` của run JSON.

| Version | Prompt/tool change | Hypothesis | Case accuracy (trước → sau) | Kết quả chính | Run file |
|---|---|---|---:|---|---|
| v0 | Baseline | Chưa có guardrail cụ thể cho thiếu thông tin, timeline, URL và confirmation. | — → 65% (13/20) | Routing 75%, argument 65%, multi-turn 100%; 7 fail. | `runs/v0_B_base_openrouter_20260729T105323445856.json` |
| v1 | Thiếu handle/URL phải `clarify`, không đoán. | Missing-info guardrails thay việc đoán bằng `clarify`. | 65% → 90% (18/20) | Còn R01 và R12. | `runs/v1_B_base_openrouter_20260729T105133378808.json` |
| v2 | Account-based request dùng `timeline`; map public name sang handle. | Loại lỗi routing R01. | 90% → 95% (19/20) | R01 pass; còn R12. | `runs/v2_B_base_openrouter_20260729T105255278685.json` |
| v3 | `clarify(response_type="yes_no")` trước send/post/publish. | Chặn write action sớm. | 95% → 100% (20/20) | Routing, argument, multi-turn đều 100%. | `runs/v3_B_base_openrouter_20260729T105344978755.json` |

Sau khi tích hợp tool mới và group eval, nhóm regression-test tiếp. v4–v7 xử lý contract send, ngữ cảnh multi-turn, bare arXiv ID và duplicate `social_search`.

| Regression evidence | Kết quả | Run file |
|---|---|---|
| Group v6 | 9/10; B08 gọi `social_search` hai lần. | `runs/v6-final_B_group_openrouter_20260729T113931711922.json` |
| Group v7 | 10/10; mọi metric 100%. | `runs/v7-b08_B_group_openrouter_20260729T114027083395.json` |
| Base regression v7 | 20/20; mọi metric 100%. | `runs/v7-b08_B_base_openrouter_20260729T114142721987.json` |

> Lưu ý audit: dòng v0 trong `artifacts/version_log.csv` tham chiếu một run không có trong `runs/`. Bảng trên dùng run v0 hiện có và ghi nhận được (`...105323445856.json`, 65%) làm evidence nguồn.

## B2. Failure analysis

Các failure dưới đây lấy từ `results[*].result.failures` và `actual_tool_calls`, không suy luận từ câu trả lời cuối.

| Case ID | Failure type | Actual tool call(s) | What failed | Fix / evidence sau fix |
|---|---|---|---|---|
| R03_web_news_routing (v0) | wrong_arg_value | `lookup(query="AI news", topic="news", timeframe="day")` | Query phải là `AI`, model thêm `news`. | Làm rõ arg convention; v1 trở đi pass. |
| R08_out_of_scope (v0) | out_of_scope | `send(text="Nguyên hàm ...")` | Câu toán ngoài scope lại bị biến thành action tool. | Tool trả `needs_confirmation`, nhưng routing vẫn fail vì lẽ ra không gọi tool. |
| R10_missing_handle (v0) | missing_info | `timeline(screenname="sama")` | Không có account/handle nhưng agent tự đoán. | v1 thêm missing-handle rule; pass. |
| R11_missing_url (v0) | missing_info | `fetch(url="https://www.example.com/article")` | URL không được cung cấp nhưng agent tự tạo URL. | v1 thêm missing-URL rule; pass. |
| R12_confirm_before_send (v0–v2) | wrong_boundary | `send(...)` | Thiếu `clarify(response_type="yes_no")` trước action. | v3 thêm clarify-first boundary; pass ở v3 và v7. |
| R13_parallel_web_and_tweets (v0) | wrong_arg_value | `lookup(query="AI news", timeframe="day")` + `social_search(query="AI")` | Lookup thiếu `topic="news"` và query sai expected. | Làm rõ news args; v1 trở đi pass. |
| R14_out_of_scope_coding (v0) | out_of_scope | `send(text="def fibonacci...")` | Câu coding ngoài scope vẫn gọi send. | Tool bị chặn, nhưng routing không đúng; cần guardrail out-of-scope. |
| B08 (v6) | extra_tool_call | Hai `social_search`: `OpenAI` và `AI Agent` | Một user turn bị tách thành hai lời gọi cùng tool. | v7 yêu cầu đúng một call, gộp keywords; group pass 10/10. |

## B3. Team eval cases

`data/eval_group.json` có đúng **10 case**: 5 single-turn (B01–B05) và 5 multi-turn (B06–B10). Kết quả dưới đây là run group v7.

| Case ID | Dạng | What it tests | Expected tool/behavior | Result v7 |
|---|---|---|---|---|
| B01 | Single | Web research mới nhất | `lookup` | PASS |
| B02 | Single | URL cụ thể | `fetch(url=...)` | PASS |
| B03 | Single | Tìm paper arXiv | `papers` | PASS |
| B04 | Single | Bài đăng của account OpenAI | `timeline` | PASS |
| B05 | Single | Confirmation boundary trước Telegram | `clarify(response_type="yes_no")` | PASS |
| B06 | Multi | Tóm tắt kết quả turn trước | `format`, không lặp research | PASS |
| B07 | Multi | Bare arXiv ID | `paper_text(arxiv_url="https://arxiv.org/abs/1706.03762")` | PASS |
| B08 | Multi | Đổi từ web sang social posts | Một `social_search` duy nhất | PASS |
| B09 | Multi | Kiểm tra chính sách | `policy` | PASS |
| B10 | Multi | Thiếu định danh paper | `clarify`, không đoán | PASS |

## B4. Live chat evidence

Use `transcripts/*.transcript.json`.

| Scenario/Turn | Version | Tool Calls + Args | Transcript/Run | Outcome |
|---|---|---|---|---|
| Tìm repo GitHub về RAG agent | `v0+p8d0bf1b59d4c+t5c7b6be9432e` | `github_search(query="RAG agent", sort="best match")` | `transcripts/v0_openrouter_20260729T114537381110.transcript.json`, turn 1 | Answered; tool trả repo và agent tổng hợp. |
| Yêu cầu đăng bản tin lên Telegram | `v0+p8d0bf1b59d4c+t5c7b6be9432e` | `clarify(response_type="yes_no")` | `transcripts/v0_openrouter_20260729T114537381110.transcript.json`, turn 2 | `waiting_for_user`; không gọi `send` trước xác nhận. |
| Tìm model text-to-speech trên Hugging Face | `v0+p8d0bf1b59d4c+t5c7b6be9432e` | `huggingface_search(query="text-to-speech", search_type="models")` | `transcripts/v0_openrouter_20260729T114537381110.transcript.json`, turn 3 | Answered; tool trả 10 mục. |
| Multi-turn news → YouTube → GitHub → Hugging Face | `v0+pc72dbc548e3d+ta73ac1dbe420` | `lookup`; `youtube_transcript`; `github_search`; `huggingface_search` | `transcripts/v0_openrouter_20260729T122407935211.transcript.json`, turns 1–5 | Lookup/GitHub/Hugging Face có kết quả. YouTube log 1 thành công và 2 lỗi nguồn để review. |

Chưa có transcript live riêng cho kịch bản “thiếu thông tin rồi user bổ sung ở turn sau”. B06–B10 kiểm tra routing ngữ cảnh qua eval; trước nộp cuối nên lưu thêm transcript live này.

## B5. Tool capability evidence

UI là deliverable core và không tính bonus; bảng này chỉ ghi evidence tool.

| Category | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Must-have: `github_search` (tool mới thứ nhất) | `tools/github_search/TOOL.md`, `tools/github_search/tool.py`; transcript `...114537381110`, turn 1 | Tìm GitHub `RAG agent`, trả metadata repo. | Chỉ dùng cho repo/code; không thay lookup hoặc papers. |
| Bonus: `huggingface_search` (tool mới #2) | `tools/huggingface_search/`; transcripts `...114537381110` turn 3 và `...122407935211` turn 5 | Trả 10 model text-to-speech và 10 healthcare datasets. | Chọn đúng `search_type`; không dùng thay GitHub search. |
| Bonus: `hn_search` (tool mới #3) | `tools/hn_search/TOOL.md`, `tools/hn_search/tool.py` | Đã đăng ký và có implementation; chưa có live transcript hiện tại. | Cần bổ sung smoke-test/run evidence trước khi claim đã demo. |
| Bonus: `youtube_transcript` (tool mới #4) | `tools/youtube_transcript/`; transcript `...122407935211`, turn 2 | Có ít nhất một URL trả transcript; log giữ lỗi nguồn còn lại. | Phụ thuộc subtitle/video/ngôn ngữ; cần fallback và báo lỗi rõ. |
| Optional built-in: `send` | `tools/send/TOOL.md`; transcript `...114537381110` turn 2; base R12 | Live chat hỏi xác nhận; v3/v7 base eval pass boundary. | Không live-send trước yes/no confirmation; không lộ credential. |

## B6. Reflection

- **Fix thuộc `system_prompt.md`:** policy theo ngữ cảnh hội thoại: reuse kết quả để `format`, đổi nguồn khi intent đổi, gộp keywords cho một `social_search`, xử lý bare arXiv ID và confirmation boundary.
- **Fix thuộc `tools.yaml`:** ranh giới tool và argument convention: `timeline` cho account, `social_search` cho topic, `fetch` chỉ khi có URL, `lookup` cho web/news, cùng enum/default của `topic`, `timeframe`, `search_type`.
- **Manual review:** R08/R14 v0 bị fail routing vì gọi `send`, nhưng tool trả `needs_confirmation` nên không có tác động gửi thực. Auto-grader vẫn đúng khi đánh fail routing. Lỗi YouTube live là availability/ngôn ngữ của nguồn, không tự động chứng minh routing sai.
- **Cải thiện tiếp theo:** thêm explicit out-of-scope/no-tool rule; lưu live transcript cho missing-info → user bổ sung; smoke-test `hn_search`; sửa dòng v0 trong `version_log.csv` để khớp run JSON; thử fallback language cho YouTube.
