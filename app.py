#!/usr/bin/env python3
"""
AI Social Media Platform - OpenAI Integration v2.1
==========================================
Complete AI-powered social media management with multi-language support,
bulk generation, image variations, scheduled posts, and VIDEO/REEL creation with Replicate
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

# Replicate Integration for Video/Reels
try:
    import replicate
    REPLICATE_AVAILABLE = True
except ImportError:
    REPLICATE_AVAILABLE = False
    st.warning("Replicate library not installed. Run: pip install replicate")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="AI Social Media Platform",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .stButton>button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .stExpander {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Constants
DB_FILE = "social_media_openai.db"
ASSETS_DIR = Path("assets")
ASSETS_DIR.mkdir(exist_ok=True)

# Language mapping with full names
LANGUAGES = {
    "English": "en",
    "Arabic": "ar",
    "French": "fr",
    "Spanish": "es",
    "German": "de"
}

# Platform-specific requirements for optimized content
PLATFORM_REQUIREMENTS = {
    "Instagram": {
        "max_length": 2200,
        "hashtags": True,
        "emojis": True,
        "style": "casual and visual"
    },
    "Facebook": {
        "max_length": 63206,
        "hashtags": False,
        "emojis": True,
        "style": "conversational and engaging"
    },
    "Twitter": {
        "max_length": 280,
        "hashtags": True,
        "emojis": True,
        "style": "concise and witty"
    },
    "LinkedIn": {
        "max_length": 3000,
        "hashtags": True,
        "emojis": False,
        "style": "professional and insightful"
    },
    "TikTok": {
        "max_length": 2200,
        "hashtags": True,
        "emojis": True,
        "style": "fun and trendy"
    }
}


# ==================== CONTENT GENERATION CLASS ====================
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
        logger.info(f"ContentGenerator initialized successfully")
    
    def test_connection(self) -> dict:
        """Test API connection"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=5
            )
            return {"success": True, "message": "✅ API connection successful!"}
        except Exception as e:
            return {"success": False, "message": f"❌ Connection failed: {str(e)}"}
    
    def generate_content(self, topic: str, platform: str, language: str = "en", 
                        image_path: Optional[str] = None, use_vision: bool = False) -> str:
        """Generate social media content with optional image analysis"""
        try:
            platform_req = PLATFORM_REQUIREMENTS.get(platform, PLATFORM_REQUIREMENTS["Instagram"])
            
            # Build system message
            system_msg = f"""You are an expert social media content creator specializing in {platform}.
            Create engaging content that is {platform_req['style']}.
            Maximum length: {platform_req['max_length']} characters.
            {"Include relevant hashtags." if platform_req['hashtags'] else "No hashtags."}
            {"Use emojis appropriately." if platform_req['emojis'] else "No emojis."}
            Language: {language}
            """
            
            messages = [
                {"role": "system", "content": system_msg},
            ]
            
            # Handle image with vision model
            if use_vision and image_path and os.path.exists(image_path):
                with open(image_path, "rb") as img_file:
                    img_data = base64.b64encode(img_file.read()).decode()
                
                messages.append({
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Create {platform} content about: {topic}. Analyze the image and create relevant content."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_data}"}}
                    ]
                })
                
                model = "gpt-4o"
            else:
                messages.append({"role": "user", "content": f"Create {platform} content about: {topic}"})
                model = "gpt-3.5-turbo"
            
            logger.info(f"Generating content with model: {model}")
            
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=500,
                temperature=0.8
            )
            
            content = response.choices[0].message.content.strip()
            logger.info(f"Content generated successfully")
            return content
            
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            raise
    
    def generate_image(self, prompt: str, size: str = "1024x1024", 
                       quality: str = "standard", style: str = "vivid") -> str:
        """Generate image using DALL-E 3"""
        try:
            logger.info(f"Generating image with DALL-E 3...")
            
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                quality=quality,
                style=style,
                n=1
            )
            
            image_url = response.data[0].url
            logger.info(f"Image generated successfully")
            return image_url
            
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            raise
    
    def generate_image_variation(self, image_path: str, n: int = 1) -> List[str]:
        """Generate variations of an existing image"""
        try:
            with open(image_path, "rb") as image_file:
                response = self.client.images.create_variation(
                    image=image_file,
                    n=n,
                    size="1024x1024"
                )
            
            variations = [img.url for img in response.data]
            logger.info(f"Generated {len(variations)} variations")
            return variations
            
        except Exception as e:
            logger.error(f"Error generating variations: {e}")
            raise


