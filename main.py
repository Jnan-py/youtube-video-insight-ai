import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
import os
from fpdf import FPDF
from dotenv import load_dotenv
import json
from urllib.parse import urlparse, parse_qs
from streamlit_option_menu import option_menu
import re
import tempfile
import yt_dlp
import streamlit.components.v1 as components
import numpy as np
import time

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API"))

content_model = genai.GenerativeModel('gemini-2.0-flash-exp',
    system_instruction="You are the content generator, who can deliver the required information based on the transcript given."
)

vision_model = genai.GenerativeModel('gemini-2.0-flash-exp', 
    system_instruction = "You are a very good video analyzer and information extractor from video"
)

def extract_video_id(url):
    parsed = urlparse(url)
    if parsed.hostname == 'youtu.be':
        return parsed.path[1:]
    if parsed.hostname in ('www.youtube.com', 'youtube.com'):
        if parsed.path == '/watch':
            return parse_qs(parsed.query).get('v', [None])[0]
        if parsed.path.startswith('/embed/'):
            return parsed.path.split('/')[2]
        if parsed.path.startswith('/v/'):
            return parsed.path.split('/')[2]
    return None

def transcribe_video(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = transcript_list.find_transcript(['en'])
        translated = transcript.translate('en').fetch()
        return {
            'translated': ' '.join([i['text'] for i in translated]),
            'original': ' '.join([i['text'] for i in transcript.fetch()]),
            'language': transcript.language
        }

    except:
        try:
            transcript = transcript_list.find_transcript([t.language_code for t in transcript_list])
            translated = transcript.translate('en').fetch()
            return {
                'translated': ' '.join([i['text'] for i in translated]),
                'original': ' '.join([i['text'] for i in transcript.fetch()]),
                'language': transcript.language
            }

        except Exception as e:
            st.error(f"Transcript error: {str(e)}")
            return None

def analyze_with_vision(my_file):
    try:
        response = vision_model.generate_content([ 
            """Analyze this video content for entertainment purposes. Return STRICT JSON format with: 
            {genre : string, 
             mood : string, 
             similar_content_suggestions : array of strings, 
             key_elements : array of strings, 
             audience_options : array of strings}""",
            my_file
        ])
        my_file.delete()
        return parse_gemini_response(response.text)

    except Exception as e:
        st.error(f"Vision analysis failed: {str(e)}")
        return None

def wait_for_file_active(file, max_retries=5, delay=5):
    retries = 0
    while retries < max_retries:
        status = file.state.name
        if status == "ACTIVE":
            return True
        elif status == "FAILED":
            st.error("File upload failed!")
            return False
        time.sleep(delay)
        retries += 1
        file = genai.get_file(file.name)  
    st.error("File activation timed out!")
    return False

DOWNLOAD_DIR = os.path.abspath("downloads")  

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

ydl_opts = {
    'format': 'best',
    'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'), 
    'concurrent_fragments': 10,
    'throttled_rate': '10M',
    'limit_rate': '5M',
    'http_chunk_size': 10485760
}

def dwl_vid(video_url):
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)  
            file_path = ydl.prepare_filename(info_dict) 
            return os.path.abspath(file_path)

    except Exception as e:
            st.error(f"Download failed: {str(e)}")
            return None

def parse_gemini_response(response_text):
    try:
        cleaned = re.sub(r'```json|```', '', response_text)
        json_str = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if json_str:
            return json.loads(json_str.group())
        return None

    except Exception as e:
        st.error(f"Failed to parse response: {str(e)}")
        return None

st.set_page_config(page_title="YouTube Video Insight AI", layout="wide")

if 'current_video' not in st.session_state:
    st.session_state.current_video = {'id': None, 'type': None}
if 'analysis' not in st.session_state:
    st.session_state.analysis = None
if 'transcript' not in st.session_state:
    st.session_state.transcript = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = {}
if 'audience' not in st.session_state:
    st.session_state.audience = "General"

st.title("YouTube Video Insight AI")

