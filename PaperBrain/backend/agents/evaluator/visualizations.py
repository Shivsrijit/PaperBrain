import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os

# ================= CONFIG =================
CSV_FILE = "results/evaluation_results.csv"  # your CSV path
JSON_FILE = "results/evaluation_results.json"  # optional
OUTPUT_FOLDER = "results/visualizations"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ================= LOAD DATA =================
df = pd.read_csv(CSV_FILE)

# For some analyses, you may want JSON too
with open(JSON_FILE, "r", encoding="utf-8") as f:
    json_data = json.load(f)

# ================= OVERALL STUDENT PERFORMANCE =================
student_scores = df.groupby(["Student Name", "Roll No"]).agg(
    total_awarded=("Awarded Marks", "sum"),
    total_possible=("Max Marks", "sum")
).reset_index()
student_scores["percentage"] = (student_scores["total_awarded"] / student_scores["total_possible"] * 100).round(2)

# Barplot: Student performance %
plt.figure(figsize=(10,6))
sns.barplot(x="Student Name", y="percentage", data=student_scores, palette="viridis")
plt.title("Overall Student Performance (%)")
plt.ylabel("Percentage Score")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_FOLDER, "student_performance.png"))
plt.close()

# ================= MOST INCORRECT QUESTIONS =================
# Count how many students got 0 or partial marks
incorrect_q = df[df["Awarded Marks"] < df["Max Marks"]]
incorrect_count = incorrect_q.groupby("Question No").size().reset_index(name="count")

plt.figure(figsize=(8,5))
sns.barplot(x="Question No", y="count", data=incorrect_count, palette="magma")
plt.title("Most Incorrect Questions (0 or Partial Marks)")
plt.ylabel("Number of Students with Incorrect Answer")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_FOLDER, "most_incorrect_questions.png"))
plt.close()

# ================= COMMON MISTAKES =================
# Extract key mistakes from Feedback
from collections import Counter
mistakes = []

for feedback in incorrect_q["Feedback"]:
    # Basic split; can be improved with NLP
    mistakes.append(feedback)

# Count most common mistake phrases
common_mistakes = Counter(mistakes).most_common(10)

mistake_df = pd.DataFrame(common_mistakes, columns=["Feedback", "Count"])
plt.figure(figsize=(10,6))
sns.barplot(y="Feedback", x="Count", data=mistake_df, palette="coolwarm")
plt.title("Top 10 Common Feedback / Mistakes Across Students")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_FOLDER, "common_mistakes.png"))
plt.close()

# ================= QUESTION-WISE AVERAGE SCORES =================
q_scores = df.groupby("Question No").agg(
    avg_awarded=("Awarded Marks", "mean"),
    max_marks=("Max Marks", "first")
).reset_index()
q_scores["percentage"] = (q_scores["avg_awarded"] / q_scores["max_marks"] * 100).round(2)

plt.figure(figsize=(10,6))
sns.barplot(x="Question No", y="percentage", data=q_scores, palette="plasma")
plt.title("Average Score (%) Per Question")
plt.ylabel("Average Percentage")
plt.ylim(0, 100)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_FOLDER, "avg_score_per_question.png"))
plt.close()

# ================= FLOWCHART-LIKE SUMMARY =================
# Overall summary table
summary_table = student_scores[["Student Name", "total_awarded", "total_possible", "percentage"]]
summary_table.to_csv(os.path.join(OUTPUT_FOLDER, "overall_summary.csv"), index=False)

print("Visualizations and summaries generated in:", OUTPUT_FOLDER)
