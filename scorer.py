"""
Job scoring module using keyword matching (no AI API required).
Scores jobs based on skill keyword matches against job title and description.
"""
import logging

logger = logging.getLogger(__name__)

# Define skill keywords relevant to the candidate
SKILL_KEYWORDS = [
    # Core skills
    "python",
    "machine learning",
    "ml",
    "ai",
    "artificial intelligence",
    
    # LLM & NLP
    "langchain",
    "llm",
    "nlp",
    "natural language",
    "transformers",
    "huggingface",
    "generative ai",
    "gpt",
    "openai",
    "claude",
    
    # Deep Learning Frameworks
    "tensorflow",
    "pytorch",
    "keras",
    "deep learning",
    
    # Specialized ML
    "faiss",
    "vector",
    "embedding",
    "rag",
    "retrieval augmented",
    
    # Backend/DevOps
    "fastapi",
    "flask",
    "django",
    "rest api",
    "docker",
    "aws",
    "gcp",
    "azure",
    "kubernetes",
    
    # Data
    "sql",
    "data engineer",
    "etl",
    "data science",
    "pandas",
    "numpy",
    "scikit-learn",
    
    # Other relevant
    "automation",
    "scripting",
    "api",
    "database",
]


def score_job(title: str, description: str) -> tuple[int, str]:
    """
    Score a job posting based on keyword matching.
    No external API needed - pure keyword matching logic.
    
    Args:
        title: Job title
        description: Job description/requirements
    
    Returns:
        Tuple of (score: 0-100, reason: explanation string)
    """
    try:
        # Combine and normalize text
        combined_text = (title + " " + description).lower()
        
        # Find matching keywords
        matched_keywords = []
        for keyword in SKILL_KEYWORDS:
            if keyword in combined_text:
                matched_keywords.append(keyword)
        
        # Calculate score: each match adds 8 points (max 100)
        score = min(100, len(matched_keywords) * 8)
        
        # Build reason string
        if matched_keywords:
            top_matches = matched_keywords[:5]
            reason = f"Matched {len(matched_keywords)} skills: {', '.join(top_matches)}"
            if len(matched_keywords) > 5:
                reason += f" (+{len(matched_keywords) - 5} more)"
        else:
            reason = "No skill keywords matched"
        
        logger.debug(f"Job scored: {score}/100 - {reason}")
        return score, reason
    
    except Exception as e:
        logger.error(f"Error scoring job: {str(e)}")
        return 0, f"Scoring error: {str(e)}"
