import streamlit as st
import os
import librosa
import numpy as np
from yt_dlp import YoutubeDL

# 페이지 설정
st.set_page_config(page_title="유튜브 키 & 코드 분석기", page_icon="🎵")

# 비밀번호 설정
PASSWORD = "1234"

def check_password():
    """비밀번호 인증 함수"""
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if st.session_state["authenticated"]:
        return True

    st.subheader("🔒 로그인이 필요해")
    input_pw = st.text_input("비밀번호를 입력해줘", type="password")
    
    if st.button("로그인"):
        if input_pw == PASSWORD:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("비밀번호가 틀렸어!")
    return False

# 메인 앱 로직
if check_password():
    st.title("🎸 유튜브 키 & 코드 분석기")
    st.markdown("유튜브 링크를 넣으면 오디오를 추출하고 키와 코드 성향을 분석해 줄게!")

    youtube_url = st.text_input("유튜브 링크를 입력해줘", placeholder="https://www.youtube.com/watch?v=...")

    if st.button("분석 시작"):
        if youtube_url:
            with st.spinner("유튜브에서 오디오를 가져와서 분석하는 중이야... 잠시만 기다려줘!"):
                try:
                    output_file = "audio.m4a"
                    if os.path.exists(output_file):
                        os.remove(output_file)

                    # iOS 및 Web 클라이언트를 복합적으로 사용하는 우회 옵션
                    ydl_opts = {
                        'format': 'bestaudio',
                        'outtmpl': output_file,
                        'extractor_args': {'youtube': {'player_client': ['ios', 'web']}},
                        'nocheckcertificate': True,
                    }
                    
                    with YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(youtube_url, download=True)
                        title = info.get('title', '제목 없음')
                    
                    st.success(f"오디오 추출 성공! 🎵 곡 제목: {title}")
                    st.audio(output_file)

                    # Librosa를 이용한 간단한 키(Key) 분석
                    st.markdown("---")
                    st.subheader("🔍 음악 AI 분석 결과")
                    
                    # 서버 용량 과부하 방지를 위해 앞부분 30초만 로드해서 분석
                    y, sr = librosa.load(output_file, duration=30)
                    
                    # 크로마(Chroma) 특징 추출을 통한 키 추정
                    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
                    chroma_mean = np.mean(chroma, axis=1)
                    
                    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
                    estimated_key_idx = np.argmax(chroma_mean)
                    estimated_key = notes[estimated_key_idx]
                    
                    st.metric(label="추정된 주요 키 (Key)", value=estimated_key)
                    st.info("💡 팁: 서버 용량 제한 때문에 곡의 앞부분 30초를 기준으로 키를 분석했어!")
                    
                except Exception as e:
                    st.error(f"분석 중에 문제가 생겼어: {e}")
        else:
            st.warning("유튜브 링크를 먼저 입력해 줘.")
