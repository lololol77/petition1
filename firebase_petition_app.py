
import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import uuid
import io

FIREBASE_URL = "https://project1-de377-default-rtdb.firebaseio.com/"

# 청원 등록 함수
def add_petition(title, content, email):
    petition_id = str(uuid.uuid4())
    data = {
        "id": petition_id,
        "title": title,
        "content": content,
        "email": email,
        "likes": 0,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    res = requests.put(f"{FIREBASE_URL}/petitions/{petition_id}.json", json=data)
    return res.ok

# 청원 목록 조회
def get_petitions():
    res = requests.get(f"{FIREBASE_URL}/petitions.json")
    if res.ok and res.json():
        data = res.json()
        return sorted(data.values(), key=lambda x: (x.get("likes", 0), x.get("date")), reverse=True)
    return []

# 좋아요 처리
def like_petition(petition):
    petition_id = petition["id"]
    petition["likes"] += 1
    res = requests.patch(f"{FIREBASE_URL}/petitions/{petition_id}.json", json={"likes": petition["likes"]})
    return res.ok

# CSV 다운로드
def get_petitions_csv():
    data = get_petitions()
    df = pd.DataFrame(data)
    return df.to_csv(index=False).encode('utf-8')

# Streamlit UI
st.title("📢 Firebase 기반 청원 시스템")

menu = ["청원 작성", "청원 목록", "CSV 다운로드"]
choice = st.sidebar.selectbox("메뉴 선택", menu)

if choice == "청원 작성":
    st.header("✍️ 새로운 청원 등록")
    title = st.text_input("제목")
    content = st.text_area("내용")
    email = st.text_input("이메일")
    if st.button("제출"):
        if title and content and email:
            if add_petition(title, content, email):
                st.success("✅ 청원이 등록되었습니다.")
            else:
                st.error("❌ 등록 실패. 다시 시도해주세요.")
        else:
            st.warning("모든 항목을 입력해주세요.")

elif choice == "청원 목록":
    st.header("📄 청원 목록")
    petitions = get_petitions()
    for p in petitions:
        st.subheader(p["title"])
        st.write(p["content"])
        st.caption(f"등록일: {p['date']} | 이메일: {p['email']} | 좋아요: {p['likes']}")
        if st.button(f"👍 좋아요 ({p['likes']})", key=p["id"]):
            if like_petition(p):
                st.success("좋아요를 눌렀습니다!")
            else:
                st.error("이미 눌렀거나 오류가 발생했습니다.")

elif choice == "CSV 다운로드":
    st.header("⬇️ 전체 청원 데이터 다운로드")
    csv = get_petitions_csv()
    st.download_button("📄 CSV 다운로드", data=csv, file_name="petitions.csv", mime="text/csv")
