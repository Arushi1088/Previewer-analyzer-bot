
from fastapi import FastAPI, UploadFile, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os, uuid, json
from typing import Optional
from core.video import extract_keyframes
from core.schemas import Config
from core.prompt import build_prompt
from core.llm import call_llm
from core.eval import evaluate_run
from core.reports import write_html_report
import yaml

app = FastAPI()
BASE_DIR = os.path.dirname(__file__)
STATIC_DIR = os.path.join(BASE_DIR, "static")
DATA_DIR = os.path.join(BASE_DIR, "data")
RUNS_DIR = os.path.join(STATIC_DIR, "runs")

os.makedirs(RUNS_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

def parse_config_text(bytes_buf: bytes) -> Config:
    text = bytes_buf.decode("utf-8", errors="ignore")
    # Try YAML/JSON then fallback to simple key:value lines
    try:
        obj = yaml.safe_load(text)
        return Config(**obj)
    except Exception:
        pass
    try:
        obj = json.loads(text)
        return Config(**obj)
    except Exception:
        pass
    # naive fallback
    kv = {}
    for line in text.splitlines():
        if ":" in line:
            k,v = line.split(":",1)
            kv[k.strip()] = v.strip()
    # Provide minimal defaults if missing
    obj = {
        "scenario_id": kv.get("scenario_id","scenario_"+str(uuid.uuid4())[:8]),
        "source_apps": [s.strip() for s in kv.get("source_apps","Outlook,ExcelPreviewer,ExcelDesktop").split(",") if s.strip()],
        "file_size_bucket": kv.get("file_size_bucket","medium"),
        "protection_level": kv.get("protection_level","none"),
        "file_type": kv.get("file_type","xlsx"),
        "notes": kv.get("notes","")
    }
    return Config(**obj)

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    # list runs
    runs = []
    if os.path.exists(RUNS_DIR):
        runs = sorted(os.listdir(RUNS_DIR), reverse=True)[:20]
    return templates.TemplateResponse("index.html", {"request": request, "runs": runs})

@app.post("/analyze")
async def analyze(request: Request, video: UploadFile, config_text: UploadFile):
    run_id = str(uuid.uuid4())
    run_dir = os.path.join(RUNS_DIR, run_id)
    frames_dir = os.path.join(run_dir, "frames")
    os.makedirs(frames_dir, exist_ok=True)

    # Save inputs
    vid_path = os.path.join(run_dir, video.filename)
    with open(vid_path, "wb") as f:
        f.write(await video.read())

    cfg_bytes = await config_text.read()
    cfg = parse_config_text(cfg_bytes)

    # Extract frames
    frames = extract_keyframes(vid_path, frames_dir)

    # Build prompt and call LLM
    prompt = build_prompt(cfg, frames)
    llm_json = await call_llm(prompt)  # returns dict

    # Persist outputs
    with open(os.path.join(run_dir, "llm_output.json"), "w", encoding="utf-8") as f:
        json.dump(llm_json, f, indent=2, ensure_ascii=False)

    # Eval vs built-in golden list
    eval_payload = evaluate_run(cfg.scenario_id, llm_json)
    with open(os.path.join(run_dir, "eval.json"), "w", encoding="utf-8") as f:
        json.dump(eval_payload, f, indent=2, ensure_ascii=False)

    # Write HTML report
    report_path = write_html_report(run_dir, cfg, frames, llm_json, eval_payload)

    return {
        "run_id": run_id,
        "report_url": f"/report/{run_id}",
        "llm_output": f"/static/runs/{run_id}/llm_output.json",
        "eval": f"/static/runs/{run_id}/eval.json",
    }

@app.get("/report/{run_id}", response_class=FileResponse)
def report(run_id: str):
    path = os.path.join(RUNS_DIR, run_id, "report.html")
    return FileResponse(path, media_type="text/html")
