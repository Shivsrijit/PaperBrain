import os
import json
import csv
from dotenv import load_dotenv
import google.generativeai as genai

# ============ Load environment variables ============ #
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("❌ GEMINI_API_KEY not found in .env file!")

# ============ Initialize Gemini ============ #
genai.configure(api_key=API_KEY)
MODEL_NAME = "gemini-2.5-flash"
model = genai.GenerativeModel(MODEL_NAME)

# ============ Load helper files ============ #
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

student_data = load_json("student_answers.json")
reference_answers = load_json("reference_answers.json")

student_info = student_data.get("student_info", {})
student_answers = student_data.get("answers", {})

with open("prompt.txt", "r", encoding="utf-8") as f:
    BASE_PROMPT = f.read()

CSV_FILE = "evaluation_results.csv"
JSON_FILE = "evaluation_results.json"

# ============ Evaluation Function ============ #
def evaluate_with_gemini(student_ans, ref_ans, max_marks):
    """
    Uses Gemini to compare student's and reference answers and award marks.
    """
    full_prompt = f"""{BASE_PROMPT}

Reference Answer:
{ref_ans}

Student Answer:
{student_ans}

Maximum Marks: {max_marks}
"""
    try:
        response = model.generate_content(full_prompt)
        text = response.text.strip()

        # Extract JSON safely
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            json_str = text[start:end+1]
            result = json.loads(json_str)
            return result.get("awarded_marks", 0), result.get("feedback", "")
        else:
            return 0, "Invalid response format"
    except Exception as e:
        return 0, f"Error: {str(e)}"

# ============ Main Evaluation Loop ============ #
evaluation_results = []
total_awarded = 0
total_possible = 0

for qno, student_ans in student_answers.items():
    ref_info = reference_answers.get(qno)
    if not ref_info:
        evaluation_results.append({
            "question_no": qno,
            "student_answer": student_ans,
            "reference_answer": "N/A",
            "max_marks": 0,
            "awarded_marks": 0,
            "feedback": "No reference answer found"
        })
        continue

    ref_ans = ref_info["answer"]
    max_marks = ref_info["marks"]

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

# ============ Save to CSV ============ #
with open(CSV_FILE, "w", newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["Question No", "Student Answer", "Reference Answer", "Max Marks", "Awarded Marks", "Feedback"])
    for r in evaluation_results:
        writer.writerow([r["question_no"], r["student_answer"], r["reference_answer"], r["max_marks"], r["awarded_marks"], r["feedback"]])

# ============ Save to JSON ============ #
output_json = {
    "student_info": student_info,
    "total_awarded_marks": total_awarded,
    "total_possible_marks": total_possible,
    "evaluation_results": evaluation_results
}

with open(JSON_FILE, "w", encoding="utf-8") as f:
    json.dump(output_json, f, indent=4, ensure_ascii=False)

print(f"\n✅ Evaluation complete!")
print(f"📁 CSV saved at: {CSV_FILE}")
print(f"📁 JSON saved at: {JSON_FILE}")
