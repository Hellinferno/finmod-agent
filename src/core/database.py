
import os
import json
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. SETUP CONNECTION
# If running on Render, use their DB. If local, use a simple file.
db_url = os.getenv("DATABASE_URL", "sqlite:///finmod_local.db")

# Fix for Render's URL format (Postgres requires 'postgresql://', Render gives 'postgres://')
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

engine = create_engine(db_url)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# 2. DEFINE THE TABLE (What we save)
class SavedValuation(Base):
    __tablename__ = "valuations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)           # e.g., "Tesla Optimistic Case"
    wacc = Column(Float)                        # e.g., 0.12
    growth_rate = Column(Float)                 # e.g., 0.03
    cash_flows = Column(Text)                   # Stored as "100,120,140" (CSV string)
    created_at = Column(DateTime, default=datetime.utcnow)

# 3. CREATE TABLES (Run this once on startup)
def init_db():
    Base.metadata.create_all(bind=engine)

# 4. HELPER FUNCTIONS (Save & Load)
def save_scenario(name, wacc, growth, cash_flows):
    session = SessionLocal()
    new_entry = SavedValuation(
        name=name, 
        wacc=float(wacc), 
        growth_rate=float(growth), 
        cash_flows=str(cash_flows)
    )
    session.add(new_entry)
    session.commit()
    session.close()
    return f"✅ Saved '{name}' successfully!"

def load_scenarios():
    session = SessionLocal()
    # Get the last 10 saves, newest first
    results = session.query(SavedValuation).order_by(SavedValuation.created_at.desc()).limit(10).all()
    session.close()
    return results
