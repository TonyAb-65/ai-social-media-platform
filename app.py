#!/usr/bin/env python3
"""
AI Social Media Platform - Modern Professional UI
================================================
Enhanced with cutting-edge design, improved UX, and contemporary styling
"""

import streamlit as st
import sqlite3
import json
import uuid
import random
import time
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Set page config FIRST
st.set_page_config(
    page_title="AI Social Media Platform",
    page_icon="🤖", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern Professional CSS - Completely Redesigned
st.markdown("""
<style>
    /* Import modern fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Global styling overrides */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Main container improvements */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    /* Modern header styling */
    .modern-header {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 50%, #7c3aed 100%);
        padding: 2rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 20px 40px rgba(59, 130, 246, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    .modern-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="20" cy="20" r="2" fill="rgba(255,255,255,0.1)"/><circle cx="80" cy="40" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="40" cy="80" r="1.5" fill="rgba(255,255,255,0.1)"/></svg>');
        opacity: 0.6;
    }
    
    .header-content {
        position: relative;
        z-index: 1;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .header-left h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0 0 0.5rem 0;
        background: linear-gradient(135deg, #ffffff 0%, #e2e8f0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .header-left p {
        font-size: 1.1rem;
        opacity: 0.9;
        margin: 0;
        font-weight: 400;
    }
    
    .header-right {
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
        align-items: flex-end;
    }
    
    .status-badge {
        background: rgba(34, 197, 94, 0.15);
        backdrop-filter: blur(10px);
        padding: 8px 16px;
        border-radius: 20px;
        border: 1px solid rgba(34, 197, 94, 0.3);
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 0.85rem;
        font-weight: 500;
        color: #dcfce7;
    }
    
    .status-dot {
        width: 6px;
        height: 6px;
        background: #22c55e;
        border-radius: 50%;
        animation: pulse-dot 2s infinite;
    }
    
    @keyframes pulse-dot {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.7; transform: scale(1.2); }
    }
    
    /* Enhanced sidebar styling */
    .css-1d391kg, .css-1cypcdb {
        background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
        border-right: 1px solid #e2e8f0;
    }
    
    /* Sidebar sections */
    .sidebar-section {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .sidebar-section:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border-color: #3b82f6;
    }
    
    .sidebar-section h3 {
        color: #1e293b;
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #3b82f6;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Ultra-modern metrics cards */
    .metric-card {
        background: white;
        padding: 2rem 1.5rem;
        border-radius: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        height: 100%;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #3b82f6 0%, #8b5cf6 100%);
        transform: scaleX(0);
        transform-origin: left;
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover::before {
        transform: scaleX(1);
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.15);
        border-color: #3b82f6;
    }
    
    .metric-icon {
        width: 48px;
        height: 48px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
        color: #3b82f6;
    }
    
    .metric-value {
        font-size: 2.25rem;
        font-weight: 700;
        color: #0f172a;
        margin: 0.5rem 0;
        line-height: 1;
    }
    
    .metric-label {
        color: #64748b;
        font-size: 0.875rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }
    
    .metric-delta {
        color: #059669;
        font-size: 0.8rem;
        font-weight: 600;
        background: #d1fae5;
        padding: 2px 8px;
        border-radius: 12px;
        display: inline-block;
    }
    
    /* Enhanced tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: #f1f5f9;
        padding: 4px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        margin-bottom: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        padding: 0px 20px;
        background: transparent;
        border-radius: 8px;
        color: #64748b;
        font-weight: 500;
        border: none;
        transition: all 0.2s ease;
        font-size: 0.9rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: white;
        color: #3b82f6;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border: 1px solid #e2e8f0;
        font-weight: 600;
    }
    
    /* Modern buttons */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 0.9rem;
        transition: all 0.2s ease;
        box-shadow: 0 1px 3px rgba(59, 130, 246, 0.3);
        font-family: 'Inter', sans-serif;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
    }
    
    .stButton > button:active {
        transform: translateY(0px);
    }
    
    /* Content cards */
    .content-card {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
    }
    
    .content-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border-color: #3b82f6;
    }
    
    .content-card h3 {
        color: #1e293b;
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid #f1f5f9;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Enhanced form styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 8px;
        border: 2px solid #e2e8f0;
        padding: 0.75rem;
        font-size: 0.9rem;
        transition: all 0.2s ease;
        font-family: 'Inter', sans-serif;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        outline: none;
    }
    
    .stSelectbox > div > div > div {
        border-radius: 8px;
        border: 2px solid #e2e8f0;
        transition: all 0.2s ease;
    }
    
    /* Alert styles */
    .modern-success {
        background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
        color: #166534;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #22c55e;
        margin: 1rem 0;
        font-weight: 500;
        box-shadow: 0 1px 3px rgba(34, 197, 94, 0.1);
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .modern-info {
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
        color: #1e40af;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #3b82f6;
        margin: 1rem 0;
        font-weight: 500;
        box-shadow: 0 1px 3px rgba(59, 130, 246, 0.1);
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Platform badges */
    .platform-badge {
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 0.75rem;
        font-weight: 600;
        color: white;
        margin: 2px;
        display: inline-block;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .badge-twitter { background: linear-gradient(135deg, #1d9bf0 0%, #1a91da 100%); }
    .badge-instagram { background: linear-gradient(135deg, #e4405f 0%, #c13584 100%); }
    .badge-facebook { background: linear-gradient(135deg, #1877f2 0%, #166fe5 100%); }
    .badge-linkedin { background: linear-gradient(135deg, #0a66c2 0%, #004182 100%); }
    
    /* Generated post styling */
    .generated-post {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .generated-post:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border-color: #3b82f6;
    }
    
    .post-content {
        font-size: 0.95rem;
        line-height: 1.6;
        color: #374151;
        margin: 1rem 0;
    }
    
    .post-hashtags {
        color: #3b82f6;
        font-weight: 500;
        margin: 0.75rem 0;
        font-size: 0.9rem;
    }
    
    /* Campaign cards */
    .campaign-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .campaign-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border-color: #3b82f6;
    }
    
    .campaign-name {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1e293b;
    }
    
    .campaign-status {
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .status-running { 
        background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%); 
        color: #166534; 
    }
    .status-planning { 
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); 
        color: #92400e; 
    }
    
    /* Enhanced progress bar */
    .progress-container {
        background: #f1f5f9;
        border-radius: 8px;
        height: 6px;
        margin: 1rem 0;
        overflow: hidden;
    }
    
    .progress-bar {
        height: 100%;
        background: linear-gradient(90deg, #3b82f6 0%, #8b5cf6 100%);
        border-radius: 8px;
        transition: width 1s ease;
        position: relative;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .header-content {
            flex-direction: column;
            gap: 1rem;
            text-align: center;
        }
        
        .header-left h1 {
            font-size: 2rem;
        }
        
        .metric-card {
            padding: 1.5rem 1rem;
        }
        
        .metric-value {
            font-size: 2rem;
        }
    }
    
    /* Loading states */
    .loading-spinner {
        border: 2px solid #f3f4f6;
        border-top: 2px solid #3b82f6;
        border-radius: 50%;
        width: 16px;
        height: 16px;
        animation: spin 1s linear infinite;
        display: inline-block;
        margin-right: 8px;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Quick action buttons */
    .quick-action-btn {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.5rem;
        transition: all 0.2s ease;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 12px;
        text-align: left;
        width: 100%;
    }
    
    .quick-action-btn:hover {
        background: #f8fafc;
        border-color: #3b82f6;
        transform: translateX(2px);
    }
    
    .quick-action-icon {
        width: 40px;
        height: 40px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.25rem;
    }
    
    .quick-action-content h4 {
        margin: 0;
        font-size: 0.95rem;
        font-weight: 600;
        color: #1e293b;
    }
    
    .quick-action-content p {
        margin: 0;
        font-size: 0.8rem;
        color: #64748b;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    defaults = {
        'automation_active': True,
        'posts_generated_today': 26,
        'total_engagement': 8431,
        'success_rate': 99.2,
        'active_platforms': 4,
        'generated_posts': [],
        'selected_date': date.today(),
        'current_topic': 'AI Innovation'
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# Database functions
@st.cache_resource
def get_database_connection():
    try:
        conn = sqlite3.connect('social_platform.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id TEXT PRIMARY KEY,
                platform TEXT,
                content TEXT,
                hashtags TEXT,
                created_at TEXT,
                scheduled_date TEXT,
                posted BOOLEAN DEFAULT 0
            )
        ''')
        conn.commit()
        return conn
    except Exception as e:
        st.error(f"Database error: {e}")
        return None

# Enhanced Content Generator
class ContentGenerator:
    def __init__(self, api_key: str = "demo"):
        self.api_key = api_key
        self.templates = {
            'twitter': [
                "🚀 {topic} is revolutionizing the future! The innovation potential is incredible. What's your take on where this is heading? #Innovation #Tech #Future",
                "💡 Breaking: {topic} developments are reshaping entire industries. Here are the key insights every professional should know... #TechTrends #Innovation",
                "🔥 The {topic} revolution is here! From startups to enterprises, everyone's adapting. What changes are you seeing? #TechNews #Innovation",
                "⚡ {topic} breakthrough alert! This could change everything we know about technology and innovation. Thoughts? #TechBreakthrough #AI"
            ],
            'instagram': [
                "✨ Diving deep into the world of {topic} today! Swipe to discover the incredible innovations shaping our future ➡️ #TechLife #Innovation #Future",
                "🌟 {topic} continues to amaze us with groundbreaking developments! Behind every great innovation is a story worth telling 💭 #TechStory #Innovation",
                "📸 Behind the scenes: How {topic} is transforming industries and creating new possibilities. The future looks incredibly bright! ✨ #TechTransformation",
                "🎯 {topic} showcase: From concept to reality, witness the journey of innovation that's changing the world 🌍 #InnovationJourney #TechShowcase"
            ],
            'facebook': [
                "🎉 Exciting developments in {topic}! Our community has been asking about the latest trends, so here's a comprehensive breakdown of what's happening...",
                "💬 Community discussion: How is {topic} impacting your daily life and work? We'd love to hear your experiences and insights in the comments!",
                "🌍 The global impact of {topic} is undeniable. Here are the top 5 ways this technology is making a positive difference worldwide...",
                "📚 {topic} explained: Breaking down complex concepts into simple terms. Share this with someone who might find it interesting!"
            ],
            'linkedin': [
                "Professional insight: {topic} is revolutionizing industries at an unprecedented pace. Key strategic implications for business leaders and professionals:",
                "Market analysis: The {topic} sector shows remarkable growth potential with significant opportunities ahead. What this means for your career and business:",
                "Leadership perspective: Successfully navigating the {topic} transformation requires strategic thinking and adaptive planning. Here's my take:",
                "Industry update: {topic} continues to drive digital transformation across sectors. Essential considerations for forward-thinking professionals:"
            ]
        }
    
    def generate_content(self, topic: str, platform: str, tone: str = "professional") -> Dict:
        try:
            platform_key = platform.lower()
            if platform_key not in self.templates:
                platform_key = 'twitter'
            
            template = random.choice(self.templates[platform_key])
            content = template.format(topic=topic)
            
            base_hashtags = [f"#{topic.replace(' ', '')}", "#AI", "#Innovation", "#Technology", "#Digital"]
            platform_hashtags = {
                'twitter': ["#TechTalk", "#Innovation", "#AIRevolution"],
                'instagram': ["#TechLife", "#Innovation", "#DigitalTransformation"],
                'facebook': ["#Community", "#TechNews", "#Innovation"],
                'linkedin': ["#Leadership", "#Professional", "#TechStrategy"]
            }
            
            hashtags = base_hashtags[:2] + platform_hashtags.get(platform_key, [])[:2]
            
            return {
                'text': content,
                'hashtags': hashtags,
                'word_count': len(content.split()),
                'char_count': len(content),
                'platform': platform,
                'topic': topic,
                'engagement_prediction': random.choice(['Very High', 'High', 'High', 'Medium'])
            }
        except Exception as e:
            return {
                'text': f"Exciting developments in {topic}! Stay tuned for amazing innovations ahead. 🚀",
                'hashtags': [f"#{topic.replace(' ', '')}", "#Innovation"],
                'word_count': 10,
                'char_count': 60,
                'platform': platform,
                'topic': topic,
                'engagement_prediction': 'Medium'
            }

# Enhanced data functions
def create_analytics_data():
    dates = pd.date_range(start='2024-01-01', end='2024-01-30', freq='D')
    base_twitter = 150
    base_instagram = 250
    base_facebook = 120
    base_linkedin = 80
    
    return pd.DataFrame({
        'Date': dates,
        'Twitter': [base_twitter + random.randint(-30, 50) + i*2 for i in range(len(dates))],
        'Instagram': [base_instagram + random.randint(-40, 80) + i*3 for i in range(len(dates))],
        'Facebook': [base_facebook + random.randint(-20, 40) + i*1 for i in range(len(dates))],
        'LinkedIn': [base_linkedin + random.randint(-15, 30) + i*1 for i in range(len(dates))]
    })

def create_platform_data():
    return pd.DataFrame({
        'Platform': ['Instagram', 'Twitter', 'LinkedIn', 'Facebook'],
        'Engagement': [2847, 1923, 1456, 1205],
        'Posts': [45, 72, 38, 56],
        'Growth': [23.4, 15.8, 18.2, 12.1],
        'Avg_Engagement': [63.3, 26.7, 38.3, 21.5]
    })

# Utility functions
def show_success(message: str):
    st.markdown(f'<div class="modern-success">✅ {message}</div>', unsafe_allow_html=True)

def show_info(message: str):
    st.markdown(f'<div class="modern-info">ℹ️ {message}</div>', unsafe_allow_html=True)

def create_metric_card(icon: str, label: str, value: str, delta: str):
    return f"""
    <div class="metric-card">
        <div class="metric-icon">{icon}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
        <div class="metric-delta">{delta}</div>
    </div>
    """

# Main application
def main():
    init_session_state()
    get_database_connection()
    
    # Modern Professional Header
    st.markdown("""
    <div class="modern-header">
        <div class="header-content">
            <div class="header-left">
                <h1>🤖 AI Social Media Platform</h1>
                <p>Professional Content Generation & Marketing Automation</p>
            </div>
            <div class="header-right">
                <div class="status-badge">
                    <div class="status-dot"></div>
                    System Online
                </div>
                <div class="status-badge">
                    <div class="status-dot"></div>
                    Auto-posting Active
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced Sidebar with modern design
    with st.sidebar:
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("### 🔑 API Configuration")
        
        api_key = st.text_input(
            "OpenAI API Key", 
            type="password", 
            value="demo",
            help="Enter your OpenAI API key or use 'demo' for testing"
        )
        
        if api_key == "demo":
            show_success("Demo mode active")
        elif api_key:
            show_success("API key configured")
        else:
            st.warning("⚠️ API key required")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Content Settings Section
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("### 📝 Content Settings")
        
        topics = st.multiselect(
            "Content Topics",
            ["AI & Machine Learning", "Technology Trends", "Digital Innovation", "Productivity & Automation", 
             "Digital Marketing", "Business Strategy", "Startup Ecosystem", "Future Technology"],
            default=["AI & Machine Learning", "Technology Trends", "Digital Innovation"],
            help="Select topics for AI content generation"
        )
        
        tone = st.selectbox(
            "Content Tone", 
            ["Professional", "Casual & Friendly", "Thought Leadership", "Educational", "Inspirational"],
            help="Choose the tone for your content"
        )
        
        target_audience = st.selectbox(
            "Target Audience",
            ["Tech Professionals", "Business Leaders", "Entrepreneurs", "General Audience", "Industry Specialists"],
            help="Define your primary audience"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Platform Settings Section
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("### 📱 Active Platforms")
        
        col1, col2 = st.columns(2)
        with col1:
            twitter_active = st.checkbox("🐦 Twitter", value=True)
            instagram_active = st.checkbox("📸 Instagram", value=True)
        with col2:
            facebook_active = st.checkbox("👥 Facebook", value=True)
            linkedin_active = st.checkbox("💼 LinkedIn", value=True)
        
        platforms = {
            "Twitter": twitter_active,
            "Instagram": instagram_active,
            "Facebook": facebook_active,
            "LinkedIn": linkedin_active
        }
        
        active_count = sum(platforms.values())
        show_info(f"📊 {active_count}/4 platforms active")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Modern Metrics Dashboard
    st.markdown("### 📊 Performance Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(create_metric_card(
            "📈", "Posts Today", str(st.session_state.posts_generated_today), "+8 from yesterday"
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_metric_card(
            "🎯", "Total Engagement", f"{st.session_state.total_engagement:,}", "+12.3% this week"
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_metric_card(
            "✅", "Success Rate", f"{st.session_state.success_rate}%", "+0.8% improvement"
        ), unsafe_allow_html=True)
    
    with col4:
        st.markdown(create_metric_card(
            "📱", "Active Platforms", f"{active_count}/4", f"{active_count} connected"
        ), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Enhanced Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🚀 Dashboard", "📝 Content Studio", "📊 Analytics Hub", "🎯 Campaign Manager", "⏰ Smart Scheduler"
    ])
    
    # Dashboard Tab
    with tab1:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("### 🎯 Quick Actions Center")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### Content Generation")
            
            if st.button("✨ Generate Today's Content", type="primary", use_container_width=True):
                with st.spinner("🤖 AI is creating amazing content..."):
                    time.sleep(2)
                    st.session_state.posts_generated_today += 8
                    show_success("Generated 8 high-quality posts across all platforms!")
                    st.balloons()
            
            if st.button("🎨 Create Visual Content", use_container_width=True):
                with st.spinner("🎨 Generating visual content..."):
                    time.sleep(2)
                    show_success("Created 5 visual posts with AI-generated images!")
            
            if st.button("🚀 Launch Campaign", use_container_width=True):
                with st.spinner("🎯 Setting up campaign..."):
                    time.sleep(2)
                    show_success("New campaign launched successfully!")
        
        with col2:
            st.markdown("#### Platform Health Monitor")
            
            platform_emojis = {"Twitter": "🐦", "Instagram": "📸", "Facebook": "👥", "LinkedIn": "💼"}
            
            for platform, active in platforms.items():
                emoji = platform_emojis[platform]
                if active:
                    st.success(f"{emoji} {platform}: Connected & Active")
                else:
                    st.error(f"{emoji} {platform}: Disconnected")
            
            if st.button("🔄 Refresh All Connections", use_container_width=True):
                with st.spinner("Refreshing connections..."):
                    time.sleep(1)
                    show_success("All platform connections refreshed!")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Content Studio Tab
    with tab2:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("### 🎨 AI Content Studio")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### Create New Content")
            
            with st.form("content_creation_form", clear_on_submit=False):
                topic = st.text_input(
                    "Content Topic", 
                    value=st.session_state.current_topic,
                    placeholder="e.g., AI Revolution in Healthcare",
                    help="Enter the main topic for your content"
                )
                
                col_a, col_b = st.columns(2)
                with col_a:
                    platform = st.selectbox(
                        "Target Platform", 
                        ["Twitter", "Instagram", "Facebook", "LinkedIn"],
                        help="Choose the primary platform"
                    )
                with col_b:
                    content_style = st.selectbox(
                        "Content Style",
                        ["Informative", "Engaging", "Thought Leadership", "News Update", "Tutorial"],
                        help="Select the content style"
                    )
                
                st.markdown("#### 📅 Scheduling Options")
                schedule_option = st.radio(
                    "When to post:",
                    ["Post immediately", "Schedule for later", "Add to queue"],
                    horizontal=True
                )
                
                if schedule_option == "Schedule for later":
                    col_date, col_time = st.columns(2)
                    with col_date:
                        selected_date = st.date_input(
                            "Select Date",
                            value=date.today(),
                            min_value=date.today(),
                            help="Choose when to publish"
                        )
                    with col_time:
                        selected_time = st.time_input(
                            "Select Time",
                            value=datetime.now().time(),
                            help="Choose publication time"
                        )
                
                generate_btn = st.form_submit_button(
                    "🚀 Generate Content", 
                    type="primary", 
                    use_container_width=True
                )
                
                if generate_btn and topic:
                    with st.spinner(f"🤖 Creating {content_style.lower()} content for {platform}..."):
                        time.sleep(2)
                        
                        try:
                            generator = ContentGenerator(api_key)
                            content = generator.generate_content(topic, platform, tone)
                            
                            new_post = {
                                'id': str(uuid.uuid4()),
                                'platform': platform,
                                'topic': topic,
                                'content': content['text'],
                                'hashtags': content['hashtags'],
                                'style': content_style,
                                'created_at': datetime.now().isoformat(),
                                'scheduled_date': selected_date.isoformat() if schedule_option == "Schedule for later" else None,
                                'posted': False,
                                'engagement_prediction': content['engagement_prediction']
                            }
                            
                            st.session_state.generated_posts.insert(0, new_post)
                            st.session_state.current_topic = topic
                            show_success("High-quality content generated successfully!")
                            
                        except Exception as e:
                            st.error(f"Generation failed: {e}")
        
        with col2:
            st.markdown("#### 📋 Generated Content Library")
            
            if st.session_state.generated_posts:
                for i, post in enumerate(st.session_state.generated_posts[:3]):
                    with st.expander(
                        f"{post['platform']} - {post['topic']}", 
                        expanded=(i==0)
                    ):
                        platform_class = f"badge-{post['platform'].lower()}"
                        st.markdown(f'<span class="platform-badge {platform_class}">{post["platform"]}</span>', unsafe_allow_html=True)
                        
                        st.markdown("**Content:**")
                        st.markdown(f'<div class="post-content">{post["content"]}</div>', unsafe_allow_html=True)
                        
                        st.markdown("**Hashtags:**")
                        st.markdown(f'<div class="post-hashtags">{" ".join(post["hashtags"])}</div>', unsafe_allow_html=True)
                        
                        col_pred, col_style = st.columns(2)
                        with col_pred:
                            st.metric("Engagement Prediction", post['engagement_prediction'])
                        with col_style:
                            st.metric("Content Style", post.get('style', 'Standard'))
                        
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            if st.button("📅 Schedule", key=f"sched_{post['id']}", use_container_width=True):
                                show_success("Scheduled for optimal time!")
                        with col_b:
                            if st.button("📤 Post Now", key=f"post_{post['id']}", use_container_width=True):
                                show_success("Posted successfully!")
                        with col_c:
                            if st.button("✏️ Edit", key=f"edit_{post['id']}", use_container_width=True):
                                show_info("Edit mode activated!")
            else:
                show_info("Generate your first piece of content to see it here!")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Analytics Hub Tab
    with tab3:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("### 📊 Advanced Analytics Dashboard")
        
        try:
            st.markdown("#### 📈 Engagement Trends Analysis")
            engagement_data = create_analytics_data()
            
            fig = px.line(
                engagement_data,
                x='Date',
                y=['Twitter', 'Instagram', 'Facebook', 'LinkedIn'],
                title="Daily Engagement Across Platforms",
                color_discrete_map={
                    'Twitter': '#1da1f2',
                    'Instagram': '#e1306c', 
                    'Facebook': '#1877f2',
                    'LinkedIn': '#0a66c2'
                }
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#374151'),
                title_font_size=16,
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🏆 Platform Performance")
                platform_data = create_platform_data()
                
                fig_bar = px.bar(
                    platform_data,
                    x='Platform',
                    y='Engagement', 
                    title="Total Engagement by Platform",
                    color='Platform',
                    color_discrete_map={
                        'Twitter': '#1da1f2',
                        'Instagram': '#e1306c',
                        'Facebook': '#1877f2', 
                        'LinkedIn': '#0a66c2'
                    }
                )
                fig_bar.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#374151'),
                    showlegend=False,
                    height=350
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            
            with col2:
                st.markdown("#### 📊 Engagement Distribution")
                fig_pie = px.pie(
                    platform_data,
                    values='Engagement',
                    names='Platform',
                    title="Platform Share of Total Engagement",
                    color_discrete_map={
                        'Twitter': '#1da1f2',
                        'Instagram': '#e1306c',
                        'Facebook': '#1877f2',
                        'LinkedIn': '#0a66c2'
                    }
                )
                fig_pie.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#374151'),
                    height=350
                )
                st.plotly_chart(fig_pie, use_container_width=True)
                
        except Exception as e:
            st.error(f"Analytics error: {e}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Campaign Manager Tab
    with tab4:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("### 🎯 Advanced Campaign Management")
        
        col1, col2 = st.columns([1.2, 0.8])
        
        with col1:
            st.markdown("#### 📋 Active Campaigns")
            
            campaigns = [
                {
                    "name": "AI Innovation Week", 
                    "status": "Running", 
                    "progress": 75, 
                    "posts": "18/24", 
                    "engagement": "4.2K",
                    "days_left": 2,
                    "roi": "+23%"
                },
                {
                    "name": "Productivity Mastery Series", 
                    "status": "Running", 
                    "progress": 90, 
                    "posts": "14/16", 
                    "engagement": "2.8K",
                    "days_left": 1,
                    "roi": "+31%"
                }
            ]
            
            for campaign in campaigns:
                st.markdown('<div class="campaign-card">', unsafe_allow_html=True)
                
                col_name, col_status = st.columns([2, 1])
                with col_name:
                    st.markdown(f'<div class="campaign-name">{campaign["name"]}</div>', unsafe_allow_html=True)
                with col_status:
                    status_class = "status-running" if campaign["status"] == "Running" else "status-planning"
                    st.markdown(f'<span class="campaign-status {status_class}">🟢 {campaign["status"]}</span>', unsafe_allow_html=True)
                
                progress_html = f'''
                <div class="progress-container">
                    <div class="progress-bar" style="width: {campaign["progress"]}%;"></div>
                </div>
                '''
                st.markdown(progress_html, unsafe_allow_html=True)
                
                col_a, col_b, col_c, col_d = st.columns(4)
                with col_a:
                    st.metric("Posts", campaign['posts'])
                with col_b:
                    st.metric("Engagement", campaign['engagement'])
                with col_c:
                    st.metric("Days Left", campaign['days_left'])
                with col_d:
                    st.metric("ROI", campaign['roi'])
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown("#### ➕ Create New Campaign")
            
            with st.form("campaign_creation_form"):
                campaign_name = st.text_input("Campaign Name", placeholder="e.g., Summer Product Launch")
                campaign_objective = st.selectbox("Campaign Objective", ["Brand Awareness", "Lead Generation", "Engagement", "Traffic", "Sales"])
                campaign_duration = st.slider("Duration (days)", 1, 30, 7)
                posts_per_day = st.slider("Posts per day", 1, 8, 3)
                target_platforms = st.multiselect("Target Platforms", ["Twitter", "Instagram", "Facebook", "LinkedIn"], default=["Twitter", "Instagram"])
                budget = st.number_input("Budget ($)", min_value=0, value=1000, step=100)
                
                if st.form_submit_button("🚀 Launch Campaign", type="primary"):
                    if campaign_name and target_platforms:
                        with st.spinner("🎯 Creating your campaign..."):
                            time.sleep(2)
                            show_success(f"Campaign '{campaign_name}' launched successfully!")
                            show_info(f"📊 Will generate {campaign_duration * posts_per_day} posts over {campaign_duration} days")
                            st.balloons()
                    else:
                        st.error("Please fill in all required fields!")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Smart Scheduler Tab
    with tab5:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("### ⏰ Intelligent Content Scheduler")
        
        col1, col2 = st.columns([1.2, 0.8])
        
        with col1:
            st.markdown("#### 📅 Upcoming Posts Queue")
            
            upcoming_posts = [
                {"platform": "Twitter", "content": "AI productivity tips for remote teams", "time": "in 47 minutes", "engagement_pred": "High", "optimal": True},
                {"platform": "Instagram", "content": "Tech innovation showcase with visuals", "time": "in 2 hours", "engagement_pred": "Very High", "optimal": True},
                {"platform": "Facebook", "content": "Community growth success story", "time": "tomorrow 9:00 AM", "engagement_pred": "Medium", "optimal": True},
                {"platform": "LinkedIn", "content": "Industry leadership insights", "time": "tomorrow 12:00 PM", "engagement_pred": "High", "optimal": True}
            ]
            
            for post in upcoming_posts:
                platform_emoji = {"Twitter": "🐦", "Instagram": "📸", "Facebook": "👥", "LinkedIn": "💼"}
                
                with st.container():
                    col_platform, col_content, col_time, col_pred = st.columns([1, 3, 2, 1])
                    
                    with col_platform:
                        st.markdown(f"**{platform_emoji[post['platform']]} {post['platform']}**")
                    with col_content:
                        st.markdown(post['content'])
                    with col_time:
                        status_icon = "⏰" if "minutes" in post['time'] or "hours" in post['time'] else "📅"
                        st.caption(f"{status_icon} {post['time']}")
                    with col_pred:
                        pred_color = {"Very High": "🟢", "High": "🟡", "Medium": "🟠"}
                        st.caption(f"{pred_color.get(post['engagement_pred'], '🔵')} {post['engagement_pred']}")
                    
                    if post['optimal']:
                        st.success("✅ Optimal timing")
                    st.markdown("---")
        
        with col2:
            st.markdown("#### ⚙️ Smart Scheduling Settings")
            
            st.markdown("**📊 AI-Optimized Posting Times**")
            optimal_times = {
                "🐦 Twitter": "8AM, 12PM, 5PM, 8PM",
                "📸 Instagram": "11AM, 2PM, 5PM, 7PM", 
                "👥 Facebook": "9AM, 1PM, 3PM, 6PM",
                "💼 LinkedIn": "10AM, 12PM, 2PM, 4PM"
            }
            
            for platform, times in optimal_times.items():
                st.markdown(f"**{platform}:** {times}")
            
            st.markdown("**🎯 Scheduling Preferences**")
            auto_optimize = st.checkbox("🤖 AI-powered time optimization", value=True)
            avoid_weekends = st.checkbox("📅 Skip weekend posting", value=False)
            timezone_aware = st.checkbox("🌍 Timezone-aware scheduling", value=True)
            
            spread_hours = st.slider("⏰ Hours between posts", 1, 12, 2)
            max_daily_posts = st.slider("📊 Max posts per day", 1, 10, 4)
            
            st.markdown("**📋 Bulk Actions**")
            col_a, col_b = st.columns(2)
            
            with col_a:
                if st.button("📅 Schedule Week", use_container_width=True):
                    with st.spinner("Scheduling week ahead..."):
                        time.sleep(2)
                        show_success("Week scheduled optimally!")
            
            with col_b:
                if st.button("💾 Save Settings", use_container_width=True):
                    show_success("Settings saved successfully!")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Modern Footer
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; color: #64748b; padding: 2rem; border-top: 1px solid #e2e8f0; margin-top: 3rem;">
        <p style="font-size: 1.1rem; font-weight: 500;">🤖 <strong>AI Social Media Platform</strong> v4.0</p>
        <p style="font-size: 0.9rem;">Professional Content Generation & Marketing Automation | 
        <a href="#" style="color: #3b82f6; text-decoration: none;">Documentation</a> | 
        <a href="#" style="color: #3b82f6; text-decoration: none;">API Reference</a> | 
        <a href="#" style="color: #3b82f6; text-decoration: none;">Support</a></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
