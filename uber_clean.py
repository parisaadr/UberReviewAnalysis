# 1. Import Required Libraries
import matplotlib.pyplot as plt
from google_play_scraper import Sort, reviews
import pandas as pd
import shutil
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from wordcloud import WordCloud
import matplotlib
matplotlib.use('TkAgg')
from textblob import TextBlob
from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

# 2. Fetch Reviews from Google Play Store
result, _ = reviews(
    'com.ubercab',  # App package name for Uber
    lang='en',      # Language: English
    country='us',   # Country: US
    sort=Sort.MOST_RELEVANT,  # Sort by relevance
    count=1000       # Number of reviews to fetch
)

# 3. Save Reviews to CSV and Create Backup
reviews_df = pd.DataFrame(result)
reviews_df.to_csv('uber_reviews.csv', index=False)
print("Reviews saved to 'uber_reviews.csv'")
shutil.copy('uber_reviews.csv', 'uber_reviews_backup.csv')

# 4. Check for Empty DataFrame Before Proceeding
if reviews_df.empty:
    print("No data to save, the DataFrame is empty.")
else:
    reviews_df.to_csv('uber_reviews.csv', index=False)
    print("Reviews saved successfully.")

import os

file_path = 'uber_reviews.csv'
if not os.path.exists(file_path) or os.stat(file_path).st_size == 0:
    print(f"The file '{file_path}' is empty or does not exist. Exiting...")
    exit()
else:
    reviews_df = pd.read_csv(file_path)
    print("Data loaded successfully:")
    print(reviews_df.head())  # Debugging: Show first few rows

try:
    reviews_df = pd.read_csv(file_path)
    if reviews_df.empty:
        print("The CSV file is empty.")
except pd.errors.EmptyDataError:
    print("The CSV file is empty or cannot be read.")

# 5. Load Reviews from CSV
reviews_df = pd.read_csv('uber_reviews.csv')
all_reviews = ' '.join(reviews_df['content'].dropna())

# 6. Tokenize Reviews and Remove Stopwords
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('punkt_tab')
stop_words = set(stopwords.words('english'))
words = word_tokenize(all_reviews.lower())
filtered_words = [word for word in words if word.isalnum() and word not in stop_words]

# 7. Count Word Frequency and Display Top 10 Words
word_freq = Counter(filtered_words)
print(word_freq.most_common(10))

# 8. Check If the CSV File is Empty Before Proceeding
if os.stat('uber_reviews.csv').st_size == 0:
    print("The file 'uber_reviews.csv' is empty. Scraping might have failed.")
    exit()

# 9. Check If the File Exists and Is Not Empty
file_path = 'uber_reviews.csv'

if not os.path.exists(file_path) or os.stat(file_path).st_size == 0:
    print(f"The file '{file_path}' is empty or does not exist. Exiting...")
    exit()

# 10. Load the CSV File and Handle Errors
try:
    reviews_df = pd.read_csv(file_path)
    print("Data loaded successfully:")
    print(reviews_df.head())  # Debugging: Show first few rows
except pd.errors.EmptyDataError:
    print("The file is empty or not formatted properly. Exiting...")
    exit()

# 11. Generate and Display Word Cloud
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(' '.join(filtered_words))

plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.show()

# 12. Sentiment Analysis of Reviews
if 'sentiment' in reviews_df.columns:
    print(reviews_df['sentiment'].value_counts())
else:
    print("'sentiment' column not found in the DataFrame.")

# 13. Analyze Sentiment for Each Review
reviews_df['polarity'] = reviews_df['content'].apply(lambda x: TextBlob(str(x)).sentiment.polarity)
reviews_df['sentiment'] = reviews_df['polarity'].apply(
    lambda x: 'positive' if x > 0 else ('negative' if x < 0 else 'neutral'))

print(reviews_df['sentiment'].value_counts())

# 14. Topic Modeling Using LDA (Latent Dirichlet Allocation)
vectorizer = CountVectorizer(max_df=0.9, min_df=10, stop_words='english')
text_matrix = vectorizer.fit_transform(reviews_df['content'].dropna())

