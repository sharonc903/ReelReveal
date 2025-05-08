import streamlit as st
import subprocess
import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="Video Ad Analyzer", layout="centered")
st.title("📺 Video Ad Analyzer")

video_url = st.text_input("Paste your TikTok or Reels video link")

if st.button("Analyze"):
    try:
        with st.spinner("Downloading video..."):
            subprocess.run(["yt-dlp", video_url, "-o", "video.mp4"], check=True)

        with st.spinner("Converting to audio..."):
            audio_file_path = "audio.mp3"
            subprocess.run([
                "ffmpeg", "-i", "video.mp4",
                "-ar", "16000", "-ac", "1", "-f", "mp3", audio_file_path
            ], check=True)

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

    except subprocess.CalledProcessError:
        st.error("Failed to download or convert the video. Please check the link.")
    except Exception as e:
        st.error(f"Error: {str(e)}")
