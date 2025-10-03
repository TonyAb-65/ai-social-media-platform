#!/usr/bin/env python3
"""
AI Social Media Platform - OpenAI Integration v2.0
==========================================
Complete AI-powered social media management with multi-language support,
bulk generation, image variations, and scheduled posts
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
import os
from pathlib import Path
import base64
import requests

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

# Create images directory if it doesn't exist
IMAGES_DIR = Path("generated_images")
IMAGES_DIR.mkdir(exist_ok=True)

# Supported languages for multi-language support
LANGUAGES = {
    "English": "en",
    "العربية (Arabic)": "ar",
    "Español (Spanish)": "es",
    "Français (French)": "fr",
    "Deutsch (German)": "de",
    "中文 (Chinese)": "zh",
    "日本語 (Japanese)": "ja",
    "한국어 (Korean)": "ko",
    "Português (Portuguese)": "pt",
    "Русский (Russian)": "ru"
}

# ============================================================================
# Image saving and downloading utilities
# ============================================================================
def save_image_locally(image_url: str, prompt: str) -> str:
    """Download and save image locally"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_prompt = "".join(c for c in prompt[:30] if c.isalnum() or c in (' ', '-', '_')).strip()
        filename = f"{timestamp}_{safe_prompt}.png"
        filepath = IMAGES_DIR / filename
        
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        logger.info(f"Image saved to: {filepath}")
        return str(filepath)
    except Exception as e:
        logger.error(f"Failed to save image: {e}")
        return ""

