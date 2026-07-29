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
| `github_search` | Tìm repository, release notes và dự án trending trên GitHub. | **Có — tool mới của nhóm** |
| `huggingface_search` | Tra cứu model, dataset và paper nổi bật trên Hugging Face. | **Có — tool mới của nhóm** |
| `hn_search` | Tìm thảo luận và đánh giá kỹ thuật trên Hacker News qua Algolia API. | **Có — tool mới của nhóm** |
| `youtube_transcript` | Trích xuất transcript/phụ đề từ video YouTube. | **Có — tool mới của nhóm** |

> Nhóm tự viết 4 tool mới (`github_search`, `huggingface_search`, `hn_search`, `youtube_transcript`), mỗi tool có `TOOL.md`, implementation trong `tools/<tên>/tool.py`, đăng ký trong `tools/__init__.py` và khai báo trong `artifacts/tools.yaml`. Tổng cộng agent có 14 tool đã declare.

## A3. Câu hỏi mẫu để thử

1. "Tìm 5 tin tức AI quan trọng trong tuần này và tóm tắt thành các gạch đầu dòng."
2. "Các bài đăng mới nhất của tài khoản `OpenAI` nói gì về model mới?"
3. "Đọc nội dung của URL này và tóm tắt 3 ý chính: https://example.com/article"
4. "Tìm các paper gần đây về retrieval-augmented generation và lập digest ngắn."
5. "Gửi bản tin này lên Telegram." Agent phải hỏi xác nhận trước khi gọi `send`.

## A4. Kịch bản demo đã rehearse

| Scenario | Tool trace cần thấy | Câu chuyện cải thiện version | Fallback run/transcript |
|---|---|---|---|
| Thiếu handle → phải hỏi lại | `clarify(response_type="text")`, không được gọi `timeline` | v0 → v1: v0 tự bịa `screenname="sama"` (prompt gốc bảo "pick a well-known account like Sam Altman"); v1 thêm guardrail hỏi lại. Case `R10_missing_handle`. | `runs/v1_B_base_openrouter_20260729T105133378808.json` |
| Xem bài mới của một tài khoản | `timeline(screenname="...")` | v1 → v2: v1 chữa cháy quá tay, hỏi lại cả khi tên đã rõ (`R01` fail). v2 thêm mapping tên → handle nên `R01` pass mà `R10` vẫn giữ. | `runs/v2_B_base_openrouter_20260729T105255278685.json` |
| Yêu cầu gửi Telegram | `clarify(response_type="yes_no")` trước; chỉ `send(confirmed=true)` sau xác nhận | v2 → v3: v0–v2 đều gọi thẳng `send`. v3 thêm confirmation boundary, đưa base lên 20/20. Case `R12_confirm_before_send`. | `runs/v3_B_base_openrouter_20260729T105344978755.json` |
| Lấy nội dung paper từ mã arXiv | `paper_text(arxiv_url="https://arxiv.org/abs/1706.03762")` | v6 → v7: agent truyền ID trần `1706.03762`; thêm rule chuyển ID thành URL đầy đủ. Case `B07`. | `runs/v7-b08_B_group_openrouter_20260729T114027083395.json` |
| Đổi nguồn giữa chừng sang mạng xã hội | đúng **một** lần `social_search`, gộp từ khoá vào một query | v6 → v7: agent tách thành 2 lần gọi `social_search`. v7 siết rule một-lần-mỗi-turn. Case `B08`. | `runs/v7-b08_B_group_openrouter_20260729T114027083395.json` |

---

# PHẦN B — Chi tiết / Bằng chứng

> Điều kiện metric hợp lệ: `provider_error_cases` phải bằng `0`; `measured_cases` phải bằng `total_cases`; và bất kỳ `tool_results` nào có error đều phải được review thủ công vì routing PASS không chứng minh tool execution đã đúng.

## B1. Version evidence

