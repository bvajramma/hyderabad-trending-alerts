import feedparser
import requests
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import textwrap
import os
import re

# ==================== PROFESSIONAL DESIGN CONFIGURATION ====================

# Professional color palette (TV news inspired)
COLORS = {
    'bg_primary': '#0a0e27',      # Deep navy studio background
    'bg_secondary': '#1a1f3a',    # Section background
    'accent_red': '#ff0050',      # Breaking news red
    'accent_cyan': '#00d9ff',     # Modern accent
    'text_primary': '#ffffff',    # Pure white
    'text_secondary': '#b8c5d6',  # Muted text
    'warning': '#ffa500',         # Alert orange
}

# Image settings
IMAGE_SIZE = (1080, 1080)
OUTPUT_DIR = "outputs"
FONTS_DIR = "fonts"

# Branding
BRAND_NAME = "HYD ALERTS"
INSTAGRAM_HANDLE = "@hyderabadtrendingalerts"
LOGO_ICON = "⚡"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(FONTS_DIR, exist_ok=True)

# ==================== FONT MANAGEMENT ====================

def download_professional_fonts():
    """Download free professional fonts (Poppins, Inter, Montserrat)"""
    fonts = {
        # Poppins (modern, highly readable)
        'Poppins-Bold.ttf': 'https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Bold.ttf',
        'Poppins-SemiBold.ttf': 'https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-SemiBold.ttf',
        'Poppins-Regular.ttf': 'https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Regular.ttf',
        'Poppins-Medium.ttf': 'https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Medium.ttf',
        
        # Inter (clean, professional)
        'Inter-Bold.ttf': 'https://github.com/google/fonts/raw/main/ofl/inter/Inter-Bold.ttf',
        'Inter-SemiBold.ttf': 'https://github.com/google/fonts/raw/main/ofl/inter/Inter-SemiBold.ttf',
    }
    
    for font_name, url in fonts.items():
        font_path = os.path.join(FONTS_DIR, font_name)
        if not os.path.exists(font_path):
            try:
                print(f"📥 Downloading {font_name}...")
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                with open(font_path, 'wb') as f:
                    f.write(response.content)
                print(f"✅ {font_name} ready")
            except Exception as e:
                print(f"⚠️ Could not download {font_name}: {e}")

def get_professional_fonts():
    """Load professional fonts with fallback"""
    try:
        fonts = {
            'headline': ImageFont.truetype(f"{FONTS_DIR}/Poppins-Bold.ttf", 72),
            'subheadline': ImageFont.truetype(f"{FONTS_DIR}/Poppins-SemiBold.ttf", 56),
            'tag': ImageFont.truetype(f"{FONTS_DIR}/Inter-Bold.ttf", 32),
            'footer': ImageFont.truetype(f"{FONTS_DIR}/Poppins-Medium.ttf", 28),
            'timestamp': ImageFont.truetype(f"{FONTS_DIR}/Poppins-Regular.ttf", 24),
            'logo': ImageFont.truetype(f"{FONTS_DIR}/Inter-Bold.ttf", 40),
        }
        print("✅ Professional fonts loaded")
        return fonts
    except Exception as e:
        print(f"⚠️ Using fallback fonts: {e}")
        # Fallback to system fonts
        try:
            base = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
            return {
                'headline': ImageFont.truetype(base, 68),
                'subheadline': ImageFont.truetype(base, 52),
                'tag': ImageFont.truetype(base, 30),
                'footer': ImageFont.truetype(base, 26),
                'timestamp': ImageFont.truetype(base, 22),
                'logo': ImageFont.truetype(base, 38),
            }
        except:
            default = ImageFont.load_default()
            return {k: default for k in ['headline', 'subheadline', 'tag', 'footer', 'timestamp', 'logo']}

# ==================== HELPER FUNCTIONS ====================

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def draw_text_with_outline(draw, position, text, font, fill, outline_color, outline_width=3):
    """Draw text with outline for better readability"""
    x, y = position
    # Draw outline
    for adj_x in range(-outline_width, outline_width + 1):
        for adj_y in range(-outline_width, outline_width + 1):
            draw.text((x + adj_x, y + adj_y), text, font=font, fill=outline_color)
    # Draw main text
    draw.text(position, text, font=font, fill=fill)

def add_gradient_overlay(img, start_color, end_color, alpha=120):
    """Add subtle gradient overlay for depth"""
    gradient = Image.new('RGBA', img.size, color=0)
    draw = ImageDraw.Draw(gradient)
    
    for y in range(img.size[1]):
        # Calculate color for this line
        ratio = y / img.size[1]
        r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
        g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
        b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
        
        draw.line([(0, y), (img.size[0], y)], fill=(r, g, b, alpha))
    
    # Composite
    img = img.convert('RGBA')
    img = Image.alpha_composite(img, gradient)
    return img.convert('RGB')

# ==================== PROFESSIONAL IMAGE CREATION ====================

