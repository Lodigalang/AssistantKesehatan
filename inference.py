from google import genai
import os
from dotenv import load_dotenv
from health_news import get_health_news
from doctor_data import get_doctor_recommendations, get_doctors_by_hospital_and_spec
from hospital_data import get_hospitals_by_prompt, get_hospital_ids_by_location


load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)
chat = client.chats.create(model="gemini-2.0-flash")

url_source = [
    'https://www.halodoc.com/artikel',
    'https://www.alodokter.com/artikel',
    'https://www.sehatq.com/artikel'
]

def is_news_query(prompt):
    keywords = ["berita", "kabar", "info terkini", "update kesehatan", "news"]
    return any(word in prompt.lower() for word in keywords)

def is_doctor_recommendation(prompt):
    keywords = ["dokter", "rekomendasi dokter", "cari dokter", "butuh dokter", "spesialis","daftar dokter"]
    return any(word in prompt.lower() for word in keywords)

def is_hospital_request(prompt):
    keywords = ["rumah sakit", "rs", "cari rs", "lokasi rs", "fasilitas kesehatan"]
    return any(word in prompt.lower() for word in keywords)

def detect_health_category(prompt):
    prompt = prompt.lower()
    if any(k in prompt for k in ["mental", "kesehatan mental", "depresi", "cemas", "stres"]):
        return "Mental Health"
    elif any(k in prompt for k in ["nutrisi", "makan", "gizi", "diet"]):
        return "Nutrition & Diet"
    elif any(k in prompt for k in ["olahraga", "fitness", "latihan", "aktif"]):
        return "Exercise & Fitness"
    elif any(k in prompt for k in ["penyakit kronis", "diabetes", "hipertensi", "jantung", "asma"]):
        return "Chronic Conditions"
    elif any(k in prompt for k in ["vaksin", "pencegahan", "imunisasi"]):
        return "Prevention"
    elif any(k in prompt for k in ["pengobatan", "obat", "terapi", "pemulihan"]):
        return "Treatment"
    else:
        return None

def chat_inference(prompt):
    if is_news_query(prompt):
        user_category = detect_health_category(prompt)
        news = get_health_news(user_category) if user_category else get_health_news()
        
        if not news:
            return "Maaf, saya tidak menemukan berita kesehatan terbaru yang relevan saat ini."

        response = "Berikut adalah beberapa berita kesehatan terbaru"
        if user_category:
            response += f" seputar **{user_category}**:\n\n"
        else:
            response += ":\n\n"

        for item in news:
            response += f"🔹 **[{item['title']}]({item['url']})**\n"
            response += f"_Sumber: {item['source']}_\n"
            if item['description']:
                response += f"{item['description']}\n"
            response += "\n"
        return response

    elif is_doctor_recommendation(prompt):
        hospital_ids = get_hospital_ids_by_location(prompt)
        if hospital_ids:
            doctors = get_doctors_by_hospital_and_spec(hospital_ids, prompt)
        else:
            doctors = get_doctor_recommendations(prompt)
    
    # 🔍 Validasi data dokter
        if not doctors or not all("name" in d and "specialization" in d and "hospital" in d for d in doctors):
            return "Maaf, kami belum dapat memahami permintaan Anda sepenuhnya atau informasi tersebut belum tersedia dalam sistem kami. Silakan coba jelaskan kembali dengan lebih spesifik."

        return {"type": "doctors", "content": doctors}
    
    elif is_hospital_request(prompt):
        hospitals = get_hospitals_by_prompt(prompt)
        if not hospitals:
            return "Maaf, saya tidak menemukan rumah sakit yang sesuai dengan permintaan Anda saat ini."

        hospital_text = "Berikut daftar rumah sakit yang relevan:\n\n"
        for rs in hospitals:
            hospital_text += f"""
🏥 **{rs['name']}**  
📍 **{rs['region']}**              
☎️ {rs.get('phone', 'N/A')}

---
"""
        return hospital_text
        
    else:
        response = chat.send_message(
        f'''
        ### Prompt Sistem untuk Asisten Virtual Kesehatan

        **Peran Anda:**  
        Kamu adalah teman yang selalu siap mendengarkan dan membantu soal kesehatan. Bisa menjawab keluhan ringan, kasih saran gaya hidup sehat, dan juga siap dengarkan cerita atau curhatan tentang kesehatan fisik maupun mental. Bukan dokter, tapi bantu kasih arah dan solusi awal yang mudah dipahami. Referensi utama: {url_source}.

        **Gaya Bahasa:**  
        - Santai, ramah, dan mudah dimengerti.  
        - Jangan pakai istilah medis yang susah tanpa penjelasan.  
        - Empati tinggi, paham kalau pengguna kadang cuma butuh didengar.  
        - Hindari kata-kata terlalu resmi, tapi juga jangan terlalu kasar atau informal.

        **Struktur Jawaban:**  
        1. Respon yang menunjukkan kamu mendengar dan peduli.  
        2. Jelaskan penyebab atau informasi yang relevan dengan bahasa sederhana.  
        3. Kasih saran atau langkah mudah yang bisa dilakukan sendiri.  
        4. Beri tahu kapan harus ke dokter atau tenaga medis.  
        5. Tanya hal-hal yang belum jelas kalau perlu, seperti umur, lama keluhan, dll.

        **Contoh:**  
        _“Wah, sakit kepala terus di pagi hari memang bikin nggak nyaman ya. Bisa jadi karena kurang tidur atau terlalu banyak pikiran. Coba coba atur pola tidur dulu dan rileks ya. Kalau masih sering terasa parah, sebaiknya periksa ke dokter supaya lebih pasti.”_

        Pertanyaan atau cerita dari pengguna: "{prompt}"
        '''
        )
        
        return response.text


#inference.py