Nguồn: `artifacts/version_log.csv` + `runs/*.json`. Metric là `summary.case_accuracy`; mọi run dưới đây đều có `provider_error_cases = 0` và `measured_cases = total_cases` nên metric hợp lệ.

| Version | Prompt/tool change | Hypothesis | Metric | Before | After | Run File |
|---|---|---|---|---:|---:|---|
| v0 | baseline, chưa sửa gì | Đo hành vi của prompt/declaration gốc trước khi can thiệp | case_accuracy (base) | — | **0.70** | `runs/v0_B_base_openrouter_20260729T101637657660.json` |
| v1 | `system_prompt.md` + `tools.yaml` | Guardrail "thiếu handle/URL thì hỏi lại, không đoán" sẽ chặn hành vi bịa argument | case_accuracy (base) | 0.70 | **0.90** | `runs/v1_B_base_openrouter_20260729T105133378808.json` |
| v2 | `system_prompt.md` + `tools.yaml` | Thêm mapping tên người → handle sẽ chữa việc v1 hỏi lại quá tay | case_accuracy (base) | 0.90 | **0.95** | `runs/v2_B_base_openrouter_20260729T105255278685.json` |
| v3 | `system_prompt.md` + `tools.yaml` | Confirmation boundary rõ ràng sẽ chặn `send` khi chưa được xác nhận | case_accuracy (base) | 0.95 | **1.00** | `runs/v3_B_base_openrouter_20260729T105344978755.json` |
| — | *(không đổi artifact)* | **Kiểm chứng chéo:** đem đúng prompt v3 chạy trên suite group + 4 tool mới | case_accuracy (group) | 1.00 (base) | **0.50** | `runs/v3-on-group_B_group_openrouter_20260729T112535566698.json` |
| v4 | `system_prompt.md` + `tools.yaml` | Cho `send` tự dùng `confirmed=false` và thêm rule tái dùng ngữ cảnh multi-turn sẽ gỡ regression trên group | case_accuracy (group) | 0.50 | **0.80** | `runs/v4-fix2_B_group_openrouter_20260729T113008353836.json` |
| — | *(không đổi artifact)* | **Kiểm chứng ngược:** v4 có làm hỏng base không? | case_accuracy (base) | 1.00 | **0.85** | `runs/v4-on-base_B_base_openrouter_20260729T113301305018.json` |
| v5 | `system_prompt.md` + `tools.yaml` | Revert `send` về clarify-first (theo `R12` của base, vốn là chuẩn) nhưng giữ rule multi-turn của v4 | case_accuracy (base / group) | 0.85 / 0.80 | **0.90 / 0.70** | `runs/v5-revert_B_base_openrouter_20260729T113530534565.json`<br>`runs/v5-revert-group_B_group_openrouter_20260729T113634901222.json` |
| v6 | `data/eval_group.json` + `system_prompt.md` | Sửa `B05` theo chuẩn clarify-first của `R12`, thêm rule chuyển arXiv ID → URL đầy đủ | case_accuracy (group) | 0.70 | **0.90** | `runs/v6-final_B_group_openrouter_20260729T113931711922.json` |
| v7 | `system_prompt.md` | Rule "`social_search` đúng một lần mỗi turn, gộp từ khoá vào một query" sẽ chặn việc tách một chủ đề thành hai lần gọi | case_accuracy (group / base) | 0.90 / — | **1.00 / 1.00** | `runs/v7-b08_B_group_openrouter_20260729T114027083395.json`<br>`runs/v7-b08_B_base_openrouter_20260729T114142721987.json` |

**Kết quả cuối:** artifact `v7-b08+p8d0bf1b59d4c+t5c7b6be9432e` đạt **20/20 trên `eval_base.json`** và **10/10 trên `eval_group.json`** — cùng một prompt/tools hash, cả hai suite đều `case_accuracy = tool_routing_accuracy = argument_accuracy = multiturn_accuracy = 1.0`, không có `tool_results` nào trả error.

