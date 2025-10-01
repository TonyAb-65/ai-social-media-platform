#!/usr/bin/env python3
"""
AI Social Media Platform - New Professional UI Design
Dark theme with modern dashboard layout
"""

import streamlit as st
import sqlite3
import json
import uuid
import random
from datetime import datetime, date
from typing import Dict, Optional
import pandas as pd
import plotly.graph_objects as go
import logging

# OpenAI Integration
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="Social Platform — Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Dark Theme CSS matching your design
st.markdown("""
<style>
    /* Import Inter font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Global styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Main container */
    .main {
        background-color: #0f1220;
        color: #e5e7eb;
    }
    
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 100%;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: rgba(21, 26, 45, 0.6);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    [data-testid="stSidebar"] .css-ng1t4o {
        background-color: transparent;
    }
    
    /* Card styling */
    .metric-card {
        background: #151a2d;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.05);
        box-shadow: 0 6px 24px rgba(0,0,0,.25), inset 0 1px 0 rgba(255,255,255,.02);
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: #9aa4b2;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-size: 1.875rem;
        font-weight: 600;
        color: #e5e7eb;
        margin-bottom: 0.25rem;
    }
    
    .metric-delta {
        font-size: 0.75rem;
        color: #22c55e;
    }
    
    /* Button styling */
    .stButton>button {
        background: #6ea8fe;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.2s;
    }
    
    .stButton>button:hover {
        background: #4e8ef6;
    }
    
    /* Input styling */
    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea,
    .stSelectbox>div>div>select {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        color: #e5e7eb;
    }
    
    /* Platform badges */
    .platform-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        color: white;
        margin-right: 0.5rem;
    }
    
    .badge-instagram { background: linear-gradient(135deg, #e4405f, #c13584); }
    .badge-tiktok { background: linear-gradient(135deg, #22c55e, #16a34a); }
    .badge-facebook { background: linear-gradient(135deg, #1877f2, #0e5fd8); }
    .badge-linkedin { background: linear-gradient(135deg, #0a66c2, #004182); }
    
    /* Status badges */
    .status-live {
        background: rgba(34, 197, 94, 0.2);
        color: #22c55e;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.75rem;
    }
    
    .status-learning {
        background: rgba(245, 158, 11, 0.2);
        color: #f59e0b;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.75rem;
    }
    
    .status-paused {
        background: rgba(255, 255, 255, 0.05);
        color: #9aa4b2;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.75rem;
    }
    
    /* Table styling */
    .stDataFrame {
        background: #151a2d;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        color: #e5e7eb;
    }
    
    /* Hide default streamlit styling */
    .css-1544g2n {
        padding: 0;
    }
    
    h1, h2, h3 {
        color: #e5e7eb;
    }
    
    /* Campaign card */
    .campaign-card {
        background: #151a2d;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.05);
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def init_session_state():
    """Initialize session state"""
    defaults = {
        'generated_posts': [],
        'api_calls_count': 0,
        'images_generated': 0,
        'current_view': 'Overview',
        'campaigns': [
            {
                'name': 'Summer Launch',
                'channels': ['Instagram', 'Facebook', 'TikTok'],
                'spend': 42300,
                'revenue': 132800,
                'roi': 214,
                'status': 'Live'
            },
            {
                'name': 'Creators Sprint',
                'channels': ['Instagram', 'TikTok'],
                'spend': 18000,
                'revenue': 39500,
                'roi': 119,
                'status': 'Learning'
            },
            {
                'name': 'B2B Retarget',
                'channels': ['LinkedIn', 'Facebook'],
                'spend': 8600,
                'revenue': 9400,
                'roi': 9,
                'status': 'Paused'
            }
        ]
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def get_database_connection():
    """Get database connection"""
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
                engagement_prediction TEXT,
                topic TEXT,
                generated_by TEXT,
                image_url TEXT,
                image_prompt_original TEXT,
                image_prompt_enhanced TEXT
            )
        ''')
        
        conn.commit()
        return conn
    except Exception as e:
        logger.error(f"Database error: {e}")
        return None

class PromptEngineer:
    """Professional DALL-E prompt engineering"""
    
    @staticmethod
    def enhance_prompt(user_input: str, platform: str) -> str:
        """Transform simple input into professional DALL-E prompt"""
        
        platform_styles = {
            'instagram': 'square 1:1 Instagram format, vibrant aesthetic, ultra-sharp 8K, professional photography, golden hour lighting',
            'tiktok': 'vertical 9:16 TikTok format, dynamic energy, trending style, mobile-optimized, engaging composition',
            'facebook': 'landscape format, warm inviting colors, natural soft lighting, professional HD quality',
            'linkedin': 'professional corporate format, sophisticated aesthetic, executive-level quality, business standard'
        }
        
        style = platform_styles.get(platform.lower(), platform_styles['instagram'])
        enhanced = f"{user_input}, {style}, cinematic depth, award-winning composition, professional color grading, masterpiece-level detail, photorealistic, commercial photography, publication-ready"
        
        return enhanced.strip()

class ContentGenerator:
    """AI-powered content generator"""
    
    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self.client = None
        
        if api_key and OPENAI_AVAILABLE:
            try:
                self.client = OpenAI(api_key=api_key)
                logger.info("OpenAI client initialized")
            except Exception as e:
                logger.error(f"OpenAI error: {e}")
                st.error(f"OpenAI initialization failed: {str(e)}")
    
    def generate_content(self, topic: str, platform: str, tone: str) -> Dict:
        """Generate text content"""
        
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": f"You are a {platform} content expert."},
                        {"role": "user", "content": f"Create a {tone} {platform} post about: {topic}. Include hashtags."}
                    ],
                    temperature=0.8,
                    max_tokens=300
                )
                
                return {
                    'text': response.choices[0].message.content,
                    'engagement_prediction': 'Very High',
                    'generated_by': 'OpenAI GPT-4'
                }
            except Exception as e:
                logger.error(f"Content generation error: {e}")
                st.error(f"OpenAI API error: {str(e)}")
        
        return {
            'text': f"Exploring {topic} and its transformative impact. What are your thoughts? #Innovation #Technology",
            'engagement_prediction': 'High',
            'generated_by': 'Template'
        }
    
    def generate_image(self, prompt: str, platform: str) -> Optional[Dict]:
        """Generate image with DALL-E"""
        
        if not self.client:
            st.error("OpenAI client not initialized. Check your API key.")
            return None
        
        try:
            enhanced_prompt = PromptEngineer.enhance_prompt(prompt, platform)
            
            with st.expander("🔍 Prompt Engineering", expanded=True):
                st.info(f"**Original:** {prompt}")
                st.success(f"**Enhanced:** {enhanced_prompt}")
            
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=enhanced_prompt,
                size="1024x1024",
                quality="standard",
                n=1
            )
            
            return {
                'url': response.data[0].url,
                'original_prompt': prompt,
                'enhanced_prompt': enhanced_prompt
            }
        except Exception as e:
            st.error(f"Image generation failed: {str(e)}")
            logger.error(f"DALL-E error: {e}")
            return None

def create_metric_card(label: str, value: str, delta: str):
    """Create a metric card matching the design"""
    return f"""
    <div class="metric-card">
        <p class="metric-label">{label}</p>
        <p class="metric-value">{value}</p>
        <p class="metric-delta">{delta}</p>
    </div>
    """

def main():
    """Main application"""
    init_session_state()
    conn = get_database_connection()
    
    # Sidebar Navigation (matching your design)
    with st.sidebar:
        # Logo and workspace
        st.markdown("""
        <div style="padding: 1.5rem 1rem; border-bottom: 1px solid rgba(255,255,255,0.05);">
            <div style="display: flex; align-items: center; gap: 0.75rem;">
                <div style="width: 36px; height: 36px; background: rgba(110, 168, 254, 0.2); border: 1px solid rgba(110, 168, 254, 0.3); border-radius: 8px; display: grid; place-items: center;">
                    <span style="font-size: 1.2rem;">📊</span>
                </div>
                <div>
                    <p style="font-weight: 600; margin: 0; color: #e5e7eb;">Social Platform</p>
                    <p style="font-size: 0.75rem; margin: 0; color: #9aa4b2;">Pro workspace</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation
        st.markdown("<br>", unsafe_allow_html=True)
        
        view = st.radio(
            "Navigation",
            ["📊 Overview", "🎯 Campaigns", "📅 Calendar", "✏️ Content Lab", "🖼️ Assets", "📥 Inbox", "📈 Insights"],
            label_visibility="collapsed"
        )
        st.session_state.current_view = view
        
        # API Configuration
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("### 🔑 API Configuration")
        
        api_key = st.text_input("OpenAI API Key", type="password", help="Enter your API key")
        
        if api_key and OPENAI_AVAILABLE:
            st.success("✅ API Active")
        else:
            st.warning("⚠️ No API Key")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("API Calls", st.session_state.api_calls_count)
        with col2:
            st.metric("Images", st.session_state.images_generated)
        
        # Workspace info
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="padding: 1rem; border-top: 1px solid rgba(255,255,255,0.05); font-size: 0.875rem; color: #9aa4b2;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span>Workspace: <span style="color: #e5e7eb;">StoreHub</span></span>
                <button style="padding: 0.25rem 0.5rem; background: rgba(255,255,255,0.05); border: none; border-radius: 4px; color: #e5e7eb; cursor: pointer;">Switch</button>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Main Content Area
    
    # Header with search and action button
    col1, col2, col3 = st.columns([2, 3, 2])
    with col1:
        st.markdown(f"# {st.session_state.current_view}")
    with col3:
        if st.button("➕ New Campaign", use_container_width=True):
            st.session_state.show_composer = True
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Route to selected view
    view = st.session_state.current_view
    
    # VIEW: Overview
    if "Overview" in view:
        # KPI Cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(create_metric_card("Reach", "1.24M", "+8.2% WoW"), unsafe_allow_html=True)
        with col2:
            st.markdown(create_metric_card("Engagements", "86,420", "+5.1% WoW"), unsafe_allow_html=True)
        with col3:
            st.markdown(create_metric_card("Revenue", "$128,940", "AOV −2.4%"), unsafe_allow_html=True)
        with col4:
            st.markdown(create_metric_card("ROI", "+212%", "↑ efficient"), unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Charts
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### Reach & Engagement")
            
            # Create line chart
            fig = go.Figure()
            
            weeks = [f'W{i+1}' for i in range(12)]
            reach_data = [82000, 95000, 93000, 110000, 120000, 125000, 119000, 138000, 142000, 150000, 158000, 165000]
            engagement_data = [4.2, 5.6, 5.1, 6.3, 7.1, 6.2, 6.9, 7.8, 8.1, 8.6, 8.2, 8.9]
            
            fig.add_trace(go.Scatter(
                x=weeks, y=reach_data,
                name='Reach',
                line=dict(color='#6ea8fe', width=2),
                fill='tonexty',
                fillcolor='rgba(110, 168, 254, 0.2)'
            ))
            
            fig.add_trace(go.Scatter(
                x=weeks, y=engagement_data,
                name='Engagement %',
                line=dict(color='#22c55e', width=2),
                yaxis='y2'
            ))
            
            fig.update_layout(
                paper_bgcolor='#151a2d',
                plot_bgcolor='#151a2d',
                font=dict(color='#9aa4b2'),
                xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                yaxis2=dict(overlaying='y', side='right', gridcolor='rgba(255,255,255,0.05)'),
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                height=300,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### ROI by Channel")
            
            fig = go.Figure(data=[go.Pie(
                labels=['Instagram', 'TikTok', 'Facebook', 'LinkedIn'],
                values=[38, 28, 22, 12],
                hole=0.68,
                marker_colors=['#6ea8fe', '#22c55e', '#f59e0b', '#ef4444']
            )])
            
            fig.update_layout(
                paper_bgcolor='#151a2d',
                plot_bgcolor='#151a2d',
                font=dict(color='#9aa4b2'),
                showlegend=False,
                height=300,
                margin=dict(l=20, r=20, t=20, b=20)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("""
            <div style="margin-top: 1rem; font-size: 0.875rem; color: #9aa4b2;">
                <div style="display: flex; justify-between; margin-bottom: 0.5rem;">
                    <span><span style="display: inline-block; width: 8px; height: 8px; background: #6ea8fe; border-radius: 50%; margin-right: 0.5rem;"></span>Instagram</span>
                    <span style="color: #e5e7eb;">+238%</span>
                </div>
                <div style="display: flex; justify-between; margin-bottom: 0.5rem;">
                    <span><span style="display: inline-block; width: 8px; height: 8px; background: #22c55e; border-radius: 50%; margin-right: 0.5rem;"></span>TikTok</span>
                    <span style="color: #e5e7eb;">+185%</span>
                </div>
                <div style="display: flex; justify-between; margin-bottom: 0.5rem;">
                    <span><span style="display: inline-block; width: 8px; height: 8px; background: #f59e0b; border-radius: 50%; margin-right: 0.5rem;"></span>Facebook</span>
                    <span style="color: #e5e7eb;">+142%</span>
                </div>
                <div style="display: flex; justify-between;">
                    <span><span style="display: inline-block; width: 8px; height: 8px; background: #ef4444; border-radius: 50%; margin-right: 0.5rem;"></span>LinkedIn</span>
                    <span style="color: #e5e7eb;">+96%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Top Posts
        st.markdown("### Top Posts (Last 30d)")
        
        top_posts = [
            {"title": "Unboxing Reel: Summer drop", "engagement": "8.4%", "saves": "1.2k", "img": "https://images.unsplash.com/photo-1514512526985-4d1b06a38a3a?w=400"},
            {"title": "Carousel: Before/After fit", "engagement": "6.9%", "ctr": "2.1%", "img": "https://images.unsplash.com/photo-1552374196-c4e7ffc6e126?w=400"},
            {"title": "UGC video: How it's made", "engagement": "6.2%", "roas": "3.4", "img": "https://images.unsplash.com/photo-1520975922284-5f573bdb7356?w=400"}
        ]
        
        for post in top_posts:
            col1, col2, col3 = st.columns([1, 3, 1])
            with col1:
                st.image(post['img'], use_column_width=True)
            with col2:
                st.markdown(f"**{post['title']}**")
                metrics = [f"{k}: {v}" for k, v in post.items() if k not in ['title', 'img']]
                st.caption(" · ".join(metrics))
            with col3:
                st.button("Repurpose", key=f"rep_{post['title']}")
    
    # VIEW: Campaigns
    elif "Campaigns" in view:
        st.markdown("### Active Campaigns")
        
        # Create DataFrame
        df = pd.DataFrame(st.session_state.campaigns)
        
        # Display campaigns in cards
        for campaign in st.session_state.campaigns:
            st.markdown(f'<div class="campaign-card">', unsafe_allow_html=True)
            
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            
            with col1:
                st.markdown(f"**{campaign['name']}**")
                channels = ", ".join([ch[:2].upper() for ch in campaign['channels']])
                st.caption(channels)
            
            with col2:
                st.metric("Spend", f"${campaign['spend']:,}")
            
            with col3:
                st.metric("Revenue", f"${campaign['revenue']:,}")
            
            with col4:
                roi_color = '#22c55e' if campaign['roi'] > 100 else '#f59e0b'
                st.markdown(f"<div style='color: {roi_color}; font-size: 1.5rem; font-weight: 600;'>+{campaign['roi']}%</div>", unsafe_allow_html=True)
                st.caption("ROI")
            
            with col5:
                status_class = f"status-{campaign['status'].lower()}"
                st.markdown(f'<span class="{status_class}">{campaign["status"]}</span>', unsafe_allow_html=True)
            
            with col6:
                st.button("Edit", key=f"edit_{campaign['name']}")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # VIEW: Content Lab
    elif "Content Lab" in view:
        st.markdown("### Compose Post")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("**Caption**")
            caption = st.text_area("", placeholder="Write something...", height=150, label_visibility="collapsed")
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.markdown("**Networks**")
                instagram = st.checkbox("Instagram", value=True)
                facebook = st.checkbox("Facebook", value=True)
                tiktok = st.checkbox("TikTok")
                linkedin = st.checkbox("LinkedIn")
            
            with col_b:
                st.markdown("**Topic & Platform**")
                topic = st.text_input("Topic", placeholder="e.g., Product Launch")
                platform = st.selectbox("Platform", ["Instagram", "TikTok", "Facebook", "LinkedIn"])
            
            st.markdown("**Image Generation**")
            generate_image = st.checkbox("Generate AI Image with DALL-E 3")
            
            if generate_image:
                image_prompt = st.text_area("Image Description", placeholder="Describe the image...", height=80)
            
            col_btn1, col_btn2, col_btn3 = st.columns(3)
            
            with col_btn1:
                if st.button("🤖 AI Caption", use_container_width=True):
                    if api_key and topic:
                        with st.spinner("Generating captions..."):
                            generator = ContentGenerator(api_key)
                            content = generator.generate_content(topic, platform, "playful")
                            st.session_state.generated_caption = content['text']
                            st.success("Caption generated!")
                            st.rerun()
            
            with col_btn2:
                if st.button("📅 Schedule", type="primary", use_container_width=True):
                    if caption or st.session_state.get('generated_caption'):
                        text = caption or st.session_state.get('generated_caption', '')
                        
                        # Generate image if requested
                        image_url = None
                        if generate_image and api_key and image_prompt:
                            with st.spinner("Generating image..."):
                                generator = ContentGenerator(api_key)
                                image_data = generator.generate_image(image_prompt, platform)
                                if image_data:
                                    image_url = image_data['url']
                                    st.session_state.images_generated += 1
                                    st.session_state.api_calls_count += 1
                        
                        post = {
                            'id': str(uuid.uuid4()),
                            'platform': platform,
                            'topic': topic,
                            'content': text,
                            'engagement_prediction': 'High',
                            'generated_by': 'User Created',
                            'image_url': image_url,
                            'created_at': datetime.now().isoformat()
                        }
                        
                        st.session_state.generated_posts.insert(0, post)
                        
                        if conn:
                            cursor = conn.cursor()
                            cursor.execute('INSERT INTO posts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                                         (post['id'], post['platform'], post['content'], '[]', 
                                          post['created_at'], post['engagement_prediction'], 
                                          post['topic'], post['generated_by'], post.get('image_url'),
                                          None, None))
                            conn.commit()
                        
                        st.success("Post scheduled!")
                        st.balloons()
                    else:
                        st.error("Enter caption or generate one")
            
            with col_btn3:
                if st.button("Cancel", use_container_width=True):
                    st.rerun()
        
        with col2:
            st.markdown("**Preview**")
            
            if st.session_state.get('generated_caption'):
                st.info(st.session_state.generated_caption)
            
            st.markdown("**Media**")
            st.markdown("""
            <div style="border: 2px dashed rgba(255,255,255,0.1); border-radius: 8px; padding: 2rem; text-align: center; background: rgba(255,255,255,0.05);">
                <p style="color: #9aa4b2; margin: 0;">Drag & drop files</p>
                <button style="margin-top: 0.5rem; padding: 0.5rem 1rem; background: rgba(255,255,255,0.1); border: none; border-radius: 4px; color: #e5e7eb; cursor: pointer;">Browse</button>
            </div>
            """, unsafe_allow_html=True)
    
    # VIEW: Assets
    elif "Assets" in view:
        st.markdown("### Generated Images")
        
        images = [p for p in st.session_state.generated_posts if p.get('image_url')]
        
        if images:
            cols = st.columns(3)
            for idx, post in enumerate(images):
                with cols[idx % 3]:
                    st.image(post['image_url'], use_column_width=True)
                    st.caption(f"{post['platform']} - {post.get('topic', 'Untitled')}")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.button("View", key=f"view_{post['id']}")
                    with col_b:
                        st.button("Regenerate", key=f"regen_{post['id']}")
        else:
            st.info("No images generated yet. Create content with images in Content Lab!")
    
    # VIEW: Insights
    elif "Insights" in view:
        st.markdown("### Performance Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Platform Breakdown")
            platform_data = pd.DataFrame({
                'Platform': ['Instagram', 'TikTok', 'Facebook', 'LinkedIn'],
                'Engagement': [38420, 28350, 15280, 8370],
                'Posts': [156, 203, 89, 45]
            })
            st.dataframe(platform_data, use_container_width=True)
        
        with col2:
            st.markdown("#### Best Performing")
            st.success("Instagram Reels have 2.3x higher engagement")
            st.info("Post between 11AM-2PM for optimal reach")
            st.warning("LinkedIn engagement down 12% this month")
    
    # Footer
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; padding: 2rem; border-top: 1px solid rgba(255,255,255,0.05); color: #9aa4b2; font-size: 0.875rem;">
        <p>Social Platform Dashboard v1.0 | Powered by OpenAI GPT-4 & DALL-E 3</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
