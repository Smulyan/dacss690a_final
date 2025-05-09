# Topic and Language classification of newly registered publication abstracts

View output on Streamlit at
https://dacss690afinalsmulyan.streamlit.app/

### Data Source
The data used for this project comes from the [Crossref REST API](https://api.crossref.org). The API contains 
metadata records for all publications registered with Crossref by their respective publishers. 

The extract_data() function in the app.py script retrieves metadata for all records that were newly registered on 
the previous day and which contain abstracts.  (abstracts are not required; only about 20% of records include them)

### Transformation
After the selected metadata, including abstracts, is reformatted into a dataframe using Pandas, two transformations 
are then applied to each abstract, both from spaCy's suite of NLP functions. The detect_language() function returns the 
ISO 639 language code for the language of the abstract's text.  The classify_topic() function returns one of a set 
of supplied subject candidates: "computer science", "biology", "physics", "chemistry", "mathematics", "engineering", 
"medicine", "social sciences", or "humanities".   The returned langauge and topic values are then appended to the 
relevant row of the dataframe. 

### Destination, part 1: csv file
Next,

### Prefect Automation

### Destination, part 2: Streamlit App

