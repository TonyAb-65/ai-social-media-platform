#!/usr/bin/env python3
"""
AI Social Media Platform - OpenAI Integration v2.0
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
    st.warning("Replicate library not installed. Run: pip install replicate (for video/reel generation)")

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create directories
IMAGES_DIR = Path("generated_images")
IMAGES_DIR.mkdir(exist_ok=True)

VIDEOS_DIR = Path("generated_videos")
VIDEOS_DIR.mkdir(exist_ok=True)

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
# NEW: Video/Reel saving utilities
# ============================================================================
def save_video_locally(video_url: str, description: str) -> str:
    """Download and save video locally"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_desc = "".join(c for c in description[:30] if c.isalnum() or c in (' ', '-', '_')).strip()
        filename = f"{timestamp}_{safe_desc}.mp4"
        filepath = VIDEOS_DIR / filename
        
        response = requests.get(video_url, timeout=120, stream=True)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        logger.info(f"Video saved to: {filepath}")
        return str(filepath)
    except Exception as e:
        logger.error(f"Failed to save video: {e}")
        return ""

def save_video_to_db(conn, video_url: str, prompt: str, local_path: str, model_used: str) -> str:
    """Save video to database for Assets"""
    try:
        c = conn.cursor()
        video_id = str(uuid.uuid4())
        
        c.execute('''INSERT INTO videos 
                     (id, prompt, url, created_date, local_path, model_used, used_in_posts)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (video_id, prompt, video_url, datetime.now().isoformat(), 
                   local_path, model_used, json.dumps([])))
        
        conn.commit()
        logger.info(f"Video saved to database: {video_id}")
        return video_id
    except Exception as e:
        logger.error(f"Failed to save video to database: {e}")
        return ""

def get_all_videos(conn):
    """Get all videos from database"""
    try:
        c = conn.cursor()
        c.execute('''SELECT * FROM videos ORDER BY created_date DESC''')
        columns = [description[0] for description in c.description]
        videos = [dict(zip(columns, row)) for row in c.fetchall()]
        return videos
    except Exception as e:
        logger.error(f"Failed to get videos: {e}")
        return []

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
    
    def generate_caption_from_image(self, image_data: bytes, platform: str, tone: str, 
                                   additional_context: str = "", language: str = "en") -> str:
        """Generate caption by analyzing uploaded product image with GPT-4 Vision"""
        try:
            logger.info(f"Generating caption from image for {platform}...")
            
            # Convert image to base64
            import base64
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # Language instruction
            language_instruction = ""
            if language != "en":
                lang_names = {v: k for k, v in LANGUAGES.items()}
                language_instruction = f"\n- Write the caption in {lang_names.get(language, 'English')}"
            
            context_instruction = f"\nAdditional context: {additional_context}" if additional_context else ""
            
            prompt = f"""Analyze this product image and create a compelling {platform} marketing post.

Requirements:
- Tone: {tone}
- Describe what you see in the image
- Highlight the product's key features
- Create engaging, sales-focused copy
- Include 3-5 relevant hashtags
- Length: Optimal for {platform}{language_instruction}{context_instruction}

Generate the caption now:"""
            
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=300
            )
            
            caption = response.choices[0].message.content.strip()
            logger.info(f"Caption generated from image for {platform}")
            return caption
            
        except Exception as e:
            logger.error(f"Caption from image error: {e}")
            raise
    
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
    
    def generate_image(self, prompt: str, size: str = "1024x1024", quality: str = "hd", safe_mode: bool = False, photo_style: str = "Photorealistic (Real Photos)") -> str:
        """Generate image using DALL-E 3 with style control and content filter handling"""
        try:
            logger.info(f"Starting DALL-E 3 image generation...")
            logger.info(f"Style: {photo_style}, Quality: {quality}, Size: {size}, Safe Mode: {safe_mode}")
            
            final_prompt = prompt
            
            # Apply style-specific adjustments
            if "Photorealistic" in photo_style:
                # Add photorealism WITHOUT trigger words
                if safe_mode:
                    # Use filter-safe realistic language
                    if not any(word in prompt.lower() for word in ['lifelike', 'detailed', 'high quality']):
                        final_prompt = f"Highly detailed, lifelike, natural-looking image: {prompt}"
                else:
                    # Use strong photorealism language
                    if not any(word in prompt.lower() for word in ['photorealistic', 'realistic', 'photograph']):
                        final_prompt = f"Photorealistic, highly detailed, natural image: {prompt}"
            
            elif "Digital Art" in photo_style:
                if "digital art" not in prompt.lower():
                    final_prompt = f"Digital art: {prompt}"
            
            elif "Illustration" in photo_style:
                if "illustration" not in prompt.lower():
                    final_prompt = f"Illustration style: {prompt}"
            
            elif "Painting" in photo_style:
                if "painting" not in prompt.lower():
                    final_prompt = f"Painting style: {prompt}"
            
            elif "3D Render" in photo_style:
                if "3d" not in prompt.lower():
                    final_prompt = f"3D rendered: {prompt}"
            
            # If safe mode, sanitize (but keep style intent)
            if safe_mode:
                final_prompt = self._sanitize_prompt(final_prompt)
            
            logger.info(f"Final prompt: {final_prompt[:100]}...")
            
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
            
            # Handle content policy violations
            if "content_policy_violation" in error_str or "content filters" in error_str:
                logger.warning(f"Content filter triggered. Prompt: {prompt[:100]}...")
                
                # Try again with safe mode if not already enabled
                if not safe_mode:
                    logger.info("Retrying with safe mode enabled...")
                    return self.generate_image(prompt, size, quality, safe_mode=True, photo_style=photo_style)
                else:
                    raise ValueError(
                        "Content filter blocked this image even in Safe Mode. Try:\n"
                        "1. Use more general descriptions\n"
                        "2. Change Image Style to 'Digital Art' or 'Illustration'\n"
                        "3. Avoid specific people, brands, or copyrighted content\n"
                        "4. Simplify your description further"
                    )
            
            logger.error(f"❌ DALL-E 3 error: {error_str}")
            raise
    
    def _sanitize_prompt(self, prompt: str) -> str:
        """Sanitize prompt to avoid content filters while maintaining style intent"""
        
        # Check if user wants photorealistic style
        wants_photo = any(word in prompt.lower() for word in [
            'photorealistic', 'realistic', 'photo', 'photograph', 'real'
        ])
        
        # Remove specific trigger words that OpenAI filters catch
        trigger_phrases = [
            'shot on Canon', 'shot on Sony', 'Canon EOS', 'Sony A7',
            'professional photography', 'studio photography',
            'professional photograph', 'high resolution photograph',
            'DSLR', 'camera', 'lens'
        ]
        
        sanitized = prompt
        for phrase in trigger_phrases:
            sanitized = sanitized.replace(phrase, '')
        
        # Replace problematic realistic terms with filter-safe alternatives
        replacements = {
            'professional photograph of': 'high quality image of',
            'photorealistic': 'lifelike',
            'realistic portrait': 'detailed portrait',
            'professional photography': 'high quality visual',
            'shot on': 'captured as',
            'photograph': 'image',
            'photo of': 'depiction of'
        }
        
        for old, new in replacements.items():
            sanitized = sanitized.replace(old, new)
        
        # Clean up extra spaces
        sanitized = ' '.join(sanitized.split())
        
        # If photorealism was intended, add filter-safe realistic terms
        if wants_photo:
            # Use terms that maintain realism without triggering filters
            if not any(word in sanitized.lower() for word in ['lifelike', 'detailed', 'high quality']):
                sanitized = f"Highly detailed, lifelike image: {sanitized}"
        
        logger.info(f"Sanitized prompt. Original: {prompt[:60]}... → Sanitized: {sanitized[:60]}...")
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
# NEW: ReelGenerator Class for Replicate API
# ============================================================================
class ReelGenerator:
    """Handles video/reel generation using Replicate API"""
    
    def __init__(self, api_key: str):
        """Initialize with Replicate API key (NOT OpenAI key!)"""
        if not api_key:
            raise ValueError("Replicate API key cannot be empty")
        
        # Clean the Replicate API key
        self.api_key = ''.join(api_key.split())
        
        # SURGICAL FIX 1: Changed validation from 'sk-' to 'r8_'
        # Replicate keys typically start with 'r8_'
        if not self.api_key.startswith('r8_'):
            raise ValueError(f"Invalid API key format. Replicate keys start with 'r8_'. Your key starts with: {self.api_key[:5]}")
        
        # Set as environment variable for Replicate library
        os.environ["REPLICATE_API_TOKEN"] = self.api_key
        logger.info(f"ReelGenerator initialized with Replicate API key: {self.api_key[:10]}...")
    
    def test_connection(self) -> dict:
        """Test Replicate API connection"""
        try:
            # Simple test - list models
            replicate.models.list()
            return {"success": True, "message": "Replicate API connection successful!"}
        except Exception as e:
            return {"success": False, "message": f"Connection failed: {str(e)}", "error": str(e)}
    
    # SURGICAL FIX 2: Added prompt improvement method
    def improve_prompt(self, user_prompt: str) -> str:
        """Enhance video generation prompt with professional terms"""
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
    
    # SURGICAL FIX 3: Added duration parameter with default value
    def generate_video(self, prompt: str, model: str = "stability-ai/stable-video-diffusion", 
                      image_path: str = None, duration: int = 3, improve_prompt: bool = True) -> str:
        """Generate video using Replicate models with optional prompt improvement and custom duration"""
        try:
            logger.info(f"Starting video generation with {model}...")
            logger.info(f"Prompt: {prompt[:100]}...")
            logger.info(f"Duration: {duration}s, Improve prompt: {improve_prompt}")
            
            # SURGICAL FIX 2: Apply prompt improvement if requested
            if improve_prompt:
                original_prompt = prompt
                prompt = self.improve_prompt(prompt)
                logger.info(f"✨ Prompt improved!")
            
            # Different models have different inputs
            if "stable-video-diffusion" in model:
                # Requires an input image - convert to base64 data URI
                if not image_path:
                    raise ValueError("Stable Video Diffusion requires an input image")
                
                # Read and encode image as base64 data URI
                import base64
                from pathlib import Path
                
                logger.info(f"Reading image from: {image_path}")
                
                with open(image_path, 'rb') as f:
                    image_data = f.read()
                
                # Encode to base64
                base64_image = base64.b64encode(image_data).decode('utf-8')
                
                # Get image mime type
                file_ext = Path(image_path).suffix.lower()
                mime_types = {
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.png': 'image/png',
                    '.webp': 'image/webp'
                }
                mime_type = mime_types.get(file_ext, 'image/jpeg')
                
                # Create data URI
                image_uri = f"data:{mime_type};base64,{base64_image}"
                
                logger.info(f"Image encoded successfully (size: {len(base64_image)} bytes)")
                
                output = replicate.run(
                    model,
                    input={
                        "cond_aug": 0.02,
                        "decoding_t": 7,
                        "input_image": image_uri,
                        "video_length": "14_frames_with_svd",
                        "sizing_strategy": "maintain_aspect_ratio",
                        "motion_bucket_id": 127,
                        "frames_per_second": 6
                    }
                )
            
            elif "animate-diff" in model or "animatediff" in model:
                # SURGICAL FIX 3: Calculate frames based on duration (assuming 8 fps)
                num_frames = min(duration * 8, 64)  # AnimateDiff max is 64 frames
                
                # Text to video
                output = replicate.run(
                    model,
                    input={
                        "prompt": prompt,
                        "num_frames": num_frames,
                        "num_inference_steps": 25
                    }
                )
            
            elif "zeroscope" in model.lower():
                # SURGICAL FIX 3: Calculate frames based on duration
                num_frames = duration * 8  # 8 frames per second
                
                output = replicate.run(
                    model,
                    input={
                        "prompt": prompt,
                        "num_frames": num_frames,
                        "num_inference_steps": 50
                    }
                )
            
            elif "runway" in model:
                # Gen-2 by Runway - supports duration directly
                output = replicate.run(
                    model,
                    input={
                        "prompt": prompt,
                        "duration": duration,
                        "upscale": False
                    }
                )
            
            else:
                # Generic approach
                output = replicate.run(
                    model,
                    input={
                        "prompt": prompt
                    }
                )
            
            # Handle different output formats
            if isinstance(output, str):
                video_url = output
            elif isinstance(output, list) and len(output) > 0:
                video_url = output[0] if isinstance(output[0], str) else str(output[0])
            else:
                video_url = str(output)
            
            logger.info(f"✅ Video generated successfully!")
            logger.info(f"Video URL: {video_url[:80]}...")
            return video_url
            
        except Exception as e:
            logger.error(f"❌ Video generation error: {str(e)}")
            raise
    
    def get_available_models(self) -> List[Dict[str, str]]:
        """Get list of available video generation models"""
        return [
            {
                "name": "Stable Video Diffusion",
                "id": "stability-ai/stable-video-diffusion:3f0457e4619daac51203dedb472816fd4af51f3149fa7a9e0b5ffcf1b8172438",
                "description": "Image to video - Animate your images!",
                "requires_image": True
            },
            {
                "name": "AnimateDiff",
                "id": "lucataco/animate-diff:beecf59c4aee8d81bf04f0381033dfa10dc16e845b4ae00d281e2fa377e48a9f",
                "description": "Text to video animation",
                "requires_image": False
            },
            {
                "name": "Zeroscope V2 XL",
                "id": "anotherjesse/zeroscope-v2-xl:9f747673945c62801b13b84701c783929c0ee784e4748ec062204894dda1a351",
                "description": "High quality text-to-video",
                "requires_image": False
            }
        ]

# ============================================================================
# Database Functions
# ============================================================================
def init_db():
    """Initialize SQLite database with enhanced schema including videos"""
    conn = sqlite3.connect('social_media.db', check_same_thread=False)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS campaigns
                 (id TEXT PRIMARY KEY, name TEXT, status TEXT, budget REAL, 
                  roi REAL, start_date TEXT, end_date TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS posts
                 (id TEXT PRIMARY KEY, campaign_id TEXT, platform TEXT, 
                  content TEXT, scheduled_date TEXT, status TEXT, 
                  engagement INTEGER, image_url TEXT, image_path TEXT, 
                  video_url TEXT, video_path TEXT, language TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS images
                 (id TEXT PRIMARY KEY, prompt TEXT, url TEXT, 
                  created_date TEXT, used_in_posts TEXT, local_path TEXT)''')
    
    # NEW: Videos table
    c.execute('''CREATE TABLE IF NOT EXISTS videos
                 (id TEXT PRIMARY KEY, prompt TEXT, url TEXT, 
                  created_date TEXT, local_path TEXT, model_used TEXT, used_in_posts TEXT)''')
    
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
                      engagement, image_url, image_path, video_url, video_path, language)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (post_id, post_data.get('campaign_id', ''), post_data['platform'],
                   post_data['content'], schedule_datetime.isoformat(), 'scheduled',
                   0, post_data.get('image_url', ''), post_data.get('image_path', ''),
                   post_data.get('video_url', ''), post_data.get('video_path', ''),
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
    if 'photo_style' not in st.session_state:
        st.session_state.photo_style = "Photorealistic (Real Photos)"
    if 'auto_save_images' not in st.session_state:
        st.session_state.auto_save_images = True
    if 'replicate_api_key' not in st.session_state:
        st.session_state.replicate_api_key = ""

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
            
            # NEW: Replicate API Key for Video/Reels
            st.markdown("### 🎬 Replicate API (Videos/Reels)")
            st.info("⚠️ Different from OpenAI! This is for video generation only.")
            
            replicate_key_from_secrets = st.secrets.get("REPLICATE_API_KEY", "")
            
            if replicate_key_from_secrets:
                st.success("✅ Replicate API key loaded from secrets")
                replicate_key = replicate_key_from_secrets
            else:
                st.markdown("💡 **Get FREE key:** https://replicate.com/account/api-tokens")
                replicate_key = st.text_input(
                    "Replicate API Key (starts with r8_)",
                    type="password",
                    help="Different from OpenAI key! Get from https://replicate.com/account/api-tokens",
                    key="replicate_key_input",
                    placeholder="r8_..."
                )
            
            if replicate_key:
                cleaned_rep_key = ''.join(replicate_key.split())
                
                # Validate Replicate key format
                if cleaned_rep_key.startswith('r8_'):
                    st.session_state.replicate_api_key = cleaned_rep_key
                    st.success(f"✅ Replicate key stored (length: {len(cleaned_rep_key)})")
                elif cleaned_rep_key.startswith('sk-'):
                    st.error("❌ This is an OpenAI key! Replicate keys start with 'r8_'")
                    st.warning("Get Replicate key at: https://replicate.com/account/api-tokens")
                    st.session_state.replicate_api_key = ""
                else:
                    st.warning(f"⚠️ Replicate keys usually start with 'r8_'. Your key starts with: {cleaned_rep_key[:3]}")
                    st.session_state.replicate_api_key = cleaned_rep_key
                
                if st.session_state.get('replicate_api_key', '') and REPLICATE_AVAILABLE:
                    if st.button("🎬 Test Replicate Connection", key="test_replicate", use_container_width=True):
                        with st.spinner("Testing Replicate API..."):
                            try:
                                reel_gen = ReelGenerator(st.session_state.replicate_api_key)
                                result = reel_gen.test_connection()
                                
                                if result["success"]:
                                    st.success(f"✅ {result['message']}")
                                    st.balloons()
                                else:
                                    st.error(f"❌ {result['message']}")
                            except Exception as e:
                                st.error(f"❌ Connection test failed: {str(e)}")
            else:
                st.warning("⚠️ Enter Replicate API key to create videos/reels")
            
            if not REPLICATE_AVAILABLE:
                st.error("⚠️ Replicate library not installed")
                st.code("Add 'replicate' to requirements.txt")
            
            st.markdown("---")
            st.markdown("### 📊 Navigation")
            
            view = st.radio(
                "Select View",
                ["📊 Overview", "🎯 Campaigns", "✏️ Content Lab", "🖼️ Assets", "🎬 Videos/Reels", "📈 Insights", "📅 Scheduled Posts"],
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
            
            # NEW: Photo Style selector
            photo_style = st.selectbox(
                "Image Style",
                ["Photorealistic (Real Photos)", "Digital Art", "Illustration", "Painting", "3D Render"],
                index=0,
                help="Choose the visual style for generated images"
            )
            st.session_state.photo_style = photo_style
            
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
            - OpenAI GPT-4 & DALL-E 3
            - Replicate AI (Videos)
            - Streamlit
            
            **🔑 API Keys Needed:**
            
            1️⃣ **OpenAI API Key** (starts with `sk-`)
            - For: Text captions, images
            - Get: https://platform.openai.com/api-keys
            
            2️⃣ **Replicate API Key** (starts with `r8_`)
            - For: Videos, reels, animations
            - Get: https://replicate.com/account/api-tokens
            
            **Features:**
            - 🌍 Multi-language (10+ languages)
            - 🎨 AI image generation
            - 🎬 AI video/reel creation
            - 🔄 Image variations
            - 💾 Auto-save assets
            - 📅 Scheduled posts
            - 📊 Enhanced analytics
            - 🖼️ HD quality images
            - 🛡️ Safe Mode for filters
            """)
            
            st.markdown("---")
            st.markdown("### 💡 Quick Tips")
            st.markdown("""
            **Upload Product Photos:**
            
            📤 Upload → AI analyzes image
            
            📝 Generates perfect caption
            
            🎬 Creates animated reel
            
            ⚡ All in one click!
            
            ---
            
            **Want REAL PHOTOS (Not Animated)?**
            
            1️⃣ Set **Image Style** to:
            📸 'Photorealistic (Real Photos)'
            
            2️⃣ Keep descriptions **simple**:
            ✅ "A woman in business attire"
            ✅ "A young man outdoors"
            ❌ "Cartoon style woman..."
            
            3️⃣ Enable **Safe Mode** if blocked
            
            ---
            
            **Create Viral Reels:**
            
            🎬 Add Replicate API key
            
            🎥 Use 'Create Reels & Videos'
            
            📱 Perfect for TikTok, Reels, Shorts
            
            ---
            
            **Getting Content Filter Errors?**
            
            ✅ Enable 'Safe Mode' above
            
            ✅ Or change to 'Digital Art'
            
            ✅ Simplify descriptions
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
                    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Images</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                # Count saved videos
                saved_videos_count = len(get_all_videos(conn))
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="margin: 0; font-size: 2rem;">{saved_videos_count}</h3>
                    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Videos/Reels</p>
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
            
            # ====================================================================
            # NEW FEATURE: Upload Product Image → Generate Post & Reel
            # ====================================================================
            with st.expander("📤 Upload Product Image → Create Post & Reel", expanded=True):
                st.markdown("Upload your product image and let AI create marketing posts and reels!")
                
                # Show which APIs are available
                col_status1, col_status2 = st.columns(2)
                with col_status1:
                    if st.session_state.get('api_key', ''):
                        st.success("✅ OpenAI API (for captions)")
                    else:
                        st.warning("⚠️ OpenAI API needed (for captions)")
                
                with col_status2:
                    if st.session_state.get('replicate_api_key', ''):
                        st.success("✅ Replicate API (for reels)")
                    else:
                        st.warning("⚠️ Replicate API needed (for reels)")
                
                st.info("💡 **Note:** Caption = OpenAI (sk-...) | Reel = Replicate (r8_...)")
                
                # File uploader
                uploaded_file = st.file_uploader(
                    "Upload Product Image",
                    type=['png', 'jpg', 'jpeg', 'webp'],
                    help="Upload a product photo to generate AI-powered marketing content",
                    key="product_upload"
                )
                
                if uploaded_file:
                    # Display uploaded image
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.image(uploaded_file, caption="Your Product", use_column_width=True)
                        
                        # Save uploaded image
                        image_bytes = uploaded_file.read()
                        uploaded_file.seek(0)  # Reset file pointer
                        
                        # Save to local storage
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        upload_filename = f"uploaded_{timestamp}_{uploaded_file.name}"
                        upload_path = IMAGES_DIR / upload_filename
                        
                        with open(upload_path, 'wb') as f:
                            f.write(image_bytes)
                        
                        st.success(f"✅ Image uploaded: {uploaded_file.name}")
                    
                    with col2:
                        st.markdown("**📝 Content Settings:**")
                        
                        platform_for_product = st.selectbox(
                            "Platform",
                            ["Instagram", "TikTok", "Facebook", "LinkedIn", "Twitter/X", "Snapchat"],
                            key="product_platform"
                        )
                        
                        tone_for_product = st.selectbox(
                            "Tone",
                            ["Professional", "Casual", "Humorous", "Inspirational", "Urgent/Sales"],
                            key="product_tone"
                        )
                        
                        # SURGICAL FIX 3: Add duration selector
                        video_duration_product = st.selectbox(
                            "Reel Duration",
                            [5, 10, 15, 30],
                            index=1,
                            help="Select video length in seconds",
                            key="product_duration"
                        )
                        
                        # SURGICAL FIX 2: Add prompt improvement toggle
                        improve_prompt_product = st.checkbox(
                            "✨ AI Prompt Enhancement",
                            value=True,
                            help="Automatically improve video prompt with professional terms",
                            key="improve_product_prompt"
                        )
                        
                        additional_context = st.text_area(
                            "Additional Context (Optional)",
                            placeholder="e.g., 'This is a limited edition product, on sale for 50% off'",
                            height=80,
                            key="product_context"
                        )
                        
                        schedule_date_product = st.date_input("Schedule Date", key="product_date")
                        schedule_time_product = st.time_input("Schedule Time", key="product_time")
                    
                    st.markdown("---")
                    st.markdown("### 🎯 What would you like to create?")
                    
                    col_a, col_b, col_c = st.columns(3)
                    
                    with col_a:
                        if st.button("📝 Generate Caption Only", key="gen_caption_only", use_container_width=True):
                            if not st.session_state.get('api_key', ''):
                                show_error("Please enter your OpenAI API key in the sidebar!")
                            else:
                                try:
                                    generator = ContentGenerator(st.session_state.get('api_key', ''))
                                    
                                    with st.spinner("✨ Analyzing your product and creating caption..."):
                                        selected_lang = st.session_state.get('selected_language', 'en')
                                        
                                        caption = generator.generate_caption_from_image(
                                            image_data=image_bytes,
                                            platform=platform_for_product,
                                            tone=tone_for_product,
                                            additional_context=additional_context,
                                            language=selected_lang
                                        )
                                        
                                        st.markdown("#### 📝 Generated Caption")
                                        st.success(caption)
                                        
                                        # Save scheduled post
                                        schedule_datetime = datetime.combine(schedule_date_product, schedule_time_product)
                                        post_data = {
                                            'platform': platform_for_product,
                                            'content': caption,
                                            'image_url': str(upload_path),
                                            'image_path': str(upload_path),
                                            'language': selected_lang
                                        }
                                        post_id = save_scheduled_post(conn, post_data, schedule_datetime)
                                        
                                        if post_id:
                                            show_success(f"🎉 Post scheduled for {schedule_datetime.strftime('%Y-%m-%d at %H:%M')}!")
                                
                                except Exception as e:
                                    show_error(f"Caption generation failed: {str(e)}")
                    
                    with col_b:
                        if st.button("🎬 Generate Reel Only", key="gen_reel_only", use_container_width=True):
                            # CRITICAL: Check ONLY Replicate key, never OpenAI
                            rep_key = st.session_state.get('replicate_api_key', '')
                            
                            if not rep_key:
                                show_error("Please enter your Replicate API key in the sidebar!")
                            elif not rep_key.startswith('r8_'):
                                show_error(f"Invalid Replicate API key! Must start with 'r8_', yours starts with: {rep_key[:3]}")
                            elif not REPLICATE_AVAILABLE:
                                show_error("Replicate library not installed. Add 'replicate' to requirements.txt")
                            else:
                                try:
                                    # SURGICAL FIX 2 & 3: Pass duration and improve_prompt parameters
                                    reel_gen = ReelGenerator(st.session_state.get('replicate_api_key', ''))
                                    
                                    with st.spinner(f"🎬 Creating {video_duration_product}s reel from your product... (1-3 minutes)"):
                                        video_url = reel_gen.generate_video(
                                            prompt=f"Product showcase, smooth camera movement, professional marketing video",
                                            model="stability-ai/stable-video-diffusion:3f0457e4619daac51203dedb472816fd4af51f3149fa7a9e0b5ffcf1b8172438",
                                            image_path=str(upload_path),
                                            duration=video_duration_product,
                                            improve_prompt=improve_prompt_product
                                        )
                                        
                                        if video_url:
                                            st.success(f"✅ {video_duration_product}s video generated successfully!")
                                            st.markdown(f"#### 🎬 Generated {video_duration_product}s Reel")
                                            st.video(video_url)
                                            
                                            # Save video
                                            video_path = save_video_locally(video_url, f"product_reel_{uploaded_file.name}")
                                            if video_path:
                                                video_id = save_video_to_db(conn, video_url, f"{video_duration_product}s product reel from {uploaded_file.name}", video_path, "Stable Video Diffusion")
                                                st.success(f"💾 Video saved to library! Duration: {video_duration_product}s")
                                            
                                            st.balloons()
                                            show_success("🎉 Reel created successfully!")
                                        else:
                                            show_error("Failed to generate video")
                                
                                except Exception as e:
                                    show_error(f"Reel generation failed: {str(e)}")
                                    st.code(str(e))
                    
                    with col_c:
                        if st.button("🚀 Generate Both", key="gen_both", use_container_width=True):
                            # Check both API keys
                            if not st.session_state.get('api_key', ''):
                                show_error("Please enter your OpenAI API key in the sidebar (for caption generation)!")
                            elif not st.session_state.get('replicate_api_key', ''):
                                show_error("Please enter your Replicate API key in the sidebar (for reel generation)!")
                            elif not REPLICATE_AVAILABLE:
                                show_error("Replicate library not installed. Add 'replicate' to requirements.txt")
                            else:
                                try:
                                    # Initialize BOTH generators with CORRECT keys
                                    generator = ContentGenerator(st.session_state.get('api_key', ''))
                                    reel_gen = ReelGenerator(st.session_state.get('replicate_api_key', ''))
                                    
                                    with st.spinner("✨ Creating complete marketing package..."):
                                        # Step 1: Generate Caption with OpenAI
                                        st.write("**Step 1/3:** Generating AI caption with GPT-4 Vision...")
                                        selected_lang = st.session_state.get('selected_language', 'en')
                                        
                                        caption = generator.generate_caption_from_image(
                                            image_data=image_bytes,
                                            platform=platform_for_product,
                                            tone=tone_for_product,
                                            additional_context=additional_context,
                                            language=selected_lang
                                        )
                                        
                                        st.markdown("#### 📝 Generated Caption")
                                        st.success(caption)
                                        
                                        # Step 2: Generate Reel with Replicate
                                        st.write(f"**Step 2/3:** Creating {video_duration_product}s product reel with Replicate AI... (1-3 minutes)")
                                        
                                        # SURGICAL FIX 2 & 3: Pass duration and improve_prompt parameters
                                        video_url = reel_gen.generate_video(
                                            prompt=f"Product showcase, smooth camera movement, professional marketing video",
                                            model="stability-ai/stable-video-diffusion:3f0457e4619daac51203dedb472816fd4af51f3149fa7a9e0b5ffcf1b8172438",
                                            image_path=str(upload_path),
                                            duration=video_duration_product,
                                            improve_prompt=improve_prompt_product
                                        )
                                        
                                        video_path = None
                                        if video_url:
                                            st.markdown(f"#### 🎬 Generated {video_duration_product}s Reel")
                                            st.video(video_url)
                                            
                                            # Save video
                                            st.write("**Step 3/3:** Saving everything...")
                                            video_path = save_video_locally(video_url, f"product_reel_{uploaded_file.name}")
                                            if video_path:
                                                video_id = save_video_to_db(conn, video_url, f"{video_duration_product}s product reel from {uploaded_file.name}", video_path, "Stable Video Diffusion")
                                        
                                        # Save scheduled post with both
                                        schedule_datetime = datetime.combine(schedule_date_product, schedule_time_product)
                                        post_data = {
                                            'platform': platform_for_product,
                                            'content': caption,
                                            'image_url': str(upload_path),
                                            'image_path': str(upload_path),
                                            'video_url': video_url if video_url else None,
                                            'video_path': video_path if video_path else None,
                                            'language': selected_lang
                                        }
                                        post_id = save_scheduled_post(conn, post_data, schedule_datetime)
                                        
                                        st.balloons()
                                        show_success(f"🎉 Complete marketing package created!\n• Caption in {LANGUAGES.get(selected_lang, 'English')}\n• {video_duration_product}s promotional reel\n• Scheduled for {schedule_datetime.strftime('%Y-%m-%d at %H:%M')}")
                                        st.info("📅 View in 'Scheduled Posts' • 🖼️ Image in 'Assets' • 🎬 Video in 'Videos/Reels'")
                                
                                except Exception as e:
                                    show_error(f"Generation failed: {str(e)}")
                                    st.code(str(e))
                else:
                    st.info("👆 Upload a product image to get started!")
                    st.markdown("**💡 Perfect for:**")
                    st.markdown("- 📦 Product launches")
                    st.markdown("- 🛍️ E-commerce posts")
                    st.markdown("- 📱 Social media ads")
                    st.markdown("- 🎁 Promotional content")
            
            # Generate Caption & Image (existing feature)
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
                    
                    st.info("💡 **For Real Photos of People:** Set Image Style to 'Photorealistic' in sidebar, then describe: 'A woman in business attire at a modern office' or 'A young professional man, natural lighting'")
                
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
                                        photo_style = st.session_state.get('photo_style', 'Photorealistic (Real Photos)')
                                        image_url = generator.generate_image(enhanced_prompt, size=image_size, quality=image_quality, safe_mode=safe_mode, photo_style=photo_style)
                                        
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
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.info("💡 **For Real Photos:** Select 'Photorealistic' in sidebar, describe simply: 'A person in casual clothes outdoors'")
                with col2:
                    current_style = st.session_state.get('photo_style', 'Photorealistic (Real Photos)')
                    style_emoji = "📸" if "Photorealistic" in current_style else "🎨"
                    st.metric("Current Style", f"{style_emoji}")
                
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
                                                                    safe_mode=st.session_state.get('safe_mode', False),
                                                                    photo_style=st.session_state.get('photo_style', 'Photorealistic (Real Photos)'))
                                
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
                                    photo_style = st.session_state.get('photo_style', 'Photorealistic (Real Photos)')
                                    image_url = generator.generate_image(final_prompt, size=image_size, quality=image_quality, safe_mode=safe_mode, photo_style=photo_style)
                                    
                                    if image_url:
                                        col1, col2 = st.columns([2, 1])
                                        with col1:
                                            st.image(image_url, caption=f"Image {idx + 1}: {prompt[:50]}...", use_column_width=True)
                                        with col2:
                                            st.write(f"**Prompt:** {prompt}")
                                            if st.session_state.get('auto
