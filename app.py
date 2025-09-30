#!/usr/bin/env python3
"""
AI Social Media Platform - Fixed Version
Working sidebar, image generation, and professional prompt engineering
"""

import streamlit as st
import sqlite3
import json
import uuid
import random
from datetime import datetime
from typing import Dict, Optional
import logging

# OpenAI Integration
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    st.error("Please install OpenAI: pip install openai")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="AI Social Platform",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Simple, clean CSS that ensures sidebar visibility
st.markdown("""
<style>
    .main { padding: 2rem; }
    .stMetric { background: white; padding: 1rem; border-radius: 8px; border: 1px solid #e0e0e0; }
    .platform-badge {
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        color: white;
        display: inline-block;
        margin: 2px;
    }
    .badge-twitter { background: #1d9bf0; }
    .badge-instagram { background: #e4405f; }
    .badge-facebook { background: #1877f2; }
    .badge-linkedin { background: #0a66c2; }
</style>
""", unsafe_allow_html=True)

def init_session():
    """Initialize session state"""
    if 'posts' not in st.session_state:
        st.session_state.posts = []
    if 'api_calls' not in st.session_state:
        st.session_state.api_calls = 0
    if 'images_generated' not in st.session_state:
        st.session_state.images_generated = 0

class PromptEngineer:
    """Professional prompt engineering for DALL-E"""
    
    @staticmethod
    def enhance_prompt(user_input: str, platform: str) -> str:
        """
        Transform simple user input into professional DALL-E prompt
        """
        
        # Platform-specific style parameters
        platform_styles = {
            'instagram': {
                'aspect': 'square composition, Instagram aesthetic',
                'mood': 'vibrant, eye-catching, highly engaging',
                'quality': 'ultra-high resolution, professional photography'
            },
            'twitter': {
                'aspect': 'wide composition, Twitter card format',
                'mood': 'clean, modern, attention-grabbing',
                'quality': 'crisp, high-definition, professional'
            },
            'facebook': {
                'aspect': 'landscape composition, Facebook-optimized',
                'mood': 'warm, inviting, community-friendly',
                'quality': 'high-resolution, professional quality'
            },
            'linkedin': {
                'aspect': 'professional composition, corporate format',
                'mood': 'sophisticated, business-appropriate, polished',
                'quality': 'executive-level quality, premium finish'
            }
        }
        
        style = platform_styles.get(platform.lower(), platform_styles['instagram'])
        
        # Build comprehensive professional prompt
        enhanced = f"""
{user_input}, 
{style['aspect']}, 
{style['mood']} visual style, 
{style['quality']}, 
professional studio lighting with soft shadows, 
perfect color grading and balance, 
trending on Behance and Dribbble, 
award-winning composition, 
crystal clear focus, 
cinematic depth of field, 
modern aesthetic with premium feel, 
expertly crafted, 
publication-ready quality, 
8K resolution, 
masterpiece-level detail
""".strip()
        
        return enhanced

class ContentGenerator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = None
        
        if api_key and api_key != "demo" and OPENAI_AVAILABLE:
            try:
                self.client = OpenAI(api_key=api_key)
            except Exception as e:
                st.error(f"OpenAI initialization failed: {str(e)}")
    
    def generate_content(self, topic: str, platform: str, tone: str) -> Dict:
        """Generate text content"""
        
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": f"You are an expert {platform} content creator. Create engaging posts in a {tone} tone."},
                        {"role": "user", "content": f"Create a {platform} post about: {topic}. Include relevant hashtags."}
                    ],
                    temperature=0.8,
                    max_tokens=300
                )
                
                content = response.choices[0].message.content
                
                return {
                    'text': content,
                    'method': 'OpenAI GPT-4',
                    'engagement': 'Very High'
                }
                
            except Exception as e:
                st.error(f"Content generation error: {str(e)}")
                return self._fallback_content(topic, platform)
        
        return self._fallback_content(topic, platform)
    
    def _fallback_content(self, topic: str, platform: str) -> Dict:
        """Fallback content generation"""
        return {
            'text': f"Exploring {topic} and its impact on the future of technology. What are your thoughts? #AI #Innovation #Technology",
            'method': 'Template',
            'engagement': 'Medium'
        }
    
    def generate_image(self, user_prompt: str, platform: str) -> Optional[Dict]:
        """Generate image with professional prompt engineering"""
        
        if not self.client:
            st.error("OpenAI client not initialized. Check your API key.")
            return None
        
        try:
            # Enhance the prompt professionally
            enhanced_prompt = PromptEngineer.enhance_prompt(user_prompt, platform)
            
            # Display what we're doing
            with st.expander("🔍 View Prompt Engineering", expanded=True):
                st.markdown("**Your Input:**")
                st.info(user_prompt)
                st.markdown("**AI-Enhanced Professional Prompt:**")
                st.success(enhanced_prompt)
            
            # Generate image
            st.info("Generating image with DALL-E 3...")
            
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=enhanced_prompt,
                size="1024x1024",
                quality="standard",
                n=1
            )
            
            image_url = response.data[0].url
            
            return {
                'url': image_url,
                'original_prompt': user_prompt,
                'enhanced_prompt': enhanced_prompt
            }
            
        except Exception as e:
            st.error(f"Image generation failed: {str(e)}")
            logger.error(f"DALL-E error: {e}")
            return None

