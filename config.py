import os
from dotenv import load_dotenv

load_dotenv()

CONFIG = {
    "email": os.getenv("NAUKRI_EMAIL"),
    "password": os.getenv("NAUKRI_PASSWORD"),
    "resume_path": os.getenv("RESUME_PATH", "resume.pdf"),
    "search_queries": ["AI Engineer", "ML Engineer", "Python Developer", "LLM Engineer"],
    "location": "Indore",
    "experience": "0-2",
    "min_score": 30,
    "max_applications": 20,
    "delay_seconds": 3,
    "headless": False,
    "candidate": {
        "name": os.getenv("CANDIDATE_NAME", "Rohit Kumar"),
        "phone": os.getenv("CANDIDATE_PHONE", ""),
        "skills": "Python, Machine Learning, LangChain, FastAPI, FAISS, RAG, HuggingFace",
        "experience_years": "1",
        "notice_period": "Immediate",
        "current_ctc": "0",
        "expected_ctc": "400000",
    }
}
