import streamlit as st

def show():
    """
    HCIS Dashboard - Main interface for the Holistic Content Integrity System.
    This page is structured to handle:
    1. Input Data (Video/Audio + Transcript)
    2. Run Integrity Check (Placeholder for pipeline integration)
    3. Display Results (Component Scores & Status)
    """

    # ------------------------------
    # Page Title
    # ------------------------------
    st.title("🛡️ Holistic Content Integrity System (HCIS)")
    st.markdown("---")

    # ------------------------------
    # 1. Input Section
    # ------------------------------
    st.header("1. Input Data")

    # Video / Audio File Uploader
    media_file = st.file_uploader(
        label="Upload Video or Audio Clip (.mp4, .wav, .avi, .mov, .mp3)",
        type=['mp4', 'mov', 'avi', 'wav', 'mp3'],
        key="media_file_uploader"
    )

    # Transcript Input
    transcript_text = st.text_area(
        label="Paste the AI-Generated Transcript or Claim Text",
        height=150,
        placeholder="E.g., 'The new policy passed yesterday will increase taxes by 50%.'",
        key="transcript_text_area"
    )

    # ------------------------------
    # 2. Run Analysis Button
    # ------------------------------
    st.markdown("---")
    if st.button("🔬 RUN HCIS INTEGRITY CHECK"):
        # Placeholder for pipeline execution
        st.info("Analysis started. Results will appear below...")
        # Example call (to implement in Week 2):
        # results = run_hcis_pipeline(media_file, transcript_text)
        st.success("Analysis completed (placeholder).")

    st.markdown("---")

    # ------------------------------
    # 3. Output Section
    # ------------------------------
    st.header("2. Integrity Results")

    # Status message
    st.warning("Awaiting Analysis Run...")

    # Component Scores (placeholders)
    st.subheader("Component Scores (Raw Output Placeholder)")
    st.code("""
Video Integrity Score (Lip-Sync): 0.0 (Awaiting Model)
Audio Integrity Score (Spectral): 0.0 (Awaiting Model)
Text Integrity Score (Fact-Check): 0.0 (Awaiting Model)
""", language='text')

    # Footer / Caption
    st.caption("This dashboard is structured and ready for integration with detection models and scoring logic.")
