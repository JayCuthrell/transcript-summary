import os
import time
import feedparser
import requests
import google.generativeai as genai
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
MEMBERSHIP_ID = os.getenv("SUPERCAST_MEMBERSHIP_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not MEMBERSHIP_ID:
    raise ValueError("SUPERCAST_MEMBERSHIP_ID not found. Please ensure it is set in your .env file.")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found. Please ensure it is set in your .env file.")

# Configure the Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Construct your private Supercast feed URL
RSS_FEED_URL = f"https://feeds.supercast.com/feeds/{MEMBERSHIP_ID}"
DOWNLOAD_DIR = "podcast_audio"

def get_last_weeks_premium_audio():
    print("Starting Premium podcast pull...")
    
    # Ensure our download directory exists
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)
        
    feed = feedparser.parse(RSS_FEED_URL)
    now = datetime.now(timezone.utc)
    one_week_ago = now - timedelta(days=7)
    
    downloaded_files = []
    
    for entry in feed.entries:
        # Safely parse the RSS publication date
        published_date = parsedate_to_datetime(entry.published)
        
        if published_date > one_week_ago:
            title = entry.title
            
            # Locate the MP3 enclosure in the RSS XML
            audio_url = None
            for link in entry.links:
                if link.rel == 'enclosure' and 'audio' in link.type:
                    audio_url = link.href
                    break
            
            if audio_url:
                # Strip out any weird characters to make a safe filename
                safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                file_name = f"{published_date.strftime('%Y%m%d')}_{safe_title.replace(' ', '_')}.mp3"
                file_path = os.path.join(DOWNLOAD_DIR, file_name)
                
                print(f"Downloading: {title}")
                
                # Download and stream the MP3 to disk
                response = requests.get(audio_url, stream=True, allow_redirects=True)
                if response.status_code == 200:
                    with open(file_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=1024):
                            f.write(chunk)
                    downloaded_files.append(file_path)
                else:
                    print(f"Failed to download: {title} (Status {response.status_code})")
                    
    return downloaded_files

def process_audio_with_gemini(audio_file_paths):
    print("\nStarting Gemini AI Studio Processing...")
    
    uploaded_files = []
    
    # 1. Upload the files to the Gemini File API
    for file_path in audio_file_paths:
        print(f"Uploading {file_path} to Gemini...")
        gemini_file = genai.upload_file(path=file_path)
        uploaded_files.append(gemini_file)
        
    # 2. Wait for files to process
    print("Waiting for audio processing to complete on Google's end...")
    for uploaded_file in uploaded_files:
        while uploaded_file.state.name == "PROCESSING":
            print(".", end="", flush=True)
            time.sleep(2)
            # Refresh the file status
            uploaded_file = genai.get_file(uploaded_file.name)
        print() # New line
            
    # 3. Initialize the model 
    model = genai.GenerativeModel('models/gemini-1.5-pro')
    
    # 4. Craft your prompt
    prompt = """
    Attached are 5 daily tech news podcast episodes from the past week. 
    Please do the following:
    1. Provide a brief, bulleted transcription/summary of the core news items discussed in each episode.
    2. Identify the top 3 overarching tech trends or themes from this week that I should discuss on my own podcast, 'What The Fudge'.
    """
    
    # 5. Call the model with the prompt AND the audio files
    print("Generating insights with Gemini 1.5 Pro (this may take a minute or two)...")
    content_request = [prompt] + uploaded_files
    response = model.generate_content(content_request)
    
    # 6. Cleanup: Delete the files from Google's servers
    print("Cleaning up uploaded files...")
    for uploaded_file in uploaded_files:
        genai.delete_file(uploaded_file.name)
        
    return response.text

def main():
    files = get_last_weeks_premium_audio()
    if not files:
        print("No episodes found from the past week.")
    else:
        print(f"\nSuccess! Downloaded {len(files)} premium audio files to the '{DOWNLOAD_DIR}' directory.")
        
        # Pass files to Gemini for processing
        gemini_output = process_audio_with_gemini(files)
        
        # Save the final output
        output_filename = f"WTF_prep_notes_{datetime.now().strftime('%Y%m%d')}.md"
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(gemini_output)
            
        print(f"\nDone! Your podcast prep notes are saved to {output_filename}")

if __name__ == "__main__":
    main()