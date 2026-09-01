import io
import edge_tts
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Mobile Recap & Voice Tool", page_icon="🎙️", layout="centered"
)

st.markdown("### 📱 Mobile Recap & Voice Tool")


# Edge-TTS အတွက် Error ကင်းရှင်းစေမည့် Synchronous Helper Function
def get_edge_audio_bytes(text, voice_name):
  async def _generate():
    communicate = edge_tts.Communicate(text, voice_name)
    audio_buffer = io.BytesIO()
    async for chunk in communicate.stream():
      if chunk["type"] == "audio":
        audio_buffer.write(chunk["data"])
    audio_buffer.seek(0)
    return audio_buffer.read()

  import asyncio

  try:
    return asyncio.run(_generate())
  except RuntimeError:
    # Streamlit Cloud ကဲ့သို့ environment များတွင် event loop ပြဿနာမရှိစေရန်
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(_generate())


# Sidebar - Voice Selection
with st.sidebar:
  st.markdown("### ⚙️ ဆက်တင်များ (Settings)")
  voice_choice = st.selectbox(
      "အသံအမျိုးအစား (Voice Type)",
      options=["my-MM-NilarNeural", "my-MM-ThuraNeural"],
      format_func=lambda x: (
          "👩 အမျိုးသမီးအသံ (Nilar)"
          if x == "my-MM-NilarNeural"
          else "👨 အမျိုးသားအသံ (Thura)"
      ),
  )

  recap_length = st.selectbox(
      "အကျဉ်းချုပ် ပုံစံ", ["အတိုစား (Short)", "အရှည် (Detailed)"]
  )

# Main Form
with st.form(key="recap_form"):
  user_text = st.text_area(
      "အကျဉ်းချုပ်လိုသော စာသားများကို ထည့်ပါ:",
      height=150,
      placeholder="ဆောင်းပါး သို့မဟုတ် စာသားရှည်များ ဤနေရာတွင် ကူးထည့်ပါ...",
  )
  submit_btn = st.form_submit_button(
      label="✨ Recap ပြုလုပ်ပြီး အသံဖိုင်ထုတ်မည်", use_container_width=True
  )

# Processing Logic
if submit_btn:
  if not user_text.strip():
    st.warning("ကျေးဇူးပြု၍ စာသားအနည်းငယ် ထည့်ပေးပါ။")
  else:
    with st.spinner("အကျဉ်းချုပ်နှင့် အသံဖိုင် ဖန်တီးနေသည်... ခဏစောင့်ပါ..."):
      # Recap Logic
      recap_result = f"ရရှိလာသော အကျဉ်းချုပ် ({recap_length}):\n\n{user_text}"
      st.session_state["recap_result"] = recap_result

      # Edge-TTS ဖြင့် အသံဖိုင်ထုတ်ယူခြင်း
      try:
        audio_bytes = get_edge_audio_bytes(recap_result, voice_choice)
        st.session_state["audio_bytes"] = audio_bytes
      except Exception as e:
        st.error(f"အသံဖိုင် ထုတ်ယူရာတွင် အမှားရှိပါသည်: {e}")

# ရလဒ်နှင့် အသံဖိုင် ပြသခြင်း
if "recap_result" in st.session_state:
  st.success("အောင်မြင်သည်!")
  st.markdown("#### 📄 ရလဒ် (Recap):")
  st.info(st.session_state["recap_result"])

  if "audio_bytes" in st.session_state:
    st.markdown("#### 🎧 အသံဖြင့် နားထောင်ရန်:")
    st.audio(st.session_state["audio_bytes"], format="audio/mp3")

  # ဖိုင်အဖြစ် သိမ်းရန် Download Button
  st.download_button(
      label="📥 Recap ကို Text ဖိုင်ဖြင့် သိမ်းမည်",
      data=st.session_state["recap_result"],
      file_name="recap_result.txt",
      mime="text/plain",
      use_container_width=True,
  )