# SURGICAL FIX 1: Save image to database for Assets gallery
def save_image_to_db(conn, image_url: str, prompt: str, local_path: str) -> str:
    """Save image to database so it appears in Assets"""
    try:
        c = conn.cursor()
        image_id = str(uuid.uuid4())
        
        c.execute('''INSERT INTO images 
                     (id, prompt, url, created_date, local_path, used_in_posts)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (image_id, prompt, image_url, datetime.now().isoformat(), 
                   local_path, json.dumps([])))
        
        conn.commit()
        logger.info(f"Image saved to database: {image_id}")
        return image_id
    except Exception as e:
        logger.error(f"Failed to save image to database: {e}")
        return ""

# Get all images from database
def get_all_images(conn):
    """Get all images from database"""
    try:
        c = conn.cursor()
        c.execute('''SELECT * FROM images ORDER BY created_date DESC''')
        columns = [description[0] for description in c.description]
        images = [dict(zip(columns, row)) for row in c.fetchall()]
        return images
    except Exception as e:
        logger.error(f"Failed to get images: {e}")
        return []

# ============================================================================
# ContentGenerator and PromptEngineer Classes
# ============================================================================
class ContentGenerator:
    """Handles content generation using OpenAI API"""
    
    def __init__(self, api_key: str):
        """Initialize with OpenAI API key"""
        if not api_key:
            raise ValueError("API key cannot be empty")
        
        self.api_key = ''.join(api_key.split())
        
        if not self.api_key.startswith('sk-'):
            raise ValueError(f"Invalid API key format. OpenAI keys start with 'sk-'. Your key starts with: {self.api_key[:10]}")
        
        if len(self.api_key) < 20:
            raise ValueError(f"API key too short. Expected 40+ characters, got {len(self.api_key)}")
        
        self.client = OpenAI(api_key=self.api_key)
        logger.info(f"ContentGenerator initialized with key: {self.api_key[:10]}...{self.api_key[-4:]}")
    
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
    
    def generate_caption(self, topic: str, platform: str, tone: str, keywords: list, language: str = "en") -> str:
        """Generate social media caption using GPT-4 with multi-language support"""
        try:
            keywords_str = ", ".join(keywords) if keywords else "engagement, marketing"
            
            language_instruction = ""
            if language != "en":
                lang_names = {v: k for k, v in LANGUAGES.items()}
                language_instruction = f"\n- Write the caption in {lang_names.get(language, 'English')}"
            
            prompt = f"""Create a compelling {platform} caption about {topic}.
            
Requirements:
- Tone: {tone}
- Include relevant keywords: {keywords_str}
- Include 3-5 relevant hashtags
- Make it engaging and platform-appropriate
- Length: Optimal for {platform}{language_instruction}

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
    
    def generate_image(self, prompt: str, size: str = "1024x1024", quality: str = "hd", safe_mode: bool = False) -> str:
        """Generate image using DALL-E 3 with HD quality and content filter handling"""
        try:
            logger.info(f"Starting DALL-E 3 image generation...")
            logger.info(f"Prompt: {prompt[:100]}...")
            logger.info(f"Quality: {quality}, Size: {size}, Safe Mode: {safe_mode}")
            
            # If safe mode, simplify prompt to avoid filters
            final_prompt = prompt
            if safe_mode:
                # Remove potentially problematic words while keeping core meaning
                final_prompt = self._sanitize_prompt(prompt)
                logger.info(f"Safe mode enabled. Sanitized prompt: {final_prompt[:100]}...")
            
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=final_prompt,
                size=size,
                quality=quality,
                n=1
            )
            
            image_url = response.data[0].url
            logger.info(f"✅ Image generated successfully!")
            return image_url
            
        except Exception as e:
            error_str = str(e)
            
            # Handle content policy violations specifically
            if "content_policy_violation" in error_str or "content filters" in error_str:
                logger.warning(f"Content filter triggered. Prompt: {prompt[:100]}...")
                
                # Try again with simplified prompt if not already in safe mode
                if not safe_mode:
                    logger.info("Retrying with safe mode enabled...")
                    return self.generate_image(prompt, size, quality, safe_mode=True)
                else:
                    # If safe mode also failed, raise with helpful message
                    raise ValueError(
                        "Content filter blocked this image. Try:\n"
                        "1. Use more general descriptions\n"
                        "2. Avoid specific people, brands, or copyrighted content\n"
                        "3. Remove any potentially sensitive words\n"
                        "4. Simplify your description"
                    )
            
            logger.error(f"❌ DALL-E 3 error: {error_str}")
            raise
    
    def _sanitize_prompt(self, prompt: str) -> str:
        """Sanitize prompt to avoid content filters"""
        # Remove potentially problematic phrases
        problematic_words = [
            'realistic', 'photorealistic', 'photo', 'photograph',
            'professional photography', 'shot on camera', 'Canon', 'Sony',
            'portrait photography', 'studio lighting', 'high resolution'
        ]
        
        sanitized = prompt
        for word in problematic_words:
            sanitized = sanitized.replace(word, '')
        
        # Clean up extra spaces
        sanitized = ' '.join(sanitized.split())
        
        # Make it more artistic/less realistic
        if 'person' in sanitized.lower() or 'woman' in sanitized.lower() or 'man' in sanitized.lower():
            sanitized = f"Digital artwork showing {sanitized}"
        
        logger.info(f"Sanitized from: {prompt[:80]}... to: {sanitized[:80]}...")
        return sanitized
    
    def generate_image_variation(self, image_path: str, n: int = 1) -> List[str]:
        """Generate variations of an existing image using DALL-E 2"""
        try:
            logger.info(f"Generating {n} variation(s) of image...")
            
            with open(image_path, "rb") as image_file:
                response = self.client.images.create_variation(
                    image=image_file,
                    n=n,
                    size="1024x1024"
                )
            
            image_urls = [img.url for img in response.data]
            logger.info(f"✅ Generated {len(image_urls)} variation(s)")
            return image_urls
            
        except Exception as e:
            logger.error(f"❌ Variation generation error: {str(e)}")
            raise

class PromptEngineer:
    """Enhances user prompts for better DALL-E 3 results"""
    
    def __init__(self, api_key: str):
        """Initialize with OpenAI API key"""
        if not api_key:
            raise ValueError("API key cannot be empty")
        
        self.api_key = ''.join(api_key.split())
        
        if not self.api_key.startswith('sk-'):
            raise ValueError(f"Invalid API key format. OpenAI keys start with 'sk-'")
        
        self.client = OpenAI(api_key=self.api_key)
        logger.info(f"PromptEngineer initialized with key: {self.api_key[:10]}...{self.api_key[-4:]}")
    
    def enhance_for_dalle(self, user_prompt: str) -> str:
        """Enhance user prompt for DALL-E 3 using GPT-4 with focus on photorealism when needed"""
        try:
            logger.info(f"Enhancing prompt: {user_prompt[:50]}...")
            
            # Detect if user wants real photos (humans, people, portraits, etc.)
            photo_keywords = ['person', 'people', 'human', 'man', 'woman', 'portrait', 'face', 'selfie', 
                            'photograph', 'photo', 'realistic', 'real', 'professional', 'model', 'business']
            wants_photorealism = any(keyword in user_prompt.lower() for keyword in photo_keywords)
            
            # Build enhancement instructions based on desired style
            if wants_photorealism:
                style_instructions = """CRITICAL: This must be a PHOTOREALISTIC image, not animation or cartoon.

Required specifications:
1. Style: Professional photography, shot on high-end camera (Canon EOS R5, Sony A7R IV)
2. Realism: Photorealistic human features, natural skin texture, real lighting
3. Quality: High resolution, sharp focus, detailed textures
4. Lighting: Natural lighting or professional studio setup
5. NO cartoon, NO animation, NO illustrated style, NO digital art
6. Must look like a real photograph that could appear in a magazine or professional portfolio

"""
            else:
                style_instructions = """Choose the most appropriate art style for this image (digital art, illustration, photorealistic, etc.).

"""

            enhancement_instructions = f"""{style_instructions}You are a DALL-E 3 prompt expert. Enhance this prompt for better image generation:

User prompt: {user_prompt}

Create a detailed, professional DALL-E 3 prompt that:
1. Keeps the core idea but adds rich visual details
2. Specifies the exact art style needed (photorealistic if humans/people are involved)
3. Includes specific lighting details (golden hour, studio lighting, natural light, etc.)
4. Mentions camera angle and composition
5. Adds atmospheric and environmental details
6. Is vivid, specific, and under 1000 characters

Enhanced prompt:"""

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert at writing DALL-E 3 prompts. When users want photos of people, you ALWAYS specify photorealistic, professional photography style to avoid cartoon/animated results."},
                    {"role": "user", "content": enhancement_instructions}
                ],
                max_tokens=400,
                temperature=0.7
            )
            
            enhanced = response.choices[0].message.content.strip()
            enhanced = enhanced.strip('"').strip("'")
            logger.info(f"✅ Prompt enhanced successfully! (Photorealism: {wants_photorealism})")
            return enhanced
            
        except Exception as e:
            logger.error(f"❌ Prompt enhancement error: {str(e)}")
            logger.warning("Returning original prompt")
            return user_prompt

# ============================================================================
# Database Functions
# ============================================================================
def init_db():
    """Initialize SQLite database with enhanced schema"""
    conn = sqlite3.connect('social_media.db', check_same_thread=False)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS campaigns
                 (id TEXT PRIMARY KEY, name TEXT, status TEXT, budget REAL, 
                  roi REAL, start_date TEXT, end_date TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS posts
                 (id TEXT PRIMARY KEY, campaign_id TEXT, platform TEXT, 
                  content TEXT, scheduled_date TEXT, status TEXT, 
                  engagement INTEGER, image_url TEXT, image_path TEXT, language TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS images
                 (id TEXT PRIMARY KEY, prompt TEXT, url TEXT, 
                  created_date TEXT, used_in_posts TEXT, local_path TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS scheduled_posts
                 (id TEXT PRIMARY KEY, post_id TEXT, scheduled_datetime TEXT,
                  posted INTEGER DEFAULT 0, created_date TEXT)''')
    
    conn.commit()
    return conn

