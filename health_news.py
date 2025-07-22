import requests
import os
from dotenv import load_dotenv

load_dotenv()
NEWS_API_KEY = os.getenv("NEWS_API_KEY")  

# Deteksi kategori manual berdasarkan kata kunci
def detect_category(article):
    text = f"{article.get('title', '')} {article.get('description', '')} {article.get('content', '')}".lower()

    if any(keyword in text for keyword in ["mental", "stress", "anxiety", "depression", "psychology", "trauma"]):
        return "Mental Health"
    if any(keyword in text for keyword in ["nutrition", "diet", "obesity", "food", "calories", "eating habits"]):
        return "Nutrition & Diet"
    if any(keyword in text for keyword in ["exercise", "fitness", "workout", "yoga", "physical activity", "training"]):
        return "Exercise & Fitness"
    if any(keyword in text for keyword in ["diabetes", "cancer", "asthma", "hypertension", "chronic", "cardiovascular", "stroke"]):
        return "Chronic Conditions"
    if any(keyword in text for keyword in ["prevention", "vaccine", "vaccination", "immunization", "preventive"]):
        return "Prevention"
    if any(keyword in text for keyword in ["treatment", "therapy", "medication", "rehabilitation", "drug", "medicine", "recovery"]):
        return "Treatment"

    return "General Health"

def get_health_news(user_category=None):
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "country": "us",
        "category": "health",
        "pageSize": 20,  
        "apiKey": NEWS_API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data["status"] != "ok":
        return []

    articles = []
    for article in data["articles"]:
        category = detect_category(article)

        if user_category is None or category == user_category:
            articles.append({
                "title": article["title"],
                "description": article["description"],
                "url": article["url"],
                "source": article["source"]["name"],
                "category": category
            })

    return articles
