import feedparser
import requests
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timedelta
from collections import Counter
import textwrap
import os
import re
import json
import random

# ==================== CONFIGURATION ====================

# Category-based RSS feeds (Feature B)
CATEGORIES = {
    'general': [
        "https://news.google.com/rss/search?q=Hyderabad+when:1h&hl=en-IN&gl=IN&ceid=IN:en",
        "https://news.google.com/rss/search?q=Telangana+when:1h&hl=en-IN&gl=IN&ceid=IN:en",
    ],
    'politics': [
        "https://news.google.com/rss/search?q=Hyderabad+politics+when:1h&hl=en-IN&gl=IN&ceid=IN:en",
        "https://news.google.com/rss/search?q=Telangana+politics+when:1h&hl=en-IN&gl=IN&ceid=IN:en",
    ],
    'tech': [
        "https://news.google.com/rss/search?q=Hyderabad+technology+startup+when:1h&hl=en-IN&gl=IN&ceid=IN:en",
        "https://news.google.com/rss/search?q=Hyderabad+IT+tech+when:1h&hl=en-IN&gl=IN&ceid=IN:en",
    ],
    'sports': [
        "https://news.google.com/rss/search?q=Hyderabad+sports+cricket+when:1h&hl=en-IN&gl=IN&ceid=IN:en",
        "https://news.google.com/rss/search?q=Telangana+sports+when:1h&hl=en-IN&gl=IN&ceid=IN:en",
    ],
    'business': [
        "https://news.google.com/rss/search?q=Hyderabad+business+economy+when:1h&hl=en-IN&gl=IN&ceid=IN:en",
    ],
}

OUTPUT_DIR = "outputs"
FONTS_DIR = "fonts"
IMAGE_SIZE = (1080, 1080)

# Theme configurations
THEMES = {
    'general': {
        'bg': '#1a1a2e',
        'text': '#eee',
        'accent': '#ff6b6b',
        'label': 'TRENDING NOW'
    },
    'politics': {
        'bg': '#2c3e50',
        'text': '#ecf0f1',
        'accent': '#e74c3c',
        'label': 'POLITICAL UPDATE'
    },
    'tech': {
        'bg': '#0f0f23',
        'text': '#00ff88',
        'accent': '#00d4ff',
        'label': 'TECH NEWS'
    },
    'sports': {
        'bg': '#1e3a5f',
        'text': '#ffffff',
        'accent': '#ffa500',
        'label': 'SPORTS FLASH'
    },
    'business': {
        'bg': '#1a472a',
        'text': '#f0f0f0',
        'accent': '#4caf50',
        'label': 'BUSINESS UPDATE'
    },
}

# Unsplash API for background images (Feature E)
UNSPLASH_ACCESS_KEY = os.getenv('UNSPLASH_ACCESS_KEY', '')  # Set in GitHub Secrets
HYDERABAD_KEYWORDS = ['hyderabad', 'city skyline', 'urban india', 'charminar', 'india architecture']

# Ensure directories exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(FONTS_DIR, exist_ok=True)

# ==================== FEATURE A: BETTER FONTS ====================

def download_fonts():
    """Download Google Fonts if not present"""
    fonts = {
        'Montserrat-Bold.ttf': 'https://github.com/google/fonts/raw/main/ofl/montserrat/Montserrat-Bold.ttf',
        'Montserrat-Regular.ttf': 'https://github.com/google/fonts/raw/main/ofl/montserrat/Montserrat-Regular.ttf',
        'Roboto-Bold.ttf': 'https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Bold.ttf',
    }
    
    for font_name, url in fonts.items():
        font_path = os.path.join(FONTS_DIR, font_name)
        if not os.path.exists(font_path):
            try:
                print(f"📥 Downloading font: {font_name}")
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    with open(font_path, 'wb') as f:
                        f.write(response.content)
                    print(f"✅ Font downloaded: {font_name}")
            except Exception as e:
                print(f"⚠️ Could not download {font_name}: {e}")