# ==================== REEL GENERATION CLASS ====================
class ReelGenerator:
    """Handles AI video/reel generation using Replicate"""
    
    def __init__(self, api_key: str):
        """Initialize with Replicate API key"""
        if not api_key:
            raise ValueError("Replicate API key cannot be empty")
        
        # Clean the API key
        self.api_key = ''.join(api_key.split())
        
        # Validate format - Replicate keys start with 'r8_'
        if not self.api_key.startswith('r8_'):
            raise ValueError(f"Invalid API key format. Replicate keys start with 'r8_'. Your key starts with: {self.api_key[:5]}")
        
        os.environ["REPLICATE_API_TOKEN"] = self.api_key
        logger.info(f"ReelGenerator initialized successfully")
    
    def test_connection(self) -> dict:
        """Test Replicate API connection"""
        try:
            # Try to list models to test connection
            replicate.models.list()
            return {"success": True, "message": "✅ Replicate API connection successful!"}
        except Exception as e:
            return {"success": False, "message": f"❌ Connection failed: {str(e)}"}
    
    def improve_prompt(self, user_prompt: str) -> str:
        """Enhance the video generation prompt with professional terms"""
        enhancements = []
        
        # Check if prompt already has quality descriptors
        quality_terms = ['cinematic', 'professional', 'high quality', 'hd', '4k', 'detailed']
        has_quality = any(term in user_prompt.lower() for term in quality_terms)
        
        # Check if prompt has camera movement
        camera_terms = ['pan', 'zoom', 'tracking', 'dolly', 'crane', 'movement', 'motion']
        has_camera = any(term in user_prompt.lower() for term in camera_terms)
        
        # Check if prompt has lighting
        lighting_terms = ['lighting', 'light', 'bright', 'dark', 'shadow', 'glow']
        has_lighting = any(term in user_prompt.lower() for term in lighting_terms)
        
        # Add missing elements
        if not has_quality:
            enhancements.append("professional video quality, high detail, sharp focus")
        
        if not has_camera:
            enhancements.append("smooth camera movement, cinematic shot")
        
        if not has_lighting:
            enhancements.append("beautiful lighting")
        
        # Add general video enhancements
        enhancements.append("fluid motion, coherent sequence")
        
        # Combine original prompt with enhancements
        improved = f"{user_prompt}, {', '.join(enhancements)}"
        
        logger.info(f"Prompt enhanced from: '{user_prompt}' to: '{improved}'")
        
        return improved
    
    def generate_video(self, prompt: str, model: str = "zeroscope", image_url: Optional[str] = None, 
                       duration: int = 10, improve_prompt: bool = True) -> Optional[str]:
        """
        Generate video/reel using Replicate AI
        
        Args:
            prompt: Description of the video
            model: Model to use (zeroscope, animatediff, stable-video)
            image_url: Optional image to animate
            duration: Video duration in seconds (5, 10, 15, 30)
            improve_prompt: Whether to enhance the prompt with AI
        """
        try:
            logger.info(f"Starting video generation - Model: {model}, Duration: {duration}s")
            
            # Improve prompt if requested
            if improve_prompt:
                original_prompt = prompt
                prompt = self.improve_prompt(prompt)
                st.info(f"✨ Prompt enhanced for better quality!")
            
            # Model configurations with duration support
            models = {
                "zeroscope": {
                    "id": "anotherjesse/zeroscope-v2-xl:9f747673945c62801b13b84701c783929c0ee784e4748ec062204894dda1a351",
                    "params": {
                        "prompt": prompt,
                        "num_frames": duration * 8,  # 8 frames per second
                        "num_inference_steps": 50
                    }
                },
                "animatediff": {
                    "id": "lucataco/animate-diff:beecf59c4aee8d81bf04f0381033dfa10dc16e845b4ae00d281e2fa377e48a9f",
                    "params": {
                        "prompt": prompt,
                        "num_frames": min(duration * 8, 64),  # AnimateDiff max is 64 frames
                        "guidance_scale": 7.5
                    }
                },
                "stable-video": {
                    "id": "stability-ai/stable-video-diffusion:3f0457e4619daac51203dedb472816fd4af51f3149fa7a9e0b5ffcf1b8172438",
                    "params": {
                        "input_image": image_url,
                        "frames_per_second": 8,
                        "num_frames": min(duration * 8, 25),  # SVD max is 25 frames
                        "motion_bucket_id": 127
                    }
                }
            }
            
            if model not in models:
                raise ValueError(f"Unknown model: {model}. Choose from: {list(models.keys())}")
            
            model_config = models[model]
            
            logger.info(f"Running Replicate model: {model_config['id']}")
            
            # Generate video
            output = replicate.run(
                model_config['id'],
                input=model_config['params']
            )
            
            # Handle different output formats
            if isinstance(output, list) and len(output) > 0:
                video_url = output[0]
            elif isinstance(output, str):
                video_url = output
            else:
                video_url = str(output)
            
            logger.info(f"✅ Video generated successfully: {video_url}")
            return video_url
            
        except Exception as e:
            logger.error(f"❌ Error generating video: {e}")
            st.error(f"Video generation failed: {e}")
            return None


