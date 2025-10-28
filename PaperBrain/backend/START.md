# How to Run and Test PaperBrain

## Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

## Step 1: Install Dependencies

Navigate to the backend directory and install required packages:

```bash
cd PaperBrain/backend
pip install -r requirements.txt
```

**Important:** If you encounter issues with certain packages:

1. **OpenCV** - If you get import errors:
   ```bash
   pip install opencv-python-headless
   ```

2. **easyocr** - First time installation might take time:
   ```bash
   pip install easyocr
   ```

3. **Google Generative AI** - You'll need an API key:
   - Create a `.env` file in `agents/evaluator/` directory
   - Add your Gemini API key:
     ```
     GEMINI_API_KEY=your_api_key_here
     ```

## Step 2: Start the Backend Server

From the backend directory:

```bash
python server.py
```

The server will start on `http://localhost:5000`

You should see:
```
 * Running on http://0.0.0.0:5000
 * Debug mode: on
```

## Step 3: Open the Frontend

Simply open `frontend/index.html` in your web browser:

- Double-click the file, OR
- Right-click → Open with → Your browser
- Or open at: `file:///path/to/PaperBrain/frontend/index.html`

## Step 4: Test the Application

### Test 1: Upload Files

1. Click "Browse" for Answer Key and select a template/blank exam sheet
2. Click "Browse" for Answer Sheet and select a filled exam sheet
3. (Optional) Add Related Docs (text files with subject matter for context)
4. Click **"Upload"** button

Expected: Status badge should show "Uploaded successfully"

### Test 2: Run Pipeline

1. Click **"Run Pipeline"** button
2. Watch the pipeline outputs section populate with results
3. Check each stage:
   - **Preprocessor**: Should show alignment score and status
   - **Region Selector**: Should show ROI coordinates
   - **Text Recognition**: Should show recognized answers
   - **Evaluator**: Should show evaluation results

### Test 3: View Output Visualizations

1. Scroll down to "Output Visualizations" section
2. You should see three sections:
   - **Aligned Images**: Preprocessed/aligned exam sheets
   - **Debug Crops**: Extracted answer regions
   - **Evaluation Visualizations**: Performance charts

3. Click any image to view it in full-screen
4. Click "✕ Close" to exit viewer

### Test 4: Check Current Student Results

1. Click **"Refresh"** button in "Evaluator - Current Student" card
2. Should display the current student's evaluation results
3. Shows scores, feedback, and awarded marks per question

## Troubleshooting

### Backend Won't Start

**Error:** `ModuleNotFoundError`
- Solution: Install missing dependencies with `pip install <package_name>`

**Error:** `Address already in use`
- Solution: Change port in `server.py` or kill the process using port 5000
  ```bash
  # Windows
  netstat -ano | findstr :5000
  taskkill /PID <PID> /F
  
  # Mac/Linux
  lsof -ti:5000 | xargs kill
  ```

### Frontend Can't Connect to Backend

**Issue:** Images not loading
- Ensure backend server is running on port 5000
- Check browser console (F12) for errors
- Verify API_BASE in `index.html` matches your setup

### Pipeline Fails

**Preprocessor Error:**
- Ensure answer key and answer sheet are proper image files
- Check that files are copied to correct directories

**Evaluator Error:**
- Ensure `.env` file exists in `agents/evaluator/` with GEMINI_API_KEY
- Verify API key is valid

## Directory Structure After Running

```
PaperBrain/
├── backend/
│   ├── server.py (running on :5000)
│   ├── uploads/ (temporary upload storage)
│   └── agents/
│       ├── preprocessor/
│       │   ├── question_paper_templates/ (uploaded answer keys)
│       │   ├── answer_scripts/ (uploaded answer sheets)
│       │   └── aligned_outputs/ (generated aligned images)
│       ├── text_recognition/
│       │   └── debug_crops/ (OCR crop images)
│       └── evaluator/
│           ├── inputs/
│           │   ├── related_docs/ (uploaded reference materials)
│           │   ├── reference_answers.json
│           │   └── student_answers.json
│           ├── temp/
│           │   └── current_student.json (latest evaluation)
│           └── results/
│               ├── evaluation_results.json
│               └── visualizations/ (charts and graphs)
```

## API Endpoints

- `GET /api/health` - Check server status
- `POST /api/upload` - Upload files (answer_key, answer_sheet, related_docs)
- `POST /api/run` - Execute full pipeline
- `GET /api/results/current-student` - Get current student results
- `GET /api/outputs/list` - List all available outputs
- `GET /api/outputs/preprocessor/<filename>` - Serve aligned images
- `GET /api/outputs/text-recognition/<filename>` - Serve debug crops
- `GET /api/outputs/visualizations/<filename>` - Serve visualizations

## Quick Test Script

To quickly test if everything is working:

```bash
# In backend directory
python -c "from controller.main_controller import PipelineController; print('Controller loaded successfully')"
```

If no errors, the setup is correct!

