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
from prefect import flow

# Global config
nlp = spacy.load("en_core_web_md")
candidate_labels = ["computer science", "biology", "physics", "chemistry", "mathematics", "engineering", "medicine", "social sciences", "humanities"]
expected_topics = candidate_labels
expected_languages = sorted(set([
    "af", "ar", "bg", "bn", "ca", "cs", "cy", "da", "de", "el", "en", "es", "et", "fa", "fi", "fr", "gu",
    "he", "hi", "hr", "hu", "id", "it", "ja", "kn", "ko", "lt", "lv", "mk", "ne", "nl", "no", "pl", "pt",
    "ro", "ru", "sk", "sl", "so", "sq", "sv", "sw", "th", "tl", "tr", "uk", "vi", "zh", "zh-cn"
]))

# --- ETL Functions ---

def extract_data():
    base_url = 'https://api.crossref.org/works'
    yesterday = date.today() - timedelta(days=1)
    filters = (
        f"filter=has-abstract:true,type:journal-article,type:posted-content,"
        f"type:proceedings-article,from-created-date:{yesterday},until-created-date:{yesterday}"
    )
    metadata_fields = 'select=DOI,title,container-title,abstract,author,published'
    cursor = '*'
    num_rows = 'rows=1000'
    results = []
    prev_len = 0

    while True:
        url = f"{base_url}?{filters}&{metadata_fields}&{num_rows}&cursor={cursor}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            page_results = response.json()
            items = page_results['message']['items']
            results.extend(items)

            if len(results) == prev_len:
                break
            prev_len = len(results)
            cursor = page_results['message']['next-cursor']
            time.sleep(1)
        except requests.RequestException as e:
            print(f"Request error: {e}")
            break

    return pd.json_normalize(results), yesterday.strftime('%Y-%m-%d')


def detect_language(text):
    try:
        return detect(text)
    except:
        return None

def classify_topic(text):
    try:
        doc = nlp(text)
        scores = {label: doc.similarity(nlp(label)) for label in candidate_labels}
        return max(scores, key=scores.get)
    except:
        return None

def transform_data(df):
    df["language"] = df["abstract"].apply(detect_language)
    df["topic"] = df["abstract"].apply(classify_topic)
    return df

def create_consistent_summary_row(date_str, df):
    topic_counts = df['topic'].value_counts().to_dict()
    topic_percentages = (df['topic'].value_counts(normalize=True) * 100).to_dict()
    language_counts = df['language'].value_counts().to_dict()
    language_percentages = (df['language'].value_counts(normalize=True) * 100).to_dict()

    row = {'date': date_str}
    for topic in expected_topics:
        row[topic] = topic_counts.get(topic, 0)
        row[f"{topic}_pct"] = round(topic_percentages.get(topic, 0), 2)

    for lang in expected_languages:
        row[lang] = language_counts.get(lang, 0)
        row[f"{lang}_pct"] = round(language_percentages.get(lang, 0), 2)

    return row

def update_summary_csv(df, date_str, csv_path="daily_summary.csv"):
    new_row = create_consistent_summary_row(date_str, df)

    if os.path.exists(csv_path):
        summary = pd.read_csv(csv_path)
        summary = pd.concat([summary, pd.DataFrame([new_row])], ignore_index=True)
    else:
        summary = pd.DataFrame([new_row])

    summary.to_csv(csv_path, index=False)

def push_to_github(date_str):
    try:
        load_dotenv()
        GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
        GITHUB_REPO = "github.com/Smulyan/dacss690a_final.git"
        REPO_DIR = "/Users/shaynsmulyan/PycharmProjects/dacss690a_final"

        if not GITHUB_TOKEN:
            raise ValueError("GitHub token not found in environment variables.")

        os.chdir(REPO_DIR)

        print("Pulling latest changes from GitHub...")
        subprocess.run(["git", "pull"], check=True)

        print("Staging CSV file...")
        subprocess.run(["git", "add", "daily_summary.csv"], check=True)

        print(f"Committing changes for {date_str}...")
        subprocess.run(["git", "commit", "-m", f"Update summary for {date_str}"], check=True)

        print("Pushing to GitHub...")
        push_url = f"https://{GITHUB_TOKEN}@{GITHUB_REPO}"
        subprocess.run(["git", "push", push_url], check=True)

        print("✅ Successfully pushed to GitHub.")

    except subprocess.CalledProcessError as e:
        print(f"❌ Git command failed: {e}")
    except Exception as e:
        print(f"❌ An error occurred: {e}")

# --- Main ---

@flow
def main():
    df, date_str = extract_data()
    if not df.empty:
        df = transform_data(df)
        update_summary_csv(df, date_str)
        push_to_github(date_str)
    else:
        print("No data extracted for the given date.")

if __name__ == "__main__":
    main()
