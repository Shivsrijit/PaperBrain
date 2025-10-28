import os
import json
from typing import Any, Dict

from flask import Flask, request, jsonify
from flask_cors import CORS

from controller.main_controller import PipelineController, run_pipeline_after_uploads


app = Flask(__name__)
CORS(app)


UPLOAD_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "uploads"))
os.makedirs(UPLOAD_ROOT, exist_ok=True)


def _save_file(field_name: str) -> str:
    file = request.files.get(field_name)
    if not file:
        return ""
    dest = os.path.join(UPLOAD_ROOT, file.filename)
    file.save(dest)
    return dest


@app.route("/api/health", methods=["GET"]) 
def health() -> Any:
    return jsonify({"status": "ok"})


@app.route("/api/upload", methods=["POST"]) 
def upload() -> Any:
    """
    Accepts multipart/form-data with fields:
    - answer_key: file
    - answer_sheet: file
    - related_docs: multiple files (use related_docs[])
    """
    answer_key_path = _save_file("answer_key")
    answer_sheet_path = _save_file("answer_sheet")

    # related_docs can be multiple
    related_docs_files = request.files.getlist("related_docs") or request.files.getlist("related_docs[]")
    related_doc_paths = []
    for f in related_docs_files:
        dest = os.path.join(UPLOAD_ROOT, f.filename)
        f.save(dest)
        related_doc_paths.append(dest)

    if not answer_key_path or not answer_sheet_path:
        return jsonify({"error": "answer_key and answer_sheet are required"}), 400

    controller = PipelineController()
    saved = controller.save_uploads(answer_key_path, answer_sheet_path, related_doc_paths)
    return jsonify({"saved": saved})


@app.route("/api/run", methods=["POST"]) 
def run_pipeline() -> Any:
    data: Dict[str, Any] = request.get_json(silent=True) or {}
    # optional: accept paths if already uploaded via other means
    answer_key = data.get("answer_key_path")
    answer_sheet = data.get("answer_sheet_path")
    related = data.get("related_docs_paths", [])

    if answer_key and answer_sheet:
        results = run_pipeline_after_uploads(answer_key, answer_sheet, related)
        return jsonify(results)

    # Otherwise run pipeline on already saved files in agents dirs
    controller = PipelineController()
    results = controller.run_pipeline()
    return jsonify({"saved": {}, "results": results})


@app.route("/api/results/current-student", methods=["GET"]) 
def current_student() -> Any:
    controller = PipelineController()
    path = controller.evaluator_temp_student
    if os.path.isfile(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return jsonify(data)
        except Exception:
            return jsonify({"error": "failed to read current_student.json"}), 500
    return jsonify({"error": "current_student.json not found"}), 404


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)