def get_fonts():
    """Get fonts with fallback"""
    try:
        title_font = ImageFont.truetype(f"{FONTS_DIR}/Montserrat-Bold.ttf", 64)
        source_font = ImageFont.truetype(f"{FONTS_DIR}/Montserrat-Regular.ttf", 28)
        label_font = ImageFont.truetype(f"{FONTS_DIR}/Roboto-Bold.ttf", 38)
        bullet_font = ImageFont.truetype(f"{FONTS_DIR}/Montserrat-Regular.ttf", 32)
    except:
        # Fallback to system fonts
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
            source_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
            label_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 35)
            bullet_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
        except:
            title_font = ImageFont.load_default()
            source_font = ImageFont.load_default()
            label_font = ImageFont.load_default()
            bullet_font = ImageFont.load_default()
    
    return title_font, source_font, label_font, bullet_font

# ==================== FEATURE E: BACKGROUND IMAGES ====================

def get_background_image():
    """Fetch Hyderabad-themed background from Unsplash"""
    if not UNSPLASH_ACCESS_KEY:
        return None
    
    try:
        keyword = random.choice(HYDERABAD_KEYWORDS)
        url = f"https://api.unsplash.com/photos/random?query={keyword}&orientation=square&client_id={UNSPLASH_ACCESS_KEY}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            image_url = data['urls']['regular']
            
            # Download image
            img_response = requests.get(image_url, timeout=15)
            if img_response.status_code == 200:
                from io import BytesIO
                img = Image.open(BytesIO(img_response.content))
                # Resize and crop to square
                img = img.resize((1080, 1080), Image.Resampling.LANCZOS)
                return img
    except Exception as e:
        print(f"⚠️ Could not fetch background image: {e}")
    
    return None

# ==================== FEATURE C: AI SUMMARIES ====================

def generate_ai_summary(title, article_text=""):
    """Generate bullet point summary using Claude API (free tier)"""
    # Note: This uses the Anthropic API that's available in artifacts
    # For GitHub Actions, you'd use the free tier or skip this feature
    
    # Simple rule-based summary for now (can be upgraded to actual API)
    summary_points = []
    
    # Extract key information from title
    sentences = title.split('.')
    for sentence in sentences[:3]:
        if len(sentence.strip()) > 10:
            summary_points.append(sentence.strip())
    
    # If we have less than 3 points, add generic ones
    if len(summary_points) < 3:
        summary_points.extend([
            "Breaking news from Hyderabad/Telangana",
            "Developing story - more details expected",
            "Local impact and updates to follow"
        ])
    
    return summary_points[:3]  # Return max 3 bullet points

# ==================== FEATURE D: MULTIPLE IMAGES (CAROUSEL) ====================

