from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
from pathlib import Path

from fmva.core.ingestion import load_json, load_csv, load_excel, load_pdf
from fmva.core.normalization import normalize
from fmva.core.schemas import FinancialStatements
from fmva.exceptions import IngestionError, FileFormatError

router = APIRouter()

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/upload", response_model=FinancialStatements)
async def upload_financials(
    file: UploadFile = File(...),
):
    filename = file.filename or ""
    suffix = Path(filename).suffix.lower()
    if suffix not in {".json", ".csv", ".xlsx", ".xls", ".pdf"}:
        raise HTTPException(
            status_code=400, 
            detail="Invalid file format. Only JSON, CSV, Excel, or PDF allowed."
        )
        
    file_path = UPLOAD_DIR / filename
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Parse data based on extension
        if suffix == ".json":
            raw_data = load_json(str(file_path))
        elif suffix == ".csv":
            raw_data = load_csv(str(file_path))
        elif suffix in (".xlsx", ".xls"):
            raw_data = load_excel(str(file_path))
        elif suffix == ".pdf":
            raw_data = load_pdf(str(file_path))
        else:
            raise ValueError(f"Unsupported file type: {suffix}")

        # Normalize the raw payload into typed FinancialStatements
        financials = normalize(raw_data)
        return financials
        
    except (FileFormatError, IngestionError, ValueError) as e:
        raise HTTPException(status_code=400, detail=f"Failed to process file: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")
    finally:
        file.file.close()
