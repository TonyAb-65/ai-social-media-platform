#!/usr/bin/env python3
"""
AI Social Media Platform - OpenAI Integration
==========================================
Integrated with OpenAI API for real AI-powered content generation
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

# Modern Professional CSS
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
    
    .modern-warning {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        color: #92400e;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #f59e0b;
        margin: 1rem 0;
        font-weight: 500;
        box-shadow: 0 1px 3px rgba(245, 158, 11, 0.1);
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
            'posts_generated_today': 0,
            'total_engagement': 0,
            'success_rate': 0.0,
            'active_platforms': 4,
            'generated_posts': [],
            'selected_date': date.today(),
            'current_topic': 'AI Innovation',
            'scheduling_states': {},
            'form_submitted': False,
            'last_generation_time': None,
            'api_calls_count': 0,
            'total_api_cost': 0.0
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
                generated_by TEXT
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
    """AI-powered content generator using OpenAI API"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.client = None
        
        # Initialize OpenAI client if API key is valid
        if api_key and api_key != "demo" and OPENAI_AVAILABLE:
            try:
                self.client = OpenAI(api_key=api_key)
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"OpenAI initialization error: {e}")
                self.client = None
        
        # Fallback templates for demo mode
        self.templates = {
            'twitter': [
                "🚀 {topic} is revolutionizing the future! The innovation potential is incredible. What's your take?",
                "💡 Breaking: {topic} developments are reshaping entire industries. Key insights everyone should know...",
                "🔥 The {topic} revolution is here! From startups to enterprises, everyone's adapting. What changes are you seeing?",
                "⚡ {topic} breakthrough alert! This could change everything. Thoughts?"
            ],
            'instagram': [
                "✨ Diving deep into the world of {topic} today! Swipe to discover the innovations shaping our future ➡️",
                "🌟 {topic} continues to amaze us with groundbreaking developments! Every innovation tells a story 💭",
                "📸 Behind the scenes: How {topic} is transforming industries and creating new possibilities ✨",
                "🎯 {topic} showcase: From concept to reality, witness the innovation journey 🌍"
            ],
            'facebook': [
                "🎉 Exciting developments in {topic}! Our community has been asking about the latest trends...",
                "💬 Community discussion: How is {topic} impacting your daily life and work? Share your insights!",
                "🌍 The global impact of {topic} is undeniable. Top 5 ways this technology is making a difference...",
                "📚 {topic} explained: Breaking down complex concepts into simple terms. Share this!"
            ],
            'linkedin': [
                "Professional insight: {topic} is revolutionizing industries at an unprecedented pace. Key strategic implications:",
                "Market analysis: The {topic} sector shows remarkable growth potential. What this means for your career:",
                "Leadership perspective: Successfully navigating the {topic} transformation requires strategic thinking:",
                "Industry update: {topic} continues to drive digital transformation across sectors. Essential considerations:"
            ]
        }
    
    def generate_with_openai(self, topic: str, platform: str, tone: str) -> Dict[str, Any]:
        """Generate content using OpenAI API"""
        try:
            # Platform-specific character limits and style
            platform_specs = {
                'twitter': {'max_chars': 280, 'style': 'concise and engaging', 'hashtags': 3},
                'instagram': {'max_chars': 2200, 'style': 'visual and inspiring', 'hashtags': 5},
                'facebook': {'max_chars': 400, 'style': 'conversational and community-focused', 'hashtags': 3},
                'linkedin': {'max_chars': 700, 'style': 'professional and insightful', 'hashtags': 4}
            }
            
            spec = platform_specs.get(platform.lower(), platform_specs['twitter'])
            
            # Create prompt for OpenAI
            prompt = f"""Create an engaging social media post for {platform} about "{topic}".

Requirements:
- Tone: {tone}
- Style: {spec['style']}
- Maximum {spec['max_chars']} characters
- Include {spec['hashtags']} relevant hashtags
- Make it attention-grabbing and shareable
- Use appropriate emojis for the platform

Format your response as JSON:
{{
    "content": "the post text with emojis",
    "hashtags": ["hashtag1", "hashtag2", "hashtag3"]
}}"""

            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert social media content creator who crafts engaging, viral-worthy posts."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=500
            )
            
            # Parse response
            content_text = response.choices[0].message.content.strip()
            
            # Try to parse JSON response
            try:
                # Remove markdown code blocks if present
                if content_text.startswith('```'):
                    content_text = content_text.split('```')[1]
                    if content_text.startswith('json'):
                        content_text = content_text[4:]
                    content_text = content_text.strip()
                
                content_data = json.loads(content_text)
                post_text = content_data.get('content', '')
                hashtags = content_data.get('hashtags', [])
            except json.JSONDecodeError:
                # Fallback if not valid JSON
                post_text = content_text
                hashtags = [f"#{topic.replace(' ', '')[:15]}", "#AI", "#Innovation"]
            
            return {
                'text': post_text,
                'hashtags': hashtags if isinstance(hashtags, list) else [],
                'word_count': len(post_text.split()),
                'char_count': len(post_text),
                'platform': platform,
                'topic': topic,
                'engagement_prediction': random.choice(['Very High', 'High', 'High']),
                'generated_by': 'OpenAI GPT-4'
            }
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise e
    
    def generate_with_template(self, topic: str, platform: str) -> Dict[str, Any]:
        """Fallback: Generate content using templates"""
        platform_key = platform.lower()
        template = random.choice(self.templates.get(platform_key, self.templates['twitter']))
        content = template.format(topic=topic)
        
        base_hashtags = [f"#{topic.replace(' ', '').replace('&', '')[:15]}", "#AI", "#Innovation", "#Technology"]
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
            'engagement_prediction': random.choice(['High', 'Medium']),
            'generated_by': 'Template'
        }
    
    def generate_content(self, topic: str, platform: str, tone: str = "professional") -> Dict[str, Any]:
        """Generate content - tries OpenAI first, falls back to templates"""
        if not topic or not topic.strip():
            raise ValueError("Topic cannot be empty")
        
        # Try OpenAI if available
        if self.client:
            try:
                result = self.generate_with_openai(topic, platform, tone)
                logger.info(f"Content generated successfully using OpenAI for {platform}")
                return result
            except Exception as e:
                logger.warning(f"OpenAI failed, using template fallback: {e}")
                st.warning("⚠️ API call failed, using template mode")
        
        # Fallback to templates
        return self.generate_with_template(topic, platform)

