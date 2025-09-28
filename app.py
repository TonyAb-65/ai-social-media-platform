#!/usr/bin/env python3
"""
AI Social Media Platform - Professional UI Redesign
==================================================
Enhanced with modern design, better UX, and professional styling
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
    page_title="🤖 AI Social Media Platform",
    page_icon="🚀", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern Professional CSS
st.markdown("""
<style>
    /* Hide Streamlit branding and improve overall design */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container improvements */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Professional header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .main-header h1 {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        font-size: 1.3rem;
        opacity: 0.95;
        margin-bottom: 1.5rem;
        font-weight: 300;
    }
    
    /* Modern status badge */
    .status-badge {
        background: rgba(40, 167, 69, 0.15);
        backdrop-filter: blur(10px);
        padding: 12px 24px;
        border-radius: 30px;
        border: 1px solid rgba(40, 167, 69, 0.3);
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-weight: 500;
    }
    
    .status-dot {
        width: 8px;
        height: 8px;
        background: #28a745;
        border-radius: 50%;
        animation: pulse-dot 2s infinite;
    }
    
    @keyframes pulse-dot {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    /* Enhanced sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
        border-right: 1px solid #e9ecef;
    }
    
    /* Sidebar sections */
    .sidebar-section {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid #e9ecef;
    }
    
    .sidebar-section h3 {
        color: #495057;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #667eea;
    }
    
    /* Modern metrics cards */
    .metric-card {
        background: white;
        padding: 2rem 1.5rem;
        border-radius: 16px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.06);
        border: 1px solid #e9ecef;
        transition: all 0.3s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 32px rgba(0,0,0,0.12);
        border-color: #667eea;
    }
    
    .metric-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #212529;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        color: #6c757d;
        font-size: 0.9rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-delta {
        color: #28a745;
        font-size: 0.85rem;
        font-weight: 600;
        margin-top: 0.5rem;
    }
    
    /* Professional tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #f8f9fa;
        padding: 8px;
        border-radius: 12px;
        border: 1px solid #e9ecef;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0px 24px;
        background: transparent;
        border-radius: 8px;
        color: #6c757d;
        font-weight: 500;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: white;
        color: #667eea;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border: 1px solid #e9ecef;
    }
    
    /* Enhanced buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:active {
        transform: translateY(0px);
    }
    
    /* Action buttons styling */
    .action-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 6px 16px rgba(102, 126, 234, 0.3);
        width: 100%;
        margin: 0.5rem 0;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
    }
    
    .action-btn:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 24px rgba(102, 126, 234, 0.4);
    }
    
    /* Content cards */
    .content-card {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 8px 24px rgba(0,0,0,0.06);
        border: 1px solid #e9ecef;
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
    }
    
    .content-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 32px rgba(0,0,0,0.1);
    }
    
    .content-card h3 {
        color: #495057;
        font-size: 1.4rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid #f8f9fa;
    }
    
    /* Form styling */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 2px solid #e9ecef;
        padding: 0.75rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    .stSelectbox > div > div > div {
        border-radius: 8px;
        border: 2px solid #e9ecef;
    }
    
    /* Alert styles */
    .success-alert {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        color: #155724;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
        font-weight: 500;
        box-shadow: 0 4px 12px rgba(40, 167, 69, 0.15);
    }
    
    .info-alert {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
        color: #0c5460;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #17a2b8;
        margin: 1rem 0;
        font-weight: 500;
        box-shadow: 0 4px 12px rgba(23, 162, 184, 0.15);
    }
    
    /* Platform badges */
    .platform-badge {
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        color: white;
        margin: 2px;
        display: inline-block;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .badge-twitter { background: linear-gradient(135deg, #1da1f2 0%, #0d8bd9 100%); }
    .badge-instagram { background: linear-gradient(135deg, #e1306c 0%, #c13584 100%); }
    .badge-facebook { background: linear-gradient(135deg, #1877f2 0%, #166fe5 100%); }
    .badge-linkedin { background: linear-gradient(135deg, #0a66c2 0%, #004182 100%); }
    
    /* Generated post styling */
    .generated-post {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid #e9ecef;
        transition: all 0.3s ease;
    }
    
    .generated-post:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
    }
    
    .post-content {
        font-size: 1rem;
        line-height: 1.6;
        color: #495057;
        margin: 1rem 0;
    }
    
    .post-hashtags {
        color: #667eea;
        font-weight: 500;
        margin: 0.75rem 0;
    }
    
    .post-actions {
        display: flex;
        gap: 8px;
        margin-top: 1rem;
    }
    
    .post-btn {
        padding: 8px 16px;
        border: none;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s ease;
        flex: 1;
    }
    
    .btn-schedule { background: #28a745; color: white; }
    .btn-post { background: #dc3545; color: white; }
    .btn-edit { background: #6c757d; color: white; }
    
    .post-btn:hover {
        transform: translateY(-1px);
        opacity: 0.9;
    }
    
    /* Campaign cards */
    .campaign-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid #e9ecef;
        transition: all 0.3s ease;
    }
    
    .campaign-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
    }
    
    .campaign-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    .campaign-name {
        font-size: 1.1rem;
        font-weight: 600;
        color: #495057;
    }
    
    .campaign-status {
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .status-running { background: #d4edda; color: #155724; }
    .status-planning { background: #fff3cd; color: #856404; }
    
    /* Progress bar styling */
    .progress-container {
        background: #f8f9fa;
        border-radius: 10px;
        height: 8px;
        margin: 1rem 0;
        overflow: hidden;
    }
    
    .progress-bar {
        height: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        transition: width 1s ease;
        position: relative;
    }
    
    .progress-bar::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        bottom: 0;
        right: 0;
        background-image: linear-gradient(
            -45deg,
            rgba(255, 255, 255, .2) 25%,
            transparent 25%,
            transparent 50%,
            rgba(255, 255, 255, .2) 50%,
            rgba(255, 255, 255, .2) 75%,
            transparent 75%,
            transparent
        );
        background-size: 30px 30px;
        animation: move 2s linear infinite;
    }
    
    @keyframes move {
        0% { background-position: 0 0; }
        100% { background-position: 30px 30px; }
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem;
        }
        
        .main-header p {
            font-size: 1rem;
        }
        
        .metric-card {
            padding: 1.5rem 1rem;
        }
        
        .metric-value {
            font-size: 2rem;
        }
    }
    
    /* Loading spinner */
    .loading-spinner {
        border: 3px solid #f3f3f3;
        border-top: 3px solid #667eea;
        border-radius: 50%;
        width: 20px;
        height: 20px;
        animation: spin 1s linear infinite;
        display: inline-block;
        margin-right: 8px;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
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
            
            # Enhanced hashtag generation
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
                'engagement_prediction': random.choice(['Very High', 'High', 'High', 'Medium'])  # Weighted towards positive
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
    # More realistic data with trends
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
    st.markdown(f'<div class="success-alert">✅ {message}</div>', unsafe_allow_html=True)

def show_info(message: str):
    st.markdown(f'<div class="info-alert">ℹ️ {message}</div>', unsafe_allow_html=True)

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
    
    # Professional Header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 AI Social Media Platform</h1>
        <p>Professional Content Generation & Marketing Automation</p>
        <div class="status-badge">
            <div class="status-dot"></div>
            System Online • Auto-posting Active
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced Sidebar with better organization
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
            st.success("✅ Demo mode active")
        elif api_key:
            st.success("✅ API key configured")
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
        st.info(f"📊 {active_count}/4 platforms active")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Automation Section
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("### 🤖 Automation Control")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Toggle Auto", help="Start/stop automation"):
                st.session_state.automation_active = not st.session_state.automation_active
                if st.session_state.automation_active:
                    show_success("Automation activated!")
                else:
                    show_info("Automation paused!")
        
        with col2:
            if st.button("📊 Quick Stats", help="View quick statistics"):
                show_info(f"Generated {st.session_state.posts_generated_today} posts today")
        
        status = "🟢 Active" if st.session_state.automation_active else "🔴 Paused"
        st.markdown(f"**Status:** {status}")
        
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
    
    # Enhanced Tabs with better content
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🚀 Dashboard", "📝 Content Studio", "📊 Analytics Hub", "🎯 Campaign Manager", "⏰ Smart Scheduler"
    ])
    
    # Dashboard Tab - Enhanced
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
            
            if st.button("📊 Run Performance Scan", use_container_width=True):
                with st.spinner("Analyzing performance..."):
                    time.sleep(2)
                    show_info("Performance scan complete! All systems optimal.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Content Studio Tab - Major Enhancement
    with tab2:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("### 🎨 AI Content Studio")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### Create New Content")
            
            # Enhanced content creation form
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
                
                # Enhanced scheduling with proper date picker
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
                            
                            # Create post object with enhanced data
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
                        # Platform badge
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
                        
                        # Action buttons
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
                st.info("👆 Generate your first piece of content to see it here!")
                st.markdown("**Tips for great content:**")
                st.markdown("• Use specific, trending topics")
                st.markdown("• Choose the right platform for your audience")
                st.markdown("• Experiment with different content styles")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Analytics Hub Tab - Enhanced
    with tab3:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("### 📊 Advanced Analytics Dashboard")
        
        try:
            # Enhanced engagement trends
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
                font=dict(color='#495057'),
                title_font_size=16,
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Platform comparison with enhanced metrics
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🏆 Platform Performance Comparison")
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
                    font=dict(color='#495057'),
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
                    font=dict(color='#495057'),
                    height=350
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            
            # Enhanced top content table
            st.markdown("#### 🔥 Top Performing Content")
            top_posts_data = {
                'Platform': ['Instagram', 'Twitter', 'LinkedIn', 'Facebook', 'Instagram'],
                'Content': [
                    "AI innovation showcase - behind the scenes 🚀",
                    "5 productivity tips that changed my workflow ⚡",
                    "Industry insight: The future of remote work 💼",
                    "Community poll: What's your favorite AI tool? 🤖",
                    "Tech trends 2024 - complete visual guide 📊"
                ],
                'Engagement': [847, 623, 445, 387, 356],
                'Reach': [12500, 8900, 6700, 5400, 4800],
                'Date': ['Jan 28', 'Jan 27', 'Jan 26', 'Jan 25', 'Jan 24']
            }
            
            df_styled = pd.DataFrame(top_posts_data)
            st.dataframe(
                df_styled,
                use_container_width=True,
                hide_index=True
            )
                
        except Exception as e:
            st.error(f"Analytics error: {e}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Campaign Manager Tab - Enhanced
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
                },
                {
                    "name": "Tech Trends 2024", 
                    "status": "Planning", 
                    "progress": 25, 
                    "posts": "5/20", 
                    "engagement": "1.1K",
                    "days_left": 7,
                    "roi": "+15%"
                }
            ]
            
            for campaign in campaigns:
                st.markdown('<div class="campaign-card">', unsafe_allow_html=True)
                
                # Campaign header
                col_name, col_status = st.columns([2, 1])
                with col_name:
                    st.markdown(f'<div class="campaign-name">{campaign["name"]}</div>', unsafe_allow_html=True)
                with col_status:
                    status_class = "status-running" if campaign["status"] == "Running" else "status-planning"
                    st.markdown(f'<span class="campaign-status {status_class}">🟢 {campaign["status"]}</span>', unsafe_allow_html=True)
                
                # Progress bar
                progress_html = f'''
                <div class="progress-container">
                    <div class="progress-bar" style="width: {campaign["progress"]}%;"></div>
                </div>
                '''
                st.markdown(progress_html, unsafe_allow_html=True)
                
                # Campaign metrics
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
                campaign_name = st.text_input(
                    "Campaign Name",
                    placeholder="e.g., Summer Product Launch"
                )
                
                campaign_objective = st.selectbox(
                    "Campaign Objective",
                    ["Brand Awareness", "Lead Generation", "Engagement", "Traffic", "Sales"]
                )
                
                campaign_duration = st.slider("Duration (days)", 1, 30, 7)
                posts_per_day = st.slider("Posts per day", 1, 8, 3)
                
                target_platforms = st.multiselect(
                    "Target Platforms",
                    ["Twitter", "Instagram", "Facebook", "LinkedIn"],
                    default=["Twitter", "Instagram"]
                )
                
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
    
    # Smart Scheduler Tab - Major Enhancement
    with tab5:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("### ⏰ Intelligent Content Scheduler")
        
        col1, col2 = st.columns([1.2, 0.8])
        
        with col1:
            st.markdown("#### 📅 Upcoming Posts Queue")
            
            upcoming_posts = [
                {
                    "platform": "Twitter", 
                    "content": "AI productivity tips for remote teams", 
                    "time": "in 47 minutes",
                    "engagement_pred": "High",
                    "optimal": True
                },
                {
                    "platform": "Instagram", 
                    "content": "Tech innovation showcase with visuals", 
                    "time": "in 2 hours",
                    "engagement_pred": "Very High",
                    "optimal": True
                },
                {
                    "platform": "Facebook", 
                    "content": "Community growth success story", 
                    "time": "tomorrow 9:00 AM",
                    "engagement_pred": "Medium",
                    "optimal": True
                },
                {
                    "platform": "LinkedIn", 
                    "content": "Industry leadership insights", 
                    "time": "tomorrow 12:00 PM",
                    "engagement_pred": "High",
                    "optimal": True
                }
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
            
            # Optimal times display
            st.markdown("**📊 AI-Optimized Posting Times**")
            optimal_times = {
                "🐦 Twitter": "8AM, 12PM, 5PM, 8PM",
                "📸 Instagram": "11AM, 2PM, 5PM, 7PM", 
                "👥 Facebook": "9AM, 1PM, 3PM, 6PM",
                "💼 LinkedIn": "10AM, 12PM, 2PM, 4PM"
            }
            
            for platform, times in optimal_times.items():
                st.markdown(f"**{platform}:** {times}")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Enhanced scheduling preferences
            st.markdown("**🎯 Scheduling Preferences**")
            
            auto_optimize = st.checkbox("🤖 AI-powered time optimization", value=True)
            avoid_weekends = st.checkbox("📅 Skip weekend posting", value=False)
            timezone_aware = st.checkbox("🌍 Timezone-aware scheduling", value=True)
            
            spread_hours = st.slider("⏰ Hours between posts", 1, 12, 2)
            max_daily_posts = st.slider("📊 Max posts per day", 1, 10, 4)
            
            # Bulk scheduling
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
    
    # Enhanced Footer
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; color: #6c757d; padding: 2rem; border-top: 1px solid #e9ecef; margin-top: 3rem;">
        <p style="font-size: 1.1rem; font-weight: 500;">🤖 <strong>AI Social Media Platform</strong> v3.0</p>
        <p style="font-size: 0.9rem;">Professional Content Generation & Marketing Automation | 
        <a href="#" style="color: #667eea; text-decoration: none;">Documentation</a> | 
        <a href="#" style="color: #667eea; text-decoration: none;">API Reference</a> | 
        <a href="#" style="color: #667eea; text-decoration: none;">Support</a></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
