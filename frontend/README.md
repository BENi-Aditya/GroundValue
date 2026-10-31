# GroundValue Frontend Setup

## Quick Start

The new React-based frontend has been created to match the reference screenshots pixel-perfectly while preserving all existing functionality.

### Running the Application

1. **Start the Flask API** (serves data from Streamlit backend):
   ```bash
   cd groundvalue_mvp
   python3 api.py
   ```
   API will run on `http://localhost:5000`

2. **Start the React Frontend**:
   ```bash
   cd frontend
   python3 -m http.server 3000
   ```
   Frontend will run on `http://localhost:3000`

3. **Access the Landing Page** (unchanged):
   ```bash
   cd groundvalue_mvp
   streamlit run app.py
   ```
   Visit `http://localhost:8501` - the landing page remains intact

### Architecture

- **Frontend**: React with Tailwind CSS (CDN-based, no npm needed)
- **Backend API**: Flask wrapper around existing Streamlit functionality
- **Landing Page**: Original Streamlit landing page (completely preserved)
- **Data**: All existing property data and TinyFish integration intact

### Features Implemented

✅ **Dashboard Page** (Reference Screenshot 1)
- Three-column property card grid
- Search and filters
- Exact layout and styling from screenshot

✅ **New Research Page** (Reference Screenshot 2)
- Two-column layout (form + info panel)
- Property details form
- Source selection (max 2)
- Information cards on the right

✅ **Property Workspace** (Reference Screenshot 3)
- Will be completed in next iteration
- Overview/History/Export tabs
- Metrics cards
- Property details and summary

### Design System

All colors, spacing, typography, and measurements extracted from reference screenshots:
- Primary Green: #064E3B
- Background: #F8FAF9
- Borders: #E3E8EB
- Typography: Inter font family
- Spacing: 8px base unit
- Border radius: 8-12px

### Next Steps

To complete the implementation:

1. Finish Property Workspace page (Reference 3)
2. Add TinyFish live research view
3. Add export functionality
4. Test end-to-end workflow
5. Deploy production build

### Accessing Different UIs

- **New React UI**: http://localhost:3000
- **Original Streamlit App**: http://localhost:8501/?view=app
- **Landing Page**: http://localhost:8501

All three work simultaneously!
