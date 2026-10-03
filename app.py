import streamlit as st
import os
import glob
import librosa
import numpy as np
from yt_dlp import YoutubeDL

# 페이지 설정
st.set_page_config(page_title="유튜브 키 & 코드 분석기", page_icon="🎵")

st.title("🎸 유튜브 키 & 코드 분석기")
st.markdown("노래 제목이나 가수명을 검색하면 유튜브에서 찾아줄게!")

# 검색어 입력
search_query = st.text_input("검색할 곡 제목을 입력해줘", placeholder="예: DAY6 예뻤어")

if search_query:
    with st.spinner("유튜브에서 곡을 검색하는 중..."):
        try:
            # 유튜브 검색 옵션 (상위 5개 검색)
            search_opts = {
                'extract_flat': True,
                'extractor_args': {'youtube': {'player_client': ['mweb']}},
            }
            
            with YoutubeDL(search_opts) as ydl:
                search_result = ydl.extract_info(f"ytsearch5:{search_query}", download=False)
                entries = search_result.get('entries', [])
            
            if not entries:
                st.warning("검색 결과가 없네. 다른 검색어로 다시 입력해 봐!")
            else:
                # 검색된 영상들의 제목과 URL을 딕셔너리로 매핑
                video_options = {}
                for entry in entries:
                    title = entry.get('title')
                    url = entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}"
                    if title:
                        video_options[title] = url
                
                # 사용자가 목록에서 선택할 수 있도록 셀렉트박스 제공
                selected_title = st.selectbox("검색된 곡 중 분석할 노래를 골라봐!", list(video_options.keys()))
                
                if st.button("선택한 곡 분석 시작"):
                    selected_url = video_options[selected_title]
                    
                    with st.spinner(f"'{selected_title}' 오디오 가져와서 분석 중이야... 잠시만 기다려줘!"):
                        # 기존 파일 청소
                        for f in glob.glob("audio.*"):
                            os.remove(f)

                        download_opts = {
                            'outtmpl': 'audio.%(ext)s',
                            'extractor_args': {'youtube': {'player_client': ['mweb']}},
                            'nocheckcertificate': True,
                        }
                        
                        with YoutubeDL(download_opts) as ydl:
                            ydl.download([selected_url])
                        
                        downloaded_files = glob.glob("audio.*")
                        if not downloaded_files:
                            raise Exception("오디오 다운로드에 실패했어.")
                        output_file = downloaded_files[0]
                        
                        st.success(f"오디오 추출 성공! 🎵 {selected_title}")
                        st.audio(output_file)

                        # Librosa를 이용한 키(Key) 분석
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
