#!/usr/bin/env python3
"""
AI Social Media Platform - Fixed Version
Issues fixed: New Campaign button, text visibility, image generation
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

# Professional Dark Theme CSS - FIXED TEXT VISIBILITY
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main {
        background-color: #0f1220;
        color: #e5e7eb;
    }
    
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 100%;
    }
    
    [data-testid="stSidebar"] {
        background-color: rgba(21, 26, 45, 0.6);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* FIX 2: Make input text WHITE and clearly visible */
    .stTextInput input,
    .stTextArea textarea,
    .stSelectbox select,
    input[type="text"],
    input[type="password"],
    textarea {
        background: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px !important;
        color: #ffffff !important;
        padding: 0.75rem !important;
    }
    
    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder {
        color: #9aa4b2 !important;
    }
    
    .stTextInput input:focus,
    .stTextArea textarea:focus,
    .stSelectbox select:focus {
        border-color: #6ea8fe !important;
        outline: none !important;
    }
    
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
    
    .campaign-card {
        background: #151a2d;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.05);
        margin-bottom: 1rem;
    }
    
    h1, h2, h3 {
        color: #e5e7eb;
    }
    
    /* Checkbox styling */
    .stCheckbox label {
        color: #e5e7eb !important;
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
        'show_new_campaign': False,  # FIX 1: Add state for new campaign modal
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
    """Professional DALL-E prompt engineering - FIX 3"""
    
    @staticmethod
    def enhance_prompt(user_input: str, platform: str) -> str:
        """Transform simple input into professional DALL-E prompt"""
        
        # Enhanced platform-specific styles
        platform_styles = {
            'instagram': 'professional Instagram post, square 1:1 aspect ratio, vibrant colors, eye-catching composition, high-quality photography style, perfect lighting, trending aesthetic, Instagram-worthy, ultra-detailed, 8K resolution',
            'tiktok': 'dynamic TikTok content style, vertical 9:16 format, energetic composition, mobile-optimized, trending visual style, attention-grabbing, high contrast, vibrant colors, professional quality',
            'facebook': 'Facebook post aesthetic, landscape format, warm and inviting atmosphere, community-friendly, professional photography, natural lighting, engaging composition, HD quality',
            'linkedin': 'professional LinkedIn content, corporate aesthetic, business-appropriate, sophisticated composition, executive-level quality, premium look, clean modern design, professional photography'
        }
        
        style = platform_styles.get(platform.lower(), platform_styles['instagram'])
        
        # Build comprehensive professional prompt
        enhanced = f"""
{user_input}, 
{style}, 
studio lighting with soft shadows, 
professional color grading and color balance, 
cinematic depth of field with bokeh effect, 
award-winning composition following rule of thirds, 
masterpiece-level attention to detail, 
photorealistic rendering with perfect textures, 
commercial photography standard, 
trending on Behance and Dribbble, 
publication-ready quality, 
sharp focus with crystal clarity, 
professionally edited, 
magazine cover quality
""".strip()
        
        logger.info(f"Enhanced prompt created: {enhanced[:100]}...")
        return enhanced

class ContentGenerator:
    """AI-powered content generator - FIX 3"""
    
    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self.client = None
        
        if api_key and OPENAI_AVAILABLE:
            try:
                self.client = OpenAI(api_key=api_key)
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"OpenAI initialization error: {e}")
                st.error(f"OpenAI initialization failed: {str(e)}")
    
    def generate_content(self, topic: str, platform: str, tone: str) -> Dict:
        """Generate text content"""
        
        if self.client:
            try:
                logger.info(f"Generating content for {platform} about {topic}")
                
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": f"You are an expert {platform} content creator specializing in {tone} content."},
                        {"role": "user", "content": f"Create a compelling {platform} post about: {topic}. Make it {tone} in tone. Include relevant hashtags."}
                    ],
                    temperature=0.8,
                    max_tokens=300
                )
                
                logger.info("Content generated successfully with OpenAI")
                
                return {
                    'text': response.choices[0].message.content,
                    'engagement_prediction': 'Very High',
                    'generated_by': 'OpenAI GPT-4'
                }
            except Exception as e:
                logger.error(f"OpenAI content generation error: {e}")
                st.error(f"Content generation failed: {str(e)}")
        
        logger.info("Using template fallback for content generation")
        return {
            'text': f"Exploring {topic} and its transformative impact. What are your thoughts? #Innovation #Technology #Trending",
            'engagement_prediction': 'High',
            'generated_by': 'Template'
        }
    
    def generate_image(self, prompt: str, platform: str) -> Optional[Dict]:
        """Generate image with DALL-E - FIX 3: Enhanced with better error handling"""
        
        if not self.client:
            error_msg = "OpenAI client not initialized. Please check your API key."
            st.error(error_msg)
            logger.error(error_msg)
            return None
        
        if not prompt or not prompt.strip():
            error_msg = "Image prompt cannot be empty."
            st.error(error_msg)
            logger.error(error_msg)
            return None
        
        try:
            logger.info(f"Starting image generation for platform: {platform}")
            logger.info(f"Original prompt: {prompt}")
            
            # Enhance prompt professionally
            enhanced_prompt = PromptEngineer.enhance_prompt(prompt, platform)
            logger.info(f"Enhanced prompt created: {enhanced_prompt[:200]}...")
            
            # Show prompt enhancement to user
            with st.expander("🔍 Prompt Engineering Details", expanded=True):
                st.markdown("**Your Original Input:**")
                st.info(prompt)
                st.markdown("**AI-Enhanced Professional Prompt:**")
                st.success(enhanced_prompt)
                st.caption("This professional prompt maximizes image quality and relevance.")
            
            # Show progress
            with st.spinner("🎨 Generating high-quality image with DALL-E 3... This may take 10-20 seconds..."):
                logger.info("Calling DALL-E 3 API...")
                
                response = self.client.images.generate(
                    model="dall-e-3",
                    prompt=enhanced_prompt,
                    size="1024x1024",
                    quality="standard",
                    n=1
                )
                
                image_url = response.data[0].url
                logger.info(f"Image generated successfully: {image_url}")
                
                st.success("✅ Image generated successfully!")
                
                return {
                    'url': image_url,
                    'original_prompt': prompt,
                    'enhanced_prompt': enhanced_prompt
                }
                
        except Exception as e:
            error_msg = f"DALL-E image generation failed: {str(e)}"
            st.error(error_msg)
            logger.error(f"DALL-E error details: {e}")
            
            # Show helpful error messages
            if "api_key" in str(e).lower():
                st.warning("⚠️ API key issue. Please verify your OpenAI API key is valid and has access to DALL-E 3.")
            elif "billing" in str(e).lower():
                st.warning("⚠️ Billing issue. Please check your OpenAI account has available credits.")
            elif "content_policy" in str(e).lower():
                st.warning("⚠️ Content policy violation. Please adjust your image description.")
            
            return None

def create_metric_card(label: str, value: str, delta: str):
    """Create a metric card"""
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
    
    # Sidebar Navigation
    with st.sidebar:
        st.markdown("""
        <div style="padding: 1.5rem 1rem; border-bottom: 1px solid rgba(255,255,255,0.05);">
            <div style="display: flex; align-items: center; gap: 0.75rem;">
                <div style="width: 36px; height: 36px; background: rgba(110, 168, 254, 0.2); border: 1px solid rgba(110, 168, 254, 0.3); border-radius: 8px; display: grid; place-items-center;">
                    <span style="font-size: 1.2rem;">📊</span>
                </div>
                <div>
                    <p style="font-weight: 600; margin: 0; color: #e5e7eb;">Social Platform</p>
                    <p style="font-size: 0.75rem; margin: 0; color: #9aa4b2;">Pro workspace</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        view = st.radio(
            "Navigation",
            ["📊 Overview", "🎯 Campaigns", "📅 Calendar", "✏️ Content Lab", "🖼️ Assets", "📥 Inbox", "📈 Insights"],
            label_visibility="collapsed"
        )
        st.session_state.current_view = view
        
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
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="padding: 1rem; border-top: 1px solid rgba(255,255,255,0.05); font-size: 0.875rem; color: #9aa4b2;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span>Workspace: <span style="color: #e5e7eb;">StoreHub</span></span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Header with New Campaign button - FIX 1
    col1, col2, col3 = st.columns([2, 3, 2])
    with col1:
        st.markdown(f"# {st.session_state.current_view}")
    with col3:
        if st.button("➕ New Campaign", use_container_width=True, type="primary"):
            st.session_state.show_new_campaign = True
            st.session_state.current_view = "🎯 Campaigns"
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Route to views
    view = st.session_state.current_view
    
    # VIEW: Overview
    if "Overview" in view:
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
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### Reach & Engagement")
            
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
    
    # VIEW: Campaigns - FIX 1: Add new campaign form
    elif "Campaigns" in view:
        st.markdown("### Campaigns")
        
        # Show new campaign form if button was clicked
        if st.session_state.get('show_new_campaign', False):
            st.markdown("#### Create New Campaign")
            
            with st.form("new_campaign_form"):
                campaign_name = st.text_input("Campaign Name", placeholder="e.g., Holiday Sale 2025")
                
                col1, col2 = st.columns(2)
                with col1:
                    budget = st.number_input("Budget ($)", min_value=0, value=5000, step=500)
                with col2:
                    duration = st.number_input("Duration (days)", min_value=1, value=30)
                
                channels = st.multiselect(
                    "Select Channels",
                    ["Instagram", "TikTok", "Facebook", "LinkedIn"],
                    default=["Instagram"]
                )
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.form_submit_button("Create Campaign", type="primary", use_container_width=True):
                        if campaign_name and channels:
                            new_campaign = {
                                'name': campaign_name,
                                'channels': channels,
                                'spend': 0,
                                'revenue': 0,
                                'roi': 0,
                                'status': 'Active'
                            }
                            st.session_state.campaigns.append(new_campaign)
                            st.session_state.show_new_campaign = False
                            st.success(f"Campaign '{campaign_name}' created!")
                            st.rerun()
                        else:
                            st.error("Please fill in all fields")
                
                with col_b:
                    if st.form_submit_button("Cancel", use_container_width=True):
                        st.session_state.show_new_campaign = False
                        st.rerun()
            
            st.markdown("---")
        
        # Display existing campaigns
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
    
    # VIEW: Content Lab - FIX 3: Enhanced image generation
    elif "Content Lab" in view:
        st.markdown("### Compose Post")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("**Caption**")
            caption = st.text_area("", placeholder="Write something engaging...", height=150, label_visibility="collapsed", key="caption_input")
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.markdown("**Networks**")
                instagram = st.checkbox("Instagram", value=True, key="net_ig")
                facebook = st.checkbox("Facebook", value=True, key="net_fb")
                tiktok = st.checkbox("TikTok", key="net_tt")
                linkedin = st.checkbox("LinkedIn", key="net_li")
            
            with col_b:
                st.markdown("**Topic & Platform**")
                topic = st.text_input("Topic", placeholder="e.g., Product Launch", key="topic_input")
                platform = st.selectbox("Platform", ["Instagram", "TikTok", "Facebook", "LinkedIn"], key="platform_select")
            
            st.markdown("**AI Image Generation**")
            generate_image = st.checkbox("Generate AI Image with DALL-E 3", key="gen_image_check")
            
            image_prompt = None
            if generate_image:
                st.info("💡 Describe what you want to see. AI will create a professional prompt automatically.")
                image_prompt = st.text_area(
                    "Image Description", 
                    placeholder="Examples:\n• Modern office workspace with laptop\n• Product photography on white background\n• Team collaboration in creative space\n• Abstract technology concept art",
                    height=100,
                    key="image_prompt_input"
                )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            col_btn1, col_btn2, col_btn3 = st.columns(3)
            
            with col_btn1:
                if st.button("🤖 AI Caption", use_container_width=True, key="ai_caption_btn"):
                    if not api_key:
                        st.error("Please enter your OpenAI API key in the sidebar")
                    elif not topic:
                        st.error("Please enter a topic first")
                    else:
                        with st.spinner("Generating caption with GPT-4..."):
                            generator = ContentGenerator(api_key)
                            content = generator.generate_content(topic, platform, "engaging")
                            st.session_state.generated_caption = content['text']
                            st.success("Caption generated!")
                            st.rerun()
            
            with col_btn2:
                if st.button("📅 Generate & Schedule", type="primary", use_container_width=True, key="schedule_btn"):
                    if not (caption or st.session_state.get('generated_caption')):
                        st.error("Please write or generate a caption first")
                    elif not topic:
                        st.error("Please enter a topic")
                    else:
                        text = caption or st.session_state.get('generated_caption', '')
                        
                        # Generate image if requested - FIX 3
                        image_url = None
                        if generate_image:
                            if not api_key:
                                st.error("Please enter your OpenAI API key in the sidebar to generate images")
                            elif not image_prompt or not image_prompt.strip():
                                st.error("Please enter an image description")
                            else:
                                st.info("🎨 Starting AI image generation with DALL-E 3...")
                                generator = ContentGenerator(api_key)
                                image_data = generator.generate_image(image_prompt.strip(), platform)
                                
                                if image_data:
                                    image_url = image_data['url']
                                    st.session_state.images_generated += 1
                                    st.session_state.api_calls_count += 1
                                    st.success("Image generated successfully!")
                                else:
                                    st.warning("Image generation failed, but post will be created without image")
                        
                        # Create post
                        post = {
                            'id': str(uuid.uuid4()),
                            'platform': platform,
                            'topic': topic,
                            'content': text,
                            'engagement_prediction': 'High',
                            'generated_by': 'User Created',
                            'image_url': image_url,
                            'image_prompt_original': image_prompt if image_prompt else None,
                            'created_at': datetime.now().isoformat()
                        }
                        
                        st.session_state.generated_posts.insert(0, post)
                        
                        if conn:
                            cursor = conn.cursor()
                            cursor.execute('INSERT INTO posts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                                         (post['id'], post['platform'], post['content'], '[]', 
                                          post['created_at'], post['engagement_prediction'], 
                                          post['topic'], post['generated_by'], post.get('image_url'),
                                          post.get('image_prompt_original'), None))
                            conn.commit()
                        
                        st.success("Post scheduled successfully!")
                        st.balloons()
                        
                        # Clear form
                        if 'generated_caption' in st.session_state:
                            del st.session_state.generated_caption
                        
                        st.rerun()
            
            with col_btn3:
                if st.button("Clear", use_container_width=True, key="clear_btn"):
                    if 'generated_caption' in st.session_state:
                        del st.session_state.generated_caption
                    st.rerun()
        
        with col2:
            st.markdown("**Preview**")
            
            if st.session_state.get('generated_caption'):
                st.success("AI Generated Caption:")
                st.write(st.session_state.generated_caption)
            
            st.markdown("**Tips for Images**")
            st.info("""
            - Be specific about what you want
            - Mention style, colors, mood
            - Describe composition clearly
            - Examples work best
            """)
    
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
                    
                    if post.get('image_prompt_original'):
                        with st.expander("View Details"):
                            st.text(f"Original: {post['image_prompt_original']}")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.button("View Full", key=f"view_{post['id']}")
                    with col_b:
                        st.button("Download", key=f"dl_{post['id']}")
        else:
            st.info("No images generated yet. Go to Content Lab and generate images with DALL-E 3!")
    
    # Footer
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; padding: 2rem; border-top: 1px solid rgba(255,255,255,0.05); color: #9aa4b2; font-size: 0.875rem;">
        <p>Social Platform Dashboard v1.1 | Powered by OpenAI GPT-4 & DALL-E 3</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
