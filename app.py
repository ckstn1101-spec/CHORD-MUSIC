import streamlit as st
import os
from yt_dlp import YoutubeDL

# 페이지 설정
st.set_page_config(page_title="유튜브 코드/스템 추출기", page_icon="🎵")

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
    st.title("🎸 유튜브 오디오 추출기")
    st.markdown("유튜브 링크를 넣으면 오디오를 추출해서 바로 들려줄게!")

    youtube_url = st.text_input("유튜브 링크를 입력해줘", placeholder="https://www.youtube.com/watch?v=...")

    if st.button("오디오 추출하기"):
        if youtube_url:
            with st.spinner("유튜브에서 오디오를 가져오는 중이야... 잠시만 기다려줘!"):
                try:
                    # 서버 환경에서 에러 안 나게 ffmpeg 없이 오디오 스트림만 다운로드
                    output_file = "audio.m4a"
                    if os.path.exists(output_file):
                        os.remove(output_file)

                    ydl_opts = {
                        'format': 'bestaudio',
                        'outtmpl': output_file,
                    }
                    
                    with YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(youtube_url, download=True)
                        title = info.get('title', '제목 없음')
                    
                    st.success(f"추출 성공! 🎵 곡 제목: {title}")
                    st.audio(output_file)
                    
                except Exception as e:
                    st.error(f"오디오를 가져오는 중에 문제가 생겼어: {e}")
        else:
            st.warning("유튜브 링크를 먼저 입력해 줘.")
