Adobe Hackathon 2025 – Document Intelligence Solution

This repository contains the solution for both Round 1A.

---

Round 1A – PDF Heading & Outline Extractor

- **Input**: A single PDF file (`input/`)
- **Output**: JSON file with title and extracted headings hierarchy
- **Script**: `main.py`
  How to Run

Locally

````bash
pip install -r requirements.txt
python main.py        # for Round 1A

---

### 🐳 With Docker

```bash
docker build -t adobe-doc-intel .
docker run --rm -v ${PWD}/input:/app/input -v ${PWD}/output:/app/output adobe-doc-intel

````

---

3. `requirements.txt`:contentReference[oaicite:2]{index=2}

- Contains all required packages:
  - `PyMuPDF`, `sentence-transformers`, `torch`, `langdetect`, `langcodes`
- Ready to install via `pip install -r requirements.txt`

---

4.  Input PDF (`long_sample_ai.pdf`):contentReference[oaicite:3]{index=3}

- Realistic structure: multiple chapters and sub-sections
- Great for evaluating heading extraction
- Works well with your current detection logic

---

5. Dockerfile

Use this final Dockerfile if you haven't already:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["python", "main.py"]

```

6. HTML File

You can run the html file to open up a window, a simple UI.
This allows user to upload output.json file to check about language and filter it out.
Other features like font, page number, heading, subheading and other details will be found in the output folder under a json file once the input is run.

#You can activate venv environment too on the system using python -m venv venv
then activating it.
