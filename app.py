import streamlit as st
from inference import chat_inference

st.set_page_config(page_title="Asisten Kesehatan Digital", page_icon="🩺")
st.title("🩺 Asisten Kesehatan Lodi Health's")

st.markdown("""
# Selamat datang di Chatbot Kesehatan Digital! 👋

Kamu bisa:
- 💬 **Tanya soal gejala atau curhat kesehatan** (fisik & mental)  
- 🧑‍⚕️ **Cari rekomendasi dokter** sesuai kebutuhanmu  
- 🏥 **Temukan rumah sakit** yang relevan dengan lokasi atau layanan  
- 📰 **Baca berita kesehatan terbaru** dari sumber terpercaya

> Chatbot ini memberikan informasi dan panduan awal berbasis AI.  
> **Bukan pengganti diagnosis atau perawatan dari dokter.**

Silakan ketik pertanyaanmu atau pilih fitur yang kamu butuhkan di bawah.
""")



with st.sidebar:
    st.header("⚙️ Pengaturan")
    if st.button("🔄 Reset Percakapan"):
        st.session_state.messages = []
        st.rerun()

# Inisialisasi state percakapan
if "messages" not in st.session_state:
    st.session_state.messages = []

# Tampilkan riwayat chat sebelumnya
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input user
prompt = st.chat_input("Ketik keluhan atau pertanyaan lainnya di sini...")

if prompt:
    # Tampilkan input user
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        with st.spinner("Sedang menganalisis..."):
            response = chat_inference(prompt)

        # Tampilkan respon asisten
        with st.chat_message("assistant"):
            if isinstance(response, dict) and response.get("type") == "doctors":
                st.markdown("Berikut beberapa rekomendasi dokter:")

                for doc in response["content"]:
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        if doc.get("image"):
                            st.image(doc["image"], width=100)
                    with col2:
                        st.markdown(f"""
**{doc['name']}**  
📚 *{doc['specialization']}*  
🏥 {doc['hospital']}  
""")
                    st.markdown("---")

                # Tambahkan ke session
                doctor_summary = "\n\n".join(
                    f"**{doc['name']}** - {doc['specialization']} ({doc['hospital']})"
                    for doc in response["content"]
                )
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": doctor_summary
                })

            else:
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

    except Exception as e:
        st.error("Maaf, terjadi kesalahan saat memproses permintaan Anda.")
        print(f"❌ Error pada inference: {e}")


#app.py 