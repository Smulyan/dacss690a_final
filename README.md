# Topic and Language classification of newly registered publication abstracts

### Data Source
The data used for this project comes from the 'Crossref Unified Resource API](https://api.crossref.org)

### Topic and Language classification 

### Prefect Flow

### Installation
Install dependences using
pip install -r requirements.txt

The SpaCy model may not automatically install using requirements.txt.  If so, run this manually  
python -m spacy download en_core_web_md

###Authentication
In the root of the project (same folder as app.py), create a file named .env and add your Github token as:
GITHUB_TOKEN=your_token_here
Make sure that .env is listed in your .gitignore file to avoid pushing it accidentally:

Modify the following lines of the push_to_github() function in app.py to reflect your own repo and repo directory
GITHUB_REPO = "github.com/your-username/your-repo-name.git"
REPO_DIR = "/path/to/your/local/repo"