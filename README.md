# YouTube Video Insight AI

**YouTube Video Insight AI** is an advanced Streamlit application that enables you to extract and interact with insights from YouTube videos. By providing a YouTube video URL, the app extracts the video ID, fetches and transcribes the video, and then uses powerful generative AI models to analyze the content. Depending on the video type—whether it is educational ("Knowledge Analytics") or entertainment ("Entertainment Analytics")—the app can generate a summary, learning roadmap, similar content recommendations, provide the transcript, and even facilitate an interactive chat about the video's content.

## Features

- **YouTube Video Processing:**

  - Extract the video ID from a provided URL.
  - Transcribe video content and translate it to English if needed.
  - Download the video (for analysis) and perform vision analysis on entertainment videos.

- **Content Analysis & Generation:**

  - For educational videos, generate detailed summaries and learning roadmaps.
  - For entertainment videos, generate comprehensive analysis and similar content recommendations.
  - Supports interactive chat with context-aware responses based on the video transcript or analysis.

- **Interactive Chat Interface:**

  - Engage in a conversation with the AI assistant regarding the video content.
  - Maintain conversation history for seamless follow-up interactions.

- **Audience Customization:**
  - Select the target audience to tailor the generated content accordingly.

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/Jnan-py/youtube-video-insight-ai.git
   cd youtube-video-insight-ai
   ```

2. **Create a Virtual Environment (Recommended):**

   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows use: venv\Scripts\activate
   ```

3. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables:**
   - Create a `.env` file in the project root with the following keys:
     ```
     GEMINI_API=your_google_gemini_api_key_here
     ```

## Usage

1. **Run the Application:**

   ```bash
   streamlit run main.py
   ```

2. **Enter a YouTube Video URL:**

   - In the sidebar, enter the URL of a YouTube video.
   - The app will extract the video ID and display an embedded video player.

3. **Process the Video:**

   - Click the **"Process Video"** button to transcribe the video and analyze its content.
   - Depending on the selected analysis type ("Knowledge Analytics" or "Entertainment Analytics"), the app will generate a transcript and additional analysis details.

4. **Interact with the Video Insights:**
   - Use the horizontal menu to choose between options such as **Summary**, **Roadmap** (for educational videos), **Similar Content** (for entertainment videos), **Transcript**, and **Chat**.
   - Ask questions or request further details via the chat interface.

## Project Structure

```
youtube-video-insight-ai/
│
├── main.py                         # Main Streamlit application file
├── downloads/                     # Directory for saving downloaded videos
├── .env                           # Environment variables file (create and add your API keys)
├── README.md                      # Project documentation
└── requirements.txt               # Python dependencies
```

## Technologies Used

- **Streamlit:** For building an interactive web interface.
- **Google Generative AI (Gemini):** For content generation, video analysis, and transcription-based insights.
- **yt-dlp:** For downloading videos from YouTube.
- **Python-Dotenv:** For managing environment variables.
- **Streamlit Option Menu:** For an intuitive sidebar navigation experience.
- **Standard Libraries:** (e.g., re, json, os, time, urllib) for various utility functions.

---

Save these files in your project directory. To launch the application, activate your virtual environment (if using one) and run:

```bash
streamlit run main.py
```

Feel free to adjust the documentation as needed. Enjoy exploring insights from YouTube videos with YouTube Video Insight AI!