with st.sidebar:
    st.title("YouTube Video Insight AI")
    video_url = st.text_input("Enter YouTube URL:", help="Paste a YouTube video URL here")
    video_id = extract_video_id(video_url) if video_url else None
    
    with st.expander("Video ID Extraction", expanded=True):
        if video_id:
            analysis_type = st.radio("Select Analysis Type:", 
                                ("Knowledge Analytics", "Entertainment Analytics"))

            st.warning("'Entertainment Analysis' takes more time to process than 'Knowledge Analysis' Please Co-Operate!")
            
            if (st.session_state.current_video['id'] != video_id or st.session_state.current_video['type'] != analysis_type):
                st.session_state.chat_history[video_id] = []
                st.session_state.current_video = {'id': video_id, 'type': analysis_type}
            
            components.html(
                f"""<iframe width="100%" height="200" 
                src="https://www.youtube.com/embed/{video_id}?controls=1" 
                frameborder="0" allowfullscreen></iframe>""",
                height=250
            )
        
        if st.button("Process Video"):
            with st.spinner("Analyzing video..."):
                if analysis_type == "Knowledge Analytics":
                    st.session_state.transcript = transcribe_video(video_id)
                    if st.session_state.transcript:
                        prompt = f"""Analyze this transcript for knowledge content. Return JSON with:
                        {{
                            "video_type": string,
                            "custom_prompt": string,
                            "audience_options": array of strings
                        }}
                        Transcript: {st.session_state.transcript['translated']}
                        """
                        response = content_model.generate_content(prompt)
                        st.session_state.analysis = parse_gemini_response(response.text)
                
                elif analysis_type == "Entertainment Analytics":
                    st.session_state.transcript = transcribe_video(video_id)
                    video_path = dwl_vid(video_url)

                    if video_path:
                        my_file = genai.upload_file(video_path)
                        if my_file.state.name == "FAILED":
                            print("Re-uploading the file...")
                            my_file = genai.upload_file(video_path)

                        if not wait_for_file_active(my_file):
                            st.stop()

                        st.session_state.analysis = analyze_with_vision(my_file)
                        os.remove(video_path)  
                        

if st.session_state.analysis and 'audience_options' in st.session_state.analysis:
    st.session_state.audience = st.selectbox(
        "Select Audience:",
        options=st.session_state.analysis.get('audience_options', ['General']),
        key='audience_selector'
    )

if st.session_state.current_video['type'] == "Knowledge Analytics":
    menu_options = ["Summary", "Roadmap", "Transcript", "Chat"]
else:
    menu_options = ["Summary", "Similar Content", "Transcript", "Chat"]

selected = option_menu(
    menu_title=None,
    options=menu_options,
    icons=["file-text", "map" if st.session_state.current_video['type'] == "Knowledge Analytics" else "film", 
           "card-text", "chat"],
    default_index=0,
    orientation="horizontal"
)

if st.session_state.analysis and video_id:
    if selected == "Summary":
        st.header("Video Summary")
        if st.button("Generate Summary"):
            with st.spinner("Generating summary..."):
                if st.session_state.current_video['type'] == "Knowledge Analytics":
                    prompt = st.session_state.analysis.get('custom_prompt', 
                        "Provide detailed summary with respect to {st.session_state.audience} audience")
                    content = st.session_state.transcript['translated']
                else:
                    prompt = "Provide comprehensive entertainment analysis summary"
                    content = json.dumps(st.session_state.analysis)
                
                response = content_model.generate_content(f"Prompt : {prompt}\n with respect to the audience : {st.session_state.audience}\nContent : {content}")
                st.write(response.text)
    
    elif selected == "Roadmap" and st.session_state.current_video['type'] == "Knowledge Analytics":
        st.header("Learning Roadmap")
        if st.button("Generate Roadmap"):
            with st.spinner("Creating roadmap..."):
                response = content_model.generate_content(
                    f"Create learning roadmap for {st.session_state.audience}\n"
                    f"Transcript: {st.session_state.transcript['translated']}"
                )
                st.write(response.text)
    
    elif selected == "Similar Content" and st.session_state.current_video['type'] == "Entertainment Analytics":
        st.header("Similar Content Recommendations")
        if st.session_state.analysis:
            st.subheader("Genre: " + st.session_state.analysis.get('genre', ''))
            st.write("Key Elements:", ", ".join(st.session_state.analysis.get('key_elements', [])))
            st.subheader("Recommended Similar Content:")
            for item in st.session_state.analysis.get('similar_content_suggestions', []):
                st.write(f"- {item}")
    
    elif selected == "Transcript":
        st.header("Video Transcript")
        if st.session_state.transcript:
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("English Translation")
                st.write(st.session_state.transcript['translated'])
            with col2:
                if st.session_state.transcript['language'] != 'en':
                    st.subheader(f"Original ({st.session_state.transcript['language']})")
                    st.write(st.session_state.transcript['original'])
    
    elif selected == "Chat":
        st.header("Video Chat Assistant")
        current_chat = st.session_state.chat_history.get(video_id, [])
        
        for message in current_chat:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        if prompt := st.chat_input("Ask about the content"):
            current_chat.append({"role": "user", "content": prompt})
            
            with st.spinner("Thinking..."):
                if st.session_state.current_video['type'] == "Knowledge Analytics":
                    context = st.session_state.transcript['translated']
                else:
                    context = json.dumps(st.session_state.analysis)
                
                response = content_model.generate_content("Answer the Question from the given Context with resprct to the given set of Audience\n"
                    f"Audience: {st.session_state.audience}\n"
                    f"Question: {prompt}\n"
                    f"Context: {context}"
                )
                current_chat.append({"role": "assistant", "content": response.text})
            
            st.session_state.chat_history[video_id] = current_chat
            
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.chat_message("assistant"):
                st.markdown(response.text)

else:
    st.info("Please enter a YouTube URL and click 'Process Video' in the sidebar")
