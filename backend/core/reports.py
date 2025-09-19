
import os, datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")

env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(['html', 'xml'])
)

def write_html_report(run_dir, cfg, frames, llm_json, eval_payload=None):
    tpl = env.get_template("report.html")
    html = tpl.render(
        scenario_id=cfg.scenario_id,
        generated=datetime.datetime.utcnow().isoformat()+"Z",
        cfg=cfg,
        frames=frames,
        llm=llm_json,
        eval=eval_payload
    )
    out = os.path.join(run_dir, "report.html")
    with open(out,"w",encoding="utf-8") as f:
        f.write(html)
    return out
