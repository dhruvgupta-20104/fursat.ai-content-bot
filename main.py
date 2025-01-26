# main.py

from typing import Dict
import uuid
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
import logging 
import uvicorn

from Bot.main import process_channel

task_results: Dict[str, Dict] = {}

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s -    %(message)s',
    filename='logs/fursat_ai.log'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Content Bot",
    description="API for managing travel content",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/process_channel")
async def process_channel_endpoint(request: Request, background_tasks: BackgroundTasks, response_model=None):
    """Process a YouTube channel"""
    data = await request.json()
    channel_url = data.get("channel_url")
    if not channel_url:
        raise HTTPException(status_code=400, detail="Missing channel_url in request body")
    
    # Process channel in background
    task_id = str(uuid.uuid4())
    task_results[task_id] = {"status": "processing"}
    background_tasks.add_task(process_channel, channel_url, task_results, task_id)
    return {"task_id": task_id, "message": "Processing started"}

@app.get("/task_status/{task_id}")
async def task_status_endpoint(task_id: str):
    """Get task status"""
    if task_id not in task_results:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task_results[task_id]

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    uvicorn.run(app, host="0.0.0.0", port=8000)