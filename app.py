import json
import re
import uuid
from pathlib import Path

import torch
from flask import Flask, render_template, request, url_for
from PIL import Image, UnidentifiedImageError
from torch import nn
from torchvision import models, transforms
from werkzeug.utils import secure_filename


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "model" / "model_oxford102_official.pth"
CLASS_NAMES_PATH = BASE_DIR / "model" / "class_names_zh_en.json"
UPLOAD_DIR = BASE_DIR / "static" / "uploads"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024
app.config["UPLOAD_FOLDER"] = UPLOAD_DIR
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

preprocess = transforms.Compose(
    [
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ]
)


def parse_class_name(raw_name):
    match = re.match(r"^(.*?)\s*\((.*?)\)\s*$", raw_name)
    if not match:
        return raw_name, raw_name
    return match.group(1).strip(), match.group(2).strip()


def load_class_names():
    with CLASS_NAMES_PATH.open("r", encoding="utf-8") as f:
        raw_mapping = json.load(f)

    class_names = []
    for idx in range(len(raw_mapping)):
        raw_name = raw_mapping[str(idx)]
        zh_name, en_name = parse_class_name(raw_name)
        class_names.append(
            {
                "id": idx,
                "raw": raw_name,
                "zh": zh_name,
                "en": en_name,
            }
        )
    return class_names


def load_model(num_classes):
    model = models.resnet18(weights=None)
    model.fc = nn.Linear(model.fc.in_features, num_classes)

    state_dict = torch.load(MODEL_PATH, map_location=DEVICE)
    if isinstance(state_dict, dict) and "model_state_dict" in state_dict:
        state_dict = state_dict["model_state_dict"]
    elif isinstance(state_dict, dict) and "state_dict" in state_dict:
        state_dict = state_dict["state_dict"]

    model.load_state_dict(state_dict)
    model.to(DEVICE)
    model.eval()
    return model


CLASS_NAMES = load_class_names()
MODEL = load_model(len(CLASS_NAMES))


def allowed_file(filename):
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def predict_image(image_path, top_k=5):
    image = Image.open(image_path).convert("RGB")
    tensor = preprocess(image).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        logits = MODEL(tensor)
        probs = torch.softmax(logits, dim=1)[0]
        values, indices = torch.topk(probs, k=top_k)

    results = []
    for rank, (prob, idx) in enumerate(zip(values.tolist(), indices.tolist()), start=1):
        label = CLASS_NAMES[idx]
        results.append(
            {
                "rank": rank,
                "class_id": idx,
                "zh": label["zh"],
                "en": label["en"],
                "confidence": prob,
                "confidence_pct": f"{prob * 100:.2f}%",
            }
        )
    return results


@app.route("/", methods=["GET", "POST"])
def index():
    error = None
    image_url = None
    top1 = None
    top5 = []

    if request.method == "POST":
        uploaded_file = request.files.get("image")

        if not uploaded_file or uploaded_file.filename == "":
            error = "请先选择一张花卉图片。"
        elif not allowed_file(uploaded_file.filename):
            error = "仅支持 jpg、jpeg、png、webp、bmp 图片。"
        else:
            filename = secure_filename(uploaded_file.filename)
            suffix = Path(filename).suffix.lower()
            saved_name = f"{uuid.uuid4().hex}{suffix}"
            saved_path = UPLOAD_DIR / saved_name

            try:
                uploaded_file.save(saved_path)
                Image.open(saved_path).verify()
                top5 = predict_image(saved_path, top_k=5)
                top1 = top5[0] if top5 else None
                image_url = url_for("static", filename=f"uploads/{saved_name}")
            except UnidentifiedImageError:
                saved_path.unlink(missing_ok=True)
                error = "上传的文件不是有效图片，请换一张再试。"
            except Exception as exc:
                saved_path.unlink(missing_ok=True)
                error = f"预测失败：{exc}"

    return render_template(
        "index.html",
        error=error,
        image_url=image_url,
        top1=top1,
        top5=top5,
        device=str(DEVICE),
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