def create_carousel_image_1(title, category, theme):
    """Image 1: Headline"""
    bg_img = get_background_image()
    
    if bg_img:
        # Apply dark overlay for readability
        img = bg_img.copy()
        overlay = Image.new('RGBA', IMAGE_SIZE, (0, 0, 0, 180))
        img = img.convert('RGBA')
        img = Image.alpha_composite(img, overlay)
        img = img.convert('RGB')
    else:
        img = Image.new('RGB', IMAGE_SIZE, theme['bg'])
    
    draw = ImageDraw.Draw(img)
    title_font, source_font, label_font, bullet_font = get_fonts()
    
    # Add label at top
    draw.rectangle([(0, 0), (1080, 100)], fill=theme['accent'])
    try:
        bbox = draw.textbbox((0, 0), theme['label'], font=label_font)
        label_width = bbox[2] - bbox[0]
    except:
        label_width = len(theme['label']) * 20
    
    draw.text(((1080 - label_width) // 2, 30), theme['label'], fill="white", font=label_font)
    
    # Wrap and draw title
    wrapper = textwrap.TextWrapper(width=22)
    title_lines = wrapper.wrap(text=title)
    
    y_offset = 300
    for line in title_lines[:5]:
        try:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            line_width = bbox[2] - bbox[0]
        except:
            line_width = len(line) * 35
        
        x = (1080 - line_width) // 2
        draw.text((x, y_offset), line, fill=theme['text'], font=title_font)
        y_offset += 85
    
    # Category badge
    draw.rectangle([(420, 950), (660, 1010)], fill=theme['accent'])
    draw.text((460, 965), f"#{category.upper()}", fill="white", font=source_font)
    
    return img

def create_carousel_image_2(summary_points, theme):
    """Image 2: Key Points"""
    img = Image.new('RGB', IMAGE_SIZE, theme['bg'])
    draw = ImageDraw.Draw(img)
    title_font, source_font, label_font, bullet_font = get_fonts()
    
    # Header
    draw.rectangle([(0, 0), (1080, 100)], fill=theme['accent'])
    header_text = "KEY POINTS"
    try:
        bbox = draw.textbbox((0, 0), header_text, font=label_font)
        header_width = bbox[2] - bbox[0]
    except:
        header_width = len(header_text) * 20
    
    draw.text(((1080 - header_width) // 2, 30), header_text, fill="white", font=label_font)
    
    # Bullet points
    y_offset = 250
    for i, point in enumerate(summary_points, 1):
        # Bullet circle
        draw.ellipse([(80, y_offset), (120, y_offset + 40)], fill=theme['accent'])
        draw.text((90, y_offset + 5), str(i), fill="white", font=source_font)
        
        # Text
        wrapper = textwrap.TextWrapper(width=35)
        point_lines = wrapper.wrap(text=point)
        
        line_y = y_offset + 10
        for line in point_lines[:3]:
            draw.text((150, line_y), line, fill=theme['text'], font=bullet_font)
            line_y += 45
        
        y_offset += 220
    
    return img

def create_carousel_image_3(source, link, theme):
    """Image 3: Source & Call to Action"""
    img = Image.new('RGB', IMAGE_SIZE, theme['bg'])
    draw = ImageDraw.Draw(img)
    title_font, source_font, label_font, bullet_font = get_fonts()
    
    # Large icon/emoji area
    draw.rectangle([(340, 200), (740, 600)], fill=theme['accent'])
    draw.text((440, 330), "📰", font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 150) if os.path.exists("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf") else label_font)
    
    # Source info
    draw.text((540, 700), "Source:", fill=theme['text'], font=source_font, anchor="mm")
    draw.text((540, 750), source, fill=theme['accent'], font=bullet_font, anchor="mm")
    
    # CTA
    draw.text((540, 850), "Read Full Story", fill=theme['text'], font=label_font, anchor="mm")
    draw.text((540, 920), "Link in Bio", fill=theme['accent'], font=bullet_font, anchor="mm")
    
    # Timestamp
    timestamp = datetime.now().strftime("%d %b %Y, %I:%M %p")
    draw.text((540, 1020), timestamp, fill="#888", font=source_font, anchor="mm")
    
    return img

# ==================== CORE FUNCTIONS ====================

def fetch_news():
    """Fetch news from all category RSS feeds"""
    all_articles = []
    
    for category, feeds in CATEGORIES.items():
        for feed_url in feeds:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries:
                    article = {
                        'title': entry.title,
                        'link': entry.link,
                        'published': entry.published if 'published' in entry else None,
                        'source': entry.source.title if 'source' in entry else 'Unknown',
                        'category': category
                    }
                    all_articles.append(article)
            except Exception as e:
                print(f"Error fetching {feed_url}: {e}")
    
    return all_articles

def extract_keywords(title):
    """Extract key terms from title for duplicate detection"""
    stop_words = {'in', 'on', 'at', 'the', 'a', 'an', 'and', 'or', 'but', 'of', 'to', 'for', 'with', 'from', 'by'}
    words = re.findall(r'\w+', title.lower())
    keywords = [w for w in words if w not in stop_words and len(w) > 3]
    return set(keywords)

def detect_trending(articles):
    """Find trending news by detecting duplicates across sources"""
    if not articles:
        return None
    
    article_clusters = []
    
    for article in articles:
        keywords = extract_keywords(article['title'])
        
        matched = False
        for cluster in article_clusters:
            cluster_keywords = extract_keywords(cluster[0]['title'])
            overlap = len(keywords & cluster_keywords)
            if overlap >= max(2, len(keywords) * 0.4):
                cluster.append(article)
                matched = True
                break
        
        if not matched:
            article_clusters.append([article])
    
    article_clusters.sort(key=lambda x: len(x), reverse=True)
    
    if article_clusters and len(article_clusters[0]) >= 1:
        return article_clusters[0][0]
    
    return articles[0] if articles else None

def create_caption(title, link, source, category):
    """Create Instagram caption with hashtags"""
    category_hashtags = {
        'general': '#HyderabadNews #TelanganaNews #BreakingNews',
        'politics': '#Politics #TelanganaPolítics #IndianPolitics #Elections',
        'tech': '#TechNews #HyderabadTech #Startups #Innovation #IT',
        'sports': '#Sports #Cricket #HyderabadSports #IndianSports',
        'business': '#Business #Economy #HyderabadBusiness #Startups',
    }
    
    caption = f"""🔥 {title}

📰 Source: {source}
🔗 Read more: {link}

#{category.title()} {category_hashtags.get(category, '')}

#Hyderabad #Telangana #TrendingNews #IndiaNews #HyderabadCity #TelanganaToday #NewsUpdate #LocalNews #HyderabadUpdates #HyderabadBuzz"""
    
    output_path = os.path.join(OUTPUT_DIR, "caption.txt")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(caption)
    
    print(f"✅ Caption saved: {output_path}")
    return caption

def main():
    print("🚀 Starting ENHANCED news automation...")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Download fonts if needed
    download_fonts()
    
    # Fetch news
    articles = fetch_news()
    print(f"📰 Fetched {len(articles)} articles across all categories")
    
    if not articles:
        print("❌ No articles found. Exiting.")
        return
    
    # Detect trending
    trending = detect_trending(articles)
    
    if not trending:
        print("❌ No trending news detected. Exiting.")
        return
    
    print(f"🔥 Trending in {trending['category']}: {trending['title'][:80]}...")
    
    # Get theme
    theme = THEMES.get(trending['category'], THEMES['general'])
    
    # Generate AI summary
    summary_points = generate_ai_summary(trending['title'])
    
    # Create carousel images (3 images)
    print("📸 Creating carousel images...")
    
    img1 = create_carousel_image_1(trending['title'], trending['category'], theme)
    img1.save(os.path.join(OUTPUT_DIR, "post_1_headline.png"))
    print("✅ Image 1 saved: post_1_headline.png")
    
    img2 = create_carousel_image_2(summary_points, theme)
    img2.save(os.path.join(OUTPUT_DIR, "post_2_keypoints.png"))
    print("✅ Image 2 saved: post_2_keypoints.png")
    
    img3 = create_carousel_image_3(trending['source'], trending['link'], theme)
    img3.save(os.path.join(OUTPUT_DIR, "post_3_source.png"))
    print("✅ Image 3 saved: post_3_source.png")
    
    # Also create single image version (backwards compatible)
    img1.save(os.path.join(OUTPUT_DIR, "post.png"))
    print("✅ Single image saved: post.png")
    
    # Create caption
    create_caption(trending['title'], trending['link'], trending['source'], trending['category'])
    
    # Save metadata
    metadata = {
        'timestamp': datetime.now().isoformat(),
        'title': trending['title'],
        'category': trending['category'],
        'source': trending['source'],
        'link': trending['link'],
        'summary': summary_points
    }
    
    with open(os.path.join(OUTPUT_DIR, "metadata.json"), 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print("✅ Metadata saved: metadata.json")
    print("🎉 ENHANCED automation complete!")
    print(f"📁 Check {OUTPUT_DIR}/ folder for 3 carousel images + caption")

if __name__ == "__main__":
    main()
