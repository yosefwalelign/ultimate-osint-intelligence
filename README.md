# 🕵️ Ultimate OSINT Intelligence Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen)](https://www.python.org/downloads/)
[![Docker Ready](https://img.shields.io/badge/Docker-Ready-blue)](https://www.docker.com/)
[![Status: Production](https://img.shields.io/badge/Status-Production%20Ready-success)]()

**The world's most comprehensive unified OSINT intelligence platform** - combining 10+ specialized OSINT tools into one enterprise-grade system.

## 📊 What This Does

A production-ready OSINT platform that performs **complete digital footprint analysis** on any target across:

✅ **550+ Social Media & Web Platforms** (Email + Username scanning)  
✅ **Instagram Deep Reconnaissance** (photos, followers, metadata)  
✅ **Google Ecosystem Intelligence** (Gmail, Drive, Gaia ID, BSSID geolocation)  
✅ **Dark Web OSINT** (AI-powered dark web search & analysis)  
✅ **Real-time Location Tracking** (IP geolocation, network reconnaissance)  
✅ **GitHub Commit Activity Analysis** (active hours, timezone detection)  
✅ **Telegram/Twitter/Telegram Activity Patterns** (message timestamps, posting habits)  
✅ **Public Database Integration** (Hudson Rock breaches, infostealer logs)  
✅ **User Activity Timeline** (commit history, social media posts, presence patterns)  
✅ **Multimedia Extraction** (download photos, profile pictures, media files)  

## 🎯 Features

### Core Capabilities
- 🔎 **Multi-Platform Username/Email Search** - 700+ website enumeration
- 📸 **Instagram OSINT** - Complete profile analysis with media extraction
- 🔍 **Google Intelligence** - Email verification, Drive analysis, geolocation
- 🌐 **Dark Web Search** - AI-powered queries via Tor network
- ⏰ **Activity Hours Analysis** - Detect target's active hours across platforms
- 📊 **Behavioral Profiling** - Timezone, habits, posting patterns
- 🔗 **Cross-Platform Pivoting** - Link identities across social media
- 🖼️ **Media Gallery** - Centralized image/post collection & display
- 📈 **Real-time Tracking** - Live updates from GitHub, Twitter, Telegram
- 🛡️ **Breach Intelligence** - Infostealer exposure detection

### Technical Features
- ⚡ **High-Throughput Async Engine** - 550+ concurrent requests
- 🌐 **Web UI + CLI** - Both interfaces fully operational
- 🐳 **Docker Deployment** - Production container support
- 📡 **REST API** - Full API for integration
- 🔐 **Proxy Rotation** - Built-in anti-detection
- 📂 **Multi-Format Export** - PDF, JSON, CSV reports
- 🤖 **AI Integration** - Claude, OpenAI, Ollama support
- 📱 **Mobile Ready** - Responsive web interface

## 🚀 Quick Start

### Option 1: Docker (Recommended)
```bash
# Clone and build
git clone https://github.com/yosefwalelign/ultimate-osint-intelligence.git
cd ultimate-osint-intelligence

# Build and run
docker-compose up -d

# Access Web UI at http://localhost:8000
# API at http://localhost:8000/api
```

### Option 2: Local Installation
```bash
# Clone repository
git clone https://github.com/yosefwalelign/ultimate-osint-intelligence.git
cd ultimate-osint-intelligence

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run backend
python app.py

# Run CLI
python cli.py --help
```

## 📖 Usage Examples

### CLI Usage
```bash
# Scan username across all platforms
python cli.py scan --username johndoe

# Scan email with cross-pivoting
python cli.py scan --email john@example.com --cross-scan --depth 2

# Instagram deep dive
python cli.py instagram --username target_username --download-photos

# Google intelligence
python cli.py google --email target@gmail.com

# Dark web search
python cli.py darkweb --query "target name"

# Analyze activity hours
python cli.py activity-analysis --username johndoe --platform github,twitter,telegram

# Export report
python cli.py scan --username johndoe --export pdf --output report.pdf

# Full intelligence report
python cli.py full-report --target johndoe --all-platforms
```

### Web UI Usage
```
1. Navigate to http://localhost:8000
2. Enter target (username, email, or handle)
3. Select modules/platforms to scan
4. Click "Start Investigation"
5. View results with media gallery
6. Export report in preferred format
```

### API Usage
```bash
# Scan username
curl -X POST http://localhost:8000/api/scan \
  -H "Content-Type: application/json" \
  -d '{"target": "johndoe", "type": "username"}'

# Get results
curl http://localhost:8000/api/results/scan_id

# Activity analysis
curl -X POST http://localhost:8000/api/analyze-activity \
  -d '{"username": "johndoe", "platforms": ["github", "twitter"]}'
```

## 📁 Project Structure

```
ultimate-osint-intelligence/
├── app.py                      # Flask web application
├── cli.py                      # CLI interface
├── api.py                      # REST API endpoints
├── requirements.txt            # Python dependencies
├── docker-compose.yml          # Docker configuration
├── Dockerfile                  # Container definition
├── config.yml                  # Configuration file
│
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── engine.py           # Main OSINT engine
│   │   ├── async_handler.py    # Async request handling
│   │   ├── cache.py            # Caching system
│   │   └── database.py         # Result storage
│   │
│   ├── modules/                # All OSINT modules
│   │   ├── username_scan.py    # Username enumeration (550+ sites)
│   │   ├── email_scan.py       # Email verification (175+ sites)
│   │   ├── instagram.py        # Instagram OSINT
│   │   ├── google_intel.py     # Google ecosystem
│   │   ├── darkweb.py          # Dark web search
│   │   ├── github.py           # GitHub activity analysis
│   │   ├── twitter.py          # Twitter/X analysis
│   │   ├── telegram.py         # Telegram metadata
│   │   ├── shadowbroker.py     # Satellite/tracking data
│   │   ├── trape.py            # People tracking
│   │   └── breach_intel.py     # Infostealer detection
│   │
│   ├── analyzers/
│   │   ├── activity_hours.py   # Active hours detection
│   │   ├── timezone.py         # Timezone inference
│   │   ├── behavior.py         # Behavioral profiling
│   │   ├── cross_platform.py   # Identity linking
│   │   └── timeline.py         # Event timeline
│   │
│   ├── scrapers/
│   │   ├── instagram_scraper.py
│   │   ├── github_scraper.py
│   │   ├── twitter_scraper.py
│   │   ├── telegram_scraper.py
│   │   └── media_downloader.py
│   │
│   ├── utils/
│   │   ├── proxy_manager.py    # Proxy rotation
│   │   ├── request_handler.py  # HTTP requests
│   │   ├── validators.py       # Data validation
│   │   └── formatters.py       # Output formatting
│   │
│   └── integrations/
│       ├── ai_models.py        # LLM integration
│       ├── apis.py             # Third-party APIs
│       └── webhooks.py         # Event webhooks
│
├── templates/                  # Web UI templates
│   ├── base.html
│   ├── dashboard.html
│   ├── scan.html
│   ├── results.html
│   ├── gallery.html
│   ├── timeline.html
│   └── settings.html
│
├── static/                     # CSS, JS, images
│   ├── css/
│   ├── js/
│   └── images/
│
├── tests/                      # Unit & integration tests
├── docs/                       # Documentation
└── logs/                       # Application logs
```

## 🔗 Merged Repositories

This project integrates capabilities from:

1. **user-scanner** (kaifcodec) - 550+ platform enumeration
2. **blackbird** (p1ngul1n0) - Social media username search
3. **osintgram** (datalux) - Instagram deep reconnaissance
4. **ghunt** (mxrch) - Google ecosystem intelligence
5. **robin** (apurvsinghgautam) - AI-powered dark web OSINT
6. **trape** (jofpin) - People tracking & social engineering
7. **shadowbroker** (bigbodycobain) - Satellite & tracking data
8. **whatsmyname** (webbreacher) - 700+ website dataset
9. **awesome-osint-arsenal** (rawfilejson) - OSINT toolkit collection
10. **osint-brazuca** (osintbrazuca) - Brazilian OSINT resources

## 📊 Supported Platforms

### Social Media (100+)
- Instagram, Twitter/X, TikTok, Facebook, LinkedIn, Snapchat
- Reddit, Discord, Telegram, WhatsApp, Pinterest
- YouTube, Twitch, Patreon, OnlyFans, Medium, Substack
- And 90+ more platforms

### Email Services (175+)
- Gmail, Outlook, Yahoo, AOL, ProtonMail
- Zoho, 163Mail, QQ Mail, iCloud
- Corporate domains & enterprise platforms
- Breached databases & infostealer logs

### Search Engines (30+)
- Google, Bing, DuckDuckGo
- Yandex, Baidu, Ecosia
- Dark web search engines (Torch, Ahmia)

### Geographic Data
- IP geolocation with accuracy
- BSSID geolocation
- Satellite imagery (via Shadowbroker)
- Flight tracking (aircraft ADS-B)
- Seismic event tracking

## ⚙️ Configuration

### Environment Variables
```bash
OSINT_API_KEY=your_api_key
GOOGLE_COOKIES_PATH=/path/to/cookies.json
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password
TOR_PROXY=socks5://127.0.0.1:9050
OLLAMA_BASE_URL=http://127.0.0.1:11434
OPENAI_API_KEY=sk-xxx
CLAUDE_API_KEY=sk-xxx
PROXY_LIST=/path/to/proxies.txt
HUDSON_ROCK_API=your_hudson_key
MAX_CONCURRENT_REQUESTS=50
TIMEOUT=30
RESULT_RETENTION_DAYS=30
```

### Configuration File (config.yml)
```yaml
osint:
  max_workers: 50
  timeout: 30
  retry_attempts: 3
  user_agent: "Mozilla/5.0..."
  
scan:
  enable_username: true
  enable_email: true
  enable_instagram: true
  enable_google: true
  enable_darkweb: true
  enable_github: true
  enable_activity_analysis: true
  
export:
  formats: ["json", "csv", "pdf"]
  include_media: true
  media_quality: "high"
  
ui:
  port: 8000
  host: "0.0.0.0"
  debug: false
  
api:
  enabled: true
  port: 8000
  auth_required: false
```

## 🎯 Active Hours Analysis

The platform automatically detects target's active hours by analyzing:

- **GitHub Commits** - commit timestamps across time zones
- **Twitter/X Posts** - posting frequency by hour/day
- **Telegram Messages** - message activity patterns
- **Instagram Stories** - story upload times
- **Comments & Interactions** - reaction timing

**Output:**
```
Target: johndoe
Detected Timezone: UTC-5 (EST)
Most Active: 2 PM - 6 PM
Least Active: 3 AM - 7 AM
Average Posts/Day: 3.2
Most Active Day: Friday
Activity Pattern: Regular 9-to-5 worker with evening social media use
```

## 🖼️ Media Gallery

Centralized media collection featuring:
- Profile pictures (high resolution)
- Instagram photos & stories
- Twitter media
- TikTok videos
- YouTube thumbnails
- Album art
- Tagged images
- Download history

## 📊 Intelligence Reports

Generated reports include:
- Executive summary
- Target identification
- Social media profiles
- Contact information
- Activity timeline
- Behavioral analysis
- Risk assessment
- Media gallery
- Data sources
- Recommendations

## 🔐 Privacy & Ethics

**Important:**
- This tool is for **authorized investigations only**
- Respect privacy laws in your jurisdiction
- Only scan targets you have permission to investigate
- Used by law enforcement, security researchers, and authorized investigators
- Educational purposes only - comply with all laws

## 📝 Installation Requirements

### System Requirements
- Python 3.10+
- 4GB RAM minimum (8GB+ recommended)
- 2GB disk space
- Linux/macOS/Windows (WSL2)

### Optional Dependencies
- Tor browser (for dark web)
- Instagram account (for Instagram OSINT)
- Google cookies (for Google intelligence)
- API keys (OpenAI, Claude, Groq)

## 🚀 Deployment

### Production Deployment
```bash
# Using Docker Swarm
docker stack deploy -c docker-compose.yml osint

# Using Kubernetes
kubectl apply -f k8s/deployment.yaml

# Using systemd
sudo cp osint.service /etc/systemd/system/
sudo systemctl enable osint
sudo systemctl start osint
```

## 📚 Documentation

- [Installation Guide](docs/INSTALLATION.md)
- [CLI Reference](docs/CLI.md)
- [API Documentation](docs/API.md)
- [Configuration Guide](docs/CONFIG.md)
- [Activity Analysis](docs/ACTIVITY_ANALYSIS.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Contributing Guidelines](docs/CONTRIBUTING.md)

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request
4. Follow code style guidelines

## 📄 License

MIT License - See [LICENSE](LICENSE) file

## ⚠️ Disclaimer

This tool is provided **for educational and authorized security research only**. Users are responsible for ensuring they have proper authorization before conducting investigations on any target. The developers assume no liability for misuse.

## 🙏 Credits

Built by integrating and enhancing work from:
- kaifcodec, p1ngul1n0, datalux, mxrch, apurvsinghgautam
- jofpin, bigbodycobain, WebBreacher, rawfilejson, osintbrazuca
- Security research community

## 📞 Support

- 📖 [Documentation](docs/)
- 💬 [Issues & Discussion](https://github.com/yosefwalelign/ultimate-osint-intelligence/issues)
- 📧 Email: support@osintplatform.io

---

**⭐ Star this repo if you find it useful!**
