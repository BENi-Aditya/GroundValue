# GroundValue

Property research and price estimation platform for Bengaluru real estate.

## Overview

GroundValue is a property valuation web application that helps users research comparable property listings and estimate asking prices for apartments in Electronic City, Bengaluru. The platform uses the TinyFish API for web scraping property data and provides detailed analysis of comparable properties.

## Features

- 🏢 Property research and price estimation
- 📊 Comparable property analysis
- 🔍 TinyFish API integration for live property data
- 📈 Interactive 3D landing page with Three.js
- 📱 Responsive React frontend
- 🖥️ Streamlit-based application interface
- 📋 Export functionality (CSV, HTML, Excel)

## Architecture

Three-tier architecture:
- **React Frontend** (CDN-based, no build step) - Port 8080
- **Flask API Backend** - Port 5001
- **Streamlit Application** with 3D landing page - Port 8501

## Tech Stack

- **Frontend**: React 18 (CDN), Tailwind CSS, Three.js
- **Backend**: Python, Flask, Streamlit
- **Database**: SQLite
- **API Integration**: TinyFish for property scraping
- **Property Sources**: 99acres, MagicBricks, Housing.com, NoBroker

## Getting Started

### Prerequisites

- Python 3.8+
- TinyFish API key (for live research)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/GroundValue.git
cd GroundValue
```

2. Set up the Python environment:
```bash
cd groundvalue_mvp
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3. Configure TinyFish API key (optional, for live research):
```bash
echo "YOUR_TINYFISH_API_KEY" > groundvalue_mvp/.tinyfish_key
```

### Running the Application

#### Option 1: Use the start script (recommended)
```bash
chmod +x start.sh
./start.sh
```

#### Option 2: Start services manually

**Terminal 1 - Streamlit (Landing Page & App):**
```bash
cd groundvalue_mvp
.venv/bin/streamlit run app.py
```

**Terminal 2 - Flask API:**
```bash
cd groundvalue_mvp
PORT=5001 python3 api.py
```

**Terminal 3 - React Frontend:**
```bash
python3 -m http.server 8080 --directory frontend
```

### Access Points

- **Landing Page**: http://localhost:8501
- **React UI**: http://localhost:8080
- **Streamlit App**: http://localhost:8501/?view=app
- **API**: http://localhost:5001/api

## Project Structure

```
GroundValue/
├── frontend/                 # React frontend application
│   ├── index.html           # Main React app
│   ├── workspace.js         # Workspace component
│   └── ...
├── groundvalue_mvp/         # Backend services
│   ├── app.py              # Streamlit entry point
│   ├── api.py              # Flask API server
│   ├── application.py      # Streamlit app UI
│   ├── core.py             # Core property logic
│   ├── research.py         # Research workflow
│   ├── tinyfish_client.py  # TinyFish integration
│   ├── landing/            # 3D landing page
│   │   ├── index.html
│   │   ├── scene.js
│   │   └── three.module.js
│   └── requirements.txt
├── GroundValue_PRD.docx     # Product Requirements Document
├── GroundValue_TinyFish.pptx # Project presentation
├── RUN.md                   # Detailed setup guide
├── EXECUTION_PLAN.md        # Development roadmap
├── PROGRESS.md              # Development tracker
└── start.sh                 # Startup script
```

## Features in Detail

### Property Research
- Enter property details (bedrooms, area, measurement basis)
- Select data sources (max 2 sources)
- Live TinyFish research with real-time progress
- Review comparable listings and exclusions

### Valuation Analysis
- Median asking price calculation
- Rate per square foot analysis
- Comparison band visualization
- Source evidence tracking

### Export Options
- CSV export for data analysis
- HTML report generation
- Excel export with formatting

## Current Coverage

**Location**: Electronic City, Bengaluru, Karnataka  
**Property Type**: Apartments for sale  
**Supported Sources**: 99acres, MagicBricks, Housing.com, NoBroker

## Development

See [EXECUTION_PLAN.md](EXECUTION_PLAN.md) for the full 11-phase development plan and [PROGRESS.md](PROGRESS.md) for current status.

## Documentation

- **PRD**: [GroundValue_PRD.docx](GroundValue_PRD.docx)
- **Presentation**: [GroundValue_TinyFish.pptx](GroundValue_TinyFish.pptx)
- **Run Guide**: [RUN.md](RUN.md)

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

**Note**: This is an MVP implementation. Live research requires a configured TinyFish API key. Property estimates are indicative and not formal appraisals.
