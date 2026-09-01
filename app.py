import io
import tempfile
import edge_tts
from google import genai
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Video Auto Recap & Voice Tool", page_icon="🎥", layout="centered"
)

st.markdown("### 🎥 Video to Myanmar Auto Recap & Voice")

# Sidebar - API Key and Settings
with st.sidebar:
  st.markdown("### ⚙️ ဆက်တင်များ (Settings)")
  api_key = st.text_input(
      "Gemini API Key ထည့်ပါ",
      type="password",
      placeholder="AIzaSy...",
      help=(
          "Google AI Studio မှ ရယူထားသော API Key ကို ဤနေရာတွင် ထည့်ပါ"
          " (သို့မဟုတ် st.secrets တွင် သုံးပါ)"
      ),
  )

  voice_choice = st.selectbox(
      "အသံအမျိုးအစား (Voice Type)",
      options=["my-MM-NilarNeural", "my-MM-ThuraNeural"],
      format_func=lambda x: (
          "👩 အမျိုးသမီးအသံ (Nilar)"
          if x == "my-MM-NilarNeural"
          else "👨 အမျိုးသားအသံ (Thura)"
      ),
  )

  recap_style = st.selectbox(
      "အကျဉ်းချုပ် ပုံစံ",
      [
          "အဓိကအချက်များ (Bullet points)",
          "အတိုစား အကျဉ်းချုပ် (Short Summary)",
          "အသေးစိတ် ရှင်းလင်းချက် (Detailed)",
      ],
  )


# Edge-TTS Helper Function
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
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(_generate())


# Main UI - Video Uploader Form
with st.form(key="video_recap_form"):
  uploaded_video = st.file_uploader(
      "ဗီဒီယိုဖိုင် တင်ပါ (MP4, MOV, AVI)", type=["mp4", "mov", "avi", "mkv"]
  )
  submit_btn = st.form_submit_button(
      label="✨ ဗီဒီယိုကို မြန်မာလို Recap လုပ်မည်", use_container_width=True
  )

# Processing Logic
if submit_btn:
  if not api_key:
    st.error(
        "ကျေးဇူးပြု၍ ဘယ်ဘက် Sidebar တွင် Gemini API Key ကို ထည့်သွင်းပေးပါ။"
    )
  elif not uploaded_video:
    st.warning("ကျေးဇူးပြု၍ ဗီဒီယိုဖိုင် တစ်ခု တင်ပေးပါ။")
  else:
    with st.spinner(
        "ဗီဒီယိုကို AI ဖြင့် ဖတ်ရှုနေသည်... (ခဏစောင့်ပါ)..."
    ):
      try:
        # Streamlit uploaded file ကို Temporary file အဖြစ် သိမ်းဆည်းခြင်း
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=".mp4"
        ) as tmp_file:
          tmp_file.write(uploaded_video.read())
          tmp_file_path = tmp_file.name

        # Google GenAI Client ကို ချိတ်ဆက်ခြင်း
        client = genai.Client(api_key=api_key)

        # Gemini ဖြင့် ဗီဒီယိုဖိုင်ကို Upload တင်ခြင်း
        st.info("ဗီဒီယိုကို Google ဆာဗာသို့ တင်နေပါပြီ...")
        video_file = client.files.upload(file=tmp_file_path)

        # Gemini API သုံးပြီး ဗီဒီယိုကို မြန်မာလို Recap လုပ်ခိုင်းခြင်း
        prompt = (
            f"ဤဗီဒီယိုပါ အကြောင်းအရာများကို လေ့လာပြီး မြန်မာဘာသာဖြင့်"
            f" {recap_style} ပုံစံဖြင့် အကျဉ်းချုပ် ရေးသားပေးပါ။ အခြားဘာသာစကားများ"
            " မရောပါစေနဲ့။"
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=[video_file, prompt]
        )

        recap_result = response.text
        st.session_state["recap_result"] = recap_result

        # ထွက်လာတဲ့ မြန်မာစာသားကို အသံဖိုင်ပြောင်းခြင်း
        audio_bytes = get_edge_audio_bytes(recap_result, voice_choice)
        st.session_state["audio_bytes"] = audio_bytes

        # အသုံးပြုပြီးသော ဖိုင်ကို ဖျက်ဆီးခြင်း
        client.files.delete(name=video_file.name)

      except Exception as e:
        st.error(f"အမှားအယွင်း ဖြစ်ပေါ်သည်: {e}")

# ရလဒ်နှင့် အသံဖိုင် ပြသခြင်း
if "recap_result" in st.session_state:
  st.success("အောင်မြင်သည်!")

  st.markdown("#### 📄 ဗီဒီယိုအကျဉ်းချုပ် (Myanmar Recap):")
  st.write(st.session_state["recap_result"])

  if "audio_bytes" in st.session_state:
    st.markdown("#### 🎧 အသံဖြင့် နားထောင်ရန်:")
    st.audio(st.session_state["audio_bytes"], format="audio/mp3")

  st.download_button(
      label="📥 အကျဉ်းချုပ်ကို Text ဖိုင်ဖြင့် သိမ်းမည်",
      data=st.session_state["recap_result"],
      file_name="video_recap.txt",
      mime="text/plain",
      use_container_width=True,
  )
