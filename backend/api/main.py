# backend/api/main.py
"""
FastAPI backend server for incident management system
"""
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from core.analyzer import IncidentAnalyzer
from db.connector import get_db

app = FastAPI(title="PORTNET Incident Management API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize analyzer
analyzer = IncidentAnalyzer()


# Request/Response models
class LogAnalysisRequest(BaseModel):
    log_line: str


class LogAnalysisResponse(BaseModel):
    incident: Dict[str, Any]
    database_context: Dict[str, Any]
    knowledge_base_results: Dict[str, Any]
    analysis: Dict[str, Any]


class DashboardStatsResponse(BaseModel):
    recent_edi_errors: List[Dict[str, Any]]
    container_status_summary: Dict[str, int]


class ContainerDetailsRequest(BaseModel):
    container_no: str


class BatchAnalysisRequest(BaseModel):
    log_lines: List[str]


# Routes
@app.get("/")
async def root():
    """Health check"""
    return {"status": "online", "service": "PORTNET Incident Management API"}


@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    try:
        # Test database connection
        db = get_db()
        db.connect()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "api": "online",
        "database": db_status,
        "rag": "initialized",
        "timestamp": "2025-10-20T00:00:00Z"
    }


@app.post("/api/analyze", response_model=LogAnalysisResponse)
async def analyze_log(request: LogAnalysisRequest):
    """
    Analyze a single log line
    
    Example request:
    {
        "log_line": "2025-10-19 14:23:15 ERROR [EDI-Parser] Failed to parse IFTMIN message: Segment missing. container: MSKU0000007"
    }
    """
    try:
        result = analyzer.analyze_log_line(request.log_line)
        
        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/api/analyze/batch")
async def analyze_batch(request: BatchAnalysisRequest):
    """
    Analyze multiple log lines
    
    Example request:
    {
        "log_lines": [
            "2025-10-19 14:23:15 ERROR ...",
            "2025-10-19 15:30:00 ERROR ..."
        ]
    }
    """
    try:
        results = []
        for log_line in request.log_lines:
            result = analyzer.analyze_log_line(log_line)
            if 'error' not in result:
                results.append(result)
        
        return {
            "total": len(request.log_lines),
            "analyzed": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")


@app.get("/api/dashboard", response_model=DashboardStatsResponse)
async def get_dashboard_stats():
    """
    Get dashboard statistics including recent EDI errors and container status summary
    """
    try:
        stats = analyzer.get_dashboard_stats()
        if 'error' in stats:
            raise HTTPException(status_code=500, detail=stats['error'])
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch stats: {str(e)}")


@app.post("/api/container/details")
async def get_container_details(request: ContainerDetailsRequest):
    """
    Get detailed information about a specific container
    
    Example request:
    {
        "container_no": "MSKU0000007"
    }
    """
    try:
        db = get_db()
        details = db.get_container_details(request.container_no)
        return details
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch container details: {str(e)}")


@app.get("/api/containers/status")
async def get_all_containers():
    """Get summary of all containers"""
    try:
        db = get_db()
        containers = db.get_all_containers_status()
        return {"containers": containers, "total": len(containers)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch containers: {str(e)}")


@app.get("/api/edi/errors")
async def get_recent_edi_errors(limit: int = 20):
    """Get recent EDI errors"""
    try:
        db = get_db()
        errors = db.get_recent_edi_errors(limit=limit)
        return {"errors": errors, "total": len(errors)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch EDI errors: {str(e)}")


@app.post("/api/upload/logs")
async def upload_log_file(file: UploadFile = File(...)):
    """
    Upload and analyze a log file
    Returns analysis for all error/warning lines in the file
    """
    try:
        content = await file.read()
        log_text = content.decode('utf-8')
        lines = log_text.split('\n')
        
        results = []
        for line in lines:
            if line.strip():
                result = analyzer.analyze_log_line(line)
                if 'error' not in result:
                    results.append(result)
        
        return {
            "filename": file.filename,
            "total_lines": len(lines),
            "analyzed_incidents": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")


@app.get("/api/search")
async def search_incidents(pattern: str):
    """
    Search for containers/vessels matching a pattern
    
    Example: /api/search?pattern=MSKU
    """
    try:
        db = get_db()
        results = db.search_incidents_by_pattern(pattern)
        return {"results": results, "total": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)