def create_professional_news_post(title, source, category='breaking'):
    """Create broadcast-quality Instagram news post"""
    
    # Initialize
    fonts = get_professional_fonts()
    img = Image.new('RGB', IMAGE_SIZE, hex_to_rgb(COLORS['bg_primary']))
    
    # Add subtle gradient for depth
    img = add_gradient_overlay(
        img,
        hex_to_rgb(COLORS['bg_primary']),
        hex_to_rgb(COLORS['bg_secondary']),
        alpha=80
    )
    
    draw = ImageDraw.Draw(img)
    
    # ============ TOP BANNER (Breaking News Tag) ============
    banner_height = 100
    
    # Red gradient banner
    for y in range(banner_height):
        alpha = int(255 * (1 - y / banner_height * 0.3))
        color = hex_to_rgb(COLORS['accent_red']) + (alpha,)
        draw.line([(0, y), (1080, y)], fill=color)
    
    # Breaking news text
    tag_text = f"{LOGO_ICON} BREAKING NEWS"
    tag_bbox = draw.textbbox((0, 0), tag_text, font=fonts['tag'])
    tag_width = tag_bbox[2] - tag_bbox[0]
    draw.text((40, 35), tag_text, fill=COLORS['text_primary'], font=fonts['tag'])
    
    # Timestamp (right side)
    timestamp = datetime.now().strftime("%I:%M %p | %d %b %Y").upper()
    time_bbox = draw.textbbox((0, 0), timestamp, font=fonts['timestamp'])
    time_width = time_bbox[2] - time_bbox[0]
    draw.text((1080 - time_width - 40, 38), timestamp, 
              fill=COLORS['text_secondary'], font=fonts['timestamp'])
    
    # ============ ACCENT LINE ============
    draw.rectangle([(0, banner_height), (1080, banner_height + 4)], 
                   fill=hex_to_rgb(COLORS['accent_cyan']))
    
    # ============ HEADLINE AREA ============
    
    # Smart text wrapping for optimal readability
    wrapper = textwrap.TextWrapper(width=20)  # Shorter lines for impact
    lines = wrapper.wrap(text=title)
    
    # Limit to 5 lines maximum
    if len(lines) > 5:
        lines = lines[:5]
        lines[-1] = lines[-1][:40] + "..."
    
    # Calculate vertical centering
    line_height = 95
    total_text_height = len(lines) * line_height
    start_y = (1080 - banner_height - 180 - total_text_height) // 2 + banner_height + 50
    
    # Draw each line with proper spacing
    for i, line in enumerate(lines):
        # Get text dimensions for centering
        bbox = draw.textbbox((0, 0), line, font=fonts['headline'])
        text_width = bbox[2] - bbox[0]
        x = (1080 - text_width) // 2
        y = start_y + (i * line_height)
        
        # Draw with subtle shadow for depth
        draw_text_with_outline(
            draw,
            (x, y),
            line,
            fonts['headline'],
            COLORS['text_primary'],
            hex_to_rgb(COLORS['bg_primary']),
            outline_width=2
        )
    
    # ============ BOTTOM BRANDING BAR ============
    footer_y = 950
    footer_height = 130
    
    # Dark footer background with transparency
    footer_overlay = Image.new('RGBA', (1080, footer_height), 
                               hex_to_rgb(COLORS['bg_secondary']) + (220,))
    img_rgba = img.convert('RGBA')
    img_rgba.paste(footer_overlay, (0, footer_y), footer_overlay)
    img = img_rgba.convert('RGB')
    draw = ImageDraw.Draw(img)
    
    # Top accent line
    draw.rectangle([(0, footer_y), (1080, footer_y + 3)], 
                   fill=hex_to_rgb(COLORS['accent_red']))
    
    # Logo icon and text (left side)
    logo_text = f"{LOGO_ICON} {BRAND_NAME}"
    draw.text((40, footer_y + 25), logo_text, 
              fill=COLORS['accent_cyan'], font=fonts['logo'])
    
    # Instagram handle (left side, below logo)
    draw.text((40, footer_y + 75), INSTAGRAM_HANDLE, 
              fill=COLORS['text_secondary'], font=fonts['footer'])
    
    # Location tag (right side)
    location = "📍 HYDERABAD"
    loc_bbox = draw.textbbox((0, 0), location, font=fonts['footer'])
    loc_width = loc_bbox[2] - loc_bbox[0]
    draw.text((1080 - loc_width - 40, footer_y + 50), location, 
              fill=COLORS['text_secondary'], font=fonts['footer'])
    
    # Save
    output_path = os.path.join(OUTPUT_DIR, "post.png")
    img.save(output_path, quality=100, optimize=True)
    print(f"✅ Professional post created: {output_path}")
    
    return output_path

# ==================== LOGO CREATION ====================

