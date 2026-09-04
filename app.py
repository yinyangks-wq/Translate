import streamlit as st
import asyncio
import edge_tts
import re

st.set_page_config(page_title="Movie Recap Voice & SRT Generator", page_icon="🎙️")

st.title("🎙️ Unlimited Voice & SRT Generator")
st.write("Movie Recap Script များကို စာလုံးရေ အကန့်အသတ်မရှိ Audio (.mp3) နှင့် Subtitle (.srt) သို့ ပြောင်းလဲပေးသည့် Tool")

# Script ထည့်ရန် Text Area
script_text = st.text_area("Recap Script စာသားများကို ဒီမှာ Paste လုပ်ပါ:", height=250)

# Voice ရွေးချယ်ရန်
voice_option = st.selectbox(
    "အသံအမျိုးအစား ရွေးပါ:",
    [
        ("မြန်မာ - Nilar (Female)", "my-MM-NilarNeural"),
        ("မြန်မာ - Thiha (Male)", "my-MM-ThihaNeural"),
        ("English - Christopher (Male)", "en-US-ChristopherNeural"),
        ("English - Ava (Female)", "en-US-AvaNeural")
    ],
    format_func=lambda x: x[0]
)

# Text မှ SRT Format သို့ ပြောင်းပေးသည့် Logic
def text_to_srt(text):
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    srt_content = ""
    start_time = 0  # Seconds
    
    for i, line in enumerate(lines, 1):
        # စာကြောင်းအရှည်ပေါ် မူတည်ပြီး ကြာချိန် တွက်ချက်ခြင်း (၁ စာလုံးလျှင် ၀.၃ စက္ကန့်ခန့်)
        duration = max(2, len(line) * 0.25)
        end_time = start_time + duration
        
        def format_time(seconds):
            hrs = int(seconds // 3600)
            mins = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            msecs = int((seconds - int(seconds)) * 1000)
            return f"{hrs:02d}:{mins:02d}:{secs:02d},{msecs:03d}"
        
        srt_content += f"{i}\n"
        srt_content += f"{format_time(start_time)} --> {format_time(end_time)}\n"
        srt_content += f"{line}\n\n"
        
        start_time = end_time
        
    return srt_content

# Edge-TTS Audio Generation Logic
async def generate_audio_file(text, voice_code):
    communicate = edge_tts.Communicate(text, voice_code)
    await communicate.save("output_voice.mp3")

# Main Action Button
if st.button("🚀 Audio နှင့် SRT ထုတ်ယူမည်"):
    if script_text.strip():
        with st.spinner("Audio နှင့် Subtitle များ ဖန်တီးနေပါသည်။ ခဏစောင့်ပါ..."):
            # 1. Voice (.mp3) ထုတ်ခြင်း
            voice_code = voice_option[1]
            asyncio.run(generate_audio_file(script_text, voice_code))
            
            # 2. Subtitle (.srt) ထုတ်ခြင်း
            srt_data = text_to_srt(script_text)
            
            st.success("✨ ဖန်တီးမှု အောင်မြင်ပါသည်။")
            
            # Audio Player
            audio_file = open("output_voice.mp3", "rb")
            audio_bytes = audio_file.read()
            st.audio(audio_bytes, format="audio/mp3")
            
            col1, col2 = st.columns(2)
            
            # Download Buttons
            with col1:
                st.download_button(
                    label="📥 Download Audio (.mp3)",
                    data=audio_bytes,
                    file_name="recap_voice.mp3",
                    mime="audio/mp3"
                )
            
            with col2:
                st.download_button(
                    label="📥 Download Subtitle (.srt)",
                    data=srt_data,
                    file_name="recap_subtitles.srt",
                    mime="text/plain"
                )
    else:
        st.error("ကျေးဇူးပြု၍ Script စာသား ထည့်သွင်းပါ။")
