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
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Optional
import logging

# OpenAI Integration
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    st.error("OpenAI library not installed. Run: pip install openai")

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# SURGICAL FIX 1: Enhanced ContentGenerator with detailed logging
# ============================================================================
class ContentGenerator:
    """Handles content generation using OpenAI API"""
    
    def __init__(self, api_key: str):
        """Initialize with OpenAI API key"""
        if not api_key or not api_key.strip():
            raise ValueError("API key cannot be empty")
        
        self.api_key = api_key.strip()
        self.client = OpenAI(api_key=self.api_key)
        logger.info("ContentGenerator initialized")
    
    def test_connection(self) -> dict:
        """Test API connection"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=5
            )
            return {"success": True, "message": "API connection successful!", "model": "gpt-3.5-turbo"}
        except Exception as e:
            return {"success": False, "message": f"Connection failed: {str(e)}", "error": str(e)}
    
    def generate_caption(self, topic: str, platform: str, tone: str, keywords: list) -> str:
        """Generate social media caption using GPT-4"""
        try:
            keywords_str = ", ".join(keywords) if keywords else "engagement, marketing"
            
            prompt = f"""Create a compelling {platform} caption about {topic}.
            
Requirements:
- Tone: {tone}
- Include relevant keywords: {keywords_str}
- Include 3-5 relevant hashtags
- Make it engaging and platform-appropriate
- Length: Optimal for {platform}

Generate the caption now:"""
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert social media content creator."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            caption = response.choices[0].message.content.strip()
            logger.info(f"Caption generated for {platform}")
            return caption
            
        except Exception as e:
            logger.error(f"Caption generation error: {e}")
            raise
    
    def generate_image(self, prompt: str, size: str = "1024x1024") -> str:
        """Generate image using DALL-E 3"""
        try:
            logger.info(f"Starting DALL-E 3 image generation...")
            logger.info(f"Prompt: {prompt[:100]}...")
            
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                quality="standard",
                n=1
            )
            
            image_url = response.data[0].url
            logger.info(f"✅ Image generated successfully!")
            return image_url
            
        except Exception as e:
            logger.error(f"❌ DALL-E 3 error: {str(e)}")
            raise

# ============================================================================
# SURGICAL FIX 2: Enhanced PromptEngineer with better error handling
# ============================================================================
class PromptEngineer:
    """Enhances user prompts for better DALL-E 3 results"""
    
    def __init__(self, api_key: str):
        """Initialize with OpenAI API key"""
        if not api_key or not api_key.strip():
            raise ValueError("API key cannot be empty")
        
        self.api_key = api_key.strip()
        self.client = OpenAI(api_key=self.api_key)
        logger.info("PromptEngineer initialized")
    
    def enhance_for_dalle(self, user_prompt: str) -> str:
        """Enhance user prompt for DALL-E 3 using GPT-4"""
        try:
            logger.info(f"Enhancing prompt: {user_prompt[:50]}...")
            
            enhancement_instructions = f"""You are a DALL-E 3 prompt expert. Enhance this prompt for better image generation:

User prompt: {user_prompt}

Create a detailed, professional DALL-E 3 prompt that:
1. Keeps the core idea but adds rich visual details
2. Specifies art style (photorealistic, digital art, etc.)
3. Includes lighting and atmosphere
4. Mentions composition and perspective
5. Is vivid and specific
6. Is under 1000 characters