# Apply LDA
lda = LatentDirichletAllocation(n_components=5, random_state=42)
lda.fit(text_matrix)

# 15. Print the Top Words in Each Topic
for idx, topic in enumerate(lda.components_):
    print(f"Topic {idx + 1}:")
    print([vectorizer.get_feature_names_out()[i] for i in topic.argsort()[-10:]])

# 16. Visualize Sentiment Distribution
sentiment_counts = reviews_df['sentiment'].value_counts()
sentiment_counts.plot(kind='bar', color=['green', 'red', 'grey'], figsize=(8, 6))
plt.title('Sentiment Distribution of Uber Reviews')
plt.xlabel('Sentiment')
plt.ylabel('Count')
plt.xticks(rotation=0)
plt.show()

from sklearn.feature_extraction.text import CountVectorizer

# 17. Bigram Analysis (frequent word pairs)
vectorizer = CountVectorizer(ngram_range=(2, 2), stop_words='english', max_df=.9, min_df=10)
bigram_matrix = vectorizer.fit_transform(reviews_df['content'].dropna())

# Get the bigram frequencies
bigram_freq = pd.DataFrame(bigram_matrix.toarray(), columns=vectorizer.get_feature_names_out())
bigram_freq = bigram_freq.sum(axis=0).sort_values(ascending=False)
print("Most common Bigrams:")
print(bigram_freq.head(10))

# 18. Analyze Review Length and Sentiment Correlation
reviews_df['review_length'] = reviews_df['content'].apply(lambda x: len(str(x).split()))
reviews_df[['review_length', 'sentiment']].groupby('sentiment').mean().plot(kind='bar', figsize=(8, 6))
plt.title('Average Review Length by Sentiment')
plt.xlabel('Sentiment')
plt.ylabel('Average Length (Words)')
plt.xticks(rotation=0)
plt.show()

# 19. Generate Word Cloud for Sentiments
sentiment_reviews = {
    'positive': reviews_df[reviews_df['sentiment'] == 'positive']['content'],
    'negative': reviews_df[reviews_df['sentiment'] == 'negative']['content'],
    'neutral': reviews_df[reviews_df['sentiment'] == 'neutral']['content']
}

for sentiment, reviews in sentiment_reviews.items():
    text = ' '.join(reviews.dropna())
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(f'Word Cloud for {sentiment.capitalize()} Reviews')
    plt.show()

# 20. Keyword Search in Reviews
keywords = ['price', 'driver', 'service', 'app', 'safety']
for keyword in keywords:
    count = reviews_df['content'].str.contains(keyword, case=False, na=False).sum()
    print(f"'{keyword}' appears {count} times in the reviews.")

# 21. Correlation Between Sentiment and Star Rating
if 'score' in reviews_df.columns:
    sentiment_rating = reviews_df.groupby('sentiment')['score'].mean()
    sentiment_rating.plot(kind='bar', color=['green', 'red', 'grey'], figsize=(8, 6))
    plt.title('Average Rating by Sentiment')
    plt.xlabel('Sentiment')
    plt.ylabel('Average Rating')
    plt.xticks(rotation=0)
    plt.show()
else:
    print("No 'score' column found in the DataFrame.")

# 22. Trend Analysis Over Time (If Date Column Exists)
if 'date' in reviews_df.columns:
    reviews_df['date'] = pd.to_datetime(reviews_df['date'])
    reviews_df.set_index('date', inplace=True)
    sentiment_time_trend = reviews_df.resample('M')['sentiment'].value_counts().unstack().fillna(0)
    sentiment_time_trend.plot(kind='line', figsize=(10, 6))
    plt.title('Sentiment Trend Over Time')
    plt.xlabel('Date')
    plt.ylabel('Count')
    plt.legend(title='Sentiment')
    plt.show()
else:
    print("No 'date' column found in the DataFrame.")
