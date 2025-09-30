#!/usr/bin/env python3
"""
AI Social Media Platform - OpenAI Integration
With Advanced Prompt Engineering for Image Generation
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
st.set_page_config(
    page_title="AI Social Media Platform",
    page_icon="🤖", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern Professional CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    [data-testid="stSidebar"] {
        display: block !important;
        min-width: 21rem !important;
    }
    
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
    }
    
    .sidebar-section {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
    }
    
    .sidebar-section h3 {
        color: #1e293b;
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #3b82f6;
    }
    
    .api-status-active {
        background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
        color: #166534;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        font-weight: 600;
        margin: 0.5rem 0;
        border: 2px solid #22c55e;
    }
    
    .api-status-demo {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        color: #92400e;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        font-weight: 600;
        margin: 0.5rem 0;
        border: 2px solid #f59e0b;
    }
    
    .api-status-error {
        background: linear-gradient(135deg, #fecaca 0%, #fca5a5 100%);
        color: #dc2626;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        font-weight: 600;
        margin: 0.5rem 0;
        border: 2px solid #ef4444;
    }
    
    .metric-card {
        background: white;
        padding: 2rem 1.5rem;
        border-radius: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.15);
        border-color: #3b82f6;
    }
    
    .metric-value {
        font-size: 2.25rem;
        font-weight: 700;
        color: #0f172a;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        color: #64748b;
        font-size: 0.875rem;
        font-weight: 500;
        text-transform: uppercase;
    }
    
    .content-card {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        margin-bottom: 1.5rem;
    }
    
    .platform-badge {
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 0.75rem;
        font-weight: 600;
        color: white;
        margin: 2px;
        display: inline-block;
    }
    
    .badge-twitter { background: linear-gradient(135deg, #1d9bf0 0%, #1a91da 100%); }
    .badge-instagram { background: linear-gradient(135deg, #e4405f 0%, #c13584 100%); }
    .badge-facebook { background: linear-gradient(135deg, #1877f2 0%, #166fe5 100%); }
    .badge-linkedin { background: linear-gradient(135deg, #0a66c2 0%, #004182 100%); }
    
    .prompt-enhancement {
        background: #f8fafc;
        border-left: 4px solid #3b82f6;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .prompt-label {
        font-weight: 600;
        color: #3b82f6;
        font-size: 0.875rem;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

def init_session_state():
    """Initialize session state"""
    defaults = {
        'posts_generated_today': 0,
        'total_engagement': 8431,
        'success_rate': 99.2,
        'generated_posts': [],
        'current_topic': 'AI Innovation',
        'api_calls_count': 0,
        'images_generated': 0
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
                platform TEXT NOT NULL,
                content TEXT NOT NULL,
                hashtags TEXT,
                created_at TEXT NOT NULL,
                engagement_prediction TEXT,
                topic TEXT,
                style TEXT,
                generated_by TEXT,
                image_url TEXT
            )
        ''')
        
        conn.commit()
        return conn
    except Exception as e:
        logger.error(f"Database error: {e}")
        return None

class ContentGenerator:
    def __init__(self, api_key: str = "demo"):
        self.api_key = api_key
        self.client = None
        
        if api_key and api_key != "demo" and OPENAI_AVAILABLE:
            try:
                self.client = OpenAI(api_key=api_key)
                logger.info("OpenAI client initialized")
            except Exception as e:
                logger.error(f"OpenAI error: {e}")
                self.client = None
        
        self.templates = {
            'twitter': [
                "🚀 {topic} is revolutionizing the future! Innovation potential is incredible.",
                "💡 Breaking: {topic} developments are reshaping entire industries.",
                "🔥 The {topic} revolution is here! What changes are you seeing?"
            ],
            'instagram': [
                "✨ Diving deep into {topic} today! Discover the innovations ➡️",
                "🌟 {topic} continues to amaze with groundbreaking developments!"
            ],
            'facebook': [
                "🎉 Exciting developments in {topic}! Here's a breakdown...",
                "💬 How is {topic} impacting your daily life?"
            ],
            'linkedin': [
                "Professional insight: {topic} is revolutionizing industries.",
                "Market analysis: The {topic} sector shows remarkable growth."
            ]
        }
    
    def enhance_image_prompt(self, simple_prompt: str, platform: str = "instagram") -> Dict[str, str]:
        """
        Transform simple user request into professional DALL-E prompt using AI
        """
        if self.client:
            try:
                # Use GPT-4 to enhance the prompt
                enhancement_request = f"""Transform this simple image request into a detailed, professional DALL-E prompt optimized for social media ({platform}).

