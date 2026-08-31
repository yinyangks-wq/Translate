import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from google import genai

# Page Configuration
st.set_page_config(
    page_title="🎬 AI Movie Recap Generator (200k Limit)",
    page_icon="🎥",
    layout="centered"
)

st.title("🎥 YouTube Movie Recap Generator (200k Limit)")
st.write("နာရီရှည်ရုပ်ရှင်များ၏ Transcript များကို စာလုံးရေ 200k အထိ ထည့်သွင်းပြီး AI ဖြင့် Recap Script တည်ဆောက်နိုင်ပါသည်။")

# API Key Input
api_key = st.text_input("Google Gemini API Key ထည့်ပါ:", type="password")

# YouTube URL Input
youtube_url = st.text_input("YouTube Video Link (ဥပမာ - https://www.youtube.com/watch?v=xxxx):")

if st.button("🚀 Recap Script စတင်ဖန်တီးမည်"):
    if not api_key:
        st.warning("ကျေးဇူးပြု၍ Gemini API Key ကို အရင်ထည့်သွင်းပေးပါ။")
    elif not youtube_url:
        st.warning("ကျေးဇူးပြု၍ YouTube ဗီဒီယိုလင့်ခ်ကို ထည့်သွင်းပေးပါ။")
    else:
        try:
            with st.spinner("ဗီဒီယိုအချက်အလက်နှင့် Transcript များကို ရယူနေပါပြီ..."):
                # 1. Extract Video ID from URL
                if "v=" in youtube_url:
                    video_id = youtube_url.split("v=")[1].split("&")[0]
                elif "youtu.be/" in youtube_url:
                    video_id = youtube_url.split("youtu.be/")[1].split("?")[0]
                else:
                    st.error("မှန်ကန်သော YouTube Link ဖြစ်ကြောင်း စစ်ဆေးပါ။")
                    st.stop()

                # 2. Get Transcript from YouTube
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'my'])
                full_transcript = " ".join([item['text'] for item in transcript_list])

            with st.spinner("Gemini AI ဖြင့် 200k စာသားများကို အခြေခံ၍ Script ရေးသားနေပါပြီ..."):
                # 3. Configure Gemini Client
                client = genai.Client(api_key=api_key)
                
                # စာလုံးရေ 200k အထိ (Characters 200,000 ခန့်) ကန့်သတ်ချက်ထားရှိခြင်း
                processed_transcript = full_transcript[:200000]

                # Prompt for Movie Recap
                prompt = f"""
                အောက်ပါ ရုပ်ရှင်/ဗီဒီယို Transcript (စာသားအရှည်) ကို အခြေခံပြီး လူကြိုက်များတဲ့ TikTok သို့မဟုတ် YouTube Shorts ပုံစံ ဆွဲဆောင်မှုရှိပြီး ဇာတ်လမ်းအစအဆုံး ပြီးပြည့်စုံတဲ့ မြန်မာလို Movie Recap Script တစ်ခု ရေးပေးပါ။
                
                လိုအပ်ချက်များ:
                - စိတ်လှုပ်ရှားစရာ အစပျိုးခန်း (Hook) ပါဝင်ရမည်။
                - ဇာတ်လမ်းအနှစ်ချုပ်ကို အပိုင်းလိုက် ရှင်းလင်းပြတ်သားစွာ ရေးပေးပါ။
                - အသံထွက်ဖတ်လို့ကောင်းမည့် သဘာဝကျသော မြန်မာဘာသာစကားကို အသုံးပြုပါ။
                
                Transcript အပြည့်အစုံ (200k Limit):
                {processed_transcript}
                """

                # Generate content using gemini-2.5-flash
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                )

            st.success("🎉 Recap Script အောင်မြင်စွာ ထွက်လာပါပြီ။")
            
            # Display the script
            st.subheader("📝 ထွက်လာသော Script:")
            st.write(response.text)

            # Download button for the script
            st.download_button(
                label="📥 Script ကို Text ဖိုင်ဖြင့် ဒေါင်းလုဒ်လုပ်ရန်",
                data=response.text,
                file_name="movie_recap_script_200k.txt",
                mime="text/plain"
            )

        except Exception as e:
            st.error(f"အမှားအယွင်း ဖြစ်ပွားသွားပါသည်: {e}")
            st.info("အကြံပြုချက် - အချို့သော YouTube ဗီဒီယိုများသည် Subtitle ပိတ်ထားတတ်သဖြင့် Transcript ရယူ၍မရနိုင်ပါ။ Subtitle ပါသည့် ဗီဒီယိုလင့်ခ်ကို အသုံးပြုပေးပါ။")
