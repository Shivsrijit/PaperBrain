import os
import json
import csv
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables (like API key)
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file!")

# Configure Gemini
genai.configure(api_key=API_KEY)
MODEL_NAME = "gemini-2.5-flash" 
model = genai.GenerativeModel(MODEL_NAME)

# --- File Paths ---
INCOMING_FOLDER = "./new_submissions" 
TEMP_DIR = "./temp"
INPUTS_DIR = "./inputs"
PROMPTS_DIR = "./prompts"
RESULTS_DIR = "./results"

STUDENT_FILE = os.path.join(INPUTS_DIR, "student_answers.json")
REFERENCE_FILE = os.path.join(INPUTS_DIR, "reference_answers.json")
PROMPT_FILE = os.path.join(PROMPTS_DIR, "prompt.txt")
DOCS_FOLDER = os.path.join(INPUTS_DIR, "related_docs")
CSV_FILE = os.path.join(RESULTS_DIR, "evaluation_results.csv")
JSON_FILE = os.path.join(RESULTS_DIR, "evaluation_results.json")
CURRENT_STUDENT_FILE = os.path.join(TEMP_DIR, "current_student.json")

# Create necessary folders if they don't exist
os.makedirs(INCOMING_FOLDER, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(INPUTS_DIR, exist_ok=True)
os.makedirs(PROMPTS_DIR, exist_ok=True)
os.makedirs(DOCS_FOLDER, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)


# --- Data Loaders ---
def load_json(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {} if "reference" in path else {"students": []} 

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# --- Initial Setup ---
reference_answers = load_json(REFERENCE_FILE)

with open(PROMPT_FILE, "r", encoding="utf-8") as f:
    BASE_PROMPT = f.read()


# --- Upload related docs ---
def upload_related_docs(folder_path):
    uploaded_files = []
    if not os.path.exists(folder_path):
        return uploaded_files

    SUPPORTED_EXTENSIONS = [".pdf", ".docx", ".txt", ".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp"]
    print("Starting document and image upload for context...")

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if not os.path.isfile(file_path):
            continue
        ext = os.path.splitext(filename)[1].lower()
        if ext not in SUPPORTED_EXTENSIONS:
            print(f"Skipping unsupported file type: {filename}")
            continue
        print(f"Uploading file: {filename}")
        try:
            uploaded_file = genai.upload_file(path=file_path)
            uploaded_files.append(uploaded_file)
        except Exception as e:
            print(f"Failed to upload {filename}: {e}")
            
    print(f"Uploaded {len(uploaded_files)} context files.")
    return uploaded_files

related_docs = upload_related_docs(DOCS_FOLDER)
if not related_docs:
    print("No context documents found. Grading will rely only on prompt and answers.")


# --- Gemini Evaluation Function ---
def evaluate_with_gemini(student_ans, ref_ans, max_marks):
    full_prompt = f"""{BASE_PROMPT}

Reference Answer:
{ref_ans}

Student Answer:
{student_ans}

Maximum Marks: {max_marks}

Use any additional context from the uploaded related documents to ensure more accurate grading.
"""
    contents = [full_prompt]
    if related_docs:
        contents.extend(related_docs)

    try:
        response = model.generate_content(contents=contents)
        text = response.text.strip()

        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end != -1:
            json_str = text[start:end+1]
            result = json.loads(json_str)
            return result.get("awarded_marks", 0), result.get("feedback", "")
        else:
            return 0, f"Invalid response format. Raw text: {text[:100]}..."
    except Exception as e:
        return 0, f"API Error: {str(e)}"


# --- Main Evaluation Logic ---
def process_new_student():
    files = [f for f in os.listdir(INCOMING_FOLDER) if f.endswith(".json")]
    if not files:
        print("No new student submission found.")
        return

    latest_file = max([os.path.join(INCOMING_FOLDER, f) for f in files], key=os.path.getctime)
    print(f"Found new submission: {latest_file}")

    with open(latest_file, "r", encoding="utf-8") as f:
        student_entry = json.load(f)

    student_info = student_entry.get("student_info", {})
    student_answers = student_entry.get("answers", {})

    student_name = student_info.get("name", "")
    roll_no = student_info.get("roll_no", "")
    print(f"Evaluating student: {student_name} ({roll_no})")

    # Load persistent results files
    student_data = load_json(STUDENT_FILE)
    master_results = load_json(JSON_FILE)

    evaluation_results = []
    total_awarded = 0
    total_possible = 0

    for qno, student_ans in student_answers.items():
        ref_info = reference_answers.get(str(qno))
        if not ref_info:
            evaluation_results.append({
                "question_no": qno, "awarded_marks": 0, "max_marks": 0,
                "feedback": "No reference answer found",
                "student_answer": student_ans, "reference_answer": "N/A"
            })
            continue

        ref_ans = ref_info["answer"]
        max_marks = ref_info["marks"]

        print(f"Processing Question {qno}...")
        awarded, feedback = evaluate_with_gemini(student_ans, ref_ans, max_marks)

        total_awarded += awarded
        total_possible += max_marks

        evaluation_results.append({
            "question_no": qno,
            "student_answer": student_ans,
            "reference_answer": ref_ans,
            "max_marks": max_marks,
            "awarded_marks": awarded,
            "feedback": feedback
        })

    # --- Prepare current_student.json with marks ---
    current_student_record = {
        "student_info": student_info,
        "total_awarded_marks": total_awarded,
        "total_possible_marks": total_possible,
        "answers": {}
    }

    for r in evaluation_results:
        current_student_record["answers"][r["question_no"]] = {
            "answer": r["student_answer"],
            "awarded_marks": r["awarded_marks"],
            "max_marks": r["max_marks"],
            "feedback": r["feedback"]
        }

    # Save temp JSON
    os.makedirs(TEMP_DIR, exist_ok=True)
    with open(CURRENT_STUDENT_FILE, "w", encoding="utf-8") as f:
        json.dump(current_student_record, f, indent=4, ensure_ascii=False)

    # Append to master JSON files
    student_data.setdefault("students", []).append(current_student_record)
    save_json(STUDENT_FILE, student_data)

    master_results.setdefault("students", []).append(current_student_record)
    save_json(JSON_FILE, master_results)

    # Append results to CSV
    csv_exists = os.path.exists(CSV_FILE)
    with open(CSV_FILE, "a", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        if not csv_exists or os.path.getsize(CSV_FILE) == 0:
            writer.writerow(["Student Name", "Roll No", "Question No", "Student Answer", 
                             "Reference Answer", "Max Marks", "Awarded Marks", "Feedback"])
        for r in evaluation_results:
            writer.writerow([student_name, roll_no, r["question_no"], r["student_answer"], 
                             r["reference_answer"], r["max_marks"], r["awarded_marks"], r["feedback"]])

    print(f"\nEvaluation complete for {student_name}")
    print(f"Final Score: {total_awarded}/{total_possible}")
    print(f"Current student record saved at: {CURRENT_STUDENT_FILE}")
    print(f"Updated results saved in JSON and CSV.")

    # Cleanup
    os.remove(latest_file)
    print(f"Removed processed file: {latest_file}")


# --- Run Script ---
if __name__ == "__main__":
    process_new_student()