# ==================== DATABASE FUNCTIONS ====================
def init_db():
    """Initialize SQLite database with all required tables"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Posts table
    c.execute('''CREATE TABLE IF NOT EXISTS posts
                 (id TEXT PRIMARY KEY,
                  platform TEXT,
                  content TEXT,
                  image_url TEXT,
                  video_url TEXT,
                  language TEXT,
                  created_at TIMESTAMP,
                  scheduled_at TIMESTAMP,
                  status TEXT)''')
    
    # Images table
    c.execute('''CREATE TABLE IF NOT EXISTS images
                 (id TEXT PRIMARY KEY,
                  prompt TEXT,
                  url TEXT,
                  local_path TEXT,
                  created_at TIMESTAMP)''')
    
    # Videos table
    c.execute('''CREATE TABLE IF NOT EXISTS videos
                 (id TEXT PRIMARY KEY,
                  url TEXT,
                  description TEXT,
                  local_path TEXT,
                  model TEXT,
                  created_at TIMESTAMP)''')
    
    conn.commit()
    logger.info("Database initialized successfully")
    return conn


def save_post(conn, post_data: dict) -> str:
    """Save post to database"""
    post_id = str(uuid.uuid4())
    c = conn.cursor()
    c.execute('''INSERT INTO posts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (post_id, post_data['platform'], post_data['content'],
               post_data.get('image_url'), post_data.get('video_url'),
               post_data['language'], datetime.now(), None, 'draft'))
    conn.commit()
    logger.info(f"Post saved with ID: {post_id}")
    return post_id


def save_scheduled_post(conn, post_data: dict, scheduled_time: datetime) -> str:
    """Save scheduled post"""
    post_id = str(uuid.uuid4())
    c = conn.cursor()
    c.execute('''INSERT INTO posts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (post_id, post_data['platform'], post_data['content'],
               post_data.get('image_url'), post_data.get('video_url'),
               post_data['language'], datetime.now(), scheduled_time, 'scheduled'))
    conn.commit()
    logger.info(f"Scheduled post saved with ID: {post_id}")
    return post_id


def get_posts(conn, status: Optional[str] = None):
    """Retrieve posts from database"""
    c = conn.cursor()
    if status:
        c.execute('SELECT * FROM posts WHERE status = ? ORDER BY created_at DESC', (status,))
    else:
        c.execute('SELECT * FROM posts ORDER BY created_at DESC')
    return c.fetchall()


def save_image(conn, prompt: str, url: str, local_path: str) -> str:
    """Save generated image to database"""
    image_id = str(uuid.uuid4())
    c = conn.cursor()
    c.execute('''INSERT INTO images VALUES (?, ?, ?, ?, ?)''',
              (image_id, prompt, url, local_path, datetime.now()))
    conn.commit()
    logger.info(f"Image saved with ID: {image_id}")
    return image_id


def get_saved_images(conn):
    """Get all saved images"""
    c = conn.cursor()
    c.execute('SELECT * FROM images ORDER BY created_at DESC')
    return c.fetchall()


def save_video_to_db(conn, url: str, description: str, local_path: str, model: str) -> str:
    """Save generated video to database"""
    video_id = str(uuid.uuid4())
    c = conn.cursor()
    c.execute('''INSERT INTO videos VALUES (?, ?, ?, ?, ?, ?)''',
              (video_id, url, description, local_path, model, datetime.now()))
    conn.commit()
    logger.info(f"Video saved with ID: {video_id}")
    return video_id


def get_saved_videos(conn):
    """Get all saved videos"""
    c = conn.cursor()
    c.execute('SELECT * FROM videos ORDER BY created_at DESC')
    return c.fetchall()


# ==================== HELPER FUNCTIONS ====================
def download_and_save_image(url: str, filename: str) -> str:
    """Download image from URL and save locally"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        filepath = ASSETS_DIR / filename
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        logger.info(f"Image saved: {filepath}")
        return str(filepath)
    except Exception as e:
        logger.error(f"Error saving image: {e}")
        return ""


def save_video_locally(url: str, filename: str) -> str:
    """Download video from URL and save locally"""
    try:
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()
        
        filepath = ASSETS_DIR / filename
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        logger.info(f"Video saved: {filepath}")
        return str(filepath)
    except Exception as e:
        logger.error(f"Error saving video: {e}")
        return ""


def show_success(message: str):
    """Display styled success message"""
    st.markdown(f"""
    <div class="success-box">
        <h3 style="margin:0;">✅ Success!</h3>
        <p style="margin:0.5rem 0 0 0;">{message}</p>
    </div>
    """, unsafe_allow_html=True)


