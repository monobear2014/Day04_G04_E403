# youtube_transcript

## Mô tả Tool
Tool `youtube_transcript` hỗ trợ trích xuất phụ đề/transcript (vietsub, english sub, v.v.) từ video trên YouTube (ví dụ: các bài keynote, hội thảo khoa học, demo sản phẩm, bài giảng AI). Tool tự động nhận diện và trích xuất Video ID từ cả đường dẫn URL lẫn mã ID video.

## Khi nào nên dùng
- Khi người dùng cung cấp link YouTube (hoặc ID video) và yêu cầu tóm tắt nội dung, dịch phụ đề, hoặc tìm kiếm thông tin có trong lời thoại của video.
- Khi cần lấy nội dung bài phát biểu, bài giảng, hội thảo trên YouTube dưới dạng văn bản.

## Khi nào KHÔNG nên dùng
- KHÔNG dùng cho bài báo khoa học PDF trên arXiv (dùng `paper_text`).
- KHÔNG dùng để lấy trang web HTML thông thường (dùng `fetch`).
- KHÔNG dùng khi video không có phụ đề/transcript.

## Tham số đầu vào (Arguments)
- `video_url_or_id` (string, bắt buộc): Đuờng dẫn URL đầy đủ (ví dụ: `"https://www.youtube.com/watch?v=dQw4w9WgXcQ"`) hoặc ID của video YouTube (ví dụ: `"dQw4w9WgXcQ"`).
- `languages` (array of strings, mặc định: `["vi", "en"]`): Danh sách mã ngôn ngữ ưu tiên theo thứ tự giảm dần.

## Định dạng trả về
Dictionary dạng:
```json
{
  "error": null,
  "data": {
    "video_id": "dQw4w9WgXcQ",
    "languages": ["vi", "en"],
    "full_text": "Toàn bộ văn bản lời thoại hợp nhất...",
    "transcript": [
      {
        "text": "Nội dung câu thứ nhất",
        "start": 0.0,
        "duration": 2.5
      }
    ]
  }
}
```
Nếu có lỗi:
```json
{
  "error": "youtube_transcript failed: <chi_tiet_loi>"
}
```
