import streamlit as st
import subprocess
import os
import openai

# בדיקה אם קיים API Key
api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="Video Ad Analyzer", layout="centered")
st.title("📺 Video Ad Analyzer")

if not api_key:
    st.error("❌ Missing OpenAI API Key. Please set OPENAI_API_KEY in Streamlit Secrets.")
else:
    openai.api_key = api_key
    video_url = st.text_input("Paste your TikTok or Reels video link")

    if st.button("Analyze"):
        try:
            with st.spinner("Downloading video..."):
                result = subprocess.run(["yt-dlp", video_url, "-o", "video.mp4"], check=True)

            if not os.path.exists("video.mp4"):
                st.error("❌ Video download failed — 'video.mp4' not found.")
            else:
                with st.spinner("Converting to audio..."):
                    audio_file_path = "audio.mp3"
                    subprocess.run([
                        "ffmpeg", "-i", "video.mp4",
                        "-ar", "16000", "-ac", "1", "-f", "mp3", audio_file_path
                    ], check=True)

                if not os.path.exists(audio_file_path):
                    st.error("❌ Audio conversion failed — 'audio.mp3' not found.")
                else:
                    with st.spinner("Transcribing with Whisper API..."):
                        with open(audio_file_path, "rb") as audio_file:
                            transcript_response = openai.Audio.transcribe("whisper-1", audio_file)
                            transcript = transcript_response["text"]

                        st.subheader("📝 Transcript")
                        st.write(transcript)

                    with st.spinner("Analyzing with GPT-4..."):
                        prompt = (
                            "Analyze the following video transcript. Extract:\n"
                            "1. The hook (what grabs attention).\n"
                            "2. A clear one-liner summarizing the message.\n"
                            "3. Key visual or emotional elements, marketing messages, or standout moments.\n\n"
                            + transcript
                        )

                        response = openai.ChatCompletion.create(
                            model="gpt-4",
                            messages=[
                                {"role": "system", "content": "You are a marketing content analyst."},
                                {"role": "user", "content": prompt}
                            ]
                        )

                        st.subheader("🎯 Analysis")
                        st.write(response['choices'][0]['message']['content'])

        except subprocess.CalledProcessError as e:
            st.error(f"❌ A subprocess failed: {str(e)}")
        except openai.error.OpenAIError as e:
            st.error(f"❌ OpenAI API error: {str(e)}")
        except Exception as e:
            st.error(f"❌ General error: {str(e)}")
