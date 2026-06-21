"""
Recommendation Engine Module
Implements content-based filtering using cosine similarity for AI course/resource recommendations.
"""

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import List, Dict, Any, Optional
import os

# Category descriptions for TF-IDF vectorization
CATEGORY_DESCRIPTIONS = {
    'Artificial Intelligence': 'artificial intelligence ai neural networks intelligent systems automation robotics expert systems knowledge representation reasoning planning',
    'Machine Learning': 'machine learning ml supervised unsupervised reinforcement learning algorithms regression classification clustering svm random forest gradient boosting',
    'Deep Learning': 'deep learning dl neural networks cnn rnn lstm transformers backpropagation tensorflow pytorch keras convolutional recurrent',
    'Computer Vision': 'computer vision cv image processing object detection recognition segmentation yolo opencv tensorflow pytorch visual perception pattern recognition',
    'NLP': 'natural language processing nlp text analysis sentiment analysis tokenization named entity recognition transformers bert gpt language models chatbots',
    'Data Science': 'data science ds statistics analysis visualization pandas numpy matplotlib seaborn tableau power bi exploratory data analysis hypothesis testing',
    'Web Development': 'web development frontend backend full stack html css javascript react angular vue node.js django flask apis rest graphql',
    'Cyber Security': 'cybersecurity security ethical hacking penetration testing network security cryptography encryption firewalls vulnerability assessment malware analysis',
    'Cloud Computing': 'cloud computing aws azure gcp devops docker kubernetes serverless infrastructure microservices deployment scaling virtualization'
}

# Item database with courses/resources
ITEMS_DATABASE = [
    {
        'name': 'AI Fundamentals Masterclass',
        'category': 'Artificial Intelligence',
        'description': 'Comprehensive introduction to AI concepts, history, and modern applications. Covers search algorithms, knowledge representation, and intelligent agents.',
        'tags': 'artificial intelligence ai neural networks intelligent systems automation'
    },
    {
        'name': 'Advanced Neural Networks',
        'category': 'Artificial Intelligence',
        'description': 'Deep dive into neural network architectures, from perceptrons to deep networks. Learn about activation functions, backpropagation, and optimization.',
        'tags': 'artificial intelligence ai neural networks deep learning backpropagation'
    },
    {
        'name': 'ML Algorithms Bootcamp',
        'category': 'Machine Learning',
        'description': 'Hands-on training with essential ML algorithms. Covers regression, classification, clustering, and ensemble methods with real-world projects.',
        'tags': 'machine learning ml supervised unsupervised algorithms regression classification clustering'
    },
    {
        'name': 'Scikit-Learn Mastery',
        'category': 'Machine Learning',
        'description': 'Master the most popular Python ML library. Build pipelines, tune hyperparameters, and deploy models to production.',
        'tags': 'machine learning ml scikit-learn python pipelines hyperparameter tuning'
    },
    {
        'name': 'Deep Learning Specialization',
        'category': 'Deep Learning',
        'description': 'Complete deep learning curriculum from basics to advanced. CNNs, RNNs, LSTMs, and Transformer architectures with TensorFlow and PyTorch.',
        'tags': 'deep learning dl neural networks cnn rnn lstm transformers tensorflow pytorch'
    },
    {
        'name': 'PyTorch for Researchers',
        'category': 'Deep Learning',
        'description': 'Learn PyTorch for academic and industry research. Dynamic computation graphs, custom layers, and cutting-edge model implementation.',
        'tags': 'deep learning dl pytorch neural networks research dynamic computation graphs'
    },
    {
        'name': 'Computer Vision A-Z',
        'category': 'Computer Vision',
        'description': 'From image basics to advanced object detection. Master OpenCV, YOLO, and modern vision transformers for real-world applications.',
        'tags': 'computer vision cv image processing object detection yolo opencv transformers'
    },
    {
        'name': 'Medical Image Analysis',
        'category': 'Computer Vision',
        'description': 'Apply computer vision to healthcare. Learn segmentation, classification, and anomaly detection on medical imaging datasets.',
        'tags': 'computer vision cv medical image segmentation classification healthcare'
    },
    {
        'name': 'NLP with Transformers',
        'category': 'NLP',
        'description': 'Master modern NLP using transformer architectures. Build chatbots, summarizers, and sentiment analysis systems with BERT and GPT.',
        'tags': 'natural language processing nlp transformers bert gpt chatbots sentiment analysis'
    },
    {
        'name': 'Text Mining & Analytics',
        'category': 'NLP',
        'description': 'Extract insights from text data. Topics include topic modeling, named entity recognition, text classification, and information extraction.',
        'tags': 'natural language processing nlp text mining topic modeling named entity recognition'
    },
    {
        'name': 'Data Science Professional',
        'category': 'Data Science',
        'description': 'End-to-end data science workflow. Data collection, cleaning, analysis, visualization, and communication of insights using Python stack.',
        'tags': 'data science ds statistics analysis visualization pandas numpy matplotlib'
    },
    {
        'name': 'Big Data Analytics',
        'category': 'Data Science',
        'description': 'Work with large-scale datasets using Spark, Hadoop, and cloud tools. Distributed computing and scalable data processing techniques.',
        'tags': 'data science ds big data spark hadoop distributed computing scalable processing'
    },
    {
        'name': 'Full Stack Web Dev',
        'category': 'Web Development',
        'description': 'Build complete web applications from scratch. Frontend with React, backend with Node.js, database design, and deployment strategies.',
        'tags': 'web development full stack frontend backend react node.js database deployment'
    },
    {
        'name': 'Modern Frontend Architecture',
        'category': 'Web Development',
        'description': 'Advanced frontend patterns, state management, performance optimization, and progressive web apps with modern JavaScript frameworks.',
        'tags': 'web development frontend react vue angular state management performance pwa'
    },
    {
        'name': 'Ethical Hacking Bootcamp',
        'category': 'Cyber Security',
        'description': 'Learn penetration testing, vulnerability assessment, and security auditing. Kali Linux, Metasploit, and real-world attack simulations.',
        'tags': 'cybersecurity ethical hacking penetration testing kali linux metasploit security'
    },
    {
        'name': 'Network Security Pro',
        'category': 'Cyber Security',
        'description': 'Secure network infrastructures. Firewalls, IDS/IPS, VPNs, encryption protocols, and enterprise security architecture design.',
        'tags': 'cybersecurity network security firewalls ids ips vpn encryption enterprise'
    },
    {
        'name': 'AWS Solutions Architect',
        'category': 'Cloud Computing',
        'description': 'Design and deploy scalable systems on AWS. EC2, S3, Lambda, RDS, and cloud-native architecture patterns for enterprise applications.',
        'tags': 'cloud computing aws ec2 s3 lambda scalable architecture cloud-native'
    },
    {
        'name': 'Kubernetes Mastery',
        'category': 'Cloud Computing',
        'description': 'Container orchestration at scale. Deploy, manage, and scale containerized applications with Kubernetes, Helm, and Docker.',
        'tags': 'cloud computing kubernetes docker containers orchestration helm scaling devops'
    }
]


