# Environment Setup Guide

Effectively managing `.env` files is crucial for seamlessly switching the FMVA from local testing to a live presentation (production mode). 

You should maintain two standard files: `.env.local` and `.env.production`. **Never commit these files to GitHub**; ensure they are listed in `.gitignore`.

## 1. Frontend Environment (`frontend/`)

In Vite, environment variables must be prefixed with `VITE_` to be exposed to the application.

### `frontend/.env.local`
Used when running `npm run dev`. This routes your Axios API Client to the local python server.
```env
VITE_API_URL=http://localhost:8000
VITE_ENVIRONMENT=development
# Hardcode Demo Mode on locally so you don't accidentally hit expensive remote LLM calls
VITE_FORCE_DEMO_MODE=true
```

### `frontend/.env.production`
Used when running `npm run build`. This routes to wherever your final FastAPI server is hosted (e.g., AWS, Render).
```env
VITE_API_URL=https://api.yourdomain.com
VITE_ENVIRONMENT=production
VITE_FORCE_DEMO_MODE=false
```

---

## 2. Backend Environment (`fmva/`)

The Python FastAPI backend uses standard variable names. It does not load Vite prefixes.

### `fmva/.env` (Local Testing)
Variables for connecting to local databases or proxy LLMs.
```env
API_ENV=local
HF_LLM_API_KEY=mock-key-for-local
FMVA_LOG_LEVEL=DEBUG
# Path to local CSV inputs instead of Cloud buckets
DRIVE_MOUNT_PATH=./data/sample_inputs/
```

### `fmva/.env.production` (Live Demo/Prod)
Variables pointing to actual infrastructure. Load these via your hosting provider's dashboard or docker secrets, rather than relying on a raw `.env` file on disk.
```env
API_ENV=production
HF_LLM_API_KEY=hf_your_actual_paid_api_key_here
FMVA_LOG_LEVEL=INFO
DRIVE_MOUNT_PATH=/var/app/data
```

## How to Switch Contexts Before a Showcase:
1. **To run the live app:** Start your backend with the command `python -m uvicorn api.main:app --env-file .env.production` (Note: requires `python-dotenv`).
2. **For Frontend**, simply run `npm run build` which automatically ingests `.env.production`, and serve the `dist/` folder statically.
