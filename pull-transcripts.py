import os
import feedparser
import requests
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
MEMBERSHIP_ID = os.getenv("SUPERCAST_MEMBERSHIP_ID")

if not MEMBERSHIP_ID:
    raise ValueError("SUPERCAST_MEMBERSHIP_ID not found. Please ensure it is set in your .env file.")

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
                # Supercast audio URLs occasionally redirect, so allow_redirects=True is helpful
                response = requests.get(audio_url, stream=True, allow_redirects=True)
                if response.status_code == 200:
                    with open(file_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=1024):
                            f.write(chunk)
                    downloaded_files.append(file_path)
                else:
                    print(f"Failed to download: {title} (Status {response.status_code})")
                    
    return downloaded_files

def main():
    files = get_last_weeks_premium_audio()
    if not files:
        print("No episodes found from the past week.")
    else:
        print(f"\nSuccess! Downloaded {len(files)} premium audio files to the '{DOWNLOAD_DIR}' directory.")

if __name__ == "__main__":
    main()