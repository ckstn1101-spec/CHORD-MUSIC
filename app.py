import streamlit as st
import os
import glob
import librosa
import numpy as np
from yt_dlp import YoutubeDL

# 페이지 설정
st.set_page_config(page_title="유튜브 키 & 코드 분석기", page_icon="🎵")

st.title("🎸 유튜브 키 & 코드 분석기")
st.markdown("노래 제목이나 가수명을 검색하면 유튜브 영상과 함께 다양한 7도화음·텐션 코드가 포함된 타임라인을 분석해 줄게!")

# 검색어 입력
search_query = st.text_input("검색할 곡 제목을 입력해줘", placeholder="예: DAY6 예뻤어")

if search_query:
    with st.spinner("유튜브에서 곡을 검색하는 중..."):
        try:
            # 검색 시에도 ios/web 조합 클라이언트 사용
            search_opts = {
                'extract_flat': True,
                'extractor_args': {'youtube': {'player_client': ['ios', 'web']}},
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
                
                # 유튜브 영상 플레이어 표시
                st.markdown("---")
                st.subheader(f"▶️ 선택한 영상: {selected_title}")
                st.video(selected_url)
                
                # 분석 버튼
                if st.button("이 영상 오디오 추출 및 상세 코드 진행 분석하기"):
                    with st.spinner("오디오를 가져와서 정밀 코드 분석 중이야... 잠시만 기다려줘!"):
                        for f in glob.glob("audio.*"):
                            os.remove(f)

                        # 💡 403 에러 우회를 위해 ios/web 클라이언트 조합 적용
                        download_opts = {
                            'format': 'bestaudio/best',
                            'outtmpl': 'audio.%(ext)s',
                            'extractor_args': {'youtube': {'player_client': ['ios', 'web']}},
                            'nocheckcertificate': True,
                        }
                        
                        with YoutubeDL(download_opts) as ydl:
                            ydl.download([selected_url])
                        
                        downloaded_files = glob.glob("audio.*")
                        if not downloaded_files:
                            raise Exception("오디오 다운로드에 실패했어.")
                        output_file = downloaded_files[0]
                        
                        st.success("오디오 추출 및 정밀 분석 완료!")

                        # ---------------------------------------------------------
                        # Librosa를 이용한 키(Key) 및 다양한 코드 템플릿 분석
                        # ---------------------------------------------------------
                        st.markdown("---")
                        st.subheader("🔍 음악 AI 정밀 분석 결과")
                        
                        # 서버 용량을 고려해 앞부분 45초 분석
                        y, sr = librosa.load(output_file, duration=45)
                        hop_length = 512
                        
                        # 크로마(Chroma) 특징 추출
                        chroma = librosa.feature.chroma_stft(y=y, sr=sr, hop_length=hop_length)
                        
                        # 전체 곡의 주요 키(Key) 추정
                        chroma_mean_total = np.mean(chroma, axis=1)
                        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
                        estimated_key = notes[np.argmax(chroma_mean_total)]
                        
                        st.metric(label="추정된 주요 키 (Key)", value=estimated_key)
                        
                        # 구간별 코드 진행 추정 (3초 단위)
                        chunk_duration = 3.0 
                        frames_per_chunk = int(sr * chunk_duration / hop_length)
                        total_frames = chroma.shape[1]
                        
                        # 다양한 코드 템플릿 정의
                        chord_templates = {
                            "": [1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0],             # Major
                            "m": [1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0],            # Minor
                            "7": [1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0],            # Dominant 7th
                            "maj7": [1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1],         # Major 7th
                            "m7": [1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0],           # Minor 7th
                            "sus4": [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0],          # Sus4
                            "sus2": [1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0],          # Sus2
                            "dim": [1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0],           # Diminished
                            "aug": [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],           # Augmented
                            "add9": [1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0],         # Add9
                        }
                        
                        chord_names = []
                        template_matrix = []
                        for i, note in enumerate(notes):
                            for suffix, template in chord_templates.items():
                                chord_names.append(note + suffix)
                                template_matrix.append(np.roll(template, i))
                        template_matrix = np.array(template_matrix)
                        
                        progression_data = []
                        for start_f in range(0, total_frames, frames_per_chunk):
                            end_f = min(start_f + frames_per_chunk, total_frames)
                            chunk_chroma = chroma[:, start_f:end_f]
                            if chunk_chroma.shape[1] == 0:
                                break
                            mean_chroma = np.mean(chunk_chroma, axis=1)
                            scores = np.dot(template_matrix, mean_chroma)
                            best_idx = np.argmax(scores)
                            
                            start_time = int(start_f * hop_length / sr)
                            end_time = int(end_f * hop_length / sr)
                            chord_name = chord_names[best_idx]
                            
                            progression_data.append({
                                "구간": f"{start_time}초 ~ {end_time}초",
                                "추정 코드": chord_name
                            })
                        
                        st.markdown("### 📊 타임라인별 상세 코드 진행 (앞부분 45초)")
                        st.table(progression_data)
                        st.info("💡 팁: 403 우회 클라이언트를 `ios, web`으로 교체했어!")
                        
        except Exception as e:
            st.error(f"분석 중에 문제가 생겼어: {e}")
