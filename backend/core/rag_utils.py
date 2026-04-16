import os
import chromadb
import re
import json
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from django.core.cache import cache

# ====================== INITIALIZATION ======================
client = OpenAI(
    base_url=os.getenv('LLM_BASE_URL', 'http://localhost:1234/v1'),
    api_key=os.getenv('LLM_API_KEY', 'lm-studio')
)

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="book_chunks")


# ====================== HELPER FUNCTIONS ======================
def get_llm_response(prompt: str, max_tokens=500):
    """Get response from local LLM with caching"""
    cache_key = f"llm_{hash(prompt)}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    try:
        response = client.chat.completions.create(
            model="local-model",          # Change to your model name if needed
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.7
        )
        answer = response.choices[0].message.content.strip()
        cache.set(cache_key, answer, timeout=3600)  # Cache for 1 hour
        return answer
    except Exception as e:
        print("LLM Connection Error:", e)
        return "Sorry, LLM is not responding."


def extract_json(text: str):
    """Extract JSON from LLM response even if it has extra text"""
    try:
        # Try direct JSON parse first
        return json.loads(text)
    except:
        # Try to find JSON object in the text
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except:
                pass
    return None


# ====================== MAIN FUNCTIONS ======================
def process_book(book):
    """Generate AI insights (Summary, Genre, Recommendations)"""
    text = book.description or book.title
    if not text:
        return

    prompt = f"""You are a strict JSON generator. Respond with **valid JSON only**. No explanations, no extra text, no markdown.

Book Title: {book.title}
Description: {text[:1800]}

Return exactly this format:
{{
  "summary": "Short 2-sentence summary of the book",
  "genre": "One main genre (e.g. Fiction, Self-help, Mystery, Romance, Philosophy)",
  "recommendations": "If you like this book, you'll also like: Book1 by Author1, Book2 by Author2"
}}

JSON:"""

    try:
        result = get_llm_response(prompt, max_tokens=450)
        print("RAW LLM RESPONSE:\n", result[:500] + "..." if len(result) > 500 else result)

        data = extract_json(result)

        if data:
            book.summary = data.get("summary", "A compelling and insightful book.")
            book.genre = data.get("genre", "Fiction")
            book.recommendations = data.get("recommendations", "The Alchemist by Paulo Coelho, Atomic Habits by James Clear")
            book.save()
            print(f"✅ Successfully processed AI insights for: {book.title}")
        else:
            raise ValueError("Could not extract JSON")

    except Exception as e:
        print("⚠️ LLM failed → using fallback")
        book.summary = "A highly recommended book with valuable insights."
        book.genre = "Fiction"
        book.recommendations = "Rich Dad Poor Dad by Robert Kiyosaki, The Psychology of Money by Morgan Housel"
        book.save()


def rag_query(question: str):
    """Full RAG Pipeline - Improved Prompt"""
    try:
        q_embedding = embedding_model.encode([question]).tolist()[0]
        
        results = collection.query(
            query_embeddings=[q_embedding],
            n_results=5   # Increased for better context
        )

        context = "\n\n---\n\n".join(results["documents"][0])
        sources = list(set([m["title"] for m in results["metadatas"][0]]))

        # Much stronger and clearer prompt
        prompt = f"""You are an expert book assistant. Answer the question **only using the provided context** below.

Context:
{context}

Question: {question}

Instructions:
- Answer directly and naturally.
- If the context doesn't have enough info, say "I don't have enough information about that."
- At the very end, write: Sources: Book1, Book2, ...

Answer:"""

        answer = get_llm_response(prompt, max_tokens=700)

        return {
            "answer": answer,
            "sources": sources
        }

    except Exception as e:
        print("RAG Error:", e)
        return {
            "answer": "Sorry, I couldn't process your question right now.",
            "sources": []
        }