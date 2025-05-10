# Topic and Language classification of newly registered publication abstracts

View output on Streamlit at
https://dacss690afinalsmulyan.streamlit.app/

### Data Source
The data used for this project comes from the [Crossref REST API](https://api.crossref.org). The API contains 
metadata records for all publications registered with Crossref by their respective publishers. 

The extract_data() function in the app.py script retrieves metadata for all records that were newly registered on 
the previous day and which contain abstracts.  (abstracts are not required by Crossref; only about 20% of all 
records in their API include them)

### Transformation
After the selected metadata, including abstracts, is reformatted into a dataframe using Pandas, two transformations 
are then applied to each abstract, both from spaCy's suite of NLP functions. The detect_language() function returns the 
ISO 639 language code for the language of the abstract's text.  The classify_topic() function returns one of a set 
of supplied subject candidates: "computer science", "biology", "physics", "chemistry", "mathematics", "engineering", 
"medicine", "social sciences", or "humanities".   

The returned langauge and topic values are then appended to the relevant row of the dataframe for each abstract.  
And, finally, summary statistics on the proportion and distribution of topics and languages for that day's worth of 
data are calculated. 

### Destination, part 1: csv file
Each time the script is run, the prior day's summary statistics are written into a new row of the 
daily_summary.csv file, along with the date. The csv file is then pushed back to the same Github repo where the 
code itself is stored.  

### Prefect Automation
After flow and task decorators were added, the app.py script was deployed to Prefect Cloud and scheduled to run once 
per day.  This enables consistent collection of data and generation of language and topic summary statistics over time. 

### Destination, part 2: Streamlit App
Finally, the csv is read into another small script, streamlit_app.py, which is deployed to Streamlit.  This allows 
users to select a date range and visualize the trends in total count and proportion of topic and language 
distribution over time.  A static chart with the total distribution of topic and language classifications is also 
include in the respective tabs on streamlit. 

### Considerations for Next Steps
This was a useful and edifying exercise in building/automating a simple NLP pipeline.  The language classification 
seems to hold up to some scrutiny; though, it could be made more useful by programatically limiting the streamlit 
visualizations to just the top-n languages represented in the dataset.  The topic classification is very obviously 
insufficient.  None of the abstracts were classified as chemistry, mathematics. Social sciences seem wildly 
overrepresented just based on my familiarity with the Crossref API overall.  Adjusting the candidate labels or using 
a larger spaCy model might help.  I plan to experiment with those options in the near future.  My initial plan had 
been to use zero-shot classification with the facebook/bart-large-mnli NLI model, or a similar pre-trained machine 
learning model.  The initial small-scale tests looked very promising in terms of accuracy, but it was simply too 
resource-intensive for me to manage at this point in time.  So, going forward, I also want to explore what options 
may be available for running a pipeline like this on an AWS GPU instance or similar.  
