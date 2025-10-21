import streamlit as st
import traceback

# Helper function for both status and color, per your rule
def get_status(value):
    if value < 40:
        return ('Fabricated', '#FF3B30')  # Red
    elif value < 70:
        return ('Suspicious', '#FFD600')  # Yellow
    else:
        return ('Authentic', '#00c853')   # Green

def report_ui():
    st.title(" HCIS — Report (Diagnostic)")
    try:
        st.markdown('<h2 style="font-size:1.2rem;">Component Analysis</h2>', unsafe_allow_html=True)

       
        
        # Example backend data; replace these with your backend values
        fusion_score = 85
        video_score = 84
        audio_score = 74
        text_score = 68

        # Get dynamic status and color for each
        fusion_label, fusion_color = get_status(fusion_score)
        video_label, video_color = get_status(video_score)
        audio_label, audio_color = get_status(audio_score)
        text_label, text_color = get_status(text_score)

        # Fusion circle and label
        st.markdown(f"""
        <div style="width:100%;display:flex;flex-direction:column;align-items:center;margin-bottom:50px;">
            <div style="
                width:220px;height:220px;border-radius:50%;
                display:flex;flex-direction:column;align-items:center;justify-content:center;
                background:{fusion_color};
                color:white;font-weight:700;font-size:28px;box-shadow:0 4px 10px rgba(0,0,0,0.18);">
                {fusion_label}<br>{fusion_score}%
            </div>
            <div style="margin-top:16px;font-size:22px;font-weight:600;color:{fusion_color};">Fusion</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Individual component circles and labels
        st.markdown(f"""
        <div style="width:100%;display:flex;justify-content:center;gap:60px;margin-bottom:35px;">
            <div style="display:flex;flex-direction:column;align-items:center;">
                <div style="width:130px;height:130px;border-radius:50%;background:{video_color};display:flex;align-items:center;justify-content:center;color:white;box-shadow:0 2px 8px rgba(0,0,0,0.11);">
                    <div style="text-align:center;font-weight:700;">🎥<br>{video_label}<br>{video_score}%</div>
                </div>
                <div style="margin-top:10px;font-size:18px;font-weight:500;color:{video_color};">Video</div>
            </div>
            <div style="display:flex;flex-direction:column;align-items:center;">
                <div style="width:130px;height:130px;border-radius:50%;background:{audio_color};display:flex;align-items:center;justify-content:center;color:white;box-shadow:0 2px 8px rgba(0,0,0,0.08);">
                    <div style="text-align:center;font-weight:700;">🔊<br>{audio_label}<br>{audio_score}%</div>
                </div>
                <div style="margin-top:10px;font-size:18px;font-weight:500;color:{audio_color};">Audio</div>
            </div>
            <div style="display:flex;flex-direction:column;align-items:center;">
                <div style="width:130px;height:130px;border-radius:50%;background:{text_color};display:flex;align-items:center;justify-content:center;color:white;box-shadow:0 2px 8px rgba(0,0,0,0.08);">
                    <div style="text-align:center;font-weight:700;">📝<br>{text_label}<br>{text_score}%</div>
                </div>
                <div style="margin-top:10px;font-size:18px;font-weight:500;color:{text_color};">Text</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.download_button("📥 Download Report", data="Report placeholder", file_name="report.txt")

    except Exception as e:
        st.error("An error occurred while rendering the report page.")
        st.exception(e)
        st.text("Full traceback:")
        st.text(traceback.format_exc())