def create_profile_logo():
    """Create Instagram profile picture logo (1:1 ratio)"""
    
    size = (500, 500)
    img = Image.new('RGB', size, hex_to_rgb(COLORS['bg_primary']))
    
    # Add gradient background
    img = add_gradient_overlay(
        img,
        hex_to_rgb(COLORS['bg_primary']),
        hex_to_rgb(COLORS['accent_red']),
        alpha=60
    )
    
    draw = ImageDraw.Draw(img)
    fonts = get_professional_fonts()
    
    # Try to load larger font for logo
    try:
        logo_font = ImageFont.truetype(f"{FONTS_DIR}/Inter-Bold.ttf", 70)
        icon_font = ImageFont.truetype(f"{FONTS_DIR}/Inter-Bold.ttf", 90)
    except:
        logo_font = fonts['logo']
        icon_font = fonts['logo']
    
    # Draw icon circle background
    circle_center = (250, 180)
    circle_radius = 80
    draw.ellipse(
        [(circle_center[0] - circle_radius, circle_center[1] - circle_radius),
         (circle_center[0] + circle_radius, circle_center[1] + circle_radius)],
        fill=hex_to_rgb(COLORS['accent_red'])
    )
    
    # Draw icon
    icon_bbox = draw.textbbox((0, 0), LOGO_ICON, font=icon_font)
    icon_width = icon_bbox[2] - icon_bbox[0]
    icon_height = icon_bbox[3] - icon_bbox[1]
    draw.text((250 - icon_width // 2, 180 - icon_height // 2 - 10), 
              LOGO_ICON, fill=COLORS['text_primary'], font=icon_font)
    
    # Draw text
    text = "HYD ALERTS"
    text_bbox = draw.textbbox((0, 0), text, font=logo_font)
    text_width = text_bbox[2] - text_bbox[0]
    draw.text((250 - text_width // 2, 310), text, 
              fill=COLORS['accent_cyan'], font=logo_font)
    
    # Save
    logo_path = os.path.join(OUTPUT_DIR, "profile_logo.png")
    img.save(logo_path, quality=100)
    print(f"✅ Profile logo created: {logo_path}")
    
    return logo_path

# ==================== NEWS FETCHING ====================

def fetch_hyderabad_news():
    """Fetch latest Hyderabad news"""
    RSS_FEEDS = [
        "https://news.google.com/rss/search?q=Hyderabad+when:2h&hl=en-IN&gl=IN&ceid=IN:en",
        "https://news.google.com/rss/search?q=Telangana+when:2h&hl=en-IN&gl=IN&ceid=IN:en",
    ]
    
    all_articles = []
    
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                article = {
                    'title': entry.get('title', 'Breaking News'),
                    'link': entry.get('link', ''),
                    'source': entry.source.title if hasattr(entry, 'source') and hasattr(entry.source, 'title') else 'News Source'
                }
                all_articles.append(article)
        except Exception as e:
            print(f"Error fetching news: {e}")
    
    return all_articles[0] if all_articles else {
        'title': 'Latest Updates from Hyderabad',
        'link': 'https://news.google.com',
        'source': 'HYD Alerts'
    }

def create_caption(title, link, source):
    """Create professional Instagram caption"""
    caption = f"""🚨 BREAKING NEWS

{title}

━━━━━━━━━━━━━━━
📰 Source: {source}
🔗 Full story: {link}
━━━━━━━━━━━━━━━

Stay updated with Hyderabad's latest news ⚡

#HyderabadNews #Hyderabad #Telangana #BreakingNews #HydAlerts #TelanganaNews #HyderabadUpdates #IndiaNews #LocalNews #NewsAlert #HyderabadCity #TrendingNews #CurrentAffairs #NewsUpdate #InstantNews"""
    
    caption_path = os.path.join(OUTPUT_DIR, "caption.txt")
    with open(caption_path, 'w', encoding='utf-8') as f:
        f.write(caption)
    
    return caption

# ==================== MAIN AUTOMATION ====================

def main():
    print("=" * 60)
    print("🎬 PROFESSIONAL NEWS POST GENERATOR")
    print("=" * 60)
    
    # Download fonts
    download_professional_fonts()
    
    # Fetch news
    print("\n📰 Fetching latest news...")
    article = fetch_hyderabad_news()
    print(f"✅ Top story: {article['title'][:60]}...")
    
    # Create professional post
    print("\n🎨 Creating professional news post...")
    create_professional_news_post(article['title'], article['source'])
    
    # Create profile logo
    print("\n🎨 Creating profile logo...")
    create_profile_logo()
    
    # Create caption
    print("\n📝 Creating caption...")
    create_caption(article['title'], article['link'], article['source'])
    
    print("\n" + "=" * 60)
    print("✅ ALL OUTPUTS READY!")
    print("=" * 60)
    print(f"📁 Location: {OUTPUT_DIR}/")
    print("   • post.png (Instagram post)")
    print("   • profile_logo.png (Profile picture)")
    print("   • caption.txt (Copy-paste caption)")
    print("=" * 60)

if __name__ == "__main__":
    main()
