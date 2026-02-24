from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fmva.api.routes import dcf, assumptions
from fmva.api.middleware import ErrorHandlingMiddleware

app = FastAPI(
    title="FMVA API",
    description="Backend API for Financial Modeling & Valuation Agent",
    version="1.0.0"
)

# Configure CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom exception handling
app.add_middleware(ErrorHandlingMiddleware)

# Include routers
app.include_router(dcf.router, prefix="/api/dcf", tags=["DCF Valuation"])
app.include_router(assumptions.router, prefix="/api/assumptions", tags=["Assumptions"])

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "fmva-backend", "version": "1.0.0"}