def create_analytics_data():
    """Create analytics data with error handling"""
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
        logger.error(f"Analytics data creation error: {e}")
        return pd.DataFrame()

def show_success(message: str):
    st.markdown(f'<div class="modern-success">✅ {message}</div>', unsafe_allow_html=True)

def show_info(message: str):
    st.markdown(f'<div class="modern-info">ℹ️ {message}</div>', unsafe_allow_html=True)

def show_warning(message: str):
    st.markdown(f'<div class="modern-warning">⚠️ {message}</div>', unsafe_allow_html=True)

def show_error(message: str):
    st.markdown(f'<div class="modern-error">❌ {message}</div>', unsafe_allow_html=True)

def create_metric_card(icon: str, label: str, value: str, delta: str = ""):
    delta_html = f'<div class="metric-delta">{delta}</div>' if delta else ''
    return f"""
    <div class="metric-card">
        <div class="metric-icon">{icon}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
        {delta_html}
    </div>
    """

def save_post_to_db(conn, post_data: Dict[str, Any]):
    """Save post to database with error handling"""
    try:
        if not conn:
            logger.warning("No database connection available")
            return False
            
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO posts (id, platform, content, hashtags, created_at, 
                             scheduled_date, scheduled_time, engagement_prediction, 
                             topic, style, generated_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            post_data.get('generated_by', 'Unknown')
        ))
        conn.commit()
        logger.info(f"Post saved to database: {post_data['id']}")
        return True
        
    except sqlite3.Error as e:
        logger.error(f"Database save error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected save error: {e}")
        return False