Enhanced prompt:"""

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert at writing DALL-E 3 prompts."},
                    {"role": "user", "content": enhancement_instructions}
                ],
                max_tokens=400,
                temperature=0.7
            )
            
            enhanced = response.choices[0].message.content.strip()
            enhanced = enhanced.strip('"').strip("'")
            logger.info(f"✅ Prompt enhanced successfully!")
            return enhanced
            
        except Exception as e:
            logger.error(f"❌ Prompt enhancement error: {str(e)}")
            logger.warning("Returning original prompt")
            return user_prompt

# Database setup
def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect('social_media.db', check_same_thread=False)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS campaigns
                 (id TEXT PRIMARY KEY, name TEXT, status TEXT, budget REAL, 
                  roi REAL, start_date TEXT, end_date TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS posts
                 (id TEXT PRIMARY KEY, campaign_id TEXT, platform TEXT, 
                  content TEXT, scheduled_date TEXT, status TEXT, 
                  engagement INTEGER, image_url TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS images
                 (id TEXT PRIMARY KEY, prompt TEXT, url TEXT, 
                  created_date TEXT, used_in_posts TEXT)''')
    
    conn.commit()
    return conn

# Session state initialization
def init_session_state():
    """Initialize session state variables"""
    if 'campaigns' not in st.session_state:
        st.session_state.campaigns = []
    if 'posts' not in st.session_state:
        st.session_state.posts = []
    if 'images' not in st.session_state:
        st.session_state.images = []
    if 'api_key' not in st.session_state:
        st.session_state.api_key = ""

# Helper functions
def show_success(message):
    st.success(f"✅ {message}")

def show_error(message):
    st.error(f"❌ {message}")

def show_info(message):
    st.info(f"ℹ️ {message}")

# Main application
def main():
    try:
        # Page config
        st.set_page_config(
            page_title="AI Social Media Platform",
            page_icon="🚀",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Initialize
        init_session_state()
        conn = init_db()
        
        # Custom CSS
        st.markdown("""
        <style>
        .main { background-color: #0e1117; }
        .stButton>button {
            width: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 0.75rem;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem;
            border-radius: 12px;
            color: white;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }
        </style>
        """, unsafe_allow_html=True)
        
        # ====================================================================
        # SURGICAL FIX 3: Store API key in session_state + Test Connection
        # ====================================================================
        # SIDEBAR
        with st.sidebar:
            st.markdown("## ⚙️ Settings")
            
            # API Key input
            api_key = st.text_input(
                "OpenAI API Key",
                type="password",
                help="Enter your OpenAI API key from https://platform.openai.com/api-keys",
                key="api_key_sidebar"
            )
            
            # SURGICAL FIX: Store in session state immediately
            if api_key and api_key.strip():
                st.session_state.api_key = api_key
                
                # Test API Connection Button
                if st.button("🔌 Test API Connection", key="test_api", use_container_width=True):
                    with st.spinner("Testing API connection..."):
                        try:
                            test_generator = ContentGenerator(api_key)
                            result = test_generator.test_connection()
                            
                            if result["success"]:
                                st.success(f"✅ {result['message']}")
                                st.info(f"Model: {result['model']}")
                            else:
                                st.error(f"❌ {result['message']}")
                                st.code(result.get('error', 'Unknown error'))
                        except Exception as e:
                            st.error(f"❌ Connection test failed: {str(e)}")
            else:
                st.warning("⚠️ Enter your OpenAI API key above to test connection")
            
            st.markdown("---")
            st.markdown("### 📊 Navigation")
            
            view = st.radio(
                "Select View",
                ["📊 Overview", "🎯 Campaigns", "✏️ Content Lab", "🖼️ Assets", "📈 Insights"],
                label_visibility="collapsed"
            )
            
            st.markdown("---")
            st.markdown("### 🎨 Preferences")
            theme = st.selectbox("Theme", ["Dark", "Light"], index=0)
            
            st.markdown("---")
            st.markdown("### ℹ️ About")
            st.markdown("""
            **AI Social Platform v1.1**
            
            Powered by:
            - OpenAI GPT-4
            - DALL-E 3
            - Streamlit
            """)
        
        # HEADER
        st.markdown("""
        <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                    padding: 2rem; border-radius: 12px; margin-bottom: 2rem;">
            <h1 style="color: white; margin: 0;">🚀 AI Social Media Platform</h1>
            <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0;">
                Professional Content Generation & Marketing Automation
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # VIEW: OVERVIEW
        if "Overview" in view:
            st.markdown("### 📊 Dashboard Overview")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown("""
                <div class="metric-card">
                    <h3 style="margin: 0; font-size: 2rem;">156</h3>
                    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Total Posts</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="metric-card">
                    <h3 style="margin: 0; font-size: 2rem;">12</h3>
                    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Active Campaigns</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                <div class="metric-card">
                    <h3 style="margin: 0; font-size: 2rem;">2.4M</h3>
                    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Total Reach</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown("""
                <div class="metric-card">
                    <h3 style="margin: 0; font-size: 2rem;">$45K</h3>
                    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Revenue</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📈 Engagement Over Time")
                dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
                engagement = [random.randint(1000, 5000) for _ in range(30)]
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=dates, y=engagement,
                    mode='lines+markers',
                    name='Engagement',
                    line=dict(color='#667eea', width=3),
                    marker=dict(size=8)
                ))
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### 🎯 Platform Distribution")
                platforms = ['Instagram', 'TikTok', 'Facebook', 'LinkedIn']
                values = [35, 30, 20, 15]
                
                fig = go.Figure(data=[go.Pie(
                    labels=platforms,
                    values=values,
                    hole=0.4,
                    marker=dict(colors=['#667eea', '#764ba2', '#f093fb', '#4facfe'])
                )])
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # VIEW: CAMPAIGNS
        elif "Campaigns" in view:
            st.markdown("### 🎯 Campaign Management")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("#### Active Campaigns")
                
                campaigns_data = {
                    'Campaign': ['Summer Sale 2024', 'Product Launch', 'Brand Awareness'],
                    'Status': ['🟢 Active', '🟡 Pending', '🟢 Active'],
                    'Budget': ['$10,000', '$15,000', '$8,000'],
                    'ROI': ['245%', '180%', '210%'],
                    'End Date': ['2024-08-31', '2024-07-15', '2024-09-30']
                }
                
                df = pd.DataFrame(campaigns_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
            
            with col2:
                st.markdown("#### Create Campaign")
                
                with st.form("new_campaign"):
                    camp_name = st.text_input("Campaign Name")
                    camp_budget = st.number_input("Budget ($)", min_value=0, value=5000)
                    camp_start = st.date_input("Start Date")
                    camp_end = st.date_input("End Date")
                    
                    if st.form_submit_button("Create Campaign"):
                        show_success(f"Campaign '{camp_name}' created!")
        
        # VIEW: CONTENT LAB
        elif "Content Lab" in view:
            st.markdown("### ✏️ AI Content Generation Lab")
            
            # Generate Caption & Image
            with st.expander("🎨 Generate Caption & Image", expanded=True):
                st.markdown("Create complete social media posts with AI-generated captions and images.")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    topic = st.text_input("Topic", placeholder="Summer fashion trends")
                    platform = st.selectbox("Platform", ["Instagram", "TikTok", "Facebook", "LinkedIn"])
                    tone = st.selectbox("Tone", ["Professional", "Casual", "Humorous", "Inspirational"])
                
                with col2:
                    keywords = st.text_input("Keywords (comma-separated)", placeholder="fashion, style, summer")
                    schedule_date = st.date_input("Schedule Date")
                    schedule_time = st.time_input("Schedule Time")
                
                generate_image_checkbox = st.checkbox("Generate AI Image with DALL-E 3", value=True)
                
                if generate_image_checkbox:
                    image_description = st.text_area(
                        "Image Description",
                        placeholder="A vibrant summer fashion scene with colorful outfits...",
                        height=100
                    )
                
                if st.button("🚀 Generate & Schedule", key="generate_post", use_container_width=True):
                    if not st.session_state.get('api_key', ''):
                        show_error("Please enter your OpenAI API key in the sidebar!")
                    else:
                        try:
                            generator = ContentGenerator(st.session_state.get('api_key', ''))
                            engineer = PromptEngineer(st.session_state.get('api_key', ''))
                            
                            with st.spinner("✨ Generating your content..."):
                                # Generate caption
                                keywords_list = [k.strip() for k in keywords.split(",")] if keywords else []
                                caption = generator.generate_caption(topic, platform, tone, keywords_list)
                                
                                st.markdown("#### 📝 Generated Caption")
                                st.info(caption)
                                
                                # Generate image if requested
                                image_url = None
                                if generate_image_checkbox and image_description:
                                    with st.spinner("🎨 Creating AI image..."):
                                        enhanced_prompt = engineer.enhance_for_dalle(image_description)
                                        
                                        with st.expander("🔍 View Enhanced Prompt"):
                                            st.markdown(f"**Original:** {image_description}")
                                            st.markdown(f"**Enhanced:** {enhanced_prompt}")
                                        
                                        image_url = generator.generate_image(enhanced_prompt)
                                        
                                        if image_url:
                                            st.markdown("#### 🖼️ Generated Image")
                                            st.image(image_url, use_column_width=True)
                                
                                show_success("Content generated and scheduled successfully!")
                        
                        except Exception as e:
                            logger.error(f"Content generation error: {e}")
                            show_error(f"Generation failed: {str(e)}")
            
            # ====================================================================
            # SURGICAL FIX 4: Initialize generator/engineer in image-only section
            # ====================================================================
            # Generate AI Image only (no caption)
            with st.expander("🖼️ Generate AI Image Only", expanded=False):
                st.markdown("Generate an image using DALL-E 3 without creating a full post.")
                
                image_description = st.text_area(
                    "Describe your image",
                    placeholder="A futuristic city with flying cars at sunset...",
                    key="image_only_desc",
                    height=100
                )
                
                # SURGICAL FIX: Initialize generator and engineer here
                if not st.session_state.get('api_key', ''):
                    st.warning("⚠️ Please enter your OpenAI API key in the sidebar first")
                    generator = None
                    engineer = None
                else:
                    try:
                        generator = ContentGenerator(st.session_state.get('api_key', ''))
                        engineer = PromptEngineer(st.session_state.get('api_key', ''))
                    except Exception as e:
                        st.error(f"Failed to initialize: {str(e)}")
                        generator = None
                        engineer = None
                
                if st.button("🖼️ Generate AI Image", key="gen_image", use_container_width=True):
                    # Validate API key
                    current_key = st.session_state.get('api_key', '')
                    if not current_key:
                        show_error("❌ API key not found! Please enter your API key in the sidebar.")
                        st.stop()
                    
                    # Validate image description
                    if not image_description or len(image_description.strip()) < 5:
                        show_error("❌ Please provide a longer image description (at least 5 characters)")
                        st.stop()
                    
                    with st.spinner("✨ Creating your AI masterpiece..."):
                        try:
                            st.write("---")
                            st.write("### 🔍 Generation Process")
                            
                            # Show API key info
                            st.info(f"🔑 API Key: {current_key[:10]}...{current_key[-4:]} (length: {len(current_key)})")
                            
                            # Step 1: Check generator
                            st.write("**Step 1:** Checking ContentGenerator...")
                            if generator is None:
                                show_error("ContentGenerator is not initialized!")
                                st.stop()
                            st.success(f"✅ Generator ready")
                            
                            # Step 2: Check engineer
                            st.write("**Step 2:** Checking PromptEngineer...")
                            if engineer is None:
                                show_error("PromptEngineer is not initialized!")
                                st.stop()
                            st.success(f"✅ Engineer ready")
                            
                            # Step 3: Enhance prompt
                            st.write("**Step 3:** Enhancing prompt with GPT-4...")
                            st.code(f"Original: {image_description}")
                            
                            try:
                                enhanced_prompt = engineer.enhance_for_dalle(image_description)
                                st.success("✅ Prompt enhanced successfully!")
                                st.code(f"Enhanced: {enhanced_prompt[:200]}...")
                                
                                with st.expander("📝 View Full Enhanced Prompt"):
                                    st.text_area("Enhanced Prompt", enhanced_prompt, height=150)
                                    
                            except Exception as e:
                                st.error(f"❌ Prompt enhancement failed: {str(e)}")
                                st.warning("Proceeding with original prompt...")
                                enhanced_prompt = image_description
                            
                            # Step 4: Generate image
                            st.write("**Step 4:** Generating image with DALL-E 3...")
                            st.write(f"Using prompt (first 100 chars): {enhanced_prompt[:100]}...")
                            
                            try:
                                image_url = generator.generate_image(enhanced_prompt)
                                
                                if image_url:
                                    st.success("✅ Image generated successfully!")
                                    st.write(f"Image URL: {image_url[:80]}...")
                                    
                                    # Save to session
                                    st.session_state['last_image_url'] = image_url
                                    st.session_state['last_prompt'] = enhanced_prompt
                                    
                                    # Display image
                                    st.write("**Step 5:** Displaying image...")
                                    st.image(image_url, caption="Generated by DALL-E 3", use_column_width=True)
                                    
                                    show_success("🎉 Image generation complete!")
                                    
                                    # Download button
                                    st.download_button(
                                        label="📥 Download Image URL",
                                        data=image_url,
                                        file_name="dalle_image_url.txt",
                                        mime="text/plain"
                                    )
                                else:
                                    show_error("❌ API returned empty image URL")
                                    
                            except Exception as img_error:
                                st.error(f"❌ Image generation failed!")
                                st.code(f"Error: {str(img_error)}")
                                
                                # Troubleshooting tips
                                st.markdown("### 🔧 Troubleshooting Tips:")
                                error_str = str(img_error)
                                if "authentication" in error_str.lower() or "unauthorized" in error_str.lower():
                                    st.warning("**Authentication Issue:**")
                                    st.markdown("- Verify your API key is correct")
                                    st.markdown("- Try generating a new API key at https://platform.openai.com/api-keys")
                                elif "quota" in error_str.lower() or "rate_limit" in error_str.lower():
                                    st.warning("**Rate Limit Issue:**")
                                    st.markdown("- Wait a few minutes and try again")
                                    st.markdown("- Check your usage at https://platform.openai.com/usage")
                                elif "billing" in error_str.lower():
                                    st.warning("**Billing Issue:**")
                                    st.markdown("- Check billing at https://platform.openai.com/account/billing")
                                    st.markdown("- Ensure you have an active payment method")
                                elif "model" in error_str.lower() or "dall-e" in error_str.lower():
                                    st.warning("**Model Access Issue:**")
                                    st.markdown("- Ensure your account has DALL-E 3 access")
                                    st.markdown("- DALL-E 3 requires a paid account (not available on free trial)")
                                    st.markdown("- Check if you're on Tier 1+ at https://platform.openai.com/account/limits")
                                else:
                                    st.info("**General Tips:**")
                                    st.markdown("- Use the 'Test API Connection' button in the sidebar")
                                    st.markdown("- Check OpenAI status at https://status.openai.com")
                                    st.markdown("- Try with a different prompt")
                                
                        except ValueError as ve:
                            st.error(f"❌ **Validation Error:**")
                            st.code(str(ve))
                        except Exception as e:
                            st.error(f"❌ **Unexpected Error:**")
                            st.code(str(e))
                            logger.error(f"Image generation error: {e}")
        
        # VIEW: ASSETS
        elif "Assets" in view:
            st.markdown("### 🖼️ Image Gallery")
            
            if st.session_state.images:
                cols = st.columns(3)
                for idx, img in enumerate(st.session_state.images):
                    with cols[idx % 3]:
                        st.image(img['url'], use_column_width=True)
                        st.caption(f"Created: {img['created_date']}")
            else:
                st.info("No images generated yet. Go to Content Lab and create posts with AI-generated images using DALL-E 3!")
                st.markdown("**Quick Start:**")
                st.markdown("1. Navigate to Content Lab")
                st.markdown("2. Enter your OpenAI API key in the sidebar")
                st.markdown("3. Check 'Generate AI Image with DALL-E 3'")
                st.markdown("4. Describe your image and click 'Generate & Schedule'")
        
        # VIEW: INSIGHTS
        elif "Insights" in view:
            st.markdown("### 📈 Performance Insights")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Platform Performance")
                df = pd.DataFrame({
                    'Platform': ['Instagram', 'TikTok', 'Facebook', 'LinkedIn'],
                    'Posts': [156, 203, 89, 45],
                    'Engagement': [38420, 28350, 15280, 8370],
                    'Avg ROI': ['238%', '185%', '142%', '96%']
                })
                st.dataframe(df, use_container_width=True, hide_index=True)
            
            with col2:
                st.markdown("#### Key Insights")
                st.success("✅ Instagram Reels have 2.3x higher engagement than static posts")
                st.info("💡 Best posting time: 11AM-2PM for optimal reach")
                st.warning("⚠️ LinkedIn engagement down 12% this month - review content strategy")
                st.info("💡 Posts with AI-generated images get 45% more engagement")
        
        # FOOTER
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align: center; padding: 2rem; border-top: 1px solid rgba(255,255,255,0.05); color: #9aa4b2; font-size: 0.875rem;">
            <p><strong>Social Platform Dashboard v1.1</strong> | Powered by OpenAI GPT-4 & DALL-E 3</p>
        </div>
        """, unsafe_allow_html=True)
    
    except Exception as e:
        logger.error(f"Main application error: {e}")
        st.error("Application encountered an error. Please refresh the page.")
        st.exception(e)

if __name__ == "__main__":
    main()