User's request: "{simple_prompt}"

Create a detailed prompt that includes:
- Main subject and action
- Visual style (modern, professional, vibrant, etc.)
- Composition and framing
- Lighting and atmosphere
- Color palette
- Quality descriptors (high-resolution, professional, etc.)
- Platform-appropriate aesthetics

Make it concise but detailed (max 150 words). Focus on creating visually stunning, social media-ready imagery.

Return ONLY the enhanced prompt, no explanations."""

                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are an expert prompt engineer specializing in DALL-E image generation for social media."},
                        {"role": "user", "content": enhancement_request}
                    ],
                    temperature=0.7,
                    max_tokens=200
                )
                
                enhanced_prompt = response.choices[0].message.content.strip()
                
                return {
                    'original': simple_prompt,
                    'enhanced': enhanced_prompt,
                    'method': 'AI Enhanced'
                }
                
            except Exception as e:
                logger.error(f"Prompt enhancement error: {e}")
                # Fall back to template-based enhancement
                return self.enhance_image_prompt_template(simple_prompt, platform)
        else:
            # Use template-based enhancement
            return self.enhance_image_prompt_template(simple_prompt, platform)
    
    def enhance_image_prompt_template(self, simple_prompt: str, platform: str = "instagram") -> Dict[str, str]:
        """
        Fallback: Template-based prompt enhancement
        """
        # Platform-specific style guides
        platform_styles = {
            'instagram': 'vibrant colors, Instagram-worthy composition, professional photography style, eye-catching',
            'twitter': 'clean, modern aesthetic, professional look, Twitter card optimized',
            'facebook': 'warm and inviting, community-focused aesthetic, engaging visual style',
            'linkedin': 'professional, corporate aesthetic, business-appropriate, sophisticated look'
        }
        
        style = platform_styles.get(platform.lower(), platform_styles['instagram'])
        
        # Build enhanced prompt
        enhanced = f"{simple_prompt}, {style}, high-resolution, professionally composed, perfect lighting, trending on social media, digital art, stunning visual quality, sharp focus, 4K quality"
        
        return {
            'original': simple_prompt,
            'enhanced': enhanced,
            'method': 'Template Enhanced'
        }
    
    def generate_content(self, topic: str, platform: str, tone: str = "professional") -> Dict[str, Any]:
        """Generate content"""
        if not topic:
            raise ValueError("Topic required")
        
        # Try OpenAI if available
        if self.client:
            try:
                prompt = f"Create an engaging {platform} post about {topic}. Tone: {tone}. Include relevant hashtags. Keep it concise and impactful."
                
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are an expert social media content creator."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.8,
                    max_tokens=300
                )
                
                content_text = response.choices[0].message.content
                
                return {
                    'text': content_text,
                    'hashtags': ["#AI", "#Innovation", "#Tech"],
                    'platform': platform,
                    'topic': topic,
                    'engagement_prediction': 'High',
                    'generated_by': 'OpenAI GPT-4'
                }
            except Exception as e:
                logger.error(f"OpenAI failed: {e}")
        
        # Fallback to template
        template = random.choice(self.templates.get(platform.lower(), self.templates['twitter']))
        content = template.format(topic=topic)
        
        return {
            'text': content,
            'hashtags': ["#AI", "#Innovation", "#Tech"],
            'platform': platform,
            'topic': topic,
            'engagement_prediction': 'Medium',
            'generated_by': 'Template'
        }
    
    def generate_image(self, prompt: str, platform: str = "instagram") -> Optional[Dict[str, Any]]:
        """
        Generate image with DALL-E using enhanced prompt
        """
        if not self.client:
            return None
        
        try:
            # Enhance the prompt first
            prompt_data = self.enhance_image_prompt(prompt, platform)
            enhanced_prompt = prompt_data['enhanced']
            
            logger.info(f"Original prompt: {prompt_data['original']}")
            logger.info(f"Enhanced prompt: {enhanced_prompt}")
            
            # Generate image with enhanced prompt
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=enhanced_prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            
            return {
                'url': response.data[0].url,
                'original_prompt': prompt_data['original'],
                'enhanced_prompt': enhanced_prompt,
                'enhancement_method': prompt_data['method']
            }
            
        except Exception as e:
            logger.error(f"DALL-E error: {e}")
            return None

def main():
    """Main application"""
    init_session_state()
    conn = get_database_connection()
    
    # Header
    st.markdown("""
    <div class="modern-header">
        <div class="header-content">
            <div class="header-left">
                <h1>🤖 AI Social Media Platform</h1>
                <p>OpenAI-Powered Content Generation with Smart Prompt Engineering</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # SIDEBAR
    with st.sidebar:
        st.title("⚙️ Control Panel")
        
        # API Configuration
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("### 🔑 API Configuration")
        
        api_key = st.text_input(
            "OpenAI API Key", 
            type="password",
            help="Enter your OpenAI API key from https://platform.openai.com/api-keys"
        )
        
        # API Status Display
        if not api_key:
            st.markdown('<div class="api-status-error">❌ No API Key - Template Mode</div>', unsafe_allow_html=True)
            api_mode = "Template Mode"
        elif api_key == "demo":
            st.markdown('<div class="api-status-demo">⚠️ Demo Mode Active</div>', unsafe_allow_html=True)
            api_mode = "Template Mode"
        elif not OPENAI_AVAILABLE:
            st.markdown('<div class="api-status-error">❌ OpenAI Not Installed</div>', unsafe_allow_html=True)
            st.error("Run: pip install openai")
            api_mode = "Error"
        else:
            st.markdown('<div class="api-status-active">✅ OpenAI API Active</div>', unsafe_allow_html=True)
            api_mode = "OpenAI GPT-4 + DALL-E"
        
        st.metric("Current Mode", api_mode)
        st.metric("API Calls Today", st.session_state.api_calls_count)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Content Settings
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("### 📝 Content Settings")
        
        topic_input = st.text_input("Quick Topic", placeholder="Enter a topic...")
        
        tone = st.selectbox(
            "Content Tone",
            ["Professional", "Casual", "Inspirational", "Educational"]
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Platform Selection
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("### 📱 Platforms")
        
        twitter = st.checkbox("🐦 Twitter", value=True)
        instagram = st.checkbox("📸 Instagram", value=True)
        facebook = st.checkbox("👥 Facebook", value=True)
        linkedin = st.checkbox("💼 LinkedIn", value=True)
        
        active_count = sum([twitter, instagram, facebook, linkedin])
        st.info(f"✅ {active_count}/4 platforms active")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Quick Actions
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("### ⚡ Quick Actions")
        
        if st.button("🚀 Generate Content", type="primary", use_container_width=True):
            if topic_input:
                st.session_state.current_topic = topic_input
                st.success(f"Topic set: {topic_input}")
            else:
                st.warning("Enter a topic first")
        
        if st.button("🎨 Generate Image", use_container_width=True):
            if api_mode == "OpenAI GPT-4 + DALL-E":
                st.info("Image generation ready")
            else:
                st.error("OpenAI API required")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # MAIN CONTENT
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{st.session_state.posts_generated_today}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Posts Generated</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{st.session_state.api_calls_count}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">API Calls</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{st.session_state.images_generated}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Images Created</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{active_count}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Active Platforms</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Content Generation
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown("### 🎨 Content Studio with Smart Prompt Engineering")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### Create Content")
        
        topic = st.text_input("Topic", value=st.session_state.current_topic)
        platform = st.selectbox("Platform", ["Twitter", "Instagram", "Facebook", "LinkedIn"])
        
        generate_image = st.checkbox("🖼️ Generate AI Image (DALL-E 3)")
        if generate_image:
            st.info("💡 Tip: Enter a simple description - our AI will enhance it into a professional prompt")
            image_prompt = st.text_area(
                "Simple Image Description", 
                placeholder="Example: 'futuristic AI workspace' or 'abstract technology concept'",
                help="Enter a simple description. AI will automatically enhance it with professional details."
            )
        
        if st.button("🚀 Generate", type="primary"):
            if topic:
                try:
                    with st.spinner("Creating content..."):
                        generator = ContentGenerator(api_key)
                        content = generator.generate_content(topic, platform, tone)
                        
                        # Generate image if requested
                        image_data = None
                        if generate_image and api_key != "demo" and image_prompt:
                            with st.spinner("🎨 Enhancing prompt and generating image..."):
                                image_data = generator.generate_image(image_prompt, platform)
                                
                                if image_data:
                                    st.session_state.images_generated += 1
                                    
                                    # Show prompt enhancement
                                    st.markdown('<div class="prompt-enhancement">', unsafe_allow_html=True)
                                    st.markdown('<div class="prompt-label">Original Prompt:</div>', unsafe_allow_html=True)
                                    st.text(image_data['original_prompt'])
                                    st.markdown('<div class="prompt-label">AI Enhanced Prompt:</div>', unsafe_allow_html=True)
                                    st.text(image_data['enhanced_prompt'])
                                    st.caption(f"Enhancement Method: {image_data['enhancement_method']}")
                                    st.markdown('</div>', unsafe_allow_html=True)
                        
                        new_post = {
                            'id': str(uuid.uuid4()),
                            'platform': platform,
                            'topic': topic,
                            'content': content['text'],
                            'hashtags': content['hashtags'],
                            'created_at': datetime.now().isoformat(),
                            'engagement_prediction': content['engagement_prediction'],
                            'generated_by': content.get('generated_by', 'Template'),
                            'image_url': image_data['url'] if image_data else None,
                            'image_prompt_original': image_data['original_prompt'] if image_data else None,
                            'image_prompt_enhanced': image_data['enhanced_prompt'] if image_data else None
                        }
                        
                        st.session_state.generated_posts.insert(0, new_post)
                        st.session_state.posts_generated_today += 1
                        
                        if content.get('generated_by') == 'OpenAI GPT-4':
                            st.session_state.api_calls_count += 1
                        
                        if conn:
                            cursor = conn.cursor()
                            cursor.execute('''
                                INSERT INTO posts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                new_post['id'], new_post['platform'], new_post['content'],
                                json.dumps(new_post['hashtags']), new_post['created_at'],
                                new_post['engagement_prediction'], new_post['topic'],
                                'Standard', new_post['generated_by'], new_post.get('image_url')
                            ))
                            conn.commit()
                        
                        st.success(f"✅ Generated by {content.get('generated_by')}!")
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            else:
                st.error("Enter a topic")
    
    with col2:
        st.markdown("#### Generated Posts")
        
        if st.session_state.generated_posts:
            for post in st.session_state.generated_posts[:5]:
                with st.expander(f"{post['platform']} - {post['topic']}", expanded=False):
                    platform_class = f"badge-{post['platform'].lower()}"
                    st.markdown(f'<span class="platform-badge {platform_class}">{post["platform"]}</span>', unsafe_allow_html=True)
                    
                    if post.get('image_url'):
                        st.image(post['image_url'], use_column_width=True)
                        
                        # Show prompt details if available
                        if post.get('image_prompt_enhanced'):
                            with st.expander("🔍 View Prompt Details"):
                                st.markdown("**Original Prompt:**")
                                st.text(post.get('image_prompt_original', 'N/A'))
                                st.markdown("**AI Enhanced Prompt:**")
                                st.text(post.get('image_prompt_enhanced', 'N/A'))
                    
                    st.write(post['content'])
                    st.markdown(f"**Hashtags:** {' '.join(post['hashtags'])}")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("Engagement", post['engagement_prediction'])
                    with col_b:
                        st.metric("Generated By", post['generated_by'])
        else:
            st.info("No posts yet. Generate your first one!")
            st.markdown("**Tips:**")
            st.markdown("• For images, use simple descriptions")
            st.markdown("• AI will enhance your prompts automatically")
            st.markdown("• Platform-optimized styling applied")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("**AI Social Media Platform v5.1** - Powered by OpenAI GPT-4 & DALL-E 3 with Smart Prompt Engineering")

if __name__ == "__main__":
    main()
