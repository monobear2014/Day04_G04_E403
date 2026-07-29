# huggingface_search

## Mô tả Tool
Tool `huggingface_search` hỗ trợ tra cứu các AI Models, Datasets, hoặc các Bài báo khoa học hot (Daily Papers) mới phát hành trên nền tảng Hugging Face thông qua SDK `huggingface_hub`.

## Khi nào nên dùng
- Khi người dùng muốn tìm kiếm các AI/ML checkpoint models (ví dụ: Llama, Mistral, Whisper, Qwen, DeepSeek).
- Khi cần tìm các bộ dữ liệu (Datasets) phục vụ huấn luyện hoặc benchmark AI.
- Khi muốn cập nhật bài báo khoa học hot (Papers) trên Hugging Face.

## Khi nào KHÔNG nên dùng
- KHÔNG dùng để tìm kiếm repositories/source code thuần trên GitHub (dùng `github_search`).
- KHÔNG dùng để tra cứu tin tức thời sự đại chúng (dùng `lookup`).
- KHÔNG dùng để trích xuất vietsub/transcript video (dùng `youtube_transcript`).

## Tham số đầu vào (Arguments)
- `query` (string, bắt buộc): Từ khóa tìm kiếm (ví dụ: `"llama-3"`, `"sentiment analysis"`, `"vietnamese speech"`).
- `search_type` (string, enum: `["models", "datasets", "papers"]`, mặc định: `"models"`): Loại đối tượng cần tra cứu trên Hugging Face.

## Định dạng trả về
Dictionary dạng:
```json
{
  "error": null,
  "data": {
    "search_type": "models",
    "count": 10,
    "items": [
      {
        "id": "meta-llama/Llama-3.1-8B-Instruct",
        "author": "meta-llama",
        "downloads": 500000,
        "likes": 3200,
        "pipeline_tag": "text-generation",
        "tags": ["llama-3", "text-generation"],
        "last_modified": "2026-07-15",
        "url": "https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct"
      }
    ]
  }
}
```
Nếu có lỗi:
```json
{
  "error": "huggingface_search failed: <chi_tiet_loi>"
}
```
