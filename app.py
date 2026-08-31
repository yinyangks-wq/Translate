import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from google import genai
import requests

# Page Configuration
st.set_page_config(
    page_title="🎬 AI Movie Recap & Voice Generator",
    page_icon="🎙️",
    layout="centered"
)

st.title("🎙️ AI Movie Recap & Voice Generator")
st.write("YouTube လင့်ခ်မှ Transcript ကို ယူ၍ Gemini ဖြင့် Script ရေးသားပြီး ElevenLabs ဖြင့် မြန်မာအသံအမျိုးမျိုး ထုတ်လုပ်နိုင်ပါသည်။")

# API Keys Input
st.subheader("🔑 API Keys ထည့်သွင်းရန်")
gemini_api_key = st.text_input("Google Gemini API Key:", type="password")
elevenlabs_api_key = st.text_input("ElevenLabs API Key:", type="password")

# YouTube URL Input
youtube_url = st.text_input("YouTube Video Link (ဥပမာ - https://www.youtube.com/watch?v=xxxx):")

# 🎙️ အသံအမျိုးမျိုး ရွေးချယ်ရန် (Voice ID များ)
st.subheader("🗣️ အသံအမျိုးအစား ရွေးချယ်ရန်")
voice_options = {
    "Rachel (အမျိုးသမီး - တည်ငြိမ်ပြေပြစ်သောသံ)": "21m00Tcm4TlvDq8ikWAM",
    "Adam (အမျိုးသား - လေးနက်ခန့်ညားသောသံ)": "pNInz6obpgDQGcFmaJgB",
    "Antony (အမျိုးသား - ဇာတ်ကြောင်းပြောရန်ကောင်းသောသံ)": "ErXwobaYiN019PkySvjV",
    "Bella (အမျိုးသမီး - ချိုသာကြည်လင်သောသံ)": "EXAVITQu4vr4xnSDxMaL",
    "Dom (အမျိုးသား - အားမာန်ပါသောသံ)": "AZnzlk1XvdvUeBnXmlld"
}

selected_voice_name = st.selectbox("ကြိုက်နှစ်သက်ရာ အသံပုံစံကို ရွေးပါ:", list(voice_options.keys()))
voice_id = voice_options[selected_voice_name]

if st.button("🚀 Script ဖန်တီး၍ အသံပြောင်းမည်"):
    if not gemini_api_key or not elevenlabs_api_key:
        st.warning("ကျေးဇူးပြု၍ Gemini API Key နှင့် ElevenLabs API Key နှစ်ခုစလုံးကို ထည့်သွင်းပေးပါ။")
    elif not youtube_url:
        st.warning("ကျေးဇူးပြု၍ YouTube ဗီဒီယိုလင့်ခ်ကို ထည့်သွင်းပေးပါ။")
    else:
        try:
            # 1. Fetch Transcript
            with st.spinner("ဗီဒီယိုမှ Transcript များကို ရယူနေပါပြီ..."):
                if "v=" in youtube_url:
                    video_id = youtube_url.split("v=")[1].split("&")[0]
                elif "youtu.be/" in youtube_url:
                    video_id = youtube_url.split("youtu.be/")[1].split("?")[0]
                else:
                    st.error("မှန်ကန်သော YouTube Link ဖြစ်ကြောင်း စစ်ဆေးပါ။")
                    st.stop()

                transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'my'])
                full_transcript = " ".join([item['text'] for item in transcript_list])

            # 2. Generate Script with Gemini
            with st.spinner("Gemini AI ဖြင့် Movie Recap Script ရေးသားနေပါပြီ..."):
                client = genai.Client(api_key=gemini_api_key)
                processed_transcript = full_transcript[:200000]

                prompt = f"""
                အောက်ပါ ရုပ်ရှင်/ဗီဒီယို Transcript ကို အခြေခံပြီး TikTok သို့မဟုတ် YouTube Shorts ပုံစံ ဆွဲဆောင်မှုရှိပြီး ဇာတ်လမ်းအစအဆုံး ပြီးပြည့်စုံတဲ့ မြန်မာလို Movie Recap Script တစ်ခု ရေးပေးပါ။ (မှတ်ချက် - အသံထွက်ဖတ်မည့် စာသားဖြစ်သောကြောင့် သဘာဝကျပြီး ပြောဆိုသကဲ့သို့ ဖြစ်ရမည်)
                
                Transcript အပြည့်အစုံ:
                {processed_transcript}
                """

                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                )
                recap_script = response.text

            st.success("🎉 Recap Script အောင်မြင်စွာ ထွက်လာပါပြီ။")
            st.subheader("📝 ထွက်လာသော Script:")
            st.write(recap_script)

            # 3. Convert Script to Speech using ElevenLabs API
            with st.spinner("ရွေးချယ်ထားသော အသံဖြင့် ElevenLabs တွင် အသံဖိုင် ထုတ်လုပ်နေပါပြီ..."):
                url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
                
                headers = {
                    "Accept": "audio/mpeg",
                    "Content-Type": "application/json",
                    "xi-api-key": elevenlabs_api_key
                }
                
                payload = {
                    "text": recap_script[:5000],
                    "model_id": "eleven_multilingual_v2",
                    "voice_settings": {
                        "stability": 0.5,
                        "similarity_boost": 0.75
                    }
                }

                tts_response = requests.post(url, json=payload, headers=headers)

                if tts_response.status_code == 200:
                    st.success("🎙️ အသံဖိုင် အောင်မြင်စွာ ထွက်ရှိလာပါပြီ။")
                    
                    # Play Audio in Streamlit
                    st.audio(tts_response.content, format="audio/mp3")

                    # Download Audio Button
                    st.download_button(
                        label="📥 အသံဖိုင် (.mp3) ကို ဒေါင်းလုဒ်လုပ်ရန်",
                        data=tts_response.content,
                        file_name="movie_recap_voiceover.mp3",
                        mime="audio/mpeg"
                    )
                else:
                    st.error(f"ElevenLabs အသံထုတ်ရာတွင် အမှားဖြစ်သွားပါသည်: {tts_response.text}")

        except Exception as e:
            st.error(f"အမှားအယွင်း ဖြစ်ပွားသွားပါသည်: {e}")
