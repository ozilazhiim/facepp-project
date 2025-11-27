import streamlit as st
import requests
import os
import time

API_KEY_FIX = "Bxi_kIv7gV01o567kkDhS3Cy7mLYaqbk"
API_SECRET_FIX = "Ak2VeBdlqDy4Q8QK0z07d_jZbSXvV8CE"
FACESET_NAME = "absensi_kantor"

st.set_page_config(page_title="Face Recognition", page_icon="⚡")
st.title("Sistem Pengenalan Wajah ")
def create_faceset_if_not_exists():
    url = "https://api-us.faceplusplus.com/facepp/v3/faceset/create"
    data = {
        'api_key': API_KEY_FIX, 
        'api_secret': API_SECRET_FIX,
        'outer_id': FACESET_NAME
    }
    requests.post(url, data=data)
def add_face_to_cloud(image_bytes, user_name):
    url_detect = "https://api-us.faceplusplus.com/facepp/v3/detect"
    files = {'image_file': image_bytes}
    data_detect = {'api_key': API_KEY_FIX, 'api_secret': API_SECRET_FIX}
    res_detect = requests.post(url_detect, data=data_detect, files=files).json()
    if "faces" in res_detect and len(res_detect["faces"]) > 0:
        face_token = res_detect["faces"][0]["face_token"]
        clean_name = user_name.replace(" ", "_")
        url_add = "https://api-us.faceplusplus.com/facepp/v3/faceset/addface"
        data_add = {
            'api_key': API_KEY_FIX, 
            'api_secret': API_SECRET_FIX,
            'outer_id': FACESET_NAME,
            'face_tokens': face_token
        }
        requests.post(url_add, data=data_add)
        url_set = "https://api-us.faceplusplus.com/facepp/v3/face/setuserid"
        data_set = {
            'api_key': API_KEY_FIX, 
            'api_secret': API_SECRET_FIX,
            'face_token': face_token,
            'user_id': clean_name
        }
        requests.post(url_set, data=data_set)
        return True, clean_name
    else:
        return False, "Wajah tidak terdeteksi"
def search_face_in_cloud(image_bytes):
    url = "https://api-us.faceplusplus.com/facepp/v3/search"
    files = {'image_file': image_bytes}
    data = {
        'api_key': API_KEY_FIX, 
        'api_secret': API_SECRET_FIX,
        'outer_id': FACESET_NAME, 
        'return_result_count': 1 
    }
    try:
        response = requests.post(url, data=data, files=files, timeout=10)
        return response.json()
    except Exception as e:
        return {"error_message": str(e)}

def _compare(img1, img2):
    url = "https://api-us.faceplusplus.com/facepp/v3/compare"
    files = {'image_file1': img1, 'image_file2': img2}
    data = {'api_key': API_KEY_FIX, 'api_secret': API_SECRET_FIX}
    return requests.post(url, data=data, files=files).json()
if 'setup_done' not in st.session_state:
    create_faceset_if_not_exists()
    st.session_state['setup_done'] = True

tab1, tab2, tab3 = st.tabs(["Registrasi", " Absensi ", "Compare"])
with tab1:
    st.header("Registrasi")
    reg_name = st.text_input("Nama User:")
    mode = st.radio("Input:", ["Kamera", "Upload"], horizontal=True, key="reg")
    
    img = st.camera_input("Foto", key="c1") if mode == "Kamera" else st.file_uploader("Upload", key="u1")
    
    if st.button("Simpan Wajah"):
        if reg_name and img:
            with st.spinner("Mendaftarkan ke"):
                success, msg = add_face_to_cloud(img.getvalue(), reg_name)
                if success:
                    st.success(f"Berhasil! {msg} terdaftar.")
                else:
                    st.error(f"Gagal: {msg}")
with tab2:
    st.header("Absensi ")
    mode_src = st.radio("Input:", ["Kamera", "Upload"], horizontal=True, key="src")
    q_img = st.camera_input("Scan", key="c2") if mode_src == "Kamera" else st.file_uploader("Upload", key="u2")
    
    if st.button("SCAN SEKARANG", type="primary"):
        if q_img:
            with st.spinner("Mencari..."):
                res = search_face_in_cloud(q_img.getvalue())

                if "results" in res:
                    if not res["results"]:
                        st.error("Wajah tidak ditemukan di database.")
                    else:
                        top_match = res["results"][0]
                        confidence = top_match["confidence"]
                        
                        if "thresholds" in res:
                            threshold = res["thresholds"]["1e-5"]
                        else:
                            threshold = 80.0
                        
                        if confidence > threshold:
                            user_id = top_match.get("user_id", "Unknown")
                            st.success(f"Halo, {user_id}!")
                            st.caption(f"Akurasi: {confidence}%")
                        else:
                            st.error("Tidak dikenal")
                            st.caption(f"Skor: {confidence}%")
                else:
                    st.error("Error dari API:")
                    st.write(res)
        else:
            st.warning("Foto belum ada.")

with tab3:
    st.write("Bandingkan 2 foto.")
    c1, c2 = st.columns(2)
    f1 = c1.file_uploader("Foto A", key="m1")
    f2 = c2.file_uploader("Foto B", key="m2")
    
    if st.button("Bandingkan"):
        if f1 and f2:
            res = _compare(f1.getvalue(), f2.getvalue())
            if "confidence" in res:
                sc = res["confidence"]
                if sc > res["thresholds"]["1e-5"]:
                    st.success(f"SAMA ({sc}%)")
                else:
                    st.error(f"BEDA ({sc}%)")
