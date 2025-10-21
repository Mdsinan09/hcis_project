import streamlit as st
import time
import os

def dashboard_ui():
    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center;'>Multimedia Deepfake & AI Hallucination Detector</h1>", unsafe_allow_html=True)
    st.markdown(
        "<div style='text-align: center;font-size:18px;'>Upload any file — <b>Video, Audio, or Text</b> — to analyze if the content is fabricated or AI-generated.</div>",
        unsafe_allow_html=True
    )
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        uploaded_file = st.file_uploader(
            "Supported File Formats",
           
            help="Video (mp4, avi, mov, mkv), Audio (mp3, wav), Text (.txt)"
        )

        st.markdown("<div style='margin: 22px 0 0;'></div>", unsafe_allow_html=True)
        analyze_clicked = st.button("🔍 Analyze File", use_container_width=True)

        if analyze_clicked:
            if uploaded_file is not None:
                file_name = uploaded_file.name
                file_ext = os.path.splitext(file_name)[1].lower()
                progress_bar = st.progress(0, text="Initializing analysis...")
                stages = [
                    "Uploading file to server",
                    "Extracting and preprocessing data",
                    "Running deepfake and hallucination detection",
                    "Aggregating multimodal results",
                    "Generating summary report"
                ]
                for i, stage in enumerate(stages):
                    progress_bar.progress((i + 1) * 20, text=stage + " ⏳")
                    time.sleep(1)
                progress_bar.empty()
                st.success(f"✅ Analysis complete for **{file_name}**!")

                # Simulated results (as before)
                if file_ext in [".mp4", ".avi", ".mov", ".mkv"]:
                    st.subheader("🎥 Video Analysis Result", divider="blue")
                    st.metric(label="Authenticity Score", value="89%")
                    st.progress(0.89)
                    st.caption("No visual manipulation or deepfake artifacts detected.")
                elif file_ext in [".mp3", ".wav"]:
                    st.subheader("🎧 Audio Analysis Result", divider="blue")
                    st.metric(label="Authenticity Score", value="75%")
                    st.progress(0.75)
                    st.caption("Voice patterns consistent with natural human speech.")
                elif file_ext == ".txt":
                    st.subheader("📝 Text Analysis Result", divider="blue")
                    st.metric(label="Reliability Score", value="68%")
                    st.progress(0.68)
                    st.caption("Minor signs of AI hallucination or altered phrasing detected.")
                else:
                    st.warning("⚠️ Unsupported file type. Please upload a valid video, audio, or text file.")
            else:
                st.warning("⚠️ Please upload a file first.")
