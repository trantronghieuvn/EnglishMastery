from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from faster_whisper import WhisperModel
import os
import tempfile
import torch

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# KIỂM TRA PHẦN CỨNG: Ưu tiên GPU (cuda) nếu có, nếu không thì dùng CPU
device = "cuda" if torch.cuda.is_available() else "cpu"
# Nếu chạy CPU, hãy dùng model 'small' hoặc 'medium'. 'large-v3' chỉ nên chạy trên GPU.
model_size = "medium" if device == "cpu" else "large-v3"
compute_type = "int8" if device == "cpu" else "float16"

print(f"--- Đang tải model '{model_size}' trên {device.upper()} ---")

model = WhisperModel(model_size, device=device, compute_type=compute_type)

@app.post("/v1/audio/transcriptions")
async def transcribe(file: UploadFile = File(...), language: str = Form("en")):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    lang_code = "vi" if language == "vi" else "en"
    
    # THAY ĐỔI QUAN TRỌNG: 
    # 1. Giảm beam_size để tăng tốc độ.
    # 2. Thêm no_speech_threshold để chặn hoàn toàn lỗi "Hãy subscribe..."
    segments, info = model.transcribe(
        tmp_path,
        language=lang_code,
        beam_size=3, 
        initial_prompt="IPA, English learning, pronunciation", # Prompt ngắn gọn hơn
        condition_on_previous_text=False, 
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=1000), # Tăng thời gian lặng để lọc kỹ hơn
        no_speech_threshold=0.6, # Nếu độ tin cậy là im lặng > 60% thì bỏ qua
        repetition_penalty=1.2 # Chống lặp từ "cupcake cupcake..."
    )

    text = "".join([segment.text for segment in segments])
    os.remove(tmp_path)
    return {"text": text.strip()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)