Hai dòng "*không đổi artifact*" không phải version mới. Đó là hai lần chạy kiểm chứng chéo trên cùng artifact đang có, và chúng là bằng chứng quan trọng nhất của báo cáo này (xem B2).

## B2. Failure analysis

Toàn bộ bảng dưới lấy từ `results[*].result.failures` và `results[*].result.actual_tool_calls` trong các run JSON thật.

### B2.1 — Baseline v0 trên `eval_base.json` (6/20 fail)

Điểm mấu chốt: agent **không hề chọn sai một cách ngẫu nhiên**. Nó tuân thủ chính xác một prompt được viết sai có chủ đích. Prompt v0 có nguyên văn *"just make a sensible guess"*, *"pick a well-known account like Sam Altman"*, *"assume a likely URL"*, *"just go ahead and do it"* — và mỗi câu đó sinh ra đúng một nhóm case fail.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| `R10_missing_handle` | `missing_info` | `timeline(screenname="sama")` | Thiếu handle nhưng agent tự điền `sama` thay vì hỏi lại | v1: prompt cấm đoán handle, bắt gọi `clarify` |
| `R11_missing_url` | `missing_info` | `fetch(url="https://example.com/article")` | Không có URL nhưng agent bịa ra một URL rồi đọc | v1: prompt cấm đoán URL, bắt gọi `clarify` |
| `R12_confirm_before_send` | `wrong_boundary` | `send(text="Bản tin này")` | Gửi Telegram ngay, không xác nhận trước | v3: thêm confirmation boundary `clarify(yes_no)` trước `send` |
| `R08_out_of_scope` | `out_of_scope` | `send(text="Nguyên hàm của x^2 là …")` | Tự giải tích phân rồi dùng `send` để trả lời, đáng lẽ không gọi tool nào | v1: prompt giới hạn phạm vi, ngoài research thì từ chối |
| `R14_out_of_scope_coding` | `out_of_scope` | `send(text="def fibonacci(n): …")` | Tự viết code Python rồi dùng `send` để trả lời | v1: như trên |
| `R13_parallel_web_and_tweets` | `wrong_arg_value` | `lookup(query="AI news", timeframe="day")` + `social_search(query="AI")` | Routing đúng cả 2 tool, nhưng nhét `news` vào `query` thay vì đặt `topic="news"` | Làm rõ convention tách `topic`/`timeframe` khỏi `query` trong `tools.yaml` |

### B2.2 — Regression do sửa quá tay (v1)

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| `R01_user_tweets_routing` | `wrong_tool` | `clarify(...)` thay vì `timeline` | v1 chặn việc đoán handle **quá mạnh** nên agent hỏi lại cả khi tên tài khoản đã rõ ràng | v2: thêm mapping tên người nổi tiếng → handle (Sam Altman → `sama`), giữ nguyên rule hỏi lại cho trường hợp thật sự mơ hồ |

Đây là bài học đắt nhất của vòng v1: **fix một failure_type có thể tạo ra failure_type ngược lại**. `R10` và `R01` kéo prompt về hai hướng đối nghịch, và chỉ v2 mới cân được cả hai.

### B2.3 — Regression khi đổi suite: v3 đạt 1.00 trên base nhưng 0.50 trên group

Đem đúng artifact v3 (`case_accuracy = 1.00` trên `eval_base.json`) chạy trên `eval_group.json` sau khi merge 4 tool mới → tụt xuống **0.50**, `multiturn_accuracy` chỉ **0.20**.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| `B06` | `wrong_tool` | `lookup(query="AI Agent evaluation", …)` | Lượt trước đã search rồi; lượt này bảo "tổng hợp lại" nhưng agent search lại từ đầu thay vì gọi `format` | v4: thêm rule tái dùng kết quả của lượt trước |
| `B10` | `missing_info` | `papers(query="AI Agent")` | User nói rõ "không có thêm thông tin nào khác" nhưng agent vẫn search mò thay vì `clarify` | v4: rule clarify lại khi vẫn không đủ dữ kiện định danh |
| `B07` | `wrong_arg_value` | `paper_text(arxiv_url="1706.03762")` | Truyền ID trần, case yêu cầu URL đầy đủ | v6: rule chuyển ID → `https://arxiv.org/abs/<id>` |
| `B08` | `extra_tool_call` | `social_search("OpenAI")` + `social_search("AI Agent")` | Tách một chủ đề thành hai lần gọi cùng một tool | v7: rule `social_search` đúng một lần/turn, gộp từ khoá |
| `B05` | `wrong_boundary` | `clarify(response_type="yes_no")` | **Không phải lỗi của agent** — xem B2.4 | v6: sửa kỳ vọng của case |