# ==================== SIDEBAR SETUP ====================
def setup_sidebar():
    """Setup sidebar with API configuration and settings"""
    with st.sidebar:
        st.markdown("## ⚙️ API Configuration")
        
        # OpenAI API Key
        openai_api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            help="Get your API key from https://platform.openai.com/api-keys",
            key="openai_key"
        )
        
        if openai_api_key:
            if st.button("🧪 Test OpenAI Connection", key="test_openai"):
                try:
                    gen = ContentGenerator(openai_api_key)
                    result = gen.test_connection()
                    if result['success']:
                        st.success(result['message'])
                    else:
                        st.error(result['message'])
                except Exception as e:
                    st.error(f"❌ Error: {e}")
        
        st.markdown("---")
        
        # Replicate API Key
        replicate_api_key = st.text_input(
            "Replicate API Key (for Videos)",
            type="password",
            help="Get your API key from https://replicate.com/account/api-tokens",
            key="replicate_key"
        )
        
        if replicate_api_key and REPLICATE_AVAILABLE:
            if st.button("🎬 Test Replicate Connection", key="test_replicate"):
                try:
                    reel_gen = ReelGenerator(replicate_api_key)
                    result = reel_gen.test_connection()
                    if result['success']:
                        st.success(result['message'])
                    else:
                        st.error(result['message'])
                except Exception as e:
                    st.error(f"❌ Error: {e}")
        
        st.markdown("---")
        
        # Image generation settings
        st.markdown("## 🎨 Image Settings")
        image_size = st.selectbox(
            "Image Size", 
            ["1024x1024", "1792x1024", "1024x1792"],
            help="Square, landscape, or portrait"
        )
        image_quality = st.selectbox(
            "Image Quality", 
            ["standard", "hd"],
            help="HD costs more but looks better"
        )
        image_style = st.selectbox(
            "Image Style",
            ["vivid", "natural"],
            help="Vivid: Hyper-real, dramatic. Natural: More realistic."
        )
        
        # About section
        with st.expander("ℹ️ About Platform", expanded=False):
            st.markdown("""
            ### 🚀 AI Social Media Platform v2.1
            
            **✨ Key Features:**
            - 🤖 AI content generation (5 languages)
            - 🎨 DALL-E 3 image generation
            - 🎬 AI video/reel creation
            - ⏱️ Custom durations (5-30s)
            - ✨ Auto prompt enhancement
            - 📅 Post scheduling
            - 📊 Analytics dashboard
            - 📸 Product marketing packages
            
            **🎥 Video Models:**
            - **Zeroscope**: Best for diverse content
            - **AnimateDiff**: Creative animations
            - **Stable Video**: Image-to-video
            
            **💡 Tips:**
            - Enable AI enhancement for better videos
            - Shorter videos (5-10s) = faster
            - Use Stable Video for product showcases
            
            **🔑 API Keys:**
            - OpenAI: `sk-...` (content & images)
            - Replicate: `r8_...` (videos/reels)
            
            ---
            **v2.1** | Made with ❤️ using Streamlit & AI
            """)
        
    return openai_api_key, replicate_api_key, image_size, image_quality, image_style


