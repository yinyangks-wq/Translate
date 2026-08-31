import streamlit as st
import requests

# Page Configuration
st.set_page_config(
    page_title="🎙️ Text/Transcript to Myanmar Voice Generator",
    page_icon="🔊",
    layout="centered"
)

st.title("🔊 Direct Text-to-Speech Voice Generator")
st.write("Transcript သို့မဟုတ် Movie Recap Script စာသားများကို ထည့်သွင်းရုံဖြင့် ElevenLabs အသုံးပြု၍ မြန်မာအသံဖိုင် (.mp3) အဖြစ် တိုက်ရိုက်ပြောင်းလဲနိုင်ပါသည်။")

# API Key Input
elevenlabs_api_key = st.text_input("ElevenLabs API Key ထည့်ပါ:", type="password")

# Text Input (Transcript သို့မဟုတ် Script ထည့်ရန်)
input_text = st.text_area("Recap Script သို့မဟုတ် Transcript စာသားများကို ဤနေရာတွင် ရိုက်ထည့်ပါ (သို့မဟုတ်) ကူးထည့်ပါ:", height=200)

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

if st.button("🚀 စာသားများကို အသံဖိုင်သို့ ပြောင်းမည်"):
    if not elevenlabs_api_key:
        st.warning("ကျေးဇူးပြု၍ ElevenLabs API Key ကို အရင်ထည့်သွင်းပေးပါ။")
    elif not input_text.strip():
        st.warning("ကျေးဇူးပြု၍ ပြောင်းလဲလိုသော စာသားများကို ထည့်သွင်းပေးပါ။")
    else:
        try:
            with st.spinner("ElevenLabs ကို အသုံးပြု၍ အသံဖိုင် ထုတ်လုပ်နေပါပြီ... ခေတ္တစောင့်ဆိုင်းပေးပါ..."):
                url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
                
                headers = {
                    "Accept": "audio/mpeg",
                    "Content-Type": "application/json",
                    "xi-api-key": elevenlabs_api_key
                }
                
                payload = {
                    "text": input_text[:5000], # ElevenLabs ကန့်သတ်ချက်အရ တစ်ခါပို့လျှင် စာလုံးရေ ၅၀၀၀ ထိ ပို့နိုင်သည်
                    "model_id": "eleven_multilingual_v2",
                    "voice_settings": {
                        "stability": 0.5,
                        "similarity_boost": 0.75
                    }
                }

                tts_response = requests.post(url, json=payload, headers=headers)

                if tts_response.status_code == 200:
                    st.success("🎉 အသံဖိုင် အောင်မြင်စွာ ထွက်ရှိလာပါပြီ။")
                    
                    # Play Audio in Streamlit
                    st.audio(tts_response.content, format="audio/mp3")

                    # Download Audio Button
                    st.download_button(
                        label="📥 အသံဖိုင် (.mp3) ကို ဒေါင်းလုဒ်လုပ်ရန်",
                        data=tts_response.content,
                        file_name="myanmar_voiceover.mp3",
                        mime="audio/mpeg"
                    )
                else:
                    st.error(f"အမှားဖြစ်သွားပါသည်: {tts_response.text}")

        except Exception as e:
            st.error(f"အမှားအယွင်း ဖြစ်ပွားသွားပါသည်: {e}")
