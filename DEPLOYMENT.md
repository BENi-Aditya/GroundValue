# GroundValue - Vercel Deployment

This document contains instructions for deploying GroundValue to Vercel.

## What Gets Deployed

The Vercel deployment hosts:
- ✅ React Frontend (CDN-based, static HTML/JS)
- ✅ 3D Landing Page (Three.js)
- ❌ Flask API (requires separate backend hosting)
- ❌ Streamlit App (requires separate backend hosting)

## Deployment Instructions

### Option 1: Deploy via Vercel CLI (Recommended)

1. **Install Vercel CLI** (if not already installed):
```bash
npm install -g vercel
```

2. **Login to Vercel**:
```bash
vercel login
```

3. **Deploy from the project directory**:
```bash
vercel
```

Follow the prompts:
- Set up and deploy? **Y**
- Which scope? Select your account
- Link to existing project? **N**
- What's your project's name? **groundvalue**
- In which directory is your code located? **.**

4. **Deploy to production**:
```bash
vercel --prod
```

### Option 2: Deploy via GitHub Integration

1. **Push your code to GitHub** (if not already done)
2. **Go to** [vercel.com](https://vercel.com)
3. **Click** "Add New Project"
4. **Import** your `GroundValue` repository
5. **Configure**:
   - Framework Preset: Other
   - Root Directory: `./`
   - Build Command: Leave empty (static site)
   - Output Directory: Leave empty
6. **Click** "Deploy"

## Configuration Files

The following files configure the Vercel deployment:

- `vercel.json` - Vercel deployment configuration
- `package.json` - Project metadata

## Important Notes

### Backend Services
The Flask API and Streamlit backend need separate hosting:

**Backend Options:**
- **Railway**: Good for Python apps, easy deployment
- **Render**: Free tier available, supports Python
- **PythonAnywhere**: Specifically for Python hosting
- **Heroku**: Classic choice, easy Python deployment
- **DigitalOcean App Platform**: Scalable, good for full-stack

### Frontend Configuration
Once deployed, you'll need to update API endpoints in:
- `frontend/index.html` - Update `API_BASE` constant to your backend URL

### Environment Variables
If you deploy the backend separately, you'll need to set:
- `TINYFISH_API_KEY` - Your TinyFish API key (in backend hosting)
- `API_URL` - Backend API URL (in Vercel project settings)

## Vercel URL
After deployment, your site will be available at:
- `https://groundvalue.vercel.app` (or custom domain)
- `https://groundvalue-<hash>.vercel.app` (preview deployments)

## Next Steps After Frontend Deployment

1. Deploy backend to Railway/Render/etc.
2. Update `API_BASE` in `frontend/index.html` with backend URL
3. Push changes to trigger redeployment
4. Test end-to-end functionality

## Support

For Vercel issues: [Vercel Documentation](https://vercel.com/docs)
For backend deployment: See respective platform documentation
