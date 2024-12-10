import os

from typing import List, Tuple

from openai import OpenAI

digix_ai_key = os.getenv("DIGIX_AI_KEY")

client = OpenAI(api_key=digix_ai_key)


async def get_relevance_score(client_query: str, specialization: str, full_name: str, city: str, age: int, gender: str,
                              cv_text: str) -> float:
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system",
                 "content": "Ты помощник, который оценивает релевантность резюме специалистов к запросу клиента."},
                {"role": "user",
                 "content": f"Запрос клиента: {client_query}\n\nДанные о специалисте: ФИО: {full_name}\n\nСпециализация: {specialization}\n\nГород: {city}\n\nВозраст: {age}\n\nПол: {gender}\n\nРезюме специалиста: {cv_text}\n\nОцени релевантность по шкале от 0 до 1. Проста отправь число!"}
            ]
        )
        relevance_score = float(response.choices[0].message.content.strip())
        print(f"Relevance_score: {relevance_score}")
        return relevance_score
    except Exception as e:
        print(f"Error getting relevance score: {e}")
        return 0.0


async def compare_texts(client_query: str, specialists: List[Tuple[int, str, str, str, int, str, str]]) -> Tuple[List[int], List[float]]:
    relevance_scores = []
    for spec_id, specialization, full_name, city, age, gender, cv_text in specialists:
        relevance = await get_relevance_score(client_query, specialization, full_name, city, age, gender, cv_text)
        relevance_scores.append((spec_id, relevance))

    relevance_scores = [(spec_id, score)
                        for spec_id, score in relevance_scores if score > 0]

    relevance_scores.sort(key=lambda x: x[1], reverse=True)

    sorted_ids = [spec_id for spec_id, _ in relevance_scores]
    sorted_scores = [score for _, score in relevance_scores]
    return sorted_ids, sorted_scores
