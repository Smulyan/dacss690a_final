import requests
import numpy as np
import pandas as pd
import json
import time
from datetime import date, timedelta
import spacy
from langdetect import detect

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

