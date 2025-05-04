import requests
import numpy as np
import pandas as pd
import json
import time
from datetime import date, timedelta
import spacy
from langdetect import detect
from dotenv import load_dotenv
import os
import subprocess

#Configure API request components
base_url = 'https://api.crossref.org/works'
yesterday = date.today() - timedelta(days=1)
yesterday_str = yesterday.strftime('%Y-%m-%d')
filters = f"filter=has-abstract:true,type:journal-article,type:posted-content,type:proceedings-article,from-created-date:{yesterday_str},until-created-date:{yesterday_str}"
metadata_fields = 'select=DOI,title,container-title,abstract,author,published'
num_rows = 'rows=1000'
cursor = '*'

#install medium English language model
nlp = spacy.load("en_core_web_md")

#topic candidate labels
candidate_labels = ["computer science", "biology", "physics", "chemistry", "mathematics", "engineering", "medicine", "social sciences", "humanities"]

#topic classification function
def classify_topic(text):
  try:
    doc = nlp(text)

    #use similarity scores to get closest topic
    scores = {label: doc.similarity(nlp(label)) for label in candidate_labels}
    topic = max(scores, key=scores.get)
    return topic
  except Exception as e:
    print(f"Error classifying topic: {e}")
    return None

#langauge detection function
def detect_language(text):
  try:
    language = detect(text)
    return language
  except Exception as e:
    print(f"Error detecting language: {e}")
    return None


#API call for yesterday's new items that contain abstracts
results = [] #list to store data from all pages
previous_len = 0 #variable to store previous results length

while True:
  url = base_url + '?' + filters + '&' + metadata_fields + '&' + num_rows + '&cursor=' + cursor

  try:
    response = requests.get(url)
    response.raise_for_status() #check for request errors


    page_results = response.json()

    #extract items from page and append to full results list
    items = page_results['message']['items']
    results.extend(items)

    #check if length of full results has increased
    current_len = len(results)
    if current_len == previous_len:
      break #exit the loop if no increase
    else:
      previous_len = current_len #update the previous length to compare next loop to

    cursor = page_results['message']['next-cursor']

    time.sleep(1) #one second delay before next request

  except requests.exceptions.RequestException as e:
    print(f"Request Error: {e}")
    raise


#create dataframe from full results list
df = pd.json_normalize(results)

#populate language and topic fields of the dataframe
df["language"] = df["abstract"].apply(detect_language)
df["topic"] = df["abstract"].apply(classify_topic)


#generate summary statistics

# Path to the CSV file
csv_path = "daily_summary.csv"

expected_topics = [
    "computer science", "biology", "physics", "chemistry",
    "mathematics", "engineering", "medicine", "social sciences", "humanities"
]

expected_languages = [
    "af", "ar", "bg", "ca", "cs", "da", "de", "el", "en", "es", "et", "fa", "fi", "fr", "gu", "hi", "hr", "hu", "id",
    "it", "ja", "kn", "ko", "lt", "lv", "mk", "ne", "nl", "no", "pl", "pt", "ro", "ru", "sk", "sl", "so" "sq", "sv",
    "th", "tl", "tr", "uk", "vi", "zh", "zh-cn"
]

#function to ensure that columns are consistent day to day
def create_consistent_summary_row(date_str, topic_counts, topic_percentages, language_counts, language_percentages):
    row = {'date': date_str}

    # Fill in topic counts
    for topic in expected_topics:
        row[topic] = topic_counts.get(topic, 0)
        row[f"{topic}_pct"] = round(topic_percentages.get(topic, 0), 2)

    # Fill in language counts
    for lang in expected_languages:
        row[lang] = language_counts.get(lang, 0)
        row[f"{lang}_pct"] = round(language_percentages.get(lang, 0), 2)

    return row

topic_counts = df['topic'].value_counts().to_dict()
topic_percentages = (df['topic'].value_counts(normalize=True) * 100).to_dict()
language_counts = df['language'].value_counts().to_dict()
language_percentages = (df['language'].value_counts(normalize=True) * 100).to_dict()

# Create a dictionary for the new row
new_row = create_consistent_summary_row(
    yesterday_str,
    topic_counts,
    topic_percentages,
    language_counts,
    language_percentages
)

# Check if the CSV already exists
if os.path.exists(csv_path):
    # Load existing data and append
    daily_summary = pd.read_csv(csv_path)
    daily_summary = pd.concat([daily_summary, pd.DataFrame([new_row])], ignore_index=True)
else:
    # Create a new DataFrame if the file doesn't exist
    daily_summary = pd.DataFrame([new_row])

# Save the updated data back to CSV
daily_summary.to_csv(csv_path, index=False)



#push csv to github repo
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = "github.com/Smulyan/dacss690a_final.git"  # <-- Replace with yours
REPO_DIR = "/Users/shaynsmulyan/PycharmProjects/dacss690a_final"  # Local clone path

os.chdir(REPO_DIR)

# Git operations
subprocess.run(["git", "pull"])
subprocess.run(["git", "add", "daily_summary.csv"])
subprocess.run(["git", "commit", "-m", f"Update summary for {yesterday_str}"])
subprocess.run(["git", "push", f"https://{GITHUB_TOKEN}@{GITHUB_REPO}"])
