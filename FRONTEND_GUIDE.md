# Frontend User Guide

## Overview
The LLM Quiz Solver now includes a professional web-based frontend that allows end users to submit quizzes for automated solving via a user-friendly interface.

## Accessing the Frontend

### Local Development
1. Start the FastAPI server:
   ```bash
   python -m uvicorn main:app --reload --port 8000
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:8000
   ```

### Features

#### 1. **Submit Quiz Tab**
The main interface for users to submit quizzes:

- **Email Address**: Student's registered email
- **Secret Key**: Unique authentication secret
- **Quiz URL**: The URL of the quiz to be solved

**Process**:
1. Fill in all three required fields
2. Click "Solve Quiz" button
3. The system will:
   - Validate credentials
   - Fetch the quiz content
   - Analyze and solve it using Groq LLM
   - Submit the answer
   - Handle multi-step quiz chains

**Response Types**:
- ✓ **Success (Green)**: Quiz accepted and processing started
- ✗ **Error (Red)**: Invalid credentials or malformed request
- ℹ **Info (Blue)**: Server status information

#### 2. **Documentation Tab**
Complete API reference including:
- Endpoint documentation
- Request/Response formats
- Status codes explanation
- Usage tips

### User Interface Components

#### Status Indicator
- **Green pulsing dot**: Server is online and responsive
- **Red dot**: Server is offline or unreachable
- **Auto-checks**: Status refreshed every 30 seconds

#### Loading State
- Shows animated spinner during quiz processing
- Displays "Processing quiz..." message
- Processing typically takes 15-30 seconds per quiz

#### Response Display
- **Success responses**: Green background with confirmation message
- **Error responses**: Red background with error details
- **Raw JSON**: Collapsible section showing complete API response

#### Input Validation
- Real-time field validation
- Visual feedback on focus with blue border
- Helpful hints below each field
- Disabled submit button during processing

### Design Features

- **Responsive Design**: Works on desktop, tablet, and mobile
- **Modern Gradient**: Purple gradient header (matching brand colors)
- **Smooth Animations**: Pulse effects, button hover states, transitions
- **Accessibility**: Proper labels, semantic HTML, keyboard support
- **Error Handling**: Clear error messages with actionable guidance

### API Integration

The frontend communicates with two endpoints:

```bash
# Check server status
GET http://localhost:8000/health
Response: {"status": "ok"}

# Submit quiz
POST http://localhost:8000/quiz
Body: {
  "email": "student@example.com",
  "secret": "your-secret-key",
  "url": "https://example.com/quiz-123"
}
Response: {"status": "accepted", "message": "Quiz processing started"}
```

### Example Usage Workflow

1. **User opens the application**
   - Frontend checks API status
   - Shows green indicator if server is running
   - Displays documentation if needed

2. **User submits a quiz**
   ```
   Email: john@university.edu
   Secret: abc123xyz789
   URL: https://quiz.example.com/challenge-42
   ```

3. **System processes the quiz**
   - Validates credentials against backend
   - Launches browser to fetch quiz content
   - Extracts quiz instruction and data
   - Calls Groq LLM to analyze and solve
   - Parses answer in correct format
   - Submits to the quiz endpoint

4. **Results displayed to user**
   - Success: "Quiz processing started"
   - Can check results by visiting the quiz URL
   - Or submit the next URL in quiz chain

### Customization

#### Change Server Address
Edit `index.html` line with:
```javascript
const API_BASE_URL = 'http://127.0.0.1:8000';
```

Change to your deployed server:
```javascript
const API_BASE_URL = 'https://your-deployed-app.com';
```

#### Change Branding
- Header text: `<h1>🤖 Quiz Solver</h1>`
- Subtitle: `<p>Powered by Groq LLM</p>`
- Colors: Edit CSS `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`

#### Add Additional Tabs
1. Add tab button in `<div class="tabs">`
2. Add tab content div with matching id
3. Update `switchTab()` function if needed

### Performance Tips

- **Quiz Processing**: Typically 15-30 seconds per quiz
- **Large Data**: PDFs and CSVs up to 50MB are supported
- **Network**: Stable internet connection recommended
- **Timeout**: 3-minute window to submit answers

### Troubleshooting

#### "API Server is offline"
- Check if FastAPI server is running
- Verify server is on expected port (8000)
- Check firewall/network settings

#### "Invalid email or secret key"
- Verify credentials in .env file
- Ensure STUDENT_EMAIL and STUDENT_SECRET are set
- Check for typos or whitespace

#### "Invalid URL"
- Ensure URL is complete (http:// or https://)
- Check if URL is accessible from server
- Verify JavaScript rendering isn't required for initial content

#### Slow Processing
- Check internet connection
- Verify Groq API key is valid
- Check if Groq API quota is available
- Monitor server logs

### Browser Compatibility

- Chrome/Edge: ✓ Fully supported
- Firefox: ✓ Fully supported
- Safari: ✓ Fully supported
- Mobile browsers: ✓ Responsive design

### Security Notes

- **Secret Key**: Never share your secret key in URLs or public channels
- **HTTPS**: Use HTTPS in production deployment
- **CORS**: Frontend accepts all origins by default (change in production)
- **Rate Limiting**: Consider implementing rate limits in production

### File Structure

```
llm-quiz-solver/
├── main.py              # FastAPI app with frontend route
├── index.html           # Frontend interface (NEW)
├── quiz_solver.py       # Core quiz solving logic
├── config.py            # Configuration
├── test_api.py          # API tests
├── FRONTEND_GUIDE.md    # This file
└── requirements.txt     # Python dependencies
```

### Next Steps

1. **Deploy to cloud**: Follow DEPLOYMENT.md for AWS/Heroku/Azure setup
2. **Update configuration**: Change STUDENT_EMAIL and STUDENT_SECRET in .env
3. **Test thoroughly**: Use test_api.py for automated testing
4. **Monitor performance**: Check logs during quiz processing
5. **Share with users**: Provide frontend URL to end users

---

**Note**: This frontend is designed for local/internal use. For production deployment, implement proper authentication, HTTPS, and rate limiting.
