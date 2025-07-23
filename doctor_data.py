import requests
import re
from hospital_data import get_hospital_ids_by_location
from difflib import get_close_matches


GITHUB_DOCTOR_DATA_URL = "https://raw.githubusercontent.com/Lodigalang/web-health/refs/heads/main/dokter/doctors.json"
BASE_IMAGE_URL = "https://raw.githubusercontent.com/Lodigalang/web-health/main/dokter/images"
STOPWORDS = {
    "di", "ke", "dari", "yang", "untuk", "dengan", "pada", "adalah", "ini", "itu",
    "rekomendasi", "daftar", "cari", "mau", "butuh", "dokter"
}

def normalize_text(text):
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    text = re.sub(r"\b(dokter|drg|dr)\b", "", text)  
    return re.sub(r"\s+", " ", text.strip())

def fetch_doctors():
    try:
        response = requests.get(GITHUB_DOCTOR_DATA_URL)
        response.raise_for_status()
        doctors = response.json()
        for doc in doctors:
            if doc["image"].startswith("/images/"):
                filename = doc["image"].split("/")[-1]
                doc["image"] = f"{BASE_IMAGE_URL}/{filename}"
        return doctors
    except Exception as e:
        print("Gagal memuat data dokter:", e)
        return []

def detect_specialization_from_data(prompt, doctors):
    prompt_norm = normalize_text(prompt)
    prompt_words = prompt_words = [word for word in prompt_norm.split() if word not in STOPWORDS]

    all_specs = {
        normalize_text(doc["specialization"]): doc["specialization"]
        for doc in doctors
    }

    prompt_text = " ".join(prompt_words)
    spec_keys = list(all_specs.keys())
    matches = get_close_matches(prompt_text, spec_keys, n=1, cutoff=0.6)
    if matches:
        return all_specs[matches[0]]
    return None

def get_doctor_recommendations(prompt=None):
    doctors = fetch_doctors()
    if not doctors:
        return []

    if prompt:
        detected_spec = detect_specialization_from_data(prompt, doctors)

        if detected_spec:
            results = [
                doc for doc in doctors
                if normalize_text(detected_spec) in normalize_text(doc["specialization"])
            ]
          
            for r in results:
                print("-", r["name"], "(", r["specialization"], ")")
            
            if results:
                return results
            else:
                return [{"message": f"Maaf, spesialis {detected_spec} belum tersedia di database kami saat ini."}]
        else:
            return [{"message": "Spesialisasi tidak terdeteksi. Silakan coba dengan istilah yang lebih spesifik."}]
    
    return doctors[:10]

def get_doctors_by_location_and_prompt(prompt):
    hospital_ids = get_hospital_ids_by_location(prompt)
    if not hospital_ids:
        return get_doctor_recommendations(prompt)
    return get_doctors_by_hospital_and_spec(hospital_ids, prompt)

def get_doctors_by_hospital_and_spec(hospital_ids, prompt=None):
    doctors = fetch_doctors()
    if not doctors:
        return []

    from difflib import get_close_matches

    # Filter berdasarkan nama rumah sakit
    filtered = []
    for doc in doctors:
        doc_hospital = doc.get("hospital", "")
        match = get_close_matches(doc_hospital, hospital_ids, cutoff=0.8)
        if match:
            filtered.append(doc)

    if prompt:
        detected_spec = detect_specialization_from_data(prompt, filtered)
        print("Spesialisasi terdeteksi:", detected_spec)

        if detected_spec:
            # Lakukan pencocokan longgar pada spesialisasi
            filtered_spec = []
            for doc in filtered:
                if get_close_matches(
                    normalize_text(detected_spec),
                    [normalize_text(doc.get("specialization", ""))],
                    cutoff=0.6
                ):
                    filtered_spec.append(doc)

            if filtered_spec:
                return filtered_spec
            else:
                return [{"message": f"Maaf, belum ada dokter dengan spesialisasi '{detected_spec}' yang ditemukan di rumah sakit tersebut."}]
        else:
            return filtered  # Jika tidak yakin, kembalikan semua dokter dari RS itu

    return filtered


#doctor_data.py 