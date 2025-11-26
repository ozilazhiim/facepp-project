import streamlit as st
import requests
import os
import time

API_KEY_FIX = "__"
API_SECRET_FIX = "__"

DB_FOLDER = "database_wajah"
if not os.path.exists(DB_FOLDER):
    os.makedirs(DB_FOLDER)

st.set_page_config(page_title="Sistem Absensi Wajah", page_icon="security")
st.title("Sistem Pengenalan Wajah")

with st.sidebar:
    st.success("API Key Terhubung") 
    st.subheader("User Terdaftar:")
    try:
        registered_files = os.listdir(DB_FOLDER)
        if registered_files:
            for file in registered_files:
                if file.endswith(('.jpg', '.png', '.jpeg')):
                    st.caption(f"- {file.split('.')[0]}")
        else:
            st.caption("Belum ada data.")
    except Exception as e:
        st.error("Error baca folder.")

def call_facepp_compare(image_bytes1, image_bytes2):
    key = API_KEY_FIX
    secret = API_SECRET_FIX
    url = "https://api-us.faceplusplus.com/facepp/v3/compare"
    files = {'image_file1': image_bytes1, 'image_file2': image_bytes2}
    data = {'api_key': key, 'api_secret': secret}
    try:
        response = requests.post(url, data=data, files=files, timeout=10)
        return response.json()
    except Exception as e:
        return {"error_message": str(e)}

tab1, tab2, tab3 = st.tabs(["Registrasi User", "Deteksi / Absensi", "Bandingkan Manual"])
with tab1:
    st.header("Daftarkan Wajah Baru")
    reg_name = st.text_input("Masukkan Nama Lengkap:")
    reg_method = st.radio("Sumber Foto:", ["Upload File", "Ambil Kamera"])
    reg_image = None
    if reg_method == "Upload File":
        reg_image = st.file_uploader("Upload Foto Profil", type=['jpg', 'jpeg', 'png'], key="reg_upload")
    else:
        reg_image = st.camera_input("Ambil Foto Selfie", key="reg_cam")
    if st.button("Simpan Data"):
        if not reg_name or not reg_image:
            st.warning("Nama dan Foto wajib diisi!")
        else:
            file_path = os.path.join(DB_FOLDER, f"{reg_name}.jpg")
            with open(file_path, "wb") as f:
                f.write(reg_image.getbuffer())
            st.success(f"User '{reg_name}' tersimpan.")
            st.rerun()

with tab2:
    st.header("Siapa ini?")
    query_method = st.radio("Input:", ["Kamera", "Upload"], horizontal=True)
    query_image = None
    if query_method == "Kamera":
        query_image = st.camera_input("Scan Wajah", key="query_cam")
    else:
        query_image = st.file_uploader("Upload Foto", type=['jpg', 'png'], key="query_upload")

    if st.button("Identifikasi Wajah"):
        if not query_image:
            st.warning("Ambil foto dulu.")
        elif not os.listdir(DB_FOLDER):
            st.error("Database kosong! Daftar dulu.")
        else:
            best_match_name = None
            best_match_score = 0
            found_match = False
            progress_bar = st.progress(0)
            status_text = st.empty()
            files = [f for f in os.listdir(DB_FOLDER) if f.endswith(('.jpg', '.png'))]
            total_files = len(files)
            query_bytes = query_image.getvalue()
            for i, filename in enumerate(files):
                name = filename.split('.')[0]
                status_text.text(f"Cek database: {name}...")
                with open(os.path.join(DB_FOLDER, filename), "rb") as db_file:
                    db_bytes = db_file.read()
                    result = call_facepp_compare(query_bytes, db_bytes)
                    if "confidence" in result:
                        score = result['confidence']
                        threshold = result['thresholds']['1e-5'] 
                        if score > threshold and score > best_match_score:
                            best_match_score = score
                            best_match_name = name
                            found_match = True
                progress_bar.progress((i + 1) / total_files)
                time.sleep(0.5)
            status_text.empty()
            progress_bar.empty()
            st.divider()
            if found_match:
                st.success(f"TERIDENTIFIKASI: {best_match_name}")
                st.metric("Akurasi", f"{best_match_score}%")
            else:
                st.error("TIDAK DIKENAL.")

with tab3:
    st.write("Mode Debug Manual")
    c1, c2 = st.columns(2)
    i1 = c1.file_uploader("Foto 1", key="m1")
    i2 = c2.file_uploader("Foto 2", key="m2")
    if st.button("Cek"):
        if i1 and i2:
            res = call_facepp_compare(i1.getvalue(), i2.getvalue())
            st.json(res)
