#!/usr/bin/env python3
import os
import requests
import smtplib
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration variables
GMAIL_SENDER = os.getenv("GMAIL_SENDER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
GMAIL_RECIPIENT = os.getenv("GMAIL_RECIPIENT")

TECHMEME_RIVER_URL = "https://techmeme.com/river"

def fetch_and_parse_river():
    print("Downloading Techmeme River page...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(TECHMEME_RIVER_URL, headers=headers, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching Techmeme River: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    permalinks_data = []
    
    # 1. Target the specific item rows directly based on Techmeme's HTML class
    item_rows = soup.find_all('tr', class_='ritem')
    print(f"Found {len(item_rows)} river items. Extracting data...")

    for row in item_rows:
        # 2. Extract the hidden 'pml' attribute to reconstruct the Techmeme permalink
        rshr_div = row.find('div', class_='rshr')
        if not rshr_div or not rshr_div.has_attr('pml'):
            continue
            
        pml = rshr_div['pml']
        if 'p' in pml:
            date_part, post_id = pml.split('p', 1)
            full_url = f"https://www.techmeme.com/{date_part}/p{post_id}"
        else:
            continue
            
        # 3. Extract the headline
        title = ""
        anchors = row.find_all('a', href=True)
        if anchors:
            # The headline is consistently the longest link text in the item row
            title = max([a.get_text(strip=True) for a in anchors], key=len)
            
        # Fallback safety
        if not title or len(title) < 5:
            title = "Techmeme Story Coverage"
            
        # Clean up whitespace
        title = " ".join(title.split())
        
        # Prevent duplicates
        if (title, full_url) not in permalinks_data:
            permalinks_data.append((title, full_url))
            
    return permalinks_data

def generate_markdown_content(links):
    content = f"# Techmeme River Permalinks Digest — {datetime.now().strftime('%B %d, %Y')}\n\n"
    content += "Below are the centralized Techmeme permalinks captured from the River page, preserving full coverage clusters:\n\n"
    for title, url in links:
        content += f"- [{title}]({url})\n"
    return content

def email_summary(content, date_str):
    print("Emailing Techmeme permalink summary to your inbox...")
    if not all([GMAIL_SENDER, GMAIL_APP_PASSWORD, GMAIL_RECIPIENT]):
        print("Skipping email: Gmail credentials not fully configured in .env")
        return

    subject = f"Techmeme River Permalink Digest - {date_str}"
    
    msg = MIMEText(content)
    msg['Subject'] = subject
    msg['From'] = GMAIL_SENDER
    msg['To'] = GMAIL_RECIPIENT

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(GMAIL_SENDER, GMAIL_APP_PASSWORD)
            server.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

def main():
    extracted_links = fetch_and_parse_river()
    if not extracted_links:
        print("No valid techmeme permalinks were extracted.")
        return

    markdown_content = generate_markdown_content(extracted_links)
    
    date_str = datetime.now().strftime('%Y%m%d')
    drive_path = os.path.expanduser("~/My Drive/Podcast/")
    
    if not os.path.exists(drive_path):
        os.makedirs(drive_path)
        
    output_file = os.path.join(drive_path, f"Techmeme_River_Permalinks_{date_str}.md")
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(markdown_content)
            
    print(f"Successfully compiled {len(extracted_links)} permalinks to {output_file}")
    email_summary(markdown_content, date_str)

if __name__ == "__main__":
    main()