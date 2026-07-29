# hn_search

## Mô tả Tool
Tool `hn_search` hỗ trợ tìm kiếm bài viết, tin tức công nghệ và thảo luận chất lượng cao của cộng đồng lập trình viên & chuyên gia AI trên Hacker News thông qua Algolia Search API.

## Khi nào nên dùng
- Khi người dùng muốn tìm kiếm phản hồi, ý kiến thảo luận của cộng đồng dev / AI về một công nghệ, thư viện, hoặc sự kiện công nghệ mới ra mắt.
- Khi cần xem các bài viết top-trending, tin tức nổi bật trên Hacker News.

## Khi nào KHÔNG nên dùng
- KHÔNG dùng để tải file PDF bài báo khoa học (dùng `papers` hoặc `paper_text`).
- KHÔNG dùng để tra cứu kho mã nguồn GitHub (dùng `github_search`).
- KHÔNG dùng để lấy phụ đề video YouTube (dùng `youtube_transcript`).

## Tham số đầu vào (Arguments)
- `query` (string, bắt buộc): Từ khóa tìm kiếm (ví dụ: `"deepseek"`, `"gpt-4o"`, `"rust vs python"`).
- `limit` (integer, mặc định: 5): Số lượng kết quả thảo luận trả về (từ 1 đến 50).

## Định dạng trả về
Dictionary dạng:
```json
{
  "error": null,
  "data": {
    "count": 5,
    "items": [
      {
        "title": "DeepSeek-V3 Technical Report",
        "url": "https://example.com/article",
        "author": "tech_dev",
        "points": 1250,
        "num_comments": 430,
        "created_at": "2026-07-01T12:00:00Z",
        "hn_url": "https://news.ycombinator.com/item?id=12345678",
        "story_text": null
      }
    ]
  }
}
```
Nếu có lỗi:
```json
{
  "error": "hn_search failed: <chi_tiet_loi>"
}
```
