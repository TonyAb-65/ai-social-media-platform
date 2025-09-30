#!/usr/bin/env python3
"""
AI Social Media Platform - OpenAI Integration with Image Generation
===================================================================
Full UI preserved with OpenAI GPT-4 and DALL-E integration
"""

import streamlit as st
import sqlite3
import json
import uuid
import random
import time as time_module
from datetime import datetime, timedelta, date, time as time_obj
from typing import Dict, List, Optional, Any
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import logging
import base64
from io import BytesIO

# OpenAI Integration
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set page config FIRST
try:
    st.set_page_config(
        page_title="AI Social Media Platform",
        page_icon="🤖", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
except Exception as e:
    logger.error(f"Page config error: {e}")

# Modern Professional CSS (YOUR ORIGINAL CSS - PRESERVED)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    .modern-header {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 50%, #7c3aed 100%);
        padding: 2rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 20px 40px rgba(59, 130, 246, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .header-content {
        position: relative;
        z-index: 1;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 1rem;
    }
    
    .header-left h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0 0 0.5rem 0;
        color: white;
    }
    
    .header-left p {
        font-size: 1.1rem;
        opacity: 0.9;
        margin: 0;
        font-weight: 400;
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
    
    .sidebar-section {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .sidebar-section h3 {
        color: #1e293b;
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #3b82f6;
    }
    
    .metric-card {
        background: white;
        padding: 2rem 1.5rem;
        border-radius: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
        height: 100%;
        position: relative;
        overflow: hidden;
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
    
    .content-card {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
    }
    
    .content-card h3 {
        color: #1e293b;
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid #f1f5f9;
    }
    
    .modern-success {
        background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
        color: #166534;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #22c55e;
        margin: 1rem 0;
        font-weight: 500;
        box-shadow: 0 1px 3px rgba(34, 197, 94, 0.1);
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
    }
    
    .modern-error {
        background: linear-gradient(135deg, #fecaca 0%, #fca5a5 100%);
        color: #dc2626;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #ef4444;
        margin: 1rem 0;
        font-weight: 500;
        box-shadow: 0 1px 3px rgba(239, 68, 68, 0.1);
    }
    
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
    
    .scheduling-interface {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1rem;
        margin-top: 1rem;
    }
    
    .campaign-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
    }
    
    .campaign-name {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1e293b;
    }
    
    .status-running { 
        background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%); 
        color: #166534; 
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    
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
    }
    
    @media (max-width: 768px) {
        .header-content {
            flex-direction: column;
            text-align: center;
        }
        
        .header-left h1 {
            font-size: 2rem;
        }
        
        .metric-card {
            padding: 1.5rem 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

def init_session_state():
    """Initialize session state with default values"""
    try:
        defaults = {
            'automation_active': True,
            'posts_generated_today': 26,
            'total_engagement': 8431,
            'success_rate': 99.2,
            'active_platforms': 4,
            'generated_posts': [],
            'selected_date': date.today(),
            'current_topic': 'AI Innovation',
            'scheduling_states': {},
            'form_submitted': False,
            'last_generation_time': None,
            'api_calls_count': 0,
            'images_generated': 0
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
                
        logger.info("Session state initialized successfully")
        
    except Exception as e:
        logger.error(f"Session state initialization error: {e}")
        st.error("Failed to initialize application state")

def get_database_connection():
    """Get database connection with proper error handling"""
    try:
        conn = sqlite3.connect('social_platform.db', check_same_thread=False)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id TEXT PRIMARY KEY,
                platform TEXT NOT NULL,
                content TEXT NOT NULL,
                hashtags TEXT,
                created_at TEXT NOT NULL,
                scheduled_date TEXT,
                scheduled_time TEXT,
                posted BOOLEAN DEFAULT 0,
                engagement_prediction TEXT,
                topic TEXT,
                style TEXT,
                generated_by TEXT,
                image_url TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                platform TEXT NOT NULL,
                engagement INTEGER DEFAULT 0,
                posts_count INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        logger.info("Database initialized successfully")
        return conn
        
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        st.error(f"Database connection failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected database error: {e}")
        st.error("Failed to initialize database")
        return None

class ContentGenerator:
    """Enhanced AI-powered content generator with OpenAI GPT-4 and DALL-E"""
    
    def __init__(self, api_key: str = "demo"):
        self.api_key = api_key
        self.client = None
        
        # Initialize OpenAI client if valid API key
        if api_key and api_key != "demo" and OPENAI_AVAILABLE:
            try:
                self.client = OpenAI(api_key=api_key)
                logger.info("OpenAI client initialized")
            except Exception as e:
                logger.error(f"OpenAI initialization error: {e}")
                self.client = None
        
        # Original templates preserved
        self.templates = {
            'twitter': [
                "🚀 {topic} is revolutionizing the future! The innovation potential is incredible. What's your take on where this is heading?",
                "💡 Breaking: {topic} developments are reshaping entire industries. Here are the key insights every professional should know...",
                "🔥 The {topic} revolution is here! From startups to enterprises, everyone's adapting. What changes are you seeing?",
                "⚡ {topic} breakthrough alert! This could change everything we know about technology and innovation. Thoughts?"
            ],
            'instagram': [
                "✨ Diving deep into the world of {topic} today! Swipe to discover the incredible innovations shaping our future ➡️",
                "🌟 {topic} continues to amaze us with groundbreaking developments! Behind every great innovation is a story worth telling 💭",
                "📸 Behind the scenes: How {topic} is transforming industries and creating new possibilities. The future looks incredibly bright! ✨",
                "🎯 {topic} showcase: From concept to reality, witness the journey of innovation that's changing the world 🌍"
            ],
            'facebook': [
                "🎉 Exciting developments in {topic}! Our community has been asking about the latest trends, so here's a comprehensive breakdown...",
                "💬 Community discussion: How is {topic} impacting your daily life and work? We'd love to hear your experiences and insights!",
                "🌍 The global impact of {topic} is undeniable. Here are the top 5 ways this technology is making a positive difference worldwide...",
                "📚 {topic} explained: Breaking down complex concepts into simple terms. Share this with someone who might find it interesting!"
            ],
            'linkedin': [
                "Professional insight: {topic} is revolutionizing industries at an unprecedented pace. Key strategic implications for business leaders:",
                "Market analysis: The {topic} sector shows remarkable growth potential with significant opportunities ahead. What this means for your career:",
                "Leadership perspective: Successfully navigating the {topic} transformation requires strategic thinking and adaptive planning. Here's my take:",
                "Industry update: {topic} continues to drive digital transformation across sectors. Essential considerations for forward-thinking professionals:"
            ]
        }
    
    def generate_with_openai(self, topic: str, platform: str, tone: str) -> Dict[str, Any]:
        """Generate content using OpenAI GPT-4"""
        try:
            platform_specs = {
                'twitter': {'max_chars': 280, 'style': 'concise and engaging'},
                'instagram': {'max_chars': 2200, 'style': 'visual and inspiring'},
                'facebook': {'max_chars': 400, 'style': 'conversational and community-focused'},
                'linkedin': {'max_chars': 700, 'style': 'professional and insightful'}
            }
            
            spec = platform_specs.get(platform.lower(), platform_specs['twitter'])
            
            prompt = f"""Create an engaging social media post for {platform} about "{topic}".

Requirements:
- Tone: {tone}
- Style: {spec['style']}
- Maximum {spec['max_chars']} characters
- Include 3-5 relevant hashtags
- Use appropriate emojis
- Make it shareable and attention-grabbing

Format response as JSON:
{{
    "content": "the post text",
    "hashtags": ["hashtag1", "hashtag2", "hashtag3"]
}}"""

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert social media content creator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=500
            )
            
            content_text = response.choices[0].message.content.strip()
            
            # Parse JSON
            try:
                if content_text.startswith('```'):
                    content_text = content_text.split('```')[1]
                    if content_text.startswith('json'):
                        content_text = content_text[4:]
                    content_text = content_text.strip()
                
                content_data = json.loads(content_text)
                post_text = content_data.get('content', '')
                hashtags = content_data.get('hashtags', [])
            except:
                post_text = content_text
                hashtags = [f"#{topic.replace(' ', '')[:15]}", "#AI", "#Innovation"]
            
            return {
                'text': post_text,
                'hashtags': hashtags if isinstance(hashtags, list) else [],
                'word_count': len(post_text.split()),
                'char_count': len(post_text),
                'platform': platform,
                'topic': topic,
                'engagement_prediction': random.choice(['Very High', 'High', 'High', 'Medium']),
                'generated_by': 'OpenAI GPT-4'
            }
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise e
    
    def generate_image(self, prompt: str, size: str = "1024x1024") -> Optional[str]:
        """Generate image using DALL-E"""
        if not self.client:
            return None
        
        try:
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                quality="standard",
                n=1,
            )
            
            image_url = response.data[0].url
            logger.info(f"Image generated successfully: {image_url}")
            return image_url
            
        except Exception as e:
            logger.error(f"DALL-E error: {e}")
            return None
    
    def generate_content(self, topic: str, platform: str, tone: str = "professional") -> Dict[str, Any]:
        """Generate content - tries OpenAI first, falls back to templates"""
        if not topic or not topic.strip():
            raise ValueError("Topic cannot be empty")
        
        # Try OpenAI
        if self.client:
            try:
                return self.generate_with_openai(topic, platform, tone)
            except Exception as e:
                logger.warning(f"OpenAI failed, using template: {e}")
        
        # Fallback to templates
        platform_key = platform.lower()
        if platform_key not in self.templates:
            platform_key = 'twitter'
        
        template = random.choice(self.templates[platform_key])
        content = template.format(topic=topic)
        
        base_hashtags = [f"#{topic.replace(' ', '').replace('&', '')[:15]}", "#AI", "#Innovation", "#Technology"]
        platform_hashtags = {
            'twitter': ["#TechTalk", "#Innovation"],
            'instagram': ["#TechLife", "#Innovation"],
            'facebook': ["#Community", "#TechNews"],
            'linkedin': ["#Leadership", "#Professional"]
        }
        
        hashtags = base_hashtags[:2] + platform_hashtags.get(platform_key, [])[:2]
        
        return {
            'text': content,
            'hashtags': hashtags,
            'word_count': len(content.split()),
            'char_count': len(content),
            'platform': platform,
            'topic': topic,
            'engagement_prediction': random.choice(['Very High', 'High', 'High', 'Medium']),
            'generated_by': 'Template'
        }

def create_analytics_data():
    """Create analytics data"""
    try:
        dates = pd.date_range(start='2024-01-01', end='2024-01-30', freq='D')
        base_values = {'Twitter': 150, 'Instagram': 250, 'Facebook': 120, 'LinkedIn': 80}
        
        data = {'Date': dates}
        for platform, base in base_values.items():
            data[platform] = [
                max(0, base + random.randint(-30, 50) + i * random.randint(1, 3)) 
                for i in range(len(dates))
            ]
        
        return pd.DataFrame(data)
    except Exception as e:
        logger.error(f"Analytics data error: {e}")
        return pd.DataFrame()

def create_platform_data():
    """Create platform data"""
    try:
        return pd.DataFrame({
            'Platform': ['Instagram', 'Twitter', 'LinkedIn', 'Facebook'],
            'Engagement': [2847, 1923, 1456, 1205],
            'Posts': [45, 72, 38, 56],
            'Growth': [23.4, 15.8, 18.2, 12.1],
            'Avg_Engagement': [63.3, 26.7, 38.3, 21.5]
        })
    except Exception as e:
        logger.error(f"Platform data error: {e}")
        return pd.DataFrame()

def show_success(message: str):
    st.markdown(f'<div class="modern-success">✅ {message}</div>', unsafe_allow_html=True)

def show_info(message: str):
    st.markdown(f'<div class="modern-info">ℹ️ {message}</div>', unsafe_allow_html=True)

def show_error(message: str):
    st.markdown(f'<div class="modern-error">❌ {message}</div>', unsafe_allow_html=True)

def create_metric_card(icon: str, label: str, value: str, delta: str):
    return f"""
    <div class="metric-card">
        <div class="metric-icon">{icon}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
        <div class="metric-delta">{delta}</div>
    </div>
    """

def save_post_to_db(conn, post_data: Dict[str, Any]):
    """Save post to database"""
    try:
        if not conn:
            return False
            
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO posts (id, platform, content, hashtags, created_at, 
                             scheduled_date, scheduled_time, engagement_prediction, 
                             topic, style, generated_by, image_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            post_data['id'],
            post_data['platform'],
            post_data['content'],
            json.dumps(post_data['hashtags']),
            post_data['created_at'],
            post_data.get('scheduled_date'),
            post_data.get('scheduled_time'),
            post_data['engagement_prediction'],
            post_data['topic'],
            post_data.get('style', 'Standard'),
            post_data.get('generated_by', 'Unknown'),
            post_data.get('image_url')
        ))
        conn.commit()
        logger.info(f"Post saved: {post_data['id']}")
        return True
    except Exception as e:
        logger.error(f"Database save error: {e}")
        return False

def main():
    """Main application - ALL ORIGINAL FEATURES PRESERVED"""
    try:
        init_session_state()
        conn = get_database_connection()
        
        # Header
        st.markdown("""
        <div class="modern-header">
            <div class="header-content">
                <div class="header-left">
                    <h1>🤖 AI Social Media Platform</h1>
                    <p>Professional Content Generation & Marketing Automation with OpenAI</p>
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
        
        # SIDEBAR - ALL ORIGINAL SECTIONS
        with st.sidebar:
            # API Configuration
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
            elif api_key and len(api_key) > 10:
                show_success("API key configured")
            else:
                st.warning("⚠️ API key required for OpenAI features")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Content Settings
            st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
            st.markdown("### 📝 Content Settings")
            
            topics = st.multiselect(
                "Content Topics",
                ["AI & Machine Learning", "Technology Trends", "Digital Innovation", 
                 "Productivity & Automation", "Digital Marketing", "Business Strategy", 
                 "Startup Ecosystem", "Future Technology"],
                default=["AI & Machine Learning", "Technology Trends", "Digital Innovation"]
            )
            
            tone = st.selectbox(
                "Content Tone", 
                ["Professional", "Casual & Friendly", "Thought Leadership", "Educational", "Inspirational"]
            )
            
            target_audience = st.selectbox(
                "Target Audience",
                ["Tech Professionals", "Business Leaders", "Entrepreneurs", "General Audience", "Industry Specialists"]
            )
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Platform Selection
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
        
        # METRICS DASHBOARD
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
        
        # MAIN TABS - ALL ORIGINAL TABS
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🚀 Dashboard", "📝 Content Studio", "📊 Analytics Hub", "🎯 Campaign Manager", "⏰ Smart Scheduler"
        ])
        
        # TAB 1: DASHBOARD
        with tab1:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.markdown("### 🎯 Quick Actions Center")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("#### Content Generation")
                
                if st.button("✨ Generate Today's Content", type="primary", key="gen_today"):
                    try:
                        with st.spinner("🤖 AI is creating amazing content..."):
                            time_module.sleep(2)
                            st.session_state.posts_generated_today += 8
                            show_success("Generated 8 high-quality posts across all platforms!")
                            st.balloons()
                    except Exception as e:
                        logger.error(f"Content generation error: {e}")
                        show_error("Failed to generate content")
                
                if st.button("🎨 Create Visual Content", key="gen_visual"):
                    try:
                        with st.spinner("🎨 Generating visual content..."):
                            time_module.sleep(2)
                            st.session_state.images_generated += 5
                            show_success("Created 5 visual posts with AI-generated images!")
                    except Exception as e:
                        show_error("Failed to create visual content")
            
            with col2:
                st.markdown("#### Platform Health Monitor")
                
                platform_emojis = {"Twitter": "🐦", "Instagram": "📸", "Facebook": "👥", "LinkedIn": "💼"}
                
                for platform, active in platforms.items():
                    emoji = platform_emojis[platform]
                    if active:
                        st.success(f"{emoji} {platform}: Connected & Active")
                    else:
                        st.error(f"{emoji} {platform}: Disconnected")
                
                if st.button("🔄 Refresh All Connections", key="refresh_connections"):
                    try:
                        with st.spinner("Refreshing connections..."):
                            time_module.sleep(1)
                            show_success("All platform connections refreshed!")
                    except Exception as e:
                        show_error("Failed to refresh connections")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # TAB 2: CONTENT STUDIO (with OpenAI + Image Generation)
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
                        placeholder="e.g., AI Revolution in Healthcare"
                    )
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        platform = st.selectbox("Target Platform", ["Twitter", "Instagram", "Facebook", "LinkedIn"])
                    with col_b:
                        content_style = st.selectbox("Content Style", 
                            ["Informative", "Engaging", "Thought Leadership", "News Update", "Tutorial"])
                    
                    # Image Generation Option
                    generate_image = st.checkbox("🖼️ Generate AI Image (DALL-E)", value=False)
                    if generate_image:
                        image_prompt = st.text_area("Image Description", 
                            placeholder="Describe the image you want to generate...",
                            help="DALL-E will create an image based on this description")
                    
                    st.markdown("#### 📅 Scheduling Options")
                    schedule_option = st.radio("When to post:", 
                        ["Post immediately", "Schedule for later", "Add to queue"], horizontal=True)
                    
                    scheduled_date = None
                    scheduled_time = None
                    if schedule_option == "Schedule for later":
                        col_date, col_time = st.columns(2)
                        with col_date:
                            scheduled_date = st.date_input("Select Date", value=date.today(), min_value=date.today())
                        with col_time:
                            scheduled_time = st.time_input("Select Time", value=datetime.now().time())
                    
                    generate_btn = st.form_submit_button("🚀 Generate Content", type="primary")
                    
                    if generate_btn:
                        if not topic or not topic.strip():
                            show_error("Please enter a content topic")
                        else:
                            try:
                                with st.spinner(f"🤖 Creating {content_style.lower()} content for {platform}..."):
                                    generator = ContentGenerator(api_key)
                                    content = generator.generate_content(topic, platform, tone)
                                    
                                    # Generate image if requested
                                    image_url = None
                                    if generate_image and api_key != "demo":
                                        if image_prompt:
                                            with st.spinner("🎨 Generating AI image with DALL-E..."):
                                                image_url = generator.generate_image(image_prompt)
                                                if image_url:
                                                    st.session_state.images_generated += 1
                                                    show_success("AI image generated!")
                                        else:
                                            show_error("Please provide an image description")
                                    
                                    new_post = {
                                        'id': str(uuid.uuid4()),
                                        'platform': platform,
                                        'topic': topic,
                                        'content': content['text'],
                                        'hashtags': content['hashtags'],
                                        'style': content_style,
                                        'created_at': datetime.now().isoformat(),
                                        'scheduled_date': scheduled_date.isoformat() if scheduled_date else None,
                                        'scheduled_time': scheduled_time.isoformat() if scheduled_time else None,
                                        'posted': False,
                                        'engagement_prediction': content['engagement_prediction'],
                                        'generated_by': content.get('generated_by', 'Template'),
                                        'image_url': image_url
                                    }
                                    
                                    st.session_state.generated_posts.insert(0, new_post)
                                    st.session_state.current_topic = topic
                                    
                                    if conn:
                                        save_post_to_db(conn, new_post)
                                    
                                    if content.get('generated_by') == 'OpenAI GPT-4':
                                        st.session_state.api_calls_count += 1
                                    
                                    show_success("High-quality content generated successfully!")
                                    st.rerun()
                                    
                            except ValueError as e:
                                show_error(f"Validation error: {str(e)}")
                            except Exception as e:
                                logger.error(f"Content generation error: {e}")
                                show_error("Failed to generate content. Please try again.")
            
            with col2:
                st.markdown("#### 📋 Generated Content Library")
                
                if st.session_state.generated_posts:
                    for i, post in enumerate(st.session_state.generated_posts[:5]):
                        with st.expander(f"{post['platform']} - {post['topic']}", expanded=(i==0)):
                            platform_class = f"badge-{post['platform'].lower()}"
                            st.markdown(f'<span class="platform-badge {platform_class}">{post["platform"]}</span>', unsafe_allow_html=True)
                            
                            # Display image if exists
                            if post.get('image_url'):
                                st.image(post['image_url'], caption="AI Generated Image", use_column_width=True)
                            
                            st.markdown("**Content:**")
                            st.write(post["content"])
                            
                            st.markdown("**Hashtags:**")
                            st.markdown(f'<div style="color: #3b82f6; font-weight: 500;">{" ".join(post["hashtags"])}</div>', unsafe_allow_html=True)
                            
                            col_pred, col_style, col_gen = st.columns(3)
                            with col_pred:
                                st.metric("Engagement", post['engagement_prediction'])
                            with col_style:
                                st.metric("Style", post.get('style', 'Standard'))
                            with col_gen:
                                st.metric("Generated By", post.get('generated_by', 'N/A'))
                            
                            if post.get('scheduled_date') and post.get('scheduled_time'):
                                try:
                                    sched_date = datetime.fromisoformat(post['scheduled_date']).strftime('%B %d, %Y')
                                    time_str = post['scheduled_time']
                                    try:
                                        parsed_time = datetime.strptime(time_str, '%H:%M:%S.%f').time()
                                    except ValueError:
                                        parsed_time = datetime.strptime(time_str, '%H:%M:%S').time()
                                    sched_time = parsed_time.strftime('%I:%M %p')
                                    st.info(f"📅 Scheduled for: {sched_date} at {sched_time}")
                                except:
                                    pass
                            
                            col_a, col_b, col_c = st.columns(3)
                            
                            with col_a:
                                if st.button("📅 Schedule", key=f"sched_{post['id']}", use_container_width=True):
                                    st.info("Scheduling feature coming soon!")
                            
                            with col_b:
                                if st.button("📤 Post Now", key=f"post_{post['id']}", use_container_width=True):
                                    try:
                                        for idx, p in enumerate(st.session_state.generated_posts):
                                            if p['id'] == post['id']:
                                                st.session_state.generated_posts[idx]['posted'] = True
                                                break
                                        show_success("Posted successfully!")
                                        st.rerun()
                                    except Exception as e:
                                        show_error("Failed to post content")
                            
                            with col_c:
                                if st.button("✏️ Edit", key=f"edit_{post['id']}", use_container_width=True):
                                    show_info("Edit functionality coming soon!")
                else:
                    show_info("Generate your first piece of content to see it here!")
                    st.markdown("**Tips for great content:**")
                    st.markdown("• Use specific, trending topics")
                    st.markdown("• Choose the right platform for your audience")
                    st.markdown("• Experiment with different content styles")
                    st.markdown("• Try AI image generation for visual impact")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # TAB 3: ANALYTICS HUB (Original preserved)
        with tab3:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.markdown("### 📊 Advanced Analytics Dashboard")
            
            try:
                st.markdown("#### 📈 Engagement Trends Analysis")
                engagement_data = create_analytics_data()
                
                if not engagement_data.empty:
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
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 🏆 Platform Performance")
                    platform_data = create_platform_data()
                    
                    if not platform_data.empty:
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
                    if not platform_data.empty:
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
                
                if st.session_state.generated_posts:
                    st.markdown("#### 📋 Generated Content Summary")
                    posts_df = pd.DataFrame([
                        {
                            'Platform': post['platform'],
                            'Topic': post['topic'],
                            'Style': post.get('style', 'Standard'),
                            'Prediction': post['engagement_prediction'],
                            'Generated By': post.get('generated_by', 'N/A'),
                            'Has Image': 'Yes' if post.get('image_url') else 'No',
                            'Created': datetime.fromisoformat(post['created_at']).strftime('%Y-%m-%d %H:%M')
                        }
                        for post in st.session_state.generated_posts
                    ])
                    st.dataframe(posts_df, use_container_width=True)
                    
            except Exception as e:
                logger.error(f"Analytics error: {e}")
                show_error("Failed to load analytics data")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # TAB 4: CAMPAIGN MANAGER (Original preserved)
        with tab4:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.markdown("### 🎯 Advanced Campaign Management")
            
            col1, col2 = st.columns([1.2, 0.8])
            
            with col1:
                st.markdown("#### 📋 Active Campaigns")
                
                campaigns = [
                    {"name": "AI Innovation Week", "status": "Running", "progress": 75, "posts": "18/24", "engagement": "4.2K", "days_left": 2, "roi": "+23%"},
                    {"name": "Productivity Series", "status": "Running", "progress": 90, "posts": "14/16", "engagement": "2.8K", "days_left": 1, "roi": "+31%"}
                ]
                
                for campaign in campaigns:
                    st.markdown('<div class="campaign-card">', unsafe_allow_html=True)
                    
                    col_name, col_status = st.columns([2, 1])
                    with col_name:
                        st.markdown(f'<div class="campaign-name">{campaign["name"]}</div>', unsafe_allow_html=True)
                    with col_status:
                        st.markdown(f'<span class="status-running">🟢 {campaign["status"]}</span>', unsafe_allow_html=True)
                    
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
                            try:
                                with st.spinner("🎯 Creating your campaign..."):
                                    time_module.sleep(2)
                                    show_success(f"Campaign '{campaign_name}' launched successfully!")
                                    show_info(f"📊 Will generate {campaign_duration * posts_per_day} posts over {campaign_duration} days")
                                    st.balloons()
                            except Exception as e:
                                show_error("Failed to create campaign")
                        else:
                            show_error("Please fill in all required fields!")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # TAB 5: SMART SCHEDULER (Original preserved)
        with tab5:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.markdown("### ⏰ Intelligent Content Scheduler")
            
            col1, col2 = st.columns([1.2, 0.8])
            
            with col1:
                st.markdown("#### 📅 Upcoming Posts Queue")
                
                scheduled_posts = [post for post in st.session_state.generated_posts if post.get('scheduled_date')]
                
                if scheduled_posts:
                    for post in scheduled_posts:
                        platform_emoji = {"Twitter": "🐦", "Instagram": "📸", "Facebook": "👥", "LinkedIn": "💼"}
                        
                        try:
                            sched_date = datetime.fromisoformat(post['scheduled_date']).strftime('%B %d, %Y')
                            if post.get('scheduled_time'):
                                time_str = post['scheduled_time']
                                try:
                                    parsed_time = datetime.strptime(time_str, '%H:%M:%S.%f').time()
                                except ValueError:
                                    parsed_time = datetime.strptime(time_str, '%H:%M:%S').time()
                                sched_time = parsed_time.strftime('%I:%M %p')
                                full_schedule = f"{sched_date} at {sched_time}"
                            else:
                                full_schedule = sched_date
                            
                            with st.container():
                                col_platform, col_content, col_time, col_pred = st.columns([1, 3, 2, 1])
                                
                                with col_platform:
                                    st.markdown(f"**{platform_emoji[post['platform']]} {post['platform']}**")
                                with col_content:
                                    content_preview = post['content'][:60] + "..." if len(post['content']) > 60 else post['content']
                                    st.markdown(content_preview)
                                with col_time:
                                    st.caption(f"📅 {full_schedule}")
                                with col_pred:
                                    pred_color = {"Very High": "🟢", "High": "🟡", "Medium": "🟠"}
                                    st.caption(f"{pred_color.get(post['engagement_prediction'], '🔵')} {post['engagement_prediction']}")
                                
                                st.success("✅ Scheduled")
                                st.markdown("---")
                        except Exception as e:
                            logger.error(f"Scheduled post display error: {e}")
                else:
                    show_info("No scheduled posts yet. Create and schedule content in the Content Studio!")
            
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
                    if st.button("📅 Schedule Week", key="schedule_week"):
                        try:
                            with st.spinner("Scheduling week ahead..."):
                                time_module.sleep(2)
                                show_success("Week scheduled optimally!")
                        except Exception as e:
                            show_error("Failed to schedule week")
                
                with col_b:
                    if st.button("💾 Save Settings", key="save_settings"):
                        try:
                            show_success("Settings saved successfully!")
                        except Exception as e:
                            show_error("Failed to save settings")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Footer
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align: center; color: #64748b; padding: 2rem; border-top: 1px solid #e2e8f0; margin-top: 3rem;">
            <p style="font-size: 1.1rem; font-weight: 500;">🤖 <strong>AI Social Media Platform</strong> v5.0 - OpenAI Enhanced</p>
            <p style="font-size: 0.9rem;">Professional Content Generation with GPT-4 & DALL-E | Marketing Automation | 
            <a href="#" style="color: #3b82f6; text-decoration: none;">Documentation</a> | 
            <a href="#" style="color: #3b82f6; text-decoration: none;">API Reference</a> | 
            <a href="#" style="color: #3b82f6; text-decoration: none;">Support</a></p>
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        logger.error(f"Main application error: {e}")
        st.error("Application encountered an error. Please refresh the page.")
        st.exception(e)

if __name__ == "__main__":
    main()
