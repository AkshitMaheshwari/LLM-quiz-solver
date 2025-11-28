# LLM Analysis Quiz Solver

An intelligent quiz solver application that uses LLMs and web automation to solve data analysis, visualization, and processing challenges. Built for the LLM Analysis Quiz project at IIT.

## Features

- **FastAPI Endpoint**: Secure POST endpoint with authentication
- **JavaScript Rendering**: Playwright headless browser for client-side rendered content
- **LLM Integration**: Groq API with Mixtral-8x7b model for intelligent problem solving
- **Multi-step Quiz Support**: Handles quiz chains, retries, and 3-minute submission window
- **Data Processing**: PDF extraction, CSV parsing, API calls, web scraping
- **Answer Parsing**: Intelligent parsing for boolean, numeric, string, JSON, and file answers
- **CORS Enabled**: Allows requests from any origin

## Quick Start

### 1. Prerequisites
- Python 3.10+
- Groq API key (get from https://console.groq.com)

### 2. Installation

```bash
# Clone repository
cd c:\AI_ML\IIT\llm-quiz-solver

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install
```

### 3. Environment Setup

Create a `.env` file in the project root:

```bash
STUDENT_EMAIL=your-email@example.com
STUDENT_SECRET=your-secret-key
GROQ_API_KEY=your-groq-api-key
```

Or copy and modify the example:
```bash
cp .env.example .env
# Edit .env with your actual values
```

### 4. Run the Server

```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Reference

### POST /quiz
Submit a quiz task to be solved.

**Request:**
```json
{
  "email": "your@email.com",
  "secret": "your-secret-key",
  "url": "https://example.com/quiz-123"
}
```

**Success Response (200):**
```json
{
  "status": "accepted",
  "message": "Quiz processing started"
}
```

**Error Responses:**
- `400`: Invalid JSON or missing fields (email, secret, url)
- `403`: Invalid credentials (email/secret mismatch)

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "ok"
}
```

## Testing

Test the endpoint locally using the provided test script:

```bash
python test_api.py
```

This tests:
- Health endpoint
- Invalid JSON handling (400)
- Missing fields handling (400)
- Invalid credentials (403)
- Valid quiz submission (200)

Test against the demo endpoint:

```bash
# Update .env with your credentials, then:
python -c "
import requests
payload = {
    'email': 'your@email.com',
    'secret': 'your-secret',
    'url': 'https://tds-llm-analysis.s-anand.net/demo'
}
response = requests.post('http://127.0.0.1:8000/quiz', json=payload)
print(response.status_code, response.json())
"
```

## Architecture

### Components

1. **FastAPI Server** (`main.py`)
   - Validates requests and credentials
   - Manages quiz processing pipeline
   - Coordinates submission and retries

2. **QuizSolver** (`quiz_solver.py`)
   - Handles data extraction (PDF, CSV, images)
   - Makes API calls and web requests
   - Parses answers in various formats
   - Integrates with Groq LLM

3. **Browser Automation**
   - Uses Playwright for JavaScript rendering
   - Executes DOM operations
   - Extracts quiz instructions

### Quiz Processing Flow

```
1. Receive quiz request (email, secret, url)
2. Validate credentials
3. Fetch and render quiz page (JavaScript support)
4. Extract quiz instruction and submit URL
5. Use LLM to analyze and solve
6. Parse answer based on question type
7. Submit answer to provided endpoint
8. Handle response:
   - If correct: proceed to next quiz (if provided)
   - If incorrect: retry or accept next URL
9. Continue until quiz complete or 3-minute timeout
```

### Supported Answer Types

- **Boolean**: True/False questions
- **Numeric**: Integers and floats
- **String**: Text answers
- **JSON**: Complex objects
- **Base64**: File attachments (as data URIs)

## Design Choices

### LLM Model Selection
- **Mixtral-8x7b-32768** (Groq): Fast, cost-effective, good at reasoning
- Chosen over GPT-4 for speed (max 3 minutes per quiz)

### Browser Automation
- **Playwright** vs Selenium: Better async support, faster execution
- Headless mode for efficiency

### Answer Parsing Strategy
- Keyword detection in instructions
- Multiple fallback formats
- Intelligent number extraction

### Error Handling
- 3-minute window for entire quiz chain
- Automatic retries for incorrect answers
- Clear HTTP status codes (400, 403)

## Quiz Types Supported

The solver can handle:
- **Data sourcing**: Website scraping, API calls, PDF downloads
- **Data cleaning**: Text normalization, CSV parsing, format conversion
- **Data analysis**: Aggregations, filtering, statistical calculations
- **Data visualization**: Chart generation, image analysis
- **Processing tasks**: Transcription, transformation, encoding

## Deployment

For production deployment:

1. Get a valid domain/HTTPS certificate
2. Set environment variables securely
3. Use a production ASGI server:

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

4. Deploy to cloud platform (AWS, Azure, Heroku, etc.)
5. Submit HTTPS endpoint URL to evaluation form

## Troubleshooting

### "GROQ_API_KEY environment variable not set"
- Ensure .env file exists
- Check GROQ_API_KEY value is correct
- Reload environment after updating .env

### Browser timeouts
- Check internet connection
- Increase timeout values in code
- Ensure Playwright browsers installed: `playwright install`

### LLM API errors
- Verify Groq API key is valid
- Check rate limits
- Monitor API usage at console.groq.com

## License

MIT License - see LICENSE file for details

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review test_api.py for examples
3. Check Groq documentation: https://console.groq.com/docs

