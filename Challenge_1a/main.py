import os
import fitz  # PyMuPDF
import json
import re
from langdetect import detect, DetectorFactory
import langcodes

DetectorFactory.seed = 0  # Make language detection deterministic

# Unicode ranges for fallback multilingual detection
SCRIPT_RANGES = {
    "hi": ("\u0900", "\u097F"), "ta": ("\u0B80", "\u0BFF"),
    "te": ("\u0C00", "\u0C7F"), "kn": ("\u0C80", "\u0CFF"),
    "bn": ("\u0980", "\u09FF"), "ja": ("\u3040", "\u30FF"),
    "ko": ("\uAC00", "\uD7AF"), "zh": ("\u4E00", "\u9FFF")
}

def fallback_language_by_script(text):
    for lang, (start, end) in SCRIPT_RANGES.items():
        if any(start <= char <= end for char in text):
            return lang
    return "unknown"

def detect_language(text):
    try:
        code = detect(text)
    except:
        code = fallback_language_by_script(text)
    try:
        name = langcodes.get(code).language_name()
    except:
        name = "Unknown"
    return code, name

def is_numbered_heading(text):
    return bool(re.match(r'^\d+(\.\d+)*[\.\)]?\s+', text))

def calculate_confidence(span, y_pos, text):
    font = span["font"]
    size = span["size"]
    flags = span["flags"]
    confidence = 0

    if size >= 24: confidence += 0.4
    elif size >= 20: confidence += 0.3
    elif size >= 16: confidence += 0.2
    elif size >= 12: confidence += 0.1

    if flags == 2 or "Bold" in font:
        confidence += 0.3
    if y_pos < 200:
        confidence += 0.2
    if is_numbered_heading(text):
        confidence += 0.1

    return round(min(confidence, 1.0), 2)

def assign_level(confidence):
    if confidence >= 0.8: return "H1"
    elif confidence >= 0.6: return "H2"
    elif confidence >= 0.4: return "H3"
    return None

def restructure_outline_hierarchy(flat_outline):
    """
    Convert a flat list of headings into a nested TOC structure using levels H1 > H2 > H3.
    """
    hierarchy = []
    current_h1 = None
    current_h2 = None

    for item in flat_outline:
        item["subsections"] = []

        if item["level"] == "H1":
            hierarchy.append(item)
            current_h1 = item
            current_h2 = None
        elif item["level"] == "H2" and current_h1:
            current_h1["subsections"].append(item)
            current_h2 = item
        elif item["level"] == "H3" and current_h2:
            current_h2["subsections"].append(item)
        elif item["level"] == "H3" and current_h1:
            current_h1["subsections"].append(item)  # fallback if no H2
    return hierarchy

def extract_outline(pdf_path):
    doc = fitz.open(pdf_path)
    title = os.path.basename(pdf_path).replace(".pdf", "")
    flat_outline = []

    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                if not line["spans"]:
                    continue

                span = line["spans"][0]
                text = " ".join(span["text"] for span in line["spans"]).strip()
                if not text or len(text) < 3:
                    continue

                y_pos = span["bbox"][1]
                confidence = calculate_confidence(span, y_pos, text)
                level = assign_level(confidence)
                lang_code, lang_name = detect_language(text)

                if level:
                    flat_outline.append({
                        "level": level,
                        "text": text,
                        "page": page_num,
                        "confidence": confidence,
                        "font": span["font"],
                        "size": span["size"],
                        "lang": lang_code,
                        "lang_name": lang_name
                    })

    hierarchical_outline = restructure_outline_hierarchy(flat_outline)
    return {
        "title": title,
        "outline": hierarchical_outline
    }

def process_all_pdfs(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".pdf"):
            filepath = os.path.join(input_dir, filename)
            result = extract_outline(filepath)
            json_name = filename.replace(".pdf", ".json")
            with open(os.path.join(output_dir, json_name), "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"✅ Processed: {filename} ➝ {json_name}")

if __name__ == "__main__":
    process_all_pdfs("input", "output")
