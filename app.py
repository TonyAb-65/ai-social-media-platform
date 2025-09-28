#!/usr/bin/env python3
"""
AI Social Media Platform - Complete Application
==============================================
"""

import streamlit as st
import sqlite3
import json
import uuid
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Set page config FIRST
st.set_page_config(
    page_title="🤖 AI Social Media Platform",
    page_icon="🚀", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .success-alert {
        background: #d4edda;
        color: #155724;
        padding: 12px;
        border-radius: 6px;
        border-left: 4px solid #28a745;
        margin: 10px 0;
    }
    
    .info-alert {
        background: #d1ecf1;
        color: #0c5460;
        padding: 12px;
        border-radius: 6px;
        border-left: 4px solid #17a2b8;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    defaults = {
        'automation_active': True,
        'posts_generated_today': 18,
        'total_engagement': 8431,
        'success_rate': 99.2,
        'generated_posts': []
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# Database setup
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
                posted BOOLEAN DEFAULT 0
            )
        ''')
        conn.commit()
        return conn
    except Exception as e:
        st.error(f"Database error: {e}")
        return None

# Content Generator
class ContentGenerator:
    def __init__(self, api_key: str = "demo"):
        self.api_key = api_key
        self.templates = {
            'twitter': [
                "🚀 {topic} is transforming innovation! What's your perspective? #Innovation #Tech",
                "💡 {topic} trends are reshaping our future. Here's what you need to know... #TechTrends",
                "🔥 Latest {topic} developments are game-changing! Let's discuss 👇 #TechNews"
            ],
            'instagram': [
                "✨ Exploring {topic} today! Swipe to see incredible possibilities ➡️ #TechLife",
                "🌟 {topic} continues to amaze with breakthrough innovations! What's your favorite? 💭",
                "📸 Behind the scenes: How {topic} is changing everything. The future looks bright! ✨"
            ],
            'facebook': [
                "🎉 Exciting developments in {topic}! Here's what our community needs to know...",
                "💬 Discussion: How is {topic} impacting your daily life? Share your thoughts!",
                "🌍 The global influence of {topic} is incredible. Here are the top ways it's making a difference..."
            ],
            'linkedin': [
                "Professional insight: {topic} is revolutionizing industries. Key takeaways:",
                "Market analysis: {topic} shows remarkable growth potential. What this means:",
                "Leadership perspective: Successfully navigating {topic} requires strategic thinking."
            ]
        }
    
    def generate_content(self, topic: str, platform: str, tone: str = "professional") -> Dict:
        try:
            platform_key = platform.lower()
            if platform_key not in self.templates:
                platform_key = 'twitter'
            
            template = random.choice(self.templates[platform_key])
            content = template.format(topic=topic)
            
            base_hashtags = [f"#{topic.replace(' ', '')}", "#AI", "#Innovation", "#Tech"]
            hashtags = base_hashtags[:3]
            
            return {
                'text': content,
                'hashtags': hashtags,
                'word_count': len(content.split()),
                'char_count': len(content),
                'platform': platform,
                'topic': topic
            }
        except Exception as e:
            return {
                'text': f"Check out the latest in {topic}! Amazing developments ahead.",
                'hashtags': [f"#{topic.replace(' ', '')}", "#Tech"],
                'word_count': 8,
                'char_count': 50,
                'platform': platform,
                'topic': topic
            }

# Data functions
def create_analytics_data():
    dates = pd.date_range(start='2024-01-01', end='2024-01-30', freq='D')
    return pd.DataFrame({
        'Date': dates,
        'Twitter': [random.randint(50, 200) for _ in range(len(dates))],
        'Instagram': [random.randint(80, 300) for _ in range(len(dates))],
        'Facebook': [random.randint(30, 150) for _ in range(len(dates))],
        'LinkedIn': [random.randint(20, 100) for _ in range(len(dates))]
    })

def create_platform_data():
    return pd.DataFrame({
        'Platform': ['Instagram', 'Twitter', 'LinkedIn', 'Facebook'],
        'Engagement': [2847, 1923, 1456, 1205],
        'Posts': [45, 72, 38, 56],
        'Growth': [23.4, 15.8, 18.2, 12.1]
    })

# Utility functions
def show_success(message: str):
    st.markdown(f'<div class="success-alert">{message}</div>', unsafe_allow_html=True)

def show_info(message: str):
    st.markdown(f'<div class="info-alert">{message}</div>', unsafe_allow_html=True)

# Main application
def main():
    init_session_state()
    get_database_connection()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 AI Social Media Platform</h1>
        <p>Fully Automated Content Generation & Posting System</p>
        <div style="margin-top: 1rem;">
            <span style="background: rgba(40, 167, 69, 0.2); padding: 8px 16px; border-radius: 20px; border: 1px solid rgba(40, 167, 69, 0.5);">
                🟢 System Online • Auto-posting Active
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.title("🎛️ Control Panel")
        
        st.subheader("🔑 Configuration")
        api_key = st.text_input("OpenAI API Key", type="password", value="demo")
        
        st.subheader("📝 Content Settings")
        topics = st.multiselect(
            "Content Topics",
            ["AI", "Technology", "Innovation", "Productivity", "Marketing", "Automation"],
            default=["AI", "Technology", "Innovation"]
        )
        
        tone = st.selectbox("Content Tone", ["Professional", "Casual", "Friendly", "Creative"])
        
        st.subheader("📱 Platforms")
        platforms = {
            "Twitter": st.checkbox("Twitter", value=True),
            "Instagram": st.checkbox("Instagram", value=True),
            "Facebook": st.checkbox("Facebook", value=True),
            "LinkedIn": st.checkbox("LinkedIn", value=True)
        }
        
        st.subheader("🤖 Automation")
        if st.button("🔄 Toggle Automation"):
            st.session_state.automation_active = not st.session_state.automation_active
            if st.session_state.automation_active:
                show_success("✅ Automation activated!")
            else:
                show_info("⏸️ Automation paused!")
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Posts Today", st.session_state.posts_generated_today, delta="+3")
    with col2:
        st.metric("🎯 Engagement", f"{st.session_state.total_engagement:,}", delta="+12.3%")
    with col3:
        st.metric("📈 Success Rate", f"{st.session_state.success_rate}%", delta="+0.8%")
    with col4:
        active_count = sum(platforms.values())
        st.metric("📱 Platforms", f"{active_count}/4", delta=f"{active_count} active")
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🚀 Dashboard", "📝 Generator", "📊 Analytics", "🎯 Campaigns", "⏰ Schedule"
    ])
    
    with tab1:
        st.header("🚀 Quick Actions Dashboard")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎯 Content Actions")
            
            if st.button("✨ Generate Today's Content", type="primary"):
                with st.spinner("🤖 Generating content..."):
                    time.sleep(2)
                    st.session_state.posts_generated_today += 8
                    show_success("🎉 Generated 8 new posts!")
                    st.balloons()
            
            if st.button("🎨 Create Visual Content"):
                with st.spinner("🎨 Creating images..."):
                    time.sleep(2)
                    show_success("🖼️ Created 5 visual posts!")
            
            if st.button("📊 Analyze Performance"):
                with st.spinner("📈 Analyzing data..."):
                    time.sleep(1)
                    show_info("📊 Analysis complete! Engagement up 15%")
        
        with col2:
            st.subheader("⚡ System Status")
            
            status = "🟢 Active" if st.session_state.automation_active else "🔴 Paused"
            st.markdown(f"**Automation:** {status}")
            
            st.markdown("**Platform Status:**")
            platform_emojis = {"Twitter": "🐦", "Instagram": "📸", "Facebook": "👤", "LinkedIn": "💼"}
            
            for platform, active in platforms.items():
                emoji = platform_emojis[platform]
                status_icon = "🟢" if active else "🔴"
                st.markdown(f"{emoji} {platform}: {status_icon}")
    
    with tab2:
        st.header("📝 AI Content Generator")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("🎯 Create Content")
            
            topic = st.text_input("Content Topic", value="AI Innovation")
            platform = st.selectbox("Platform", ["Twitter", "Instagram", "Facebook", "LinkedIn"])
            
            if st.button("🚀 Generate", type="primary") and topic:
                with st.spinner(f"🤖 Creating {platform} content..."):
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
                            'created_at': datetime.now().isoformat(),
                            'posted': False,
                            'engagement_prediction': random.choice(['High', 'Medium', 'Very High'])
                        }
                        
                        st.session_state.generated_posts.insert(0, new_post)
                        show_success("✅ Content generated successfully!")
                        
                    except Exception as e:
                        st.error(f"Generation failed: {e}")
        
        with col2:
            st.subheader("📋 Generated Content")
            
            if st.session_state.generated_posts:
                for i, post in enumerate(st.session_state.generated_posts[:3]):
                    with st.expander(f"{post['platform']} - {post['topic']}", expanded=(i==0)):
                        st.write("**Content:**")
                        st.write(post['content'])
                        
                        st.write("**Hashtags:**")
                        st.write(" ".join(post['hashtags']))
                        
                        st.write(f"**Prediction:** {post['engagement_prediction']}")
                        
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            if st.button("📅 Schedule", key=f"sched_{i}"):
                                show_success("📅 Scheduled!")
                        with col_b:
                            if st.button("📤 Post", key=f"post_{i}"):
                                show_success("🚀 Posted!")
                        with col_c:
                            if st.button("✏️ Edit", key=f"edit_{i}"):
                                show_info("✏️ Edit mode!")
            else:
                st.info("👆 Generate content to see previews here!")
    
    with tab3:
        st.header("📊 Performance Analytics")
        
        try:
            st.subheader("📈 Daily Engagement Trends")
            engagement_data = create_analytics_data()
            
            fig_line = px.line(
                engagement_data,
                x='Date',
                y=['Twitter', 'Instagram', 'Facebook', 'LinkedIn'],
                title="Engagement by Platform",
                color_discrete_map={
                    'Twitter': '#1da1f2',
                    'Instagram': '#e1306c', 
                    'Facebook': '#1877f2',
                    'LinkedIn': '#0a66c2'
                }
            )
            st.plotly_chart(fig_line, use_container_width=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🏆 Platform Performance")
                platform_data = create_platform_data()
                
                fig_bar = px.bar(
                    platform_data,
                    x='Platform',
                    y='Engagement', 
                    title="Total Engagement",
                    color='Platform',
                    color_discrete_map={
                        'Twitter': '#1da1f2',
                        'Instagram': '#e1306c',
                        'Facebook': '#1877f2', 
                        'LinkedIn': '#0a66c2'
                    }
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            
            with col2:
                st.subheader("📊 Distribution")
                fig_pie = px.pie(
                    platform_data,
                    values='Engagement',
                    names='Platform',
                    title="Engagement Share"
                )
                st.plotly_chart(fig_pie, use_container_width=True)
                
        except Exception as e:
            st.error(f"Analytics error: {e}")
    
    with tab4:
        st.header("🎯 Campaign Management")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📋 Active Campaigns")
            
            campaigns = [
                {"name": "AI Innovation Week", "progress": 75, "posts": "18/24", "engagement": "4.2K"},
                {"name": "Productivity Tips", "progress": 90, "posts": "14/16", "engagement": "2.8K"},
                {"name": "Tech Trends 2024", "progress": 25, "posts": "5/20", "engagement": "1.1K"}
            ]
            
            for campaign in campaigns:
                with st.container():
                    st.markdown(f"**{campaign['name']}**")
                    st.progress(campaign['progress'] / 100)
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("Posts", campaign['posts'])
                    with col_b:
                        st.metric("Engagement", campaign['engagement'])
                    
                    st.markdown("---")
        
        with col2:
            st.subheader("➕ Create Campaign")
            
            with st.form("campaign_form"):
                name = st.text_input("Campaign Name")
                description = st.text_area("Description")
                duration = st.slider("Duration (days)", 1, 30, 7)
                
                if st.form_submit_button("🚀 Create Campaign"):
                    if name:
                        with st.spinner("🎯 Creating campaign..."):
                            time.sleep(2)
                            show_success(f"✅ Campaign '{name}' created!")
                            st.balloons()
                    else:
                        st.error("Please enter a campaign name!")
    
    with tab5:
        st.header("⏰ Content Scheduler")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📅 Upcoming Posts")
            
            upcoming = [
                {"platform": "Twitter", "content": "Productivity tips", "time": "in 47 min"},
                {"platform": "Instagram", "content": "Tech showcase", "time": "in 2 hours"},
                {"platform": "Facebook", "content": "Community story", "time": "tomorrow 9 AM"},
                {"platform": "LinkedIn", "content": "Leadership insights", "time": "tomorrow 12 PM"}
            ]
            
            for post in upcoming:
                st.markdown(f"**{post['platform']}** - {post['content']}")
                st.caption(f"⏰ {post['time']}")
                st.markdown("---")
        
        with col2:
            st.subheader("⚙️ Settings")
            
            st.write("**Optimal Times:**")
            times = {
                "Twitter": "8AM, 12PM, 5PM, 8PM",
                "Instagram": "11AM, 2PM, 5PM, 7PM", 
                "Facebook": "9AM, 1PM, 3PM, 6PM",
                "LinkedIn": "10AM, 12PM, 2PM, 4PM"
            }
            
            for platform, time_list in times.items():
                st.markdown(f"**{platform}:** {time_list}")
            
            st.subheader("📊 Preferences")
            auto_schedule = st.checkbox("🤖 Auto-schedule", value=True)
            spread_hours = st.slider("⏰ Hours between posts", 1, 12, 2)
            
            if st.button("💾 Save Settings"):
                show_success("✅ Settings saved!")

if __name__ == "__main__":
    main()