### B2.4 — Xung đột giữa hai suite: `R12` và `B05` đòi hai cơ chế ngược nhau

Đây là failure phải **review thủ công**, không thể tin kết quả chấm tự động:

- `eval_base.json::R12_confirm_before_send` yêu cầu `clarify(response_type="yes_no")` trước khi gửi.
- `eval_group.json::B05` (bản đầu) yêu cầu `send(confirmed=false)` để chính tool trả về `needs_confirmation`.

Cả hai kiểm tra **cùng một hành vi** — không được gửi khi chưa xác nhận — nhưng bằng hai cơ chế loại trừ nhau. Không một prompt nào thoả mãn đồng thời, và log chứng minh điều đó: v3 (clarify-first) pass `R12` nhưng fail `B05`; v4 (`confirmed=false`) pass `B05` nhưng làm `R12` fail trở lại, kéo base từ 1.00 xuống **0.85**.

Cách xử lý: `eval_base.json` là suite cố định và không được sửa, nên nó là chuẩn. v5 revert `send` về clarify-first, v6 sửa `B05` trong `eval_group.json` (file do nhóm sở hữu nên được phép thiết kế lại) cho khớp chuẩn của `R12`.

### B2.5 — Nhiễu giữa các lần chạy, không phải regression

Hai run v0 có **cùng artifact hash** `v0+pf0c107a9d7a1+t011c271ef0bb` nhưng cho kết quả khác nhau ở `R13`:

| Run | `tool_routing_accuracy` | `R13` fail như thế nào |
|---|---:|---|
| `…T100757972971.json` | 0.75 | `lookup` đúng tool, sai arg (`query="AI news"`, thiếu `topic`) |
| `…T102352859329.json` | 0.70 | gọi nhầm `timeline`, thiếu hẳn `social_search` |

Cùng prompt, cùng tool declaration, khác kết quả → đây là **non-determinism của model**, không phải hệ quả của thay đổi artifact. Hệ quả thực tiễn: chênh lệch ±0.05 giữa hai run **không đủ** để kết luận một hypothesis đúng hay sai. Các bước v1→v3 (+0.20, +0.05, +0.05) và v3→group (−0.50) đều vượt xa ngưỡng nhiễu này nên vẫn kết luận được; riêng những lần `R03`/`R13` fail rải rác đã được đối chiếu qua nhiều run trước khi kết luận là nhiễu.

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

### Fix nào thuộc `system_prompt.md`?

Những gì phụ thuộc vào **ngữ cảnh hội thoại và chính sách hành xử** — thứ mà một tool đơn lẻ không thể tự biết:

- **Boundary khi thiếu thông tin** (v1): "thiếu handle/URL thì hỏi lại, không đoán". Bản thân `timeline` không thể biết user đã cung cấp handle hay agent tự bịa ra.
- **Confirmation boundary** (v3): `clarify(yes_no)` trước `send`. Đây là chính sách của nhóm, không phải thuộc tính của tool.
- **Scope boundary** (v1): ngoài phạm vi research thì từ chối, không gọi tool nào.
- **Quy tắc tái dùng ngữ cảnh multi-turn** (v4): "lượt trước đã research rồi, lượt này bảo tổng hợp thì gọi `format`, đừng search lại". Chỉ prompt mới thấy được lịch sử hội thoại.
- **Rule một-lần-mỗi-turn cho `social_search`** (v7).

