# github_search

## Mô tả Tool
Tool `github_search` hỗ trợ tìm kiếm kho mã nguồn (Repositories), danh sách Release Notes, dự án Open Source hoặc Trending Projects trên GitHub liên quan đến các chủ đề nghiên cứu AI, phần mềm và công nghệ.

## Khi nào nên dùng
- Khi người dùng muốn tìm kiếm dự án open-source, codebase, framework hoặc thư viện mã nguồn mở trên GitHub.
- Khi cần tra cứu các dự án nổi bật (dựa theo lượt stars, forks, hoặc cập nhật gần đây) về một chủ đề công nghệ.
- Khi cần tìm repository chính thức của một mô hình, thuật toán hoặc công bố khoa học.

## Khi nào KHÔNG nên dùng
- KHÔNG dùng để tra cứu tin tức thời sự chung hoặc thảo luận không thuộc GitHub (dùng `lookup` hoặc `hn_search`).
- KHÔNG dùng để tìm kiếm các model/dataset đã đóng gói trên Hugging Face (dùng `huggingface_search`).
- KHÔNG dùng để tìm kiếm bài báo khoa học dạng arXiv PDF (dùng `papers`).

## Tham số đầu vào (Arguments)
- `query` (string, bắt buộc): Từ khóa tìm kiếm (ví dụ: `"machine learning"`, `"llm agent"`, `"rag framework"`).
- `sort` (string, tùy chọn): Tiêu chí sắp xếp. Hỗ trợ: `"best match"` (mặc định), `"stars"`, `"forks"`, `"updated"`.

## Định dạng trả về
Dictionary dạng:
```json
{
  "error": null,
  "data": {
    "total_count": 1500,
    "items": [
      {
        "name": "repo-name",
        "full_name": "owner/repo-name",
        "html_url": "https://github.com/owner/repo-name",
        "description": "Mô tả dự án",
        "stargazers_count": 12000,
        "forks_count": 1500,
        "language": "Python",
        "updated_at": "2026-07-20T10:00:00Z",
        "owner": "owner"
      }
    ]
  }
}
```
Nếu có lỗi:
```json
{
  "error": "github_search failed: <chi_tiet_loi>"
}
```