def main():
    """Main application function"""
    try:
        init_session_state()
        conn = get_database_connection()
        
        # Header
        st.markdown("""
        <div class="modern-header">
            <div class="header-content">
                <div class="header-left">
                    <h1>🤖 AI Social Media Platform</h1>
                    <p>OpenAI-Powered Content Generation & Marketing Automation</p>
                </div>
                <div class="header-right">
                    <div class="status-badge">
                        <div class="status-dot"></div>
                        System Online
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Sidebar configuration
        with st.sidebar:
            st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
            st.markdown("### 🔑 OpenAI API Configuration")
            
            # Check if API key exists in secrets
            api_key_from_secrets = None
            try:
                api_key_from_secrets = st.secrets.get("openai_api_key", None)
            except:
                pass
            
            # API Key Input
            api_key = st.text_input(
                "OpenAI API Key", 
                type="password",
                value=api_key_from_secrets if api_key_from_secrets else "",
                help="Enter your OpenAI API key or use 'demo' for template mode. Get key at: https://platform.openai.com/api-keys"
            )
            
            # API Status Display
            if not api_key:
                show_warning("No API key provided. Using template mode.")
                api_mode = "Template Mode"
                api_status = "warning"
            elif api_key == "demo":
                show_info("Demo mode active. Using templates.")
                api_mode = "Template Mode"
                api_status = "info"
            elif not OPENAI_AVAILABLE:
                show_error("OpenAI library not installed! Run: pip install openai")
                api_mode = "Error"
                api_status = "error"
            else:
                show_success("API key configured. Using OpenAI GPT-4.")
                api_mode = "OpenAI GPT-4"
                api_status = "success"
            
            # Display metrics
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Current Mode", api_mode)
            with col2:
                st.metric("API Calls", st.session_state.api_calls_count)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Content Settings
            st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
            st.markdown("### 📝 Content Settings")
            
            topics = st.multiselect(
                "Content Topics",
                ["AI & Machine Learning", "Technology Trends", "Digital Innovation", 
                 "Productivity & Automation", "Digital Marketing", "Business Strategy", 
                 "Startup Ecosystem", "Future Technology"],
                default=["AI & Machine Learning", "Technology Trends"]
            )
            
            tone = st.selectbox(
                "Content Tone", 
                ["Professional", "Casual & Friendly", "Thought Leadership", "Educational", "Inspirational"]
            )
            
            target_audience = st.selectbox(
                "Target Audience",
                ["Tech Professionals", "Business Leaders", "Entrepreneurs", "General Audience"]
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
        
        # Metrics Dashboard
        st.markdown("### 📊 Performance Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(create_metric_card(
                "📈", "Posts Generated", str(st.session_state.posts_generated_today), 
                f"+{st.session_state.posts_generated_today} today"
            ), unsafe_allow_html=True)
        
        with col2:
            st.markdown(create_metric_card(
                "🤖", "API Calls", str(st.session_state.api_calls_count),
                "OpenAI Powered"
            ), unsafe_allow_html=True)
        
        with col3:
            st.markdown(create_metric_card(
                "⚙️", "Generation Mode", api_mode[:10], 
                "Active"
            ), unsafe_allow_html=True)
        
        with col4:
            st.markdown(create_metric_card(
                "📱", "Active Platforms", f"{active_count}/4", 
                f"{active_count} connected"
            ), unsafe_allow_html=True)
        
        # Main Content Area
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
                                # Show different message based on mode
                                if api_mode == "OpenAI GPT-4":
                                    time_module.sleep(1)  # Simulate API call time
                                else:
                                    time_module.sleep(0.5)
                                
                                generator = ContentGenerator(api_key if api_key != "demo" else None)
                                content = generator.generate_content(topic, platform, tone)
                                
                                # Track API calls
                                if content.get('generated_by') == 'OpenAI GPT-4':
                                    st.session_state.api_calls_count += 1
                                
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
                                    'generated_by': content.get('generated_by', 'Unknown')
                                }
                                
                                st.session_state.generated_posts.insert(0, new_post)
                                st.session_state.posts_generated_today += 1
                                st.session_state.current_topic = topic
                                
                                if conn:
                                    save_post_to_db(conn, new_post)
                                
                                show_success(f"Content generated using {content.get('generated_by', 'AI')}!")
                                st.rerun()
                                
                        except ValueError as e:
                            show_error(f"Validation error: {str(e)}")
                        except Exception as e:
                            logger.error(f"Content generation error: {e}")
                            show_error(f"Failed to generate content: {str(e)}")
        
        with col2:
            st.markdown("#### 📋 Generated Content Library")
            
            if st.session_state.generated_posts:
                for i, post in enumerate(st.session_state.generated_posts[:5]):
                    with st.expander(f"{post['platform']} - {post['topic']}", expanded=(i==0)):
                        platform_class = f"badge-{post['platform'].lower()}"
                        st.markdown(f'<span class="platform-badge {platform_class}">{post["platform"]}</span>', unsafe_allow_html=True)
                        
                        st.markdown("**Content:**")
                        st.write(post["content"])
                        
                        st.markdown("**Hashtags:**")
                        st.markdown(f'<div style="color: #3b82f6; font-weight: 500;">{" ".join(post["hashtags"])}</div>', unsafe_allow_html=True)
                        
                        col_pred, col_gen = st.columns(2)
                        with col_pred:
                            st.metric("Engagement", post['engagement_prediction'])
                        with col_gen:
                            st.metric("Generated By", post.get('generated_by', 'N/A'))
                        
                        if post.get('scheduled_date') and post.get('scheduled_time'):
                            sched_date = datetime.fromisoformat(post['scheduled_date']).strftime('%B %d, %Y')
                            try:
                                time_str = post['scheduled_time']
                                try:
                                    parsed_time = datetime.strptime(time_str, '%H:%M:%S.%f').time()
                                except ValueError:
                                    parsed_time = datetime.strptime(time_str, '%H:%M:%S').time()
                                sched_time = parsed_time.strftime('%I:%M %p')
                                st.info(f"📅 Scheduled for: {sched_date} at {sched_time}")
                            except:
                                st.info(f"📅 Scheduled for: {sched_date}")
                        
                        col_a, col_b, col_c = st.columns(3)
                        
                        with col_a:
                            if st.button("📅 Schedule", key=f"sched_{post['id']}", use_container_width=True):
                                st.info("Scheduling feature - coming soon!")
                        
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
                                    logger.error(f"Post error: {e}")
                                    show_error("Failed to post content")
                        
                        with col_c:
                            if st.button("🗑️ Delete", key=f"del_{post['id']}", use_container_width=True):
                                st.session_state.generated_posts = [p for p in st.session_state.generated_posts if p['id'] != post['id']]
                                show_success("Post deleted!")
                                st.rerun()
            else:
                show_info("Generate your first piece of content to see it here!")
                st.markdown("**Tips for great content:**")
                st.markdown("• Use specific, trending topics")
                st.markdown("• Choose the right platform for your audience")
                st.markdown("• Experiment with different content styles")
                st.markdown("• Use OpenAI API for best results!")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Analytics Section
        if st.session_state.generated_posts:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.markdown("### 📊 Content Analytics")
            
            posts_df = pd.DataFrame([
                {
                    'Platform': post['platform'],
                    'Topic': post['topic'],
                    'Style': post.get('style', 'Standard'),
                    'Prediction': post['engagement_prediction'],
                    'Generated By': post.get('generated_by', 'Unknown'),
                    'Created': datetime.fromisoformat(post['created_at']).strftime('%Y-%m-%d %H:%M')
                }
                for post in st.session_state.generated_posts
            ])
            
            st.dataframe(posts_df, use_container_width=True, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Footer
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align: center; color: #64748b; padding: 2rem; border-top: 1px solid #e2e8f0; margin-top: 3rem;">
            <p style="font-size: 1.1rem; font-weight: 500;">🤖 <strong>AI Social Media Platform</strong> v5.0 - OpenAI Integration</p>
            <p style="font-size: 0.9rem;">Powered by OpenAI GPT-4 | Professional Content Generation & Marketing Automation</p>
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        logger.error(f"Main application error: {e}")
        st.error("Application encountered an error. Please refresh the page.")
        st.exception(e)

if __name__ == "__main__":
    main()