# ==================== MAIN APPLICATION ====================
def main():
    """Main application entry point"""
    
    # Initialize database
    conn = init_db()
    
    # Header
    st.markdown('<h1 class="main-header">🚀 AI Social Media Platform</h1>', unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666; margin-top: -1rem;'>Your Complete AI-Powered Content Creation Suite</p>", unsafe_allow_html=True)
    
    # Setup sidebar and get configuration
    openai_api_key, replicate_api_key, image_size, image_quality, image_style = setup_sidebar()
    
    # Navigation tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Overview", 
        "✨ Content Lab", 
        "📅 Scheduled Posts", 
        "🖼️ Image Assets", 
        "🎬 Videos/Reels", 
        "📈 Analytics"
    ])
    
    # ==================== TAB 1: OVERVIEW ====================
    with tab1:
        st.markdown("## 📊 Dashboard Overview")
        
        # Get metrics
        posts = get_posts(conn)
        scheduled = get_posts(conn, 'scheduled')
        images = get_saved_images(conn)
        videos = get_saved_videos(conn)
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📝 Total Posts", len(posts))
        with col2:
            st.metric("📅 Scheduled", len(scheduled))
        with col3:
            st.metric("🖼️ Images", len(images))
        with col4:
            st.metric("🎬 Videos/Reels", len(videos))
        
        st.markdown("---")
        
        # Recent activity
        st.markdown("### 📋 Recent Activity")
        if posts:
            recent_df = pd.DataFrame(posts, columns=[
                'ID', 'Platform', 'Content', 'Image', 'Video', 
                'Language', 'Created', 'Scheduled', 'Status'
            ])
            st.dataframe(
                recent_df[['Platform', 'Content', 'Language', 'Status', 'Created']].head(10),
                use_container_width=True
            )
        else:
            st.info("🎯 No posts yet. Start creating content in the Content Lab!")
    
    # ==================== TAB 2: CONTENT LAB ====================
    with tab2:
        st.markdown("## ✨ AI Content Laboratory")
        st.markdown("Create amazing content with AI - from text to images to videos!")
        
        if not openai_api_key:
            st.warning("⚠️ Please add your OpenAI API key in the sidebar to use the Content Lab!")
        else:
            try:
                content_gen = ContentGenerator(openai_api_key)
                
                # SECTION 1: Bulk Content Generation
                with st.expander("📝 Bulk Content Generation", expanded=True):
                    st.markdown("### Generate Multiple Posts at Once")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        bulk_topic = st.text_area(
                            "Content Topic/Theme",
                            "Sustainable fashion trends for 2024",
                            height=100,
                            help="What should the posts be about?"
                        )
                        bulk_platform = st.selectbox(
                            "Platform", 
                            list(PLATFORM_REQUIREMENTS.keys()), 
                            key="bulk_platform"
                        )
                        bulk_language = st.selectbox(
                            "Language", 
                            list(LANGUAGES.keys()), 
                            key="bulk_lang"
                        )
                    
                    with col2:
                        num_posts = st.slider("Number of Posts", 1, 10, 3)
                        variation_style = st.multiselect(
                            "Content Variations",
                            ["Educational", "Promotional", "Entertaining", "Inspirational", "Question-based"],
                            default=["Educational", "Promotional"]
                        )
                    
                    if st.button("🚀 Generate Bulk Content", key="bulk_gen"):
                        with st.spinner(f"✨ Generating {num_posts} posts..."):
                            progress_bar = st.progress(0)
                            generated_posts = []
                            
                            for i in range(num_posts):
                                style = variation_style[i % len(variation_style)] if variation_style else "Educational"
                                prompt = f"{bulk_topic} - {style} style"
                                
                                content = content_gen.generate_content(
                                    prompt,
                                    bulk_platform,
                                    LANGUAGES[bulk_language]
                                )
                                
                                post_data = {
                                    'platform': bulk_platform,
                                    'content': content,
                                    'language': LANGUAGES[bulk_language]
                                }
                                post_id = save_post(conn, post_data)
                                generated_posts.append((i+1, content))
                                
                                progress_bar.progress((i + 1) / num_posts)
                            
                            st.success(f"✅ Generated {num_posts} posts successfully!")
                            st.balloons()
                            
                            for idx, content in generated_posts:
                                with st.expander(f"📄 Post {idx}"):
                                    st.write(content)
                
                # SECTION 2: Generate AI Image
                with st.expander("🎨 Generate AI Image Only", expanded=False):
                    st.markdown("### Create Stunning Images with DALL-E 3")
                    
                    image_prompt = st.text_area(
                        "Describe Your Image",
                        "A serene mountain landscape at sunset with a lake reflection",
                        height=100,
                        help="Be descriptive and specific"
                    )
                    
                    if st.button("🎨 Generate AI Image", key="single_image"):
                        with st.spinner("🎨 Creating your image..."):
                            image_url = content_gen.generate_image(
                                image_prompt,
                                size=image_size,
                                quality=image_quality,
                                style=image_style
                            )
                            
                            if image_url:
                                st.image(image_url, caption="Generated Image", use_container_width=True)
                                
                                # Save image
                                filename = f"image_{int(time_module.time())}.png"
                                local_path = download_and_save_image(image_url, filename)
                                if local_path:
                                    image_id = save_image(conn, image_prompt, image_url, local_path)
                                    st.success("✅ Image generated and saved to your library!")
                                    st.balloons()
                
                # SECTION 3: Create Reels & Videos
                if REPLICATE_AVAILABLE and replicate_api_key:
                    with st.expander("🎬 Create Reels & Videos", expanded=False):
                        st.markdown("### Generate Professional Videos & Reels")
                        
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            video_model = st.selectbox(
                                "Video Model",
                                ["zeroscope", "animatediff", "stable-video"],
                                help="Zeroscope: general videos | AnimateDiff: animations | Stable Video: image-to-video"
                            )
                        
                        with col2:
                            video_duration = st.selectbox(
                                "Duration (seconds)",
                                [5, 10, 15, 30],
                                index=1,
                                help="Video length"
                            )
                        
                        video_prompt = st.text_area(
                            "Describe Your Video",
                            "A person walking on a beach at sunset, waves crashing gently",
                            height=80,
                            help="Describe the scene, action, mood"
                        )
                        
                        improve_prompt_checkbox = st.checkbox(
                            "✨ AI Prompt Enhancement",
                            value=True,
                            help="Automatically improve your prompt with professional video terms"
                        )
                        
                        use_saved_image = False
                        selected_image_url = None
                        
                        if video_model == "stable-video":
                            st.info("💡 Stable Video requires an image to animate")
                            use_saved_image = st.checkbox("Use a saved image from Assets")
                            
                            if use_saved_image:
                                saved_images = get_saved_images(conn)
                                if saved_images:
                                    image_options = {img[1]: img[2] for img in saved_images}
                                    selected_image = st.selectbox("Select Image to Animate", list(image_options.keys()))
                                    selected_image_url = image_options[selected_image]
                                else:
                                    st.warning("⚠️ No saved images found. Generate some images first!")
                        
                        if st.button("🎬 Generate Reel/Video", key="gen_video"):
                            if video_model == "stable-video" and not selected_image_url:
                                st.error("⚠️ Stable Video requires an image. Please select one!")
                            else:
                                try:
                                    with st.spinner(f"🎬 Creating your {video_duration}s video... (this may take 1-3 minutes)"):
                                        reel_gen = ReelGenerator(replicate_api_key)
                                        
                                        video_url = reel_gen.generate_video(
                                            prompt=video_prompt,
                                            model=video_model,
                                            image_url=selected_image_url,
                                            duration=video_duration,
                                            improve_prompt=improve_prompt_checkbox
                                        )
                                        
                                        if video_url:
                                            st.success(f"✅ {video_duration}s video generated successfully!")
                                            st.video(video_url)
                                            
                                            # Save video
                                            video_path = save_video_locally(video_url, f"reel_{int(time_module.time())}.mp4")
                                            if video_path:
                                                video_id = save_video_to_db(
                                                    conn, 
                                                    video_url, 
                                                    f"{video_duration}s {video_model} reel: {video_prompt[:50]}...", 
                                                    video_path, 
                                                    video_model
                                                )
                                                st.success(f"💾 Video saved to library! Duration: {video_duration}s")
                                                st.balloons()
                                        else:
                                            st.error("❌ Failed to generate video. Please try again.")
                                
                                except ValueError as ve:
                                    st.error(f"⚠️ Configuration Error: {ve}")
                                    st.info("💡 Tip: Replicate API keys start with 'r8_'")
                                except Exception as e:
                                    logger.error(f"Error in video generation: {e}")
                                    st.error(f"❌ Error: {e}")
                                    st.info("💡 Check your Replicate API key and credits")
                
                # SECTION 4: Product Upload → Marketing Package
                if REPLICATE_AVAILABLE and replicate_api_key:
                    with st.expander("📸 Upload Product Image → Generate Post & Reel", expanded=False):
                        st.markdown("### Complete Marketing Package from Product Photo")
                        st.markdown("Upload a product image to get an AI-generated caption + promotional reel!")
                        
                        uploaded_file = st.file_uploader(
                            "Upload Product Image",
                            type=['png', 'jpg', 'jpeg'],
                            key="product_upload",
                            help="Upload a clear photo of your product"
                        )
                        
                        if uploaded_file:
                            col1, col2 = st.columns([1, 2])
                            
                            with col1:
                                st.image(uploaded_file, caption="Product Preview", use_container_width=True)
                            
                            with col2:
                                st.markdown("#### Marketing Package Settings")
                                
                                platform_for_product = st.selectbox(
                                    "Platform",
                                    ["Instagram", "Facebook", "Twitter", "LinkedIn", "TikTok"],
                                    key="platform_product"
                                )
                                
                                selected_lang = st.selectbox(
                                    "Caption Language",
                                    list(LANGUAGES.keys()),
                                    key="lang_product"
                                )
                                
                                video_duration_product = st.selectbox(
                                    "Reel Duration",
                                    [5, 10, 15, 30],
                                    index=1,
                                    help="Length of promotional reel",
                                    key="duration_product"
                                )
                                
                                additional_context = st.text_input(
                                    "Product Context (optional)",
                                    placeholder="e.g., luxury watch, eco-friendly, summer collection",
                                    key="context_product"
                                )
                                
                                improve_video_prompt = st.checkbox(
                                    "✨ Enhance Video Prompt",
                                    value=True,
                                    help="AI will improve the video prompt",
                                    key="improve_product"
                                )
                            
                            st.markdown("#### Schedule Marketing Package")
                            col1, col2 = st.columns(2)
                            with col1:
                                schedule_date_product = st.date_input(
                                    "Post Date",
                                    value=datetime.now().date() + timedelta(days=1),
                                    key="date_product"
                                )
                            with col2:
                                schedule_time_product = st.time_input(
                                    "Post Time",
                                    value=datetime.now().time(),
                                    key="time_product"
                                )
                            
                            if st.button("🚀 Generate Complete Marketing Package", key="gen_product_package"):
                                try:
                                    with st.spinner("✨ Creating your marketing package..."):
                                        # Save uploaded image
                                        upload_path = ASSETS_DIR / f"product_{int(time_module.time())}_{uploaded_file.name}"
                                        with open(upload_path, "wb") as f:
                                            f.write(uploaded_file.getbuffer())
                                        
                                        # Step 1: Generate Caption
                                        st.write(f"**Step 1/3:** Generating {LANGUAGES[selected_lang]} caption...")
                                        
                                        caption_prompt = f"Create an engaging social media caption for this {additional_context if additional_context else 'product'} image for {platform_for_product}"
                                        caption = content_gen.generate_content(
                                            caption_prompt, 
                                            platform_for_product, 
                                            LANGUAGES[selected_lang], 
                                            image_path=str(upload_path),
                                            use_vision=True
                                        )
                                        
                                        st.markdown("#### 📝 Generated Caption")
                                        st.success(caption)
                                        
                                        # Step 2: Generate Reel
                                        st.write(f"**Step 2/3:** Creating {video_duration_product}s product reel...")
                                        
                                        reel_gen = ReelGenerator(replicate_api_key)
                                        video_prompt = f"Product showcase, smooth camera movement, professional marketing video, {additional_context if additional_context else 'high quality'}"
                                        
                                        video_url = reel_gen.generate_video(
                                            prompt=video_prompt,
                                            model="stable-video",
                                            image_url=str(upload_path),
                                            duration=video_duration_product,
                                            improve_prompt=improve_video_prompt
                                        )
                                        
                                        video_path = None
                                        if video_url:
                                            st.markdown(f"#### 🎬 Generated {video_duration_product}s Reel")
                                            st.video(video_url)
                                            
                                            # Step 3: Save everything
                                            st.write("**Step 3/3:** Saving everything...")
                                            video_path = save_video_locally(video_url, f"product_reel_{uploaded_file.name}")
                                            if video_path:
                                                video_id = save_video_to_db(
                                                    conn, 
                                                    video_url, 
                                                    f"{video_duration_product}s product reel from {uploaded_file.name}", 
                                                    video_path, 
                                                    "Stable Video Diffusion"
                                                )
                                        
                                        # Save scheduled post
                                        schedule_datetime = datetime.combine(schedule_date_product, schedule_time_product)
                                        post_data = {
                                            'platform': platform_for_product,
                                            'content': caption,
                                            'image_url': str(upload_path),
                                            'video_url': video_url if video_url else None,
                                            'language': LANGUAGES[selected_lang]
                                        }
                                        post_id = save_scheduled_post(conn, post_data, schedule_datetime)
                                        
                                        st.balloons()
                                        show_success(f"🎉 Complete marketing package created!\n• Caption in {LANGUAGES[selected_lang]}\n• {video_duration_product}s promotional reel\n• Scheduled for {schedule_datetime.strftime('%Y-%m-%d at %H:%M')}")
                                
                                except ValueError as ve:
                                    st.error(f"⚠️ Error: {ve}")
                                except Exception as e:
                                    logger.error(f"Error generating marketing package: {e}")
                                    st.error(f"❌ Error: {e}")
                
                # SECTION 5: Schedule Content
                with st.expander("📅 Schedule New Content", expanded=False):
                    st.markdown("### Schedule a Post for Later")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        sched_platform = st.selectbox(
                            "Platform", 
                            list(PLATFORM_REQUIREMENTS.keys()), 
                            key="sched_plat"
                        )
                        sched_language = st.selectbox(
                            "Language", 
                            list(LANGUAGES.keys()), 
                            key="sched_lang"
                        )
                        sched_topic = st.text_area(
                            "Content Topic", 
                            "Weekly newsletter announcement", 
                            key="sched_topic",
                            height=100
                        )
                    
                    with col2:
                        sched_date = st.date_input(
                            "Schedule Date", 
                            value=datetime.now().date() + timedelta(days=1),
                            key="sched_date"
                        )
                        sched_time = st.time_input(
                            "Schedule Time", 
                            value=datetime.now().time(),
                            key="sched_time"
                        )
                        use_ai_image = st.checkbox(
                            "Generate AI Image for this post",
                            key="use_ai_image"
                        )
                    
                    if st.button("📅 Schedule Post", key="schedule_btn"):
                        with st.spinner("📝 Creating and scheduling post..."):
                            # Generate content
                            content = content_gen.generate_content(
                                sched_topic,
                                sched_platform,
                                LANGUAGES[sched_language]
                            )
                            
                            image_url = None
                            if use_ai_image:
                                image_url = content_gen.generate_image(
                                    f"Social media image for: {sched_topic}",
                                    size=image_size,
                                    quality=image_quality,
                                    style=image_style
                                )
                            
                            # Schedule post
                            schedule_datetime = datetime.combine(sched_date, sched_time)
                            post_data = {
                                'platform': sched_platform,
                                'content': content,
                                'image_url': image_url,
                                'language': LANGUAGES[sched_language]
                            }
                            post_id = save_scheduled_post(conn, post_data, schedule_datetime)
                            
                            show_success(f"Post scheduled for {schedule_datetime.strftime('%Y-%m-%d at %H:%M')}!")
                            
                            st.markdown("**Generated Content:**")
                            st.info(content)
                            
                            if image_url:
                                st.image(image_url, caption="Generated Image", use_container_width=True)
            
            except Exception as e:
                st.error(f"❌ Error initializing Content Generator: {e}")
                logger.error(f"Content Generator error: {e}")
    
    # ==================== TAB 3: SCHEDULED POSTS ====================
    with tab3:
        st.markdown("## 📅 Scheduled Posts")
        
        scheduled_posts = get_posts(conn, 'scheduled')
        
        if scheduled_posts:
            st.info(f"📊 You have {len(scheduled_posts)} scheduled posts")
            
            for post in scheduled_posts:
                with st.expander(f"📝 {post[1]} - {post[7]}", expanded=False):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**Platform:** {post[1]}")
                        st.markdown(f"**Language:** {post[5]}")
                        st.markdown(f"**Scheduled:** {post[7]}")
                        st.markdown("**Content:**")
                        st.write(post[2])
                    
                    with col2:
                        if post[3]:  # Image
                            st.image(post[3], caption="Attached Image", use_container_width=True)
                        if post[4]:  # Video
                            st.video(post[4])
        else:
            st.info("📭 No scheduled posts yet! Create some in the Content Lab.")
    
    # ==================== TAB 4: IMAGE ASSETS ====================
    with tab4:
        st.markdown("## 🖼️ Image Asset Library")
        
        saved_images = get_saved_images(conn)
        
        if saved_images:
            st.success(f"📊 Total Images: {len(saved_images)}")
            
            # Display in grid
            cols = st.columns(3)
            for idx, img in enumerate(saved_images):
                with cols[idx % 3]:
                    st.image(img[2], caption=img[1][:50] + "...", use_container_width=True)
                    st.caption(f"🕒 Created: {img[4]}")
        else:
            st.info("🎨 No images saved yet. Generate some in the Content Lab!")
    
    # ==================== TAB 5: VIDEOS/REELS ====================
    with tab5:
        st.markdown("## 🎬 Videos & Reels Library")
        
        saved_videos = get_saved_videos(conn)
        
        if saved_videos:
            st.success(f"📊 Total Videos: {len(saved_videos)}")
            
            for video in saved_videos:
                with st.expander(f"🎬 {video[2]}", expanded=False):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.video(video[1])
                    
                    with col2:
                        st.markdown(f"**Description:** {video[2]}")
                        st.markdown(f"**Model:** {video[4]}")
                        st.markdown(f"**Created:** {video[5]}")
                        st.markdown(f"**Local Path:** `{video[3]}`")
        else:
            st.info("🎥 No videos saved yet. Generate reels in the Content Lab!")
    
    # ==================== TAB 6: ANALYTICS ====================
    with tab6:
        st.markdown("## 📈 Analytics Dashboard")
        
        posts = get_posts(conn)
        
        if posts:
            df = pd.DataFrame(posts, columns=[
                'ID', 'Platform', 'Content', 'Image', 'Video', 
                'Language', 'Created', 'Scheduled', 'Status'
            ])
            
            # Row 1: Platform and Language Distribution
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📱 Posts by Platform")
                platform_counts = df['Platform'].value_counts()
                fig = px.pie(
                    values=platform_counts.values, 
                    names=platform_counts.index, 
                    title="Content Distribution by Platform",
                    hole=0.3
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("### 🌍 Posts by Language")
                lang_counts = df['Language'].value_counts()
                fig = px.bar(
                    x=lang_counts.index, 
                    y=lang_counts.values,
                    title="Language Distribution",
                    labels={'x': 'Language', 'y': 'Count'},
                    color=lang_counts.values,
                    color_continuous_scale='Viridis'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Row 2: Timeline
            st.markdown("### 📅 Content Creation Timeline")
            df['Created'] = pd.to_datetime(df['Created'])
            timeline_data = df.groupby(df['Created'].dt.date).size().reset_index()
            timeline_data.columns = ['Date', 'Count']
            
            fig = px.line(
                timeline_data, 
                x='Date', 
                y='Count',
                title="Posts Created Over Time",
                markers=True
            )
            fig.update_traces(line_color='#667eea', line_width=3)
            st.plotly_chart(fig, use_container_width=True)
            
            # Row 3: Status breakdown
            st.markdown("### 📊 Post Status")
            status_counts = df['Status'].value_counts()
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("📝 Draft", status_counts.get('draft', 0))
            with col2:
                st.metric("📅 Scheduled", status_counts.get('scheduled', 0))
            with col3:
                st.metric("✅ Published", status_counts.get('published', 0))
            
        else:
            st.info("📊 No analytics data available yet. Start creating content to see insights!")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: #888;'>Made with ❤️ using Streamlit & AI | v2.1</p>", 
        unsafe_allow_html=True
    )


# ==================== APPLICATION ENTRY POINT ====================
if __name__ == "__main__":
    main()
