import streamlit as st
from gtts import gTTS
import os

# Page Configuration
st.set_page_config(
    page_title="🔊 gTTS Myanmar Voice Generator",
    page_icon="🎙️",
    layout="centered"
)

st.title("🔊 gTTS Text-to-Myanmar Speech Generator")
st.write("Recap Script သို့မဟုတ် Transcript စာသားများကို ထည့်သွင်းရုံဖြင့် gTTS ဖြင့် အခမဲ့ မြန်မာအသံဖိုင် (.mp3) အဖြစ် ပြောင်းလဲနိုင်ပါသည်။ (API Key လုံးဝ မလိုပါ။)")

# Text Input (Script သို့မဟုတ် Transcript ထည့်ရန်)
input_text = st.text_area("ပြောင်းလဲလိုသော စာသားများကို ဤနေရာတွင် ရိုက်ထည့်ပါ (သို့မဟုတ်) ကူးထည့်ပါ:", height=200)

if st.button("🚀 အသံဖိုင်သို့ ပြောင်းမည်"):
    if not input_text.strip():
        st.warning("ကျေးဇူးပြု၍ ပြောင်းလဲလိုသော စာသားများကို ထည့်သွင်းပေးပါ။")
    else:
        try:
            with st.spinner("အသံဖိုင် ထုတ်လုပ်နေပါပြီ... ခေတ္တစောင့်ဆိုင်းပေးပါ..."):
                # gTTS ဖြင့် မြန်မာဘာသာစကား (`my`) ဖြင့် အသံဖိုင်ထုတ်ခြင်း
                tts = gTTS(text=input_text, lang='my', slow=False)
                
                # Temp audio file သိမ်းဆည်းရန်
                audio_file = "output_voice.mp3"
                tts.save(audio_file)

                st.success("🎉 အသံဖိုင် အောင်မြင်စွာ ထွက်ရှိလာပါပြီ။")
                
                # Play Audio in Streamlit
                st.audio(audio_file, format="audio/mp3")

                # Download Audio Button
                with open(audio_file, "rb") as f:
                    audio_bytes = f.read()
                    st.download_button(
                        label="📥 အသံဖိုင် (.mp3) ကို ဒေါင်းလုဒ်လုပ်ရန်",
                        data=audio_bytes,
                        file_name="myanmar_gtts_voice.mp3",
                        mime="audio/mpeg"
                    )

        except Exception as e:
            st.error(f"အမှားအယွင်း ဖြစ်ပွားသွားပါသည်: {e}")