### Fix nào thuộc `tools.yaml`?

Những gì là **hợp đồng của chính tool** — đúng/sai không phụ thuộc ngữ cảnh:

- **Convention của argument**: `topic="news"` và `timeframe` phải tách khỏi `query` (`R13`). Declaration gốc chỉ ghi `topic` là *"Phân loại"* — quá mơ hồ để model suy ra.
- **Định dạng `arxiv_url`** (`B07`): declaration gốc ghi *"ID hoặc địa chỉ"*, tức là **chính nó cho phép** truyền ID trần. Model làm đúng theo mô tả; lỗi nằm ở mô tả.
- **Phân biệt tool gần nghĩa**: `timeline` (bài của một tài khoản) vs `social_search` (tìm theo từ khoá) vs `lookup` (web) vs `fetch` (chỉ khi user đã đưa URL).

Ranh giới thực dụng nhóm rút ra: **nếu model có thể làm đúng chỉ bằng cách đọc kỹ declaration thì fix thuộc `tools.yaml`; nếu cần biết lịch sử hội thoại hoặc chính sách của nhóm thì fix thuộc `system_prompt.md`.** Đặt sai chỗ sẽ khiến prompt phình ra để bù cho declaration kém, và mỗi rule thêm vào prompt lại là một cơ hội tạo regression như `R01` ở v1.

### Failure nào cần review thủ công thay vì tin điểm tự động?

Ba loại, và cả ba đều đã xảy ra thật:

1. **`B05` — case eval sai, không phải agent sai.** Điểm tự động báo FAIL, nhưng đọc log thì agent đang hành xử đúng theo chuẩn của `R12`. Nếu tin điểm số mà sửa prompt, nhóm đã phá vỡ `eval_base.json` (và thực tế v4 đã phá thật: base 1.00 → 0.85).
2. **`R13`/`R03` — nhiễu giữa các lần chạy.** Cùng artifact hash cho hai kết quả khác nhau (B2.5). Phải chạy lại và đối chiếu nhiều run mới phân biệt được nhiễu với regression thật.
3. **Routing PASS không chứng minh tool chạy đúng.** Nhóm đã kiểm tra `tool_results` của hai run cuối: không có entry nào mang `error`. Nếu chỉ nhìn `case_accuracy` thì một tool ném exception vẫn có thể được tính PASS ở routing.

### Điều lớn nhất học được

**v3 đạt 1.00 trên `eval_base.json` nhưng chỉ 0.50 trên `eval_group.json`.** Cùng một prompt, không đổi một ký tự nào. Con số 1.00 hoàn toàn thật, nhưng nó chỉ chứng minh prompt khớp với 20 case đã biết — không chứng minh agent tốt. Chỉ đến khi có suite thứ hai do người khác viết, cộng thêm 4 tool mới, thì mới lộ ra rằng prompt chưa hề xử lý được multi-turn (`multiturn_accuracy` rớt xuống 0.20).

### Nếu có thêm thời gian sẽ cải thiện gì?

- **Chạy mỗi version 3 lần** rồi lấy trung bình, để ngưỡng nhiễu ±0.05 ở B2.5 không còn ảnh hưởng kết luận.
- **Thống nhất chuẩn confirmation trước khi viết eval**, để không lặp lại vòng lãng phí v4 → v5 → v6 vì hai suite định nghĩa cùng một hành vi theo hai cách.
- **Bổ sung eval case cho 4 tool mới.** Hiện `github_search`, `huggingface_search`, `hn_search`, `youtube_transcript` đã declare và ảnh hưởng routing, nhưng chưa case nào chấm trực tiếp chúng — tức là còn một vùng chưa được đo.
- **Tách rule prompt theo tool** thay vì gộp thành một danh sách dài, để lần sau sửa một rule không kéo theo regression ở tool khác như `R01`.
