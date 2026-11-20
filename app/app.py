"""Flask API + UI for the job recommendation engine (Task 5) and report viewer."""
import sys
from pathlib import Path
from flask import Flask, jsonify, render_template, request, send_from_directory, abort

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.common import REPORTS, MODELS            # noqa: E402
from src.task5_recommender import JobRecommender, MODEL_PATH  # noqa: E402

app = Flask(__name__)
_rec = None


def rec() -> JobRecommender:
    global _rec
    if _rec is None:
        if not MODEL_PATH.exists():
            from src.task5_recommender import run
            run()
        _rec = JobRecommender.load()
    return _rec


@app.get("/")
def index():
    return render_template("index.html", meta=rec().meta())


@app.get("/api/health")
def health():
    return {"status": "ok", "jobs_indexed": len(rec().jobs)}


@app.get("/api/meta")
def meta():
    return jsonify(rec().meta())


@app.route("/api/recommend", methods=["GET", "POST"])
def recommend():
    p = request.get_json(silent=True) or request.args
    q = (p.get("query") or p.get("q") or "").strip()
    if not q:
        return jsonify(error="'query' is required (skills, role or keywords)"), 400
    try:
        top_n = max(1, min(int(p.get("top_n", 10)), 50))
        min_rate = float(p["min_rate"]) if p.get("min_rate") not in (None, "") else None
    except (TypeError, ValueError):
        return jsonify(error="top_n and min_rate must be numbers"), 400
    job_type = p.get("job_type") or None
    if job_type not in (None, "hourly", "fixed"):
        return jsonify(error="job_type must be 'hourly' or 'fixed'"), 400
    remote = str(p.get("remote_only", "")).lower() in ("1", "true", "yes", "on")
    res = rec().recommend(q, top_n=top_n, country=p.get("country") or None, job_type=job_type, min_rate=min_rate, remote_only=remote)
    return jsonify(query=q, count=len(res), results=res)


@app.get("/dashboard")
def dashboard():
    return send_from_directory(REPORTS, "task6_dashboard.html")


@app.get("/reports/<path:name>")
def reports(name):
    if not (REPORTS / name).is_file():
        abort(404)
    return send_from_directory(REPORTS, name)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
