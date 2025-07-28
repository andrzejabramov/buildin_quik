from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime, timezone
from typing import List, Optional
import sqlite3
import logging
import os

# === Настройка логирования ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Review Sentiment API",
    description="Сервис для сбора отзывов и анализа их тональности в реальном времени.",
    version="1.0.0"
)

# === Конфигурация БД ===
DATABASE = "reviews.db"

# Создаём директорию, если её нет
os.makedirs(os.path.dirname(DATABASE) if os.path.dirname(DATABASE) else '.', exist_ok=True)

def init_db():
    """Инициализация базы данных и таблицы reviews."""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                sentiment TEXT NOT NULL CHECK(sentiment IN ('positive', 'negative', 'neutral')),
                created_at TEXT NOT NULL  -- ISO 8601 с TZ
            )
        """)
        conn.commit()
    logger.info(f"База данных инициализирована: {DATABASE}")

# Запускаем при старте
init_db()

# === Pydantic-модели ===
class ReviewInput(BaseModel):
    text: str

class Review(BaseModel):
    id: int
    text: str
    sentiment: str
    created_at: str

# === Анализ тональности ===
def analyze_sentiment(text: str) -> str:
    """
    Простой анализ тональности по ключевым словам.
    Работает на основе вхождения корней слов.
    """
    text_lower = text.lower()

    positive_roots = ["хорош", "отличн", "прекрасн", "класс", "люблю", "нрав", "супер",
                      "замечательн", "великолепн", "рад", "доволен", "понрав"]
    negative_roots = ["плохо", "ужасн", "отвратительн", "ненавиж", "фу", "кошмар", "скучн",
                      "разочарован", "грустн", "тоска", "никогда", "не работает", "сломал"]

    has_positive = any(root in text_lower for root in positive_roots)
    has_negative = any(root in text_lower for root in negative_roots)

    if has_positive and not has_negative:
        return "positive"
    elif has_negative and not has_positive:
        return "negative"
    else:
        return "neutral"

# === Маршруты ===

@app.post("/reviews", response_model=Review, status_code=201)
def add_review(review_input: ReviewInput):
    """
    Добавить новый отзыв.
    Автоматически определяет тональность и сохраняет с временем в UTC.
    """
    text = review_input.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Поле 'text' не может быть пустым или состоять только из пробелов.")

    sentiment = analyze_sentiment(text)

    # Используем осознанное время (timezone-aware) — современный стандарт
    created_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO reviews (text, sentiment, created_at) VALUES (?, ?, ?)",
                (text, sentiment, created_at)
            )
            review_id = cursor.lastrowid
            conn.commit()

        logger.info(f"Добавлен отзыв #{review_id} (sentiment: {sentiment})")

        return {
            "id": review_id,
            "text": text,
            "sentiment": sentiment,
            "created_at": created_at
        }

    except sqlite3.Error as e:
        logger.error(f"Ошибка при сохранении отзыва в БД: {e}")
        raise HTTPException(status_code=500, detail="Не удалось сохранить отзыв")

@app.get("/reviews", response_model=List[Review])
def get_reviews(sentiment: Optional[str] = Query(None, description="Фильтр по тональности: positive, negative, neutral")):
    """
    Получить список отзывов. Можно отфильтровать по `sentiment`.
    """
    query = "SELECT id, text, sentiment, created_at FROM reviews"
    params = []

    if sentiment:
        if sentiment not in ("positive", "negative", "neutral"):
            raise HTTPException(status_code=400, detail="sentiment должен быть одним из: positive, negative, neutral")
        query += " WHERE sentiment = ?"
        params.append(sentiment)

    query += " ORDER BY created_at DESC"

    try:
        with sqlite3.connect(DATABASE) as conn:
            conn.row_factory = sqlite3.Row  # Доступ по имени колонки
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()

        result = [
            {
                "id": row["id"],
                "text": row["text"],
                "sentiment": row["sentiment"],
                "created_at": row["created_at"]
            }
            for row in rows
        ]

        logger.info(f"Получено {len(result)} отзывов (фильтр: sentiment={sentiment})")
        return result

    except sqlite3.Error as e:
        logger.error(f"Ошибка при чтении отзывов из БД: {e}")
        raise HTTPException(status_code=500, detail="Не удалось получить отзывы")

# === Информационный маршрут ===
@app.get("/")
def root():
    return {
        "message": "Добро пожаловать в Review Sentiment API",
        "docs": "/docs",
        "redoc": "/redoc"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)