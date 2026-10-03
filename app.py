import streamlit as st
import os
import glob
import librosa
import numpy as np
from yt_dlp import YoutubeDL

# 페이지 설정
st.set_page_config(page_title="유튜브 키 & 코드 분석기", page_icon="🎵")

st.title("🎸 유튜브 키 & 코드 분석기")
st.markdown("노래 제목이나 가수명을 검색하면 유튜브 영상을 직접 띄워줄게!")

# 검색어 입력
search_query = st.text_input("검색할 곡 제목을 입력해줘", placeholder="예: DAY6 예뻤어")

if search_query:
    with st.spinner("유튜브에서 곡을 검색하는 중..."):
        try:
            search_opts = {
                'extract_flat': True,
                'extractor_args': {'youtube': {'player_client': ['tv_embedded']}},
                'nocheckcertificate': True,
            }
            
            with YoutubeDL(search_opts) as ydl:
                search_result = ydl.extract_info(f"ytsearch5:{search_query}", download=False)
                entries = search_result.get('entries', [])
            
            if not entries:
                st.warning("검색 결과가 없네. 다른 검색어로 다시 입력해 봐!")
            else:
                video_options = {}
                for entry in entries:
                    title = entry.get('title')
                    url = entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}"
                    if title:
                        video_options[title] = url
                
                # 사용자가 목록에서 선택
                selected_title = st.selectbox("검색된 곡 중 확인할 노래를 골라봐!", list(video_options.keys()))
                selected_url = video_options[selected_title]
                
                # 💡 유튜브 영상 플레이어를 화면에 직접 띄우기
                st.markdown("---")
                st.subheader(f"▶️ 선택한 영상: {selected_title}")
                st.video(selected_url)
                
                # 분석 버튼
                if st.button("이 영상 오디오 추출 및 키 분석하기"):
                    with st.spinner("오디오를 가져와서 분석 중이야... 잠시만 기다려줘!"):
                        for f in glob.glob("audio.*"):
                            os.remove(f)

                        download_opts = {
                            'outtmpl': 'audio.%(ext)s',
                            'extractor_args': {'youtube': {'player_client': ['tv_embedded']}},
                            'nocheckcertificate': True,
                        }
                        
                        with YoutubeDL(download_opts) as ydl:
                            ydl.download([selected_url])
                        
                        downloaded_files = glob.glob("audio.*")
                        if not downloaded_files:
                            raise Exception("오디오 다운로드에 실패했어.")
                        output_file = downloaded_files[0]
                        
                        st.success("오디오 추출 성공!")

                        # Librosa 키 분석
                        st.markdown("---")
                        st.subheader("🔍 음악 AI 분석 결과")
                        
                        y, sr = librosa.load(output_file, duration=30)
                        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
                        chroma_mean = np.mean(chroma, axis=1)
                        
                        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
                        estimated_key_idx = np.argmax(chroma_mean)
                        estimated_key = notes[estimated_key_idx]
                        
                        st.metric(label="추정된 주요 키 (Key)", value=estimated_key)
                        st.info("💡 팁: 서버 용량 제한 때문에 곡의 앞부분 30초를 기준으로 키를 분석했어!")
                        
        except Exception as e:
            st.error(f"분석 중에 문제가 생겼어: {e}")
