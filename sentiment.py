# import packages
import requests
from bs4 import BeautifulSoup
import json
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import glob
import os
from statistics import mean
import plotly.express as px
from tqdm import tqdm
# nltk.download('vader_lexicon')
# nltk.download('punkt')
# ! jupyter labextension install @jupyter-widgets/jupyterlab-manager jupyterlab-plotly

# find all news articles using beautifulsoup
response = requests.get('https://www.aljazeera.com/where/mozambique/')
soup = BeautifulSoup(response.text, 'lxml')
news = soup.find_all('a', class_ = 'u-clickable-card__link')

# extract ten most recent articles
count = 0
for i in tqdm(range(len(news))):
    if count == 10:
        break
    # follow url to article page
    url = 'https://www.aljazeera.com' + str(news[i]['href'])
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    # find the block with news text
    content = soup.find('div', class_ ="wysiwyg wysiwyg--all-content css-1ck9wyi")
    # skip news that only contains video
    if not content:
        continue
    # preprocessing. only extract news without comments, dates, or ads.
    para = content.find_all('p')
    # combine all elements of news
    final = ' '.join([j.get_text() for j in para])
    count += 1
    # save news in .json files
    with open(str(count-1) + '. ' + str(news[i]['href'].split('/')[-1]) + '.json', 'w') as outfile:
    # with open(str(i['href'].split('/')[-1])+'.json', 'w') as outfile:
        json.dump(final, outfile)

ref = {}
# read all news saved locally
for filename in glob.glob('*.json'):
    with open(os.path.join(os.getcwd(), filename), 'r') as f:
        text = json.load(f)
        sia = SentimentIntensityAnalyzer()
        # get sentiment scores by sentences in each news
        score = [sia.polarity_scores(i)['compound'] for i in nltk.sent_tokenize(text)]
        # save mean sentiment scores to dictionary
        ref[filename] = mean(score)

# show scatterplots of sentiments
fig = px.scatter(x=ref.keys(), y=ref.values())
fig.show()
