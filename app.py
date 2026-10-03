import streamlit as st

# 페이지 설정
st.set_page_config(page_title="유튜브 코드/스템 추출기", page_icon="🎵")

# 비밀번호 설정 (나중에 편하게 바꿔서 쓰면 돼)
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

# 메인 앱 로직 (로그인 성공 시에만 실행됨)
if check_password():
    st.title("🎸 유튜브 악기 분리 & 코드 추출기")
    st.markdown("유튜브 링크를 넣으면 스템(보컬/악기)을 분리하고 코드 진행을 분석해 줄게!")

    # 유튜브 링크 입력받기
    youtube_url = st.text_input("유튜브 링크를 입력해줘", placeholder="https://www.youtube.com/watch?v=...")

    if st.button("분석 시작"):
        if youtube_url:
            st.success(f"입력된 링크: {youtube_url} (분석 기능은 다음 단계에 붙여볼게!)")
        else:
            st.warning("유튜브 링크를 먼저 입력해 줘.")
