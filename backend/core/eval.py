
import csv, re, os
# from rapidfuzz import fuzz

def simple_similarity(a, b):
    """Simple string similarity function to replace rapidfuzz"""
    if not a or not b:
        return 0
    a_words = set(a.lower().split())
    b_words = set(b.lower().split())
    if not a_words or not b_words:
        return 0
    intersection = len(a_words.intersection(b_words))
    union = len(a_words.union(b_words))
    return int((intersection / union) * 100) if union > 0 else 0

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

def normalize(title: str) -> str:
    x = (title or "").lower()
    x = re.sub(r'[^a-z0-9 ]+',' ', x)
    x = re.sub(r'\s+',' ', x).strip()
    return x

def load_golden(default_golden_csv=None):
    path = default_golden_csv or os.path.join(DATA_DIR, "golden_bugs.csv")
    rows=[]
    if not os.path.exists(path):
        return rows
    with open(path, newline='', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            rows.append({"id": r["id"], "title": r["title"]})
    return rows

def evaluate_run(scenario_id, llm_json, default_golden_csv=None, threshold=80):
    golden = load_golden(default_golden_csv)
    pred_titles = []
    for bset in ("bugs","bugs_strong","bugs_minor"):
        for b in (llm_json.get(bset) or []):
            pred_titles.append(normalize(b.get("title","")))
    golden_titles = [normalize(g["title"]) for g in golden]

    matched, missed, extras = [], [], []
    # Match each golden against predictions
    for i, gt in enumerate(golden_titles):
        best, score = None, 0
        for j, pt in enumerate(pred_titles):
            s = simple_similarity(gt, pt)
            if s > score: best, score = j, s
        if score >= threshold:
            matched.append(golden[i]["id"])
        else:
            missed.append(golden[i]["id"])

    # Extras: predicted that didn't match any golden
    for j, pt in enumerate(pred_titles):
        best, score = None, 0
        for i, gt in enumerate(golden_titles):
            s = simple_similarity(gt, pt)
            if s > score: best, score = i, s
        if score < threshold:
            extras.append(f"pred-{j}")

    tp, fp, fn = len(matched), len(extras), len(missed)
    precision = tp/(tp+fp) if (tp+fp)>0 else 0.0
    recall    = tp/(tp+fn) if (tp+fn)>0 else 0.0
    f1        = 2*precision*recall/(precision+recall) if (precision+recall)>0 else 0.0

    return {
      "scenario_id": scenario_id,
      "precision": round(precision,3),
      "recall": round(recall,3),
      "f1": round(f1,3),
      "matched": matched,
      "missed": missed,
      "extras": extras
    }