def main():
    init_session()
    
    # Title
    st.title("🤖 AI Social Media Platform")
    st.caption("Professional Content Generation with OpenAI GPT-4 & DALL-E 3")
    
    # ========== SIDEBAR ==========
    with st.sidebar:
        st.header("⚙️ Control Panel")
        
        # API Configuration
        st.subheader("🔑 API Configuration")
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            help="Get your API key from https://platform.openai.com/api-keys"
        )
        
        # API Status
        if not api_key:
            st.error("⛔ No API Key")
            api_status = "Inactive"
        elif not OPENAI_AVAILABLE:
            st.error("⛔ OpenAI not installed")
            api_status = "Error"
        else:
            st.success("✅ API Active")
            api_status = "Active"
        
        st.metric("API Status", api_status)
        st.metric("API Calls", st.session_state.api_calls)
        st.metric("Images Created", st.session_state.images_generated)
        
        st.divider()
        
        # Content Settings
        st.subheader("📝 Settings")
        
        tone = st.selectbox(
            "Content Tone",
            ["Professional", "Casual", "Inspirational", "Educational"]
        )
        
        st.divider()
        
        # Platform Selection
        st.subheader("📱 Platforms")
        
        platforms = {}
        platforms['Twitter'] = st.checkbox("🐦 Twitter", value=True)
        platforms['Instagram'] = st.checkbox("📸 Instagram", value=True)
        platforms['Facebook'] = st.checkbox("👥 Facebook", value=False)
        platforms['LinkedIn'] = st.checkbox("💼 LinkedIn", value=False)
        
        active_platforms = sum(platforms.values())
        st.info(f"{active_platforms} platforms active")
        
        st.divider()
        
        # Info
        st.caption("v5.2 - Enhanced Prompt Engineering")
    
    # ========== MAIN CONTENT ==========
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Posts Generated", len(st.session_state.posts))
    with col2:
        st.metric("API Calls", st.session_state.api_calls)
    with col3:
        st.metric("Images Created", st.session_state.images_generated)
    
    st.divider()
    
    # Content Creation
    st.header("🎨 Content Studio")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Create Content")
        
        with st.form("content_form"):
            topic = st.text_input(
                "Content Topic",
                placeholder="e.g., AI in Healthcare, Future of Work, etc."
            )
            
            platform = st.selectbox(
                "Target Platform",
                ["Twitter", "Instagram", "Facebook", "LinkedIn"]
            )
            
            st.markdown("---")
            
            # Image Generation
            generate_image = st.checkbox("🎨 Generate AI Image with DALL-E 3")
            
            if generate_image:
                st.info("💡 Enter a simple description - AI will create a professional prompt")
                
                image_description = st.text_area(
                    "Simple Image Description",
                    placeholder="Examples:\n- Modern office with AI technology\n- Abstract data visualization\n- Futuristic workspace\n- Team collaboration concept",
                    height=100
                )
                
                st.caption("Pro tip: Keep it simple. The AI will add professional details automatically.")
            
            submitted = st.form_submit_button("🚀 Generate Content", type="primary")
            
            if submitted:
                if not topic:
                    st.error("Please enter a topic")
                elif generate_image and not image_description:
                    st.error("Please enter an image description")
                else:
                    if not api_key:
                        st.error("Please enter your OpenAI API key in the sidebar")
                    else:
                        with st.spinner("Creating your content..."):
                            generator = ContentGenerator(api_key)
                            
                            # Generate text content
                            content = generator.generate_content(topic, platform, tone)
                            
                            if content['method'] == 'OpenAI GPT-4':
                                st.session_state.api_calls += 1
                            
                            # Generate image if requested
                            image_data = None
                            if generate_image:
                                image_data = generator.generate_image(image_description, platform)
                                if image_data:
                                    st.session_state.images_generated += 1
                                    st.session_state.api_calls += 1
                            
                            # Create post
                            post = {
                                'id': str(uuid.uuid4()),
                                'platform': platform,
                                'topic': topic,
                                'content': content['text'],
                                'method': content['method'],
                                'engagement': content['engagement'],
                                'image_url': image_data['url'] if image_data else None,
                                'image_prompt_original': image_data['original_prompt'] if image_data else None,
                                'image_prompt_enhanced': image_data['enhanced_prompt'] if image_data else None,
                                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M')
                            }
                            
                            st.session_state.posts.insert(0, post)
                            
                            st.success("Content generated successfully!")
                            st.balloons()
                            st.rerun()
    
    with col2:
        st.subheader("Generated Content")
        
        if st.session_state.posts:
            for post in st.session_state.posts[:5]:
                with st.expander(f"{post['platform']} - {post['topic']}", expanded=True):
                    # Platform badge
                    badge_class = f"badge-{post['platform'].lower()}"
                    st.markdown(f'<span class="platform-badge {badge_class}">{post["platform"]}</span>', unsafe_allow_html=True)
                    
                    # Image if exists
                    if post.get('image_url'):
                        st.image(post['image_url'], use_column_width=True)
                        
                        # Show prompt engineering details
                        with st.expander("🔍 Prompt Engineering Details"):
                            st.markdown("**Original Input:**")
                            st.code(post['image_prompt_original'])
                            st.markdown("**AI-Enhanced Professional Prompt:**")
                            st.code(post['image_prompt_enhanced'])
                    
                    # Content
                    st.markdown("**Content:**")
                    st.write(post['content'])
                    
                    # Metrics
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("Engagement", post['engagement'])
                    with col_b:
                        st.metric("Method", post['method'])
                    with col_c:
                        st.caption(post['created_at'])
        else:
            st.info("No posts yet. Create your first one!")
            st.markdown("""
            **Tips for great images:**
            - Use simple, clear descriptions
            - Let AI handle the technical details
            - Specify the main subject clearly
            - Examples: "modern office", "abstract tech", "team meeting"
            """)

if __name__ == "__main__":
    main()
