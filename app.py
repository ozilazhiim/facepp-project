import streamlit as st
import requests
import os
import time

API_KEY_FIX = "GANTI_DENGAN_API_KEY_ANDA"
API_SECRET_FIX = "GANTI_DENGAN_API_SECRET_ANDA"

DB_FOLDER = "database_wajah"
if not os.path.exists(DB_FOLDER):
    os.makedirs(DB_FOLDER)

st.set_page_config(page_title="Sistem Absensi Wajah", page_icon="security")
st.title("Sistem Pengenalan Wajah")

with st.sidebar:
    st.success("Sistem Online")
    st.caption("Mode: Hybrid (Cam/Upload)")
    
    st.subheader("User Terdaftar:")
    files = os.listdir(DB_FOLDER)
    if files:
        for f in files:
            if f.endswith('.jpg'):
                st.caption(f"- {f.split('.')[0]}")
    else:
        st.caption("Belum ada data.")

def call_facepp_compare(image_bytes1, image_bytes2):
    url = "https://api-us.faceplusplus.com/facepp/v3/compare"
    files = {'image_file1': image_bytes1, 'image_file2': image_bytes2}
    data = {'api_key': API_KEY_FIX, 'api_secret': API_SECRET_FIX}
    
    try:
        response = requests.post(url, data=data, files=files, timeout=10)
        return response.json()
    except Exception as e:
        return {"error_message": str(e)}

tab1, tab2, tab3 = st.tabs(["Registrasi User", "Deteksi / Absensi", "Bandingkan Manual"])

with tab1:
    st.header("Daftar Wajah Baru")
    reg_name = st.text_input("Masukkan Nama Lengkap:")
    
    mode = st.radio("Sumber Foto:", ["Kamera", "Upload File"], horizontal=True, key="mode_reg")
    
    reg_image = None
    if mode == "Kamera":
        reg_image = st.camera_input("Ambil Foto", key="reg_cam")
    else:
        reg_image = st.file_uploader("Upload Foto Profil", type=['jpg', 'jpeg', 'png'], key="reg_upload")

    if st.button("Simpan Data"):
        if reg_name and reg_image:
            file_path = os.path.join(DB_FOLDER, f"{reg_name}.jpg")
            with open(file_path, "wb") as f:
                f.write(reg_image.getbuffer())
            st.success(f"Berhasil disimpan: {reg_name}")
            time.sleep(1)
            st.rerun()
        else:
            st.warning("Nama dan Foto wajib diisi.")

with tab2:
    st.header("Cek Identitas")
    
    mode_cek = st.radio("Input Wajah:", ["Kamera", "Upload File"], horizontal=True, key="mode_cek")
    
    query_image = None
    if mode_cek == "Kamera":
        query_image = st.camera_input("Scan Wajah", key="query_cam")
    else:
        query_image = st.file_uploader("Upload Foto Wajah", type=['jpg', 'jpeg', 'png'], key="query_upload")

    if st.button("Identifikasi Wajah"):
        if query_image and os.listdir(DB_FOLDER):
            found = False
            match_name = ""
            
            db_files = [f for f in os.listdir(DB_FOLDER) if f.endswith('.jpg')]
            query_bytes = query_image.getvalue()
            
            progress = st.progress(0)
            status = st.empty()
            
            for i, filename in enumerate(db_files):
                clean_name = filename.split('.')[0]
                status.caption(f"Mengecek: {clean_name}...")
                
                with open(os.path.join(DB_FOLDER, filename), "rb") as db_file:
                    res = call_facepp_compare(query_bytes, db_file.read())
                    if "confidence" in res:
                        if res['confidence'] > res['thresholds']['1e-5']:
                            found = True
                            match_name = clean_name
                            break 
                
                progress.progress((i + 1) / len(db_files))
                time.sleep(0.5)
            
            progress.empty()
            status.empty()
            
            if found:
                st.success(f"Halo, {match_name}!")
            else:
                st.error("Tidak dikenal")
        else:
            st.warning("Pastikan foto diupload dan database tidak kosong.")

with tab3:
    st.header("Cek 1 vs 1")
    c1, c2 = st.columns(2)
    i1 = c1.file_uploader("Foto 1", key="m1")
    i2 = c2.file_uploader("Foto 2", key="m2")
    
    if st.button("Cek Kemiripan", type="primary"):
        if i1 and i2:
            with st.spinner("Menganalisa..."):
                res = call_facepp_compare(i1.getvalue(), i2.getvalue())
                
                if "confidence" in res:
                    score = res['confidence']
                    threshold = res['thresholds']['1e-5']
                    
                    if score > threshold:
                        st.success("Orang yang sama")
                    else:
                        st.error("Orang berbeda")
                else:
                    st.warning("Gagal mendeteksi wajah di salah satu foto.")
