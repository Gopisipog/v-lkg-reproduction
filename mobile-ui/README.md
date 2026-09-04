# V-LKG Mobile Frontend

React 19 + Vite + Tailwind CSS mobile web interface for the Video Leadership Knowledge Graph (V-LKG) platform.

## Features
- **Phone Frame & Desktop Responsive**: Toggle between realistic smartphone mockup frame and full-screen responsive layout.
- **Child Apps Hub**: Workspace cards for Executive Leadership, Sales Accelerator, Communication Mastery, and GTM AI Engineering.
- **Linear Words & Semantic Pathways**: Concept chips and semantic relation pathways replacing node graphs.
- **Transcript & Semantics Explorer**: Searchable transcript moments with keyword highlighting and timestamp seeking.
- **Global Transcript Search**: Search across 3,184 transcript segments across 16 videos.
- **Voice Intelligence Note-Taker**: Live voice recording and audio file transcription.

## Development
```bash
npm install
npm run dev
```

## Production Build
```bash
npm run build
```
Built output is generated into `dist/` and served automatically by the FastAPI backend (`mobile_api/server.py`).
