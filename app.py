import asyncio
import io
import edge_tts
import streamlit as st

# Page Configuration (Mobile-friendly layout)
st.set_page_config(
    page_title="Mobile Recap & Voice Tool", page_icon="🎙️", layout="centered"
)

st.markdown("### 📱 Mobile Recap & Voice Tool")


# Async function for Edge-TTS (GitHub မှာ ချောမွေ့စွာ run နိုင်ရန်)
async def generate_edge_audio(text, voice_name):
  communicate = edge_tts.Communicate(text, voice_name)
  audio_buffer = io.BytesIO()
  async for chunk in communicate.stream():
    if chunk["type"] == "audio":
      audio_buffer.write(chunk["data"])
  audio_buffer.seek(0)
  return audio_buffer.read()


# Sidebar - Voice Selection (Mobile မှာ menu ကနေ ဝင်ရလို့ သန့်ရှင်းပါတယ်)
with st.sidebar:
  st.markdown("### ⚙️ ဆက်တင်များ (Settings)")
  voice_choice = st.selectbox(
      "အသံအမျိုးအစား (Voice Type)",
      options=[
          ("my-MM-NilarNeural", "👩 အမျိုးသမီးအသံ (Nilar - Natural)"),
          ("my-MM-ThuraNeural", "👨 အမျိုးသားအသံ (Thura - Natural)"),
      ],
      format_func=lambda x: x[1],
  )
  recap_length = st.selectbox(
      "အကျဉ်းချုပ် ပုံစံ", ["အတိုစား (Short)", "အရှည် (Detailed)"]
  )

# Main Form (ဖုန်းမှာ Input တွေ ရှုပ်မသွားအောင် Form နဲ့ သုံးထားပါတယ်)
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
      # ဤနေရာတွင် AI Recap logic ထည့်နိုင်ပါသည်။ (ယခု ဥပမာအနေဖြင့် ထည့်ထားသော စာသားကို ပြထားပါသည်)
      recap_result = f"ရရှိလာသော အကျဉ်းချုပ် ({recap_length}):\n\n{user_text}"

      # Session State ထဲမှာ သိမ်းဆည်းခြင်း (Refresh ဖြစ်တဲ့အခါ ပျောက်မသွားရန်)
      st.session_state["recap_result"] = recap_result

      # Edge-TTS ဖြင့် အသံဖိုင်ထုတ်ယူခြင်း
      try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        audio_bytes = loop.run_until_complete(
            generate_edge_audio(recap_result, voice_choice)
        )
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