def get_category_vector(category: str) -> str:
    """Get the description vector for a category."""
    return CATEGORY_DESCRIPTIONS.get(category, category.lower())


def create_user_profile_vector(preferences: List[Dict[str, Any]]) -> str:
    """
    Create a user profile vector from their preferences.
    Higher-rated categories contribute more to the profile.
    """
    profile_parts = []
    
    for pref in preferences:
        category = pref['category']
        rating = pref.get('rating', 3)
        
        # Get category description
        cat_desc = get_category_vector(category)
        
        # Weight by rating (1-5 scale)
        weight = max(1, int(rating))
        
        # Repeat the description based on weight (higher rating = more emphasis)
        for _ in range(weight):
            profile_parts.append(cat_desc)
    
    return ' '.join(profile_parts)


def compute_similarity(user_profile: str, items: List[Dict[str, Any]], top_n: int = 5) -> List[Dict[str, Any]]:
    """
    Compute cosine similarity between user profile and items.
    Returns top N recommendations with similarity scores.
    """
    if not user_profile.strip():
        # Return random items if no profile
        selected = np.random.choice(len(items), min(top_n, len(items)), replace=False)
        recommendations = []
        for i, idx in enumerate(selected, 1):
            item = items[idx]
            recommendations.append({
                'item_name': item['name'],
                'category': item['category'],
                'similarity_score': 0.5,
                'match_percentage': 50.0,
                'description': item['description'],
                'rank': i
            })
        return recommendations
    
    # Prepare documents for TF-IDF
    documents = [user_profile]
    item_texts = []
    
    for item in items:
        # Combine item tags and description
        item_text = f"{item['tags']} {item['description']}"
        item_texts.append(item_text)
        documents.append(item_text)
    
    # Compute TF-IDF vectors
    vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
    tfidf_matrix = vectorizer.fit_transform(documents)
    
    # User profile is the first document
    user_vector = tfidf_matrix[0]
    item_vectors = tfidf_matrix[1:]
    
    # Compute cosine similarity
    similarities = cosine_similarity(user_vector, item_vectors).flatten()
    
    # Get top N indices
    top_indices = similarities.argsort()[-top_n:][::-1]
    
    recommendations = []
    for rank, idx in enumerate(top_indices, 1):
        similarity = float(similarities[idx])
        item = items[idx]
        
        recommendations.append({
            'item_name': item['name'],
            'category': item['category'],
            'similarity_score': round(similarity, 4),
            'match_percentage': round(similarity * 100, 2),
            'description': item['description'],
            'rank': rank
        })
    
    return recommendations


def get_content_based_recommendations(preferences: List[Dict[str, Any]], 
                                      top_n: int = 5) -> List[Dict[str, Any]]:
    """
    Main function to get content-based recommendations.
    Takes user preferences and returns top N recommended items.
    """
    # Create user profile
    user_profile = create_user_profile_vector(preferences)
    
    # Compute similarities
    recommendations = compute_similarity(user_profile, ITEMS_DATABASE, top_n)
    
    return recommendations


def get_categories() -> List[str]:
    """Get all available categories."""
    return list(CATEGORY_DESCRIPTIONS.keys())


def get_category_distribution(preferences: List[Dict[str, Any]]) -> Dict[str, int]:
    """Get distribution of categories in preferences."""
    distribution = {}
    for pref in preferences:
        cat = pref['category']
        distribution[cat] = distribution.get(cat, 0) + 1
    return distribution


def get_trending_categories() -> List[Dict[str, Any]]:
    """Get trending categories based on item database."""
    category_counts = {}
    for item in ITEMS_DATABASE:
        cat = item['category']
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    sorted_cats = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
    return [{'category': cat, 'count': count} for cat, count in sorted_cats]
