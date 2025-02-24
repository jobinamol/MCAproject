import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os

# Load dataset
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, 'dataset', 'google_hotel_data_clean_v2.csv')

df = pd.read_csv(DATASET_PATH)

# Ensure necessary columns exist
if 'Hotel_Name' not in df.columns or 'Hotel_Rating' not in df.columns or 'City' not in df.columns:
    raise ValueError("Dataset must contain 'Hotel_Name', 'Hotel_Rating', and 'City' columns.")

# Combine all features into a single text field
df['combined_features'] = df[['Feature_1', 'Feature_2', 'Feature_3', 'Feature_4', 'Feature_5', 'Feature_6', 'Feature_7']].fillna('').agg(' '.join, axis=1)

# TF-IDF Vectorization
vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = vectorizer.fit_transform(df['combined_features'])

# Compute Cosine Similarity
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

# Function to get similar resorts
def recommend_resorts(hotel_name, top_n=5):
    if hotel_name not in df['Hotel_Name'].values:
        return "Hotel not found!"
    
    idx = df[df['Hotel_Name'] == hotel_name].index[0]
    similarity_scores = list(enumerate(cosine_sim[idx]))
    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)[1:top_n+1]
    
    resort_indices = [i[0] for i in similarity_scores]
    return df.iloc[resort_indices][['Hotel_Name', 'Hotel_Rating', 'City']]
