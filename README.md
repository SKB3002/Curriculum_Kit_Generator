# Curriculum_Kit_Generator (apZ)

**AI-powered, teacher-controlled lesson planning — without hallucination**

LessonForge converts textbook or chapter PDFs into **structured, syllabus-aligned lesson plans** using AI, while keeping **teachers fully in control of topics and sections**.

---

## ✨ Key Features

- 📄 **PDF → Lesson Plans** (45–50 min per lesson)
- 🧠 **Topic-locked generation** (no topic hallucination)
- 🧩 **Fully modular lesson structure**
  - Enable/disable sections via checkboxes
  - Only Grade, Chapter & Topic are mandatory
- ➕ **Custom sections** (teacher-defined title + content)
- 🎯 **One topic per lesson plan** (strict mapping)
- 🎨 **Modern, aesthetic Streamlit UI**
- ⚡ **Free LLM backend via Groq API**

---

## 🧱 Lesson Plan Structure (Configurable)

- Grade *(mandatory)*
- Chapter Name *(mandatory)*
- Topic Name *(mandatory)*
- Domains *(optional)*
- Curricular Goals *(optional)*
- Competencies *(optional)*
- Learning Outcomes *(optional)*
- Teaching Aids *(optional)*
- Strategy / Pedagogy *(optional)*
- Interdisciplinary Approach *(optional)*
- Extended Learning Assignment *(optional)*
- Custom Sections *(teacher-authored)*

Unchecked sections are **not generated or displayed**.

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit (custom CSS theming)
- **LLM:** Groq API
- **Backend:** Python
- **PDF Processing:** Custom chunking + word-count heuristics

---

## 🚀 Running Locally

```bash
git clone https://github.com/your-username/Curriculum_Kit_Generator.git
cd Curriculum_Kit_Generator
pip install -r requirements.txt
export GROQ_API_KEY="your_api_key"
streamlit run app.py
```
---

## 📌 Use Cases

Teachers & educators

Curriculum designers

EdTech platforms

Schools needing board-aligned lesson plans

## 📄 License

MIT License