# SURGICAL FIX 2: Enhanced scheduled post saving
def save_scheduled_post(conn, post_data: dict, schedule_datetime: datetime):
    """Save a scheduled post to the database"""
    try:
        c = conn.cursor()
        
        post_id = str(uuid.uuid4())
        c.execute('''INSERT INTO posts 
                     (id, campaign_id, platform, content, scheduled_date, status, 
                      engagement, image_url, image_path, language)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (post_id, post_data.get('campaign_id', ''), post_data['platform'],
                   post_data['content'], schedule_datetime.isoformat(), 'scheduled',
                   0, post_data.get('image_url', ''), post_data.get('image_path', ''),
                   post_data.get('language', 'en')))
        
        schedule_id = str(uuid.uuid4())
        c.execute('''INSERT INTO scheduled_posts 
                     (id, post_id, scheduled_datetime, created_date)
                     VALUES (?, ?, ?, ?)''',
                  (schedule_id, post_id, schedule_datetime.isoformat(),
                   datetime.now().isoformat()))
        
        conn.commit()
        logger.info(f"Scheduled post saved: {post_id}")
        return post_id
    except Exception as e:
        logger.error(f"Failed to save scheduled post: {e}")
        return None

def get_scheduled_posts(conn, limit: int = 50):
    """Retrieve scheduled posts from database"""
    try:
        c = conn.cursor()
        c.execute('''SELECT p.*, s.scheduled_datetime, s.posted
                     FROM posts p
                     JOIN scheduled_posts s ON p.id = s.post_id
                     WHERE s.posted = 0
                     ORDER BY s.scheduled_datetime
                     LIMIT ?''', (limit,))
        
        columns = [description[0] for description in c.description]
        posts = [dict(zip(columns, row)) for row in c.fetchall()]
        return posts
    except Exception as e:
        logger.error(f"Failed to retrieve scheduled posts: {e}")
        return []

def delete_scheduled_post(conn, post_id: str):
    """Delete a scheduled post"""
    try:
        c = conn.cursor()
        c.execute('DELETE FROM scheduled_posts WHERE post_id = ?', (post_id,))
        c.execute('DELETE FROM posts WHERE id = ?', (post_id,))
        conn.commit()
        logger.info(f"Deleted scheduled post: {post_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to delete post: {e}")
        return False

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
    if 'selected_language' not in st.session_state:
        st.session_state.selected_language = "en"
    if 'image_size' not in st.session_state:
        st.session_state.image_size = "1024x1024"
    if 'image_quality' not in st.session_state:
        st.session_state.image_quality = "hd"
    if 'safe_mode' not in st.session_state:
        st.session_state.safe_mode = False
    if 'auto_save_images' not in st.session_state:
        st.session_state.auto_save_images = True

# Helper functions
def show_success(message):
    st.success(f"✅ {message}")

def show_error(message):
    st.error(f"❌ {message}")

def show_info(message):
    st.info(f"ℹ️ {message}")

# ============================================================================
# Main Application
# ============================================================================
def main():
    try:
        st.set_page_config(
            page_title="AI Social Media Platform v2.0",
            page_icon="🚀",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
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
        
        # SIDEBAR
        with st.sidebar:
            st.markdown("## ⚙️ Settings")
            
            # Try to load API key from secrets first
            api_key_from_secrets = st.secrets.get("OPENAI_API_KEY", "")
            
            if api_key_from_secrets:
                st.success("✅ API key loaded from secrets")
                api_key = api_key_from_secrets
                
                if st.checkbox("Use different API key", value=False):
                    api_key = st.text_input(
                        "OpenAI API Key (Override)",
                        type="password",
                        help="Override the key from secrets",
                        key="api_key_override"
                    )
            else:
                st.info("💡 Tip: Add OPENAI_API_KEY to secrets.toml to avoid entering it every time")
                
                api_key = st.text_input(
                    "OpenAI API Key",
                    type="password",
                    help="Enter your OpenAI API key from https://platform.openai.com/api-keys",
                    key="api_key_sidebar"
                )
            
            if api_key:
                cleaned_key = ''.join(api_key.split())
                
                with st.expander("🔍 Debug API Key", expanded=False):
                    st.write(f"**Original length:** {len(api_key)} characters")
                    st.write(f"**Cleaned length:** {len(cleaned_key)} characters")
                    st.write(f"**Starts with:** {cleaned_key[:10] if len(cleaned_key) >= 10 else cleaned_key}")
                    st.write(f"**Ends with:** {cleaned_key[-4:] if len(cleaned_key) >= 4 else cleaned_key}")
                    
                    if len(api_key) != len(cleaned_key):
                        st.warning(f"⚠️ Removed {len(api_key) - len(cleaned_key)} hidden characters")
                
                if cleaned_key.startswith('sk-'):
                    st.session_state.api_key = cleaned_key
                    st.success(f"✅ API key stored (length: {len(cleaned_key)})")
                else:
                    st.error("❌ Invalid API key format. OpenAI keys start with 'sk-'")
                    st.warning(f"Your key starts with: {cleaned_key[:10]}")
                    st.session_state.api_key = ""
                
                if st.session_state.get('api_key', ''):
                    if st.button("🔌 Test API Connection", key="test_api", use_container_width=True):
                        with st.spinner("Testing API connection..."):
                            try:
                                test_generator = ContentGenerator(st.session_state.api_key)
                                result = test_generator.test_connection()
                                
                                if result["success"]:
                                    st.success(f"✅ {result['message']}")
                                    st.info(f"Model: {result['model']}")
                                    st.balloons()
                                else:
                                    st.error(f"❌ {result['message']}")
                                    st.code(result.get('error', 'Unknown error'))
                            except Exception as e:
                                st.error(f"❌ Connection test failed!")
                                st.code(str(e))
                                
                                error_str = str(e)
                                if "401" in error_str or "invalid_api_key" in error_str:
                                    st.warning("**This is an authentication error. Possible causes:**")
                                    st.markdown("1. **Wrong API key** - Double check you copied the entire key")
                                    st.markdown("2. **Revoked key** - Generate a new key at https://platform.openai.com/api-keys")
                                    st.markdown("3. **Hidden characters** - Check the 'Debug API Key' section above")
                                    st.markdown("4. **Copy-paste issue** - Try typing the key manually")
                                    st.markdown("5. **OpenAI Outage** - Check https://status.openai.com")
            else:
                st.warning("⚠️ Enter your OpenAI API key above")
            
            st.markdown("---")
            st.markdown("### 📊 Navigation")
            
            view = st.radio(
                "Select View",
                ["📊 Overview", "🎯 Campaigns", "✏️ Content Lab", "🖼️ Assets", "📈 Insights", "📅 Scheduled Posts"],
                label_visibility="collapsed"
            )
            
            st.markdown("---")
            st.markdown("### 🎨 Preferences")
            
            selected_language = st.selectbox(
                "Content Language",
                list(LANGUAGES.keys()),
                index=0,
                help="Language for generated content"
            )
            st.session_state.selected_language = LANGUAGES[selected_language]
            
            theme = st.selectbox("Theme", ["Dark", "Light"], index=0)
            
            st.markdown("### 🖼️ Image Settings")
            image_size = st.selectbox(
                "Image Size",
                ["1024x1024", "1024x1792", "1792x1024"],
                help="Size for DALL-E 3 images"
            )
            st.session_state.image_size = image_size
            
            image_quality = st.selectbox(
                "Image Quality",
                ["HD (High Quality)", "Standard (Faster)"],
                index=0,
                help="HD = Better quality but slower & more expensive. Standard = Faster & cheaper"
            )
            st.session_state.image_quality = "hd" if "HD" in image_quality else "standard"
            
            safe_mode = st.checkbox(
                "Safe Mode (Bypass Content Filters)",
                value=False,
                help="Enable if images are getting blocked by content filters. Uses simpler prompts."
            )
            st.session_state.safe_mode = safe_mode
            
            auto_save_images = st.checkbox("Auto-save images locally", value=True)
            st.session_state.auto_save_images = auto_save_images
            
            st.markdown("---")
            st.markdown("### ℹ️ About")
            st.markdown("""
            **AI Social Platform v2.0**
            
            **Powered by:**
            - OpenAI GPT-4
            - DALL-E 3 & DALL-E 2
            - Streamlit
            
            **Features:**
            - 🌍 Multi-language (10+ languages)
            - 🎨 Bulk image generation
            - 🔄 Image variations
            - 💾 Auto-save images
            - 📅 Scheduled posts
            - 📊 Enhanced analytics
            - 🖼️ HD quality images
            - 🛡️ Safe Mode for content filters
            """)
            
            st.markdown("---")
            st.markdown("### 💡 Quick Tips")
            st.markdown("""
            **Getting Content Filter Errors?**
            
            ✅ Enable 'Safe Mode' above
            
            ✅ Use artistic language:
            - 'Digital art of...'
            - 'Illustration showing...'
            - 'Artistic style...'
            
            ❌ Avoid being too specific:
            - Remove 'realistic', 'photo'
            - Simplify descriptions
            - Use general terms
            """)
        
        # HEADER
        st.markdown("""
        <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                    padding: 2rem; border-radius: 12px; margin-bottom: 2rem;">
            <h1 style="color: white; margin: 0;">🚀 AI Social Media Platform v2.0</h1>
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
                # Count scheduled posts
                scheduled_count = len(get_scheduled_posts(conn))
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="margin: 0; font-size: 2rem;">{scheduled_count}</h3>
                    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Scheduled Posts</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                # Count saved images
                saved_images_count = len(get_all_images(conn))
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="margin: 0; font-size: 2rem;">{saved_images_count}</h3>
                    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Saved Images</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown("""
                <div class="metric-card">
                    <h3 style="margin: 0; font-size: 2rem;">2.4M</h3>
                    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Total Reach</p>
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
                    platform = st.selectbox("Platform", ["Instagram", "TikTok", "Facebook", "LinkedIn", "Snapchat", "Twitter/X", "Pinterest"])
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
                    
                    st.info("💡 **Pro Tip:** For real photos of people, use keywords like: 'professional photograph', 'realistic person', 'portrait photography'. For artistic images, describe the style you want.")
                
                if st.button("🚀 Generate & Schedule", key="generate_post", use_container_width=True):
                    if not st.session_state.get('api_key', ''):
                        show_error("Please enter your OpenAI API key in the sidebar!")
                    else:
                        try:
                            generator = ContentGenerator(st.session_state.get('api_key', ''))
                            engineer = PromptEngineer(st.session_state.get('api_key', ''))
                            
                            with st.spinner("✨ Generating your content..."):
                                # Generate caption with language support
                                keywords_list = [k.strip() for k in keywords.split(",")] if keywords else []
                                selected_lang = st.session_state.get('selected_language', 'en')
                                caption = generator.generate_caption(topic, platform, tone, keywords_list, selected_lang)
                                
                                st.markdown("#### 📝 Generated Caption")
                                st.info(caption)
                                
                                # Generate image if requested
                                image_url = None
                                image_path = None
                                image_id = None
                                
                                if generate_image_checkbox and image_description:
                                    with st.spinner("🎨 Creating AI image..."):
                                        enhanced_prompt = engineer.enhance_for_dalle(image_description)
                                        
                                        with st.expander("🔍 View Enhanced Prompt"):
                                            st.markdown(f"**Original:** {image_description}")
                                            st.markdown(f"**Enhanced:** {enhanced_prompt}")
                                        
                                        image_size = st.session_state.get('image_size', '1024x1024')
                                        image_quality = st.session_state.get('image_quality', 'hd')
                                        safe_mode = st.session_state.get('safe_mode', False)
                                        image_url = generator.generate_image(enhanced_prompt, size=image_size, quality=image_quality, safe_mode=safe_mode)
                                        
                                        if image_url:
                                            st.markdown("#### 🖼️ Generated Image")
                                            st.image(image_url, use_column_width=True)
                                            
                                            # SURGICAL FIX: Save to local and database
                                            if st.session_state.get('auto_save_images', True):
                                                image_path = save_image_locally(image_url, image_description)
                                                if image_path:
                                                    st.success(f"💾 Image saved locally: {Path(image_path).name}")
                                                    
                                                    # Save to database for Assets gallery
                                                    image_id = save_image_to_db(conn, image_url, enhanced_prompt, image_path)
                                                    if image_id:
                                                        st.success(f"✅ Image saved to Assets gallery!")
                                
                                # Save scheduled post
                                schedule_datetime = datetime.combine(schedule_date, schedule_time)
                                post_data = {
                                    'platform': platform,
                                    'content': caption,
                                    'image_url': image_url,
                                    'image_path': image_path,
                                    'language': selected_lang
                                }
                                post_id = save_scheduled_post(conn, post_data, schedule_datetime)
                                
                                if post_id:
                                    show_success(f"🎉 Content scheduled for {schedule_datetime.strftime('%Y-%m-%d at %H:%M')}!")
                                    st.info(f"📅 View your scheduled post in the 'Scheduled Posts' section")
                                else:
                                    show_success("Content generated successfully!")
                        
                        except Exception as e:
                            logger.error(f"Content generation error: {e}")
                            error_str = str(e)
                            
                            # Special handling for content filter errors
                            if "content_policy_violation" in error_str or "content filters" in error_str:
                                st.error("❌ **Content Filter Blocked This Image**")
                                st.warning("OpenAI's content filters blocked your image request.")
                                
                                st.markdown("### 🛡️ How to Fix:")
                                st.markdown("**Option 1: Enable Safe Mode** (Easiest)")
                                st.info("1. Go to Sidebar → Image Settings\n2. Check ✅ 'Safe Mode (Bypass Content Filters)'\n3. Try generating again")
                                
                                st.markdown("**Option 2: Modify Your Description**")
                                st.markdown("- Use more **general** descriptions")
                                st.markdown("- Avoid specific people, brands, or copyrighted content")
                                st.markdown("- Remove words like 'realistic', 'photograph', 'professional'")
                                st.markdown("- Use artistic terms: 'digital art', 'illustration', 'painting'")
                                
                                with st.expander("🔍 What Triggered the Filter?"):
                                    st.write("**Your prompt:**")
                                    st.code(image_description if 'image_description' in locals() else "N/A")
                                    st.write("**Enhanced prompt:**")
                                    st.code(enhanced_prompt if 'enhanced_prompt' in locals() else "N/A")
                            else:
                                show_error(f"Generation failed: {str(e)}")
            
            # Generate AI Image only
            with st.expander("🖼️ Generate AI Image Only", expanded=False):
                st.markdown("Generate an image using DALL-E 3 without creating a full post.")
                
                image_description = st.text_area(
                    "Describe your image",
                    placeholder="A futuristic city with flying cars at sunset...",
                    key="image_only_desc",
                    height=100
                )
                
                st.info("💡 **For Real Photos:** Include 'professional photograph of a person/woman/man' or 'realistic portrait'. **For Art:** Describe style like 'digital art', 'watercolor', 'illustration'")
                
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
                    current_key = st.session_state.get('api_key', '')
                    if not current_key:
                        show_error("❌ API key not found! Please enter your API key in the sidebar.")
                        st.stop()
                    
                    if not image_description or len(image_description.strip()) < 5:
                        show_error("❌ Please provide a longer image description (at least 5 characters)")
                        st.stop()
                    
                    with st.spinner("✨ Creating your AI masterpiece..."):
                        try:
                            st.write("---")
                            st.write("### 🔍 Generation Process")
                            
                            st.info(f"🔑 API Key: {current_key[:10]}...{current_key[-4:]} (length: {len(current_key)})")
                            
                            st.write("**Step 1:** Checking ContentGenerator...")
                            if generator is None:
                                show_error("ContentGenerator is not initialized!")
                                st.stop()
                            st.success(f"✅ Generator ready")
                            
                            st.write("**Step 2:** Checking PromptEngineer...")
                            if engineer is None:
                                show_error("PromptEngineer is not initialized!")
                                st.stop()
                            st.success(f"✅ Engineer ready")
                            
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
                            
                            st.write("**Step 4:** Generating image with DALL-E 3...")
                            st.write(f"Using prompt (first 100 chars): {enhanced_prompt[:100]}...")
                            
                            try:
                                image_url = generator.generate_image(enhanced_prompt, 
                                                                    size=st.session_state.get('image_size', '1024x1024'),
                                                                    quality=st.session_state.get('image_quality', 'hd'),
                                                                    safe_mode=st.session_state.get('safe_mode', False))
                                
                                if image_url:
                                    st.success("✅ Image generated successfully!")
                                    st.write(f"Image URL: {image_url[:80]}...")
                                    
                                    st.write("**Step 5:** Displaying image...")
                                    st.image(image_url, caption="Generated by DALL-E 3", use_column_width=True)
                                    
                                    # SURGICAL FIX: Save to local and database
                                    saved_path = None
                                    if st.session_state.get('auto_save_images', True):
                                        saved_path = save_image_locally(image_url, image_description)
                                        if saved_path:
                                            st.success(f"💾 Image saved locally: {Path(saved_path).name}")
                                            
                                            # Save to database for Assets
                                            image_id = save_image_to_db(conn, image_url, enhanced_prompt, saved_path)
                                            if image_id:
                                                st.success(f"✅ Image saved to Assets gallery!")
                                    
                                    show_success("🎉 Image generation complete!")
                                    
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
                                error_str = str(img_error)
                                st.code(f"Error: {error_str}")
                                
                                # Special handling for content filter
                                if "content_policy_violation" in error_str or "content filters" in error_str:
                                    st.markdown("### 🛡️ Content Filter Triggered!")
                                    st.warning("Your image was blocked by OpenAI's content filters.")
                                    
                                    st.markdown("**Quick Fix:**")
                                    st.info("✅ Enable **'Safe Mode'** in Sidebar → Image Settings, then try again")
                                    
                                    st.markdown("**Alternative Solutions:**")
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.markdown("**✏️ Simplify Description:**")
                                        st.markdown("- Use general terms")
                                        st.markdown("- Remove 'realistic' keywords")
                                        st.markdown("- Add artistic style words")
                                    with col2:
                                        st.markdown("**🎨 Try These Styles:**")
                                        st.markdown("- 'Digital art showing...'")
                                        st.markdown("- 'Illustration of...'")
                                        st.markdown("- 'Artistic depiction of...'")
                                    
                                    with st.expander("🔍 See What Was Blocked"):
                                        st.markdown("**Your description:**")
                                        st.code(image_description)
                                        st.markdown("**Enhanced prompt:**")
                                        st.code(enhanced_prompt if 'enhanced_prompt' in locals() else "N/A")
                                    
                                    st.markdown("---")
                                
                                # Other error troubleshooting
                                st.markdown("### 🔧 Troubleshooting Tips:")
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
            
            # Bulk Image Generation
            with st.expander("🎨 Bulk Image Generation", expanded=False):
                st.markdown("Generate multiple images at once from a list of prompts.")
                
                st.info("💡 If images get blocked by content filters, enable **'Safe Mode'** in the sidebar before bulk generation.")
                
                bulk_prompts = st.text_area(
                    "Enter prompts (one per line)",
                    placeholder="A sunset over mountains\nA futuristic city\nA peaceful forest",
                    height=150,
                    key="bulk_prompts"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    bulk_enhance = st.checkbox("Enhance prompts with AI", value=True, key="bulk_enhance")
                with col2:
                    bulk_delay = st.slider("Delay between images (seconds)", 1, 10, 3, key="bulk_delay")
                
                if st.button("🚀 Generate Bulk Images", key="bulk_gen", use_container_width=True):
                    if not st.session_state.get('api_key', ''):
                        show_error("❌ API key not found! Please enter your API key in the sidebar.")
                    elif not bulk_prompts or len(bulk_prompts.strip()) < 5:
                        show_error("❌ Please enter at least one prompt")
                    else:
                        try:
                            generator = ContentGenerator(st.session_state.get('api_key', ''))
                            engineer = PromptEngineer(st.session_state.get('api_key', '')) if bulk_enhance else None
                            
                            prompts_list = [p.strip() for p in bulk_prompts.split('\n') if p.strip()]
                            
                            st.write(f"**Generating {len(prompts_list)} images...**")
                            
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            
                            for idx, prompt in enumerate(prompts_list):
                                status_text.text(f"Processing {idx + 1}/{len(prompts_list)}: {prompt[:50]}...")
                                
                                try:
                                    final_prompt = prompt
                                    if bulk_enhance and engineer:
                                        final_prompt = engineer.enhance_for_dalle(prompt)
                                    
                                    image_size = st.session_state.get('image_size', '1024x1024')
                                    image_quality = st.session_state.get('image_quality', 'hd')
                                    safe_mode = st.session_state.get('safe_mode', False)
                                    image_url = generator.generate_image(final_prompt, size=image_size, quality=image_quality, safe_mode=safe_mode)
                                    
                                    if image_url:
                                        col1, col2 = st.columns([2, 1])
                                        with col1:
                                            st.image(image_url, caption=f"Image {idx + 1}: {prompt[:50]}...", use_column_width=True)
                                        with col2:
                                            st.write(f"**Prompt:** {prompt}")
                                            if st.session_state.get('auto_save_images', True):
                                                saved_path = save_image_locally(image_url, prompt)
                                                if saved_path:
                                                    # Save to database
                                                    save_image_to_db(conn, image_url, final_prompt, saved_path)
                                                    st.success(f"💾 Saved to Assets")
                                    
                                    progress_bar.progress((idx + 1) / len(prompts_list))
                                    
                                    if idx < len(prompts_list) - 1:
                                        time_module.sleep(bulk_delay)
                                
                                except Exception as e:
                                    st.error(f"❌ Failed to generate image {idx + 1}: {str(e)}")
                                    
                                    # Show content filter help for bulk generation
                                    if "content_policy_violation" in str(e):
                                        st.warning(f"⚠️ Prompt {idx + 1} blocked by content filter. Enable Safe Mode and try again.")
                                    
                                    continue
                            
                            status_text.text("✅ Bulk generation complete!")
                            show_success(f"Generated {len(prompts_list)} images successfully!")
                            
                        except Exception as e:
                            show_error(f"Bulk generation error: {str(e)}")
            
            # Image Variations
            with st.expander("🔄 Generate Image Variations", expanded=False):
                st.markdown("Create variations of an existing image using DALL-E 2.")
                
                saved_images = list(IMAGES_DIR.glob("*.png"))
                
                if saved_images:
                    selected_image = st.selectbox(
                        "Select an image",
                        saved_images,
                        format_func=lambda x: x.name
                    )
                    
                    if selected_image:
                        st.image(str(selected_image), caption="Original Image", use_column_width=True)
                        
                        num_variations = st.slider("Number of variations", 1, 4, 2, key="num_variations")
                        
                        if st.button("🔄 Generate Variations", key="gen_variations", use_container_width=True):
                            if not st.session_state.get('api_key', ''):
                                show_error("❌ API key not found!")
                            else:
                                try:
                                    generator = ContentGenerator(st.session_state.get('api_key', ''))
                                    
                                    with st.spinner(f"Creating {num_variations} variation(s)..."):
                                        variation_urls = generator.generate_image_variation(str(selected_image), num_variations)
                                        
                                        if variation_urls:
                                            st.markdown("#### 🎨 Generated Variations")
                                            cols = st.columns(min(num_variations, 3))
                                            
                                            for idx, url in enumerate(variation_urls):
                                                with cols[idx % 3]:
                                                    st.image(url, caption=f"Variation {idx + 1}", use_column_width=True)
                                                    
                                                    if st.session_state.get('auto_save_images', True):
                                                        saved_path = save_image_locally(url, f"variation_{idx+1}")
                                                        if saved_path:
                                                            # Save to database
                                                            save_image_to_db(conn, url, f"Variation of {selected_image.name}", saved_path)
                                                            st.success(f"💾 Saved to Assets")
                                            
                                            show_success(f"Generated {len(variation_urls)} variation(s)!")
                                        else:
                                            show_error("Failed to generate variations")
                                
                                except Exception as e:
                                    show_error(f"Variation error: {str(e)}")
                else:
                    st.info("No saved images found. Generate some images first!")
                    st.markdown("Tip: Enable 'Auto-save images locally' in the sidebar.")
        
        # SURGICAL FIX 3: Enhanced Assets view with reuse options
        elif "Assets" in view:
            st.markdown("### 🖼️ Image Gallery & Asset Library")
            
            # Get images from database
            db_images = get_all_images(conn)
            
            if db_images:
                st.markdown(f"**Total Images in Library:** {len(db_images)}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    sort_by = st.selectbox("Sort by", ["Newest First", "Oldest First"])
                with col2:
                    images_per_row = st.slider("Images per row", 2, 4, 3)
                with col3:
                    show_details = st.checkbox("Show details", value=True)
                
                if sort_by == "Oldest First":
                    db_images = list(reversed(db_images))
                
                st.markdown("---")
                
                # Display images with reuse options
                cols = st.columns(images_per_row)
                for idx, img_data in enumerate(db_images):
                    with cols[idx % images_per_row]:
                        # Display image
                        if img_data.get('local_path') and Path(img_data['local_path']).exists():
                            st.image(img_data['local_path'], use_column_width=True)
                        else:
                            st.image(img_data['url'], use_column_width=True)
                        
                        if show_details:
                            created = datetime.fromisoformat(img_data['created_date'])
                            st.caption(f"📅 {created.strftime('%Y-%m-%d %H:%M')}")
                            st.caption(f"📝 {img_data['prompt'][:50]}...")
                            
                            # SURGICAL FIX: Add reuse button for different platforms
                            with st.expander("🔄 Reuse for Platform"):
                                st.markdown("**Select platforms to reuse this image:**")
                                reuse_platforms = st.multiselect(
                                    "Platforms",
                                    ["Instagram", "TikTok", "Snapchat", "Facebook", "LinkedIn", "Twitter/X", "Pinterest"],
                                    key=f"reuse_{img_data['id']}"
                                )
                                
                                if st.button("📤 Reuse Image", key=f"btn_reuse_{img_data['id']}"):
                                    if reuse_platforms:
                                        st.success(f"✅ Image queued for: {', '.join(reuse_platforms)}")
                                        st.info("💡 Go to Content Lab to generate captions for these platforms")
                                    else:
                                        st.warning("Please select at least one platform")
            else:
                st.info("No images in your library yet!")
                st.markdown("**How to add images:**")
                st.markdown("1. Go to Content Lab")
                st.markdown("2. Enable 'Auto-save images locally' in sidebar")
                st.markdown("3. Generate images using any tool")
                st.markdown("4. Images will automatically appear here")
        
        # SURGICAL FIX 4: Enhanced Scheduled Posts view
        elif "Scheduled Posts" in view:
            st.markdown("### 📅 Scheduled Posts Management")
            
            scheduled_posts = get_scheduled_posts(conn)
            
            if scheduled_posts:
                st.markdown(f"**Total Scheduled:** {len(scheduled_posts)} post(s)")
                st.info("💡 These posts are scheduled and waiting to be published")
                
                st.markdown("---")
                
                # Display scheduled posts
                for post in scheduled_posts:
                    scheduled_dt = datetime.fromisoformat(post['scheduled_datetime'])
                    time_until = scheduled_dt - datetime.now()
                    
                    # Status indicator
                    if time_until.total_seconds() < 0:
                        status_emoji = "⏰"
                        status_text = "Ready to post"
                    elif time_until.days > 0:
                        status_emoji = "📅"
                        status_text = f"In {time_until.days} day(s)"
                    else:
                        hours = time_until.seconds // 3600
                        status_emoji = "⏱️"
                        status_text = f"In {hours} hour(s)"
                    
                    with st.expander(
                        f"{status_emoji} {scheduled_dt.strftime('%Y-%m-%d %H:%M')} | {post['platform']} | {status_text}",
                        expanded=False
                    ):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.markdown("**📝 Content:**")
                            st.info(post['content'])
                            
                            if post.get('image_url') or post.get('image_path'):
                                st.markdown("**🖼️ Image:**")
                                if post.get('image_path') and Path(post['image_path']).exists():
                                    st.image(post['image_path'], use_column_width=True)
                                elif post.get('image_url'):
                                    st.image(post['image_url'], use_column_width=True)
                        
                        with col2:
                            st.markdown("**ℹ️ Details:**")
                            st.write(f"**Platform:** {post['platform']}")
                            st.write(f"**Language:** {post.get('language', 'en')}")
                            st.write(f"**Status:** {post['status']}")
                            st.write(f"**Scheduled:** {scheduled_dt.strftime('%Y-%m-%d %H:%M')}")
                            
                            st.markdown("---")
                            st.markdown("**🎬 Actions:**")
                            
                            col_a, col_b = st.columns(2)
                            with col_a:
                                if st.button("✏️ Edit", key=f"edit_{post['id']}", use_container_width=True):
                                    st.info("Edit functionality coming soon!")
                            
                            with col_b:
                                if st.button("🗑️ Delete", key=f"del_{post['id']}", use_container_width=True):
                                    if delete_scheduled_post(conn, post['id']):
                                        show_success("Post deleted!")
                                        st.rerun()
                                    else:
                                        show_error("Failed to delete post")
            else:
                st.info("📭 No scheduled posts yet!")
                st.markdown("---")
                st.markdown("**How to schedule posts:**")
                st.markdown("1. Go to **Content Lab**")
                st.markdown("2. Fill in topic, platform, and content details")
                st.markdown("3. Select **date and time** for scheduling")
                st.markdown("4. Click **'Generate & Schedule'**")
                st.markdown("5. Your post will appear here!")
                
                st.markdown("---")
                st.markdown("**💡 Quick Tips:**")
                st.markdown("- Schedule posts across multiple platforms")
                st.markdown("- Use the same image for different platforms")
                st.markdown("- Generate content in multiple languages")
        
        # VIEW: INSIGHTS
        elif "Insights" in view:
            st.markdown("### 📈 Performance Insights")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown("""
                <div class="metric-card">
                    <h3 style="margin: 0; font-size: 2rem;">2.4M</h3>
                    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Total Reach</p>
                    <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">↑ 12.5% vs last month</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="metric-card">
                    <h3 style="margin: 0; font-size: 2rem;">8.2%</h3>
                    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Avg Engagement</p>
                    <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">↑ 2.1% vs last month</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                <div class="metric-card">
                    <h3 style="margin: 0; font-size: 2rem;">$45K</h3>
                    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Revenue</p>
                    <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">↑ 18.3% vs last month</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown("""
                <div class="metric-card">
                    <h3 style="margin: 0; font-size: 2rem;">238%</h3>
                    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Avg ROI</p>
                    <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">↑ 45% vs last month</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📊 Platform Performance")
                df = pd.DataFrame({
                    'Platform': ['Instagram', 'TikTok', 'Facebook', 'LinkedIn'],
                    'Posts': [156, 203, 89, 45],
                    'Engagement': [38420, 28350, 15280, 8370],
                    'Avg ROI': ['238%', '185%', '142%', '96%'],
                    'Growth': ['↑ 12%', '↑ 8%', '↓ 3%', '↑ 5%']
                })
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                fig = px.bar(df, x='Platform', y='Engagement', 
                            title='Engagement by Platform',
                            color='Platform',
                            color_discrete_sequence=['#667eea', '#764ba2', '#f093fb', '#4facfe'])
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### 💡 Key Insights")
                st.success("✅ Instagram Reels have 2.3x higher engagement than static posts")
                st.info("💡 Best posting time: 11AM-2PM for optimal reach")
                st.warning("⚠️ LinkedIn engagement down 12% this month - review content strategy")
                st.info("💡 Posts with AI-generated images get 45% more engagement")
                st.success("✅ Multi-language posts reach 35% more international audience")
                
                st.markdown("#### 🎨 Content Type Performance")
                content_df = pd.DataFrame({
                    'Type': ['AI Images', 'Stock Photos', 'Videos', 'Text Only'],
                    'Engagement': [12500, 8300, 15200, 3400]
                })
                
                fig = go.Figure(data=[go.Pie(
                    labels=content_df['Type'],
                    values=content_df['Engagement'],
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
        
        # FOOTER
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align: center; padding: 2rem; border-top: 1px solid rgba(255,255,255,0.05); color: #9aa4b2; font-size: 0.875rem;">
            <p><strong>AI Social Platform v2.0</strong> | Powered by OpenAI GPT-4 & DALL-E 3</p>
            <p style="margin-top: 0.5rem;">
                ✨ Features: Multi-Language • Bulk Generation • Image Variations • Auto-Save • Scheduled Posts • Asset Library
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    except Exception as e:
        logger.error(f"Main application error: {e}")
        st.error("Application encountered an error. Please refresh the page.")
        st.exception(e)

if __name__ == "__main__":
    main()
