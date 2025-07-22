import requests
import re
from difflib import get_close_matches

HOSPITAL_DATA_URL = "https://raw.githubusercontent.com/Lodigalang/web-health/refs/heads/main/hospital.json"
STOPWORDS = {"di", "ke", "dari", "yang", "untuk", "dengan", "pada", "adalah", "ini", "itu"}

# Normalisasi teks
def normalize_text(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    return text.strip()

def remove_stopwords(text):
    words = text.split()
    filtered = [word for word in words if word not in STOPWORDS]
    return " ".join(filtered)

# Ambil data rumah sakit dari URL
def fetch_hospital_data():
    try:
        response = requests.get(HOSPITAL_DATA_URL)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print("Gagal mengambil data rumah sakit:", e)
        return []

# Ambil rumah sakit berdasarkan prompt lokasi
def get_hospitals_by_prompt(prompt):
    hospitals_data = fetch_hospital_data()
    if not hospitals_data:
        return []

    prompt = normalize_text(prompt)
    prompt = remove_stopwords(prompt)
    prompt_words = prompt.split()

    results = []
    seen_keys = set()

    # Bikin key unik pakai name + region (karena tidak ada ID)
    def hospital_key(h):
        return normalize_text(h.get("name", "")) + "|" + normalize_text(h.get("region", ""))

    # 1. Pencocokan langsung: minimal 2 kata dari prompt cocok dalam region
    for h in hospitals_data:
        region = normalize_text(h.get("region", ""))
        key = hospital_key(h)
        match_score = sum(1 for word in prompt_words if word in region)
        if match_score >= 2 and key not in seen_keys:
            results.append(h)
            seen_keys.add(key)

    if results:
        return results

    # 2. Fallback: get_close_matches tanpa n=1
    region_names = list({
        normalize_text(h["region"]) for h in hospitals_data if h.get("region")
    })

    region_match = get_close_matches(prompt, region_names, cutoff=0.7)
    if region_match:
        for keyword in region_match:
            for h in hospitals_data:
                region = normalize_text(h.get("region", ""))
                key = hospital_key(h)
                if keyword in region and key not in seen_keys:
                    results.append(h)
                    seen_keys.add(key)
        if results:
            return results

    # 3. Fallback per kata (longgar)
    region_keywords = set(word for region in region_names for word in region.split())
    for word in prompt_words:
        word_match = get_close_matches(word, region_keywords, cutoff=0.8)
        if word_match:
            for h in hospitals_data:
                region = normalize_text(h.get("region", ""))
                key = hospital_key(h)
                if word_match[0] in region and key not in seen_keys:
                    results.append(h)
                    seen_keys.add(key)
            if results:
                return results

    return [{"error": "Lokasi tidak dikenali dari prompt."}]


# Ambil daftar rumah sakit
def get_hospital_ids_by_location(prompt):
    hospitals = get_hospitals_by_prompt(prompt)
    result = [h["name"] for h in hospitals if "name" in h]

    if not result:
        try:
            response = requests.get(HOSPITAL_DATA_URL)
            response.raise_for_status()
            all_hospitals = response.json()

            # Exact match (case-insensitive)
            prompt_upper = normalize_text(prompt).upper()
            for h in all_hospitals:
                if normalize_text(h["name"]).upper() in prompt_upper:
                    print("Langsung cocok ke nama rumah sakit:", h["name"])
                    return [h["name"]]
        except Exception as e:
            print("Gagal fallback nama rumah sakit:", e)

    return result


#hospital_data.py
