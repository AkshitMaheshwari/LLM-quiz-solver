import os
import re
import json
import base64
import asyncio
import sys
from datetime import datetime, timedelta
from typing import Optional, Any
import requests
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from playwright.async_api import async_playwright
from groq import Groq
import pandas as pd
import io
import uuid
from dotenv import load_dotenv
from quiz_solver import QuizSolver

# Load environment variables
load_dotenv()

# Fix for Windows Event Loop (Playwright requires ProactorEventLoop)
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Configuration
STUDENT_EMAIL = os.getenv("STUDENT_EMAIL", "")
STUDENT_SECRET = os.getenv("STUDENT_SECRET", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable not set")

app = FastAPI(title="LLM Quiz Solver")

# Store for quiz results
quiz_results = {}

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize solver
solver = QuizSolver(GROQ_API_KEY)

# Request models
class QuizRequest(BaseModel):
    email: str
    secret: str
    url: str

# Store for active quiz sessions
quiz_sessions = {}

def verify_credentials(email: str, secret: str) -> bool:
    """Verify student credentials"""
    return email == STUDENT_EMAIL and secret == STUDENT_SECRET

async def fetch_quiz_page(url: str) -> str:
    """Fetch and render JavaScript-rendered quiz page"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle")
        content = await page.content()
        await browser.close()
        return content

def extract_quiz_instruction(html: str) -> dict:
    """Parse quiz instruction from HTML"""
    # Extract text content from result div
    import re
    match = re.search(r'<div[^>]*id="result"[^>]*>(.*?)</div>', html, re.DOTALL)
    if match:
        content = match.group(1)
        # Remove HTML tags
        instruction = re.sub(r'<[^>]+>', '', content)
        instruction = instruction.strip()
        return {"instruction": instruction}
    return {"instruction": ""}

def extract_submit_url(html: str) -> Optional[str]:
    """Extract submit endpoint URL from quiz page"""
    # Look for common patterns where submit URL is mentioned
    patterns = [
        r'https?://[^\s"\'<>]+/submit',
        r'https?://[^\s"\'<>]+/api/submit',
        r'"url":\s*"(https?://[^"]+)"'
    ]
    for pattern in patterns:
        match = re.search(pattern, html)
        if match:
            return match.group(0).replace('"', '')
    return None

async def solve_quiz(quiz_data: dict) -> Any:
    """Use Groq LLM to analyze and solve the quiz"""
    instruction = quiz_data.get("instruction", "")
    
    system_prompt = """You are an expert data analyst and problem solver. 
Your task is to analyze data queries, perform calculations, and provide accurate answers.
Always extract the exact numerical answer or required information from the context.
Focus on precision and accuracy. Return ONLY the final answer in the requested format."""
    
    return solver.analyze_data(instruction, instruction)

def parse_answer(response_text: str, instruction: str) -> Any:
    """Parse LLM response to extract the answer in correct format"""
    return solver.parse_answer(response_text, instruction)

async def submit_answer(submit_url: str, email: str, secret: str, quiz_url: str, answer: Any) -> dict:
    """Submit answer to the quiz endpoint"""
    payload = {
        "email": email,
        "secret": secret,
        "url": quiz_url,
        "answer": answer
    }
    
    try:
        response = requests.post(submit_url, json=payload, timeout=30)
        return response.json()
    except Exception as e:
        print(f"Error submitting answer: {e}")
        return {"correct": False, "reason": str(e)}

async def process_quiz_chain(task_id: str, email: str, secret: str, initial_url: str):
    """Process quiz chain until completion"""
    # Initialize result entry
    quiz_results[task_id] = {
        "status": "processing",
        "logs": [],
        "result": None
    }
    
    def log(message: str):
        print(message)
        timestamp = datetime.now().strftime('%H:%M:%S')
        quiz_results[task_id]["logs"].append(f"[{timestamp}] {message}")

    current_url = initial_url
    attempt_start = datetime.now()
    max_attempts = 10
    attempt_count = 0
    
    log(f"Starting quiz processing for {initial_url}")
    
    while current_url and attempt_count < max_attempts:
        attempt_count += 1
        
        # Check if within 3-minute window (from initial request)
        if (datetime.now() - attempt_start) > timedelta(minutes=3):
            log(f"Exceeded 3-minute limit for quiz at {current_url}")
            quiz_results[task_id]["status"] = "failed"
            quiz_results[task_id]["result"] = {"error": "Time limit exceeded"}
            break
        
        log(f"Processing quiz at {current_url} (attempt {attempt_count})")
        
        try:
            # Fetch quiz page
            log("Fetching quiz page...")
            html = await fetch_quiz_page(current_url)
            
            # Extract instruction
            quiz_data = extract_quiz_instruction(html)
            log(f"Quiz instruction: {quiz_data['instruction'][:100]}...")
            
            # Get submit URL from page
            submit_url = extract_submit_url(html)
            if not submit_url:
                log(f"Could not extract submit URL from {current_url}")
                quiz_results[task_id]["status"] = "failed"
                quiz_results[task_id]["result"] = {"error": "Could not find submit URL"}
                break
            
            # Solve quiz using LLM
            log("Solving quiz using LLM...")
            solution = await solve_quiz(quiz_data)
            log(f"LLM solution: {solution[:100]}...")
            
            # Parse answer
            answer = parse_answer(solution, quiz_data.get("instruction", ""))
            log(f"Parsed answer: {answer}")
            
            # Submit answer
            log("Submitting answer...")
            result = await submit_answer(submit_url, email, secret, current_url, answer)
            log(f"Submission result: {result}")
            
            # Check if correct
            if result.get("correct"):
                log("Answer correct!")
                current_url = result.get("url")  # Get next quiz if available
                if not current_url:
                    log("Quiz completed successfully!")
                    quiz_results[task_id]["status"] = "completed"
                    quiz_results[task_id]["result"] = {"success": True, "message": "All quizzes completed"}
                    break
            else:
                # Try again or move to next URL
                next_url = result.get("url")
                if next_url:
                    log(f"Moving to next URL: {next_url}")
                    current_url = next_url
                else:
                    reason = result.get('reason', 'Unknown error')
                    log(f"No next URL provided. Reason: {reason}")
                    quiz_results[task_id]["status"] = "failed"
                    quiz_results[task_id]["result"] = {"error": reason}
                    break
                    
        except Exception as e:
            import traceback
            error_details = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
            log(f"Error processing quiz: {error_details}")
            quiz_results[task_id]["status"] = "failed"
            quiz_results[task_id]["result"] = {"error": str(e) or "Unknown error occurred"}
            break
        
        await asyncio.sleep(1)  # Rate limiting
    
    if attempt_count >= max_attempts:
        log("Max attempts reached")
        quiz_results[task_id]["status"] = "failed"
        quiz_results[task_id]["result"] = {"error": "Max attempts reached"}

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the frontend HTML page"""
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Frontend not found</h1>"

@app.post("/quiz")
async def handle_quiz(request: QuizRequest, background_tasks: BackgroundTasks):
    """Main quiz endpoint"""
    
    # Validate JSON structure
    if not request.email or not request.secret or not request.url:
        raise HTTPException(status_code=400, detail="Missing required fields: email, secret, url")
    
    # Verify credentials
    if not verify_credentials(request.email, request.secret):
        raise HTTPException(status_code=403, detail="Invalid credentials")
    
    # Generate task ID
    task_id = str(uuid.uuid4())
    
    # Start quiz processing in background
    background_tasks.add_task(process_quiz_chain, task_id, request.email, request.secret, request.url)
    
    return {"status": "accepted", "message": "Quiz processing started", "task_id": task_id}

@app.get("/quiz/status/{task_id}")
async def get_quiz_status(task_id: str):
    """Get status of a quiz task"""
    if task_id not in quiz_results:
        raise HTTPException(status_code=404, detail="Task not found")
    return quiz_results[task_id]

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
