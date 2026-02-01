#!/usr/bin/env python3
"""
Challenge #1: Advanced Data Wrangling & AI Sentiment Analysis
Author: AI-Assisted Development
Description: Comprehensive customer review analysis using VADER sentiment analysis
"""

import pandas as pd
import numpy as np
import random
import re
from collections import Counter
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer
import warnings
warnings.filterwarnings('ignore')

def generate_dataset(n_reviews=1000):
    """Generate realistic messy tech product reviews"""
    
    positive_templates = [
        "Amazing {product}! Battery lasts all day and performance is incredible.",
        "Best {product} I've ever owned. Fast, reliable, and great value.",
        "Excellent build quality. The {feature} feature is outstanding!",
    ]
    
    negative_templates = [
        "Terrible {product}. Battery dies quickly and constantly crashes.",
        "Worst purchase ever! {product} broke after just {time_period}.",
        "Poor quality control. Multiple defects including {defect}.",
    ]
    
    neutral_templates = [
        "Decent {product} for the price. Nothing special but works okay.",
        "Average performance. Some good features but also some issues.",
        "It's fine I guess. Does what it's supposed to do.",
    ]
    
    products = ['smartphone', 'laptop', 'tablet', 'smartwatch', 'headphones']
    features = ['camera', 'display', 'audio', 'connectivity', 'design']
    defects = ['screen bleeding', 'button sticking', 'charging issues']
    time_periods = ['one week', 'two days', 'a month']
    
    data = []
    for i in range(1, n_reviews + 1):
        rating = np.random.choice([1,2,3,4,5], p=[0.1, 0.15, 0.2, 0.35, 0.2])
        
        if rating >= 4:
            template = random.choice(positive_templates)
        elif rating <= 2:
            template = random.choice(negative_templates)
        else:
            template = random.choice(neutral_templates)
        
        review_text = template.format(
            product=random.choice(products),
            feature=random.choice(features),
            defect=random.choice(defects),
            time_period=random.choice(time_periods)
        )
        
        # Add typos (20% chance)
        if random.random() < 0.2:
            review_text = review_text.replace('the', 'teh').replace('great', 'gerat')
        
        # Add missing values (8% chance)
        if random.random() < 0.08:
            review_text = np.nan
            
        data.append([i, review_text, rating])
    
    return pd.DataFrame(data, columns=['Review_ID', 'Review_Text', 'Rating'])

def clean_data(df):
    """Advanced data cleaning pipeline"""
    
    # Handle missing values
    df['Review_Text'] = df['Review_Text'].fillna("No review provided")
    df['Rating'] = df['Rating'].fillna(3)
    
    # Remove special characters
    df['Clean_Text'] = df['Review_Text'].apply(
        lambda x: re.sub(r'[^a-zA-Z0-9\s.,!?\'-]', '', str(x)).strip()
    )
    
    # Fix common typos
    df['Clean_Text'] = df['Clean_Text'].str.replace('teh', 'the').str.replace('gerat', 'great')
    
    return df

def analyze_sentiment(df):
    """VADER sentiment analysis (superior for reviews)"""
    
    analyzer = SentimentIntensityAnalyzer()
    
    def get_sentiment(text):
        scores = analyzer.polarity_scores(str(text))
        compound = scores['compound']
        
        if compound >= 0.05:
            return 'Positive', compound
        elif compound <= -0.05:
            return 'Negative', compound
        else:
            return 'Neutral', compound
    
    sentiment_data = df['Clean_Text'].apply(get_sentiment)
    df['Sentiment'] = [s[0] for s in sentiment_data]
    df['Sentiment_Score'] = [s[1] for s in sentiment_data]
    
    return df

def find_top_complaints(df):
    """Extract top 3 complaints using TF-IDF"""
    
    negative_reviews = df[df['Sentiment'] == 'Negative']['Clean_Text']
    
    if len(negative_reviews) == 0:
        return []
    
    # Use TF-IDF for intelligent complaint extraction
    vectorizer = TfidfVectorizer(
        max_features=50,
        stop_words='english',
        ngram_range=(1, 2),
        min_df=2
    )
    
    tfidf_matrix = vectorizer.fit_transform(negative_reviews)
    feature_names = vectorizer.get_feature_names_out()
    tfidf_scores = tfidf_matrix.sum(axis=0).A1
    
    # Filter for complaint-related terms
    complaint_indicators = [
        'terrible', 'awful', 'bad', 'poor', 'broken', 'slow', 
        'battery', 'crash', 'problem', 'issue', 'fail'
    ]
    
    complaints = []
    for term, score in zip(feature_names, tfidf_scores):
        if any(indicator in term.lower() for indicator in complaint_indicators):
            count = sum(1 for review in negative_reviews if term.lower() in str(review).lower())
            complaints.append((term, count, score))
    
    return sorted(complaints, key=lambda x: x[2], reverse=True)[:3]

def main():
    """Main analysis pipeline"""
    
    print("🚀 Starting Advanced Customer Review Analysis")
    print("=" * 50)
    
    # 1. Generate dataset
    print("\n📊 Generating realistic dataset...")
    df = generate_dataset(1000)
    df.to_csv('customer_reviews.csv', index=False)
    print(f"   Generated {len(df)} reviews")
    
    # 2. Clean data
    print("\n🧹 Cleaning data...")
    df_clean = clean_data(df)
    print(f"   Cleaned {len(df_clean)} reviews")
    
    # 3. Sentiment analysis
    print("\n🎯 Analyzing sentiment with VADER...")
    df_sentiment = analyze_sentiment(df_clean)
    
    sentiment_counts = df_sentiment['Sentiment'].value_counts()
    print("   Sentiment Distribution:")
    for sentiment, count in sentiment_counts.items():
        print(f"     {sentiment}: {count} ({count/len(df_sentiment)*100:.1f}%)")
    
    # 4. Find complaints
    print("\n🔍 Extracting top complaints...")
    top_complaints = find_top_complaints(df_sentiment)
    
    print("   Top 3 Complaints:")
    for i, (complaint, count, score) in enumerate(top_complaints, 1):
        print(f"     {i}. '{complaint}' - {count} mentions (relevance: {score:.3f})")
    
    # 5. Save results
    df_sentiment.to_csv('analysis_results.csv', index=False)
    
    print("\n✅ Analysis Complete!")
    print(f"   📄 Results saved to 'analysis_results.csv'")
    print(f"   📊 Total reviews: {len(df_sentiment)}")
    print(f"   🎯 VADER sentiment analysis used (superior for reviews)")
    print(f"   🔍 TF-IDF complaint extraction implemented")
    
    return df_sentiment

if __name__ == "__main__":
    results = main()