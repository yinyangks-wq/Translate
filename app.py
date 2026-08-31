import streamlit as st
import edge_tts
import asyncio
import os

# Page Configuration
st.set_page_config(
    page_title="🎙️ Edge TTS Myanmar Voice Generator",
    page_icon="🔊",
    layout="centered"
)

st.title("🎙️ Edge TTS Myanmar Voice Generator")
st.write("စာသားများကို ထည့်သွင်းရုံဖြင့် Microsoft Edge ၏ အခမဲ့ AI အသံများဖြင့် အမျိုးသား/အမျိုးသမီး အသံအမျိုးမျိုး ပြောင်းလဲထုတ်လုပ်နိုင်ပါသည်။ (API Key လုံးဝ မလိုပါ)")

# Text Input
input_text = st.text_area("ပြောင်းလဲလိုသော စာသားများကို ဤနေရာတွင် ရိုက်ထည့်ပါ (သို့မဟုတ်) ကူးထည့်ပါ:", height=200)

# 🗣️ Edge TTS ၏ မြန်မာဘာသာစကားအတွက် အသံအမျိုးမျိုး (Voices)
voice_options = {
    "Thiha (အမျိုးသားအသံ - မြန်မာ)": "my-MM-ThihaNeural",
    "Nilar (အမျိုးသမီးအသံ - မြန်မာ)": "my-MM-NilarNeural"
}

selected_voice_name = st.selectbox("ကြိုက်နှစ်သက်ရာ အသံပုံစံကို ရွေးပါ:", list(voice_options.keys()))
selected_voice = voice_options[selected_voice_name]

# Async function to generate audio using edge_tts
async def generate_edge_tts(text, voice, output_file):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)

if st.button("🚀 အသံဖိုင်သို့ ပြောင်းမည်"):
    if not input_text.strip():
        st.warning("ကျေးဇူးပြု၍ ပြောင်းလဲလိုသော စာသားများကို ထည့်သွင်းပေးပါ။")
    else:
        output_file = "edge_output.mp3"
        
        with st.spinner("Microsoft Edge TTS ဖြင့် အသံဖိုင် ထုတ်လုပ်နေပါပြီ... ခေတ္တစောင့်ဆိုင်းပေးပါ..."):
            try:
                # Run async function in Streamlit
                asyncio.run(generate_edge_tts(input_text, selected_voice, output_file))

                st.success("🎉 အသံဖိုင် အောင်မြင်စွာ ထွက်ရှိလာပါပြီ။")
                
                # Play Audio in Streamlit
                st.audio(output_file, format="audio/mp3")

                # Download Audio Button
                with open(output_file, "rb") as f:
                    audio_bytes = f.read()
                    st.download_button(
                        label="📥 အသံဖိုင် (.mp3) ကို ဒေါင်းလုဒ်လုပ်ရန်",
                        data=audio_bytes,
                        file_name="edge_myanmar_voice.mp3",
                        mime="audio/mpeg"
                    )

            except Exception as e:
                st.error(f"အမှားအယွင်း ဖြစ်ပွားသွားပါသည်: {e}")
