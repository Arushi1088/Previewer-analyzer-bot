
import json, os, textwrap, base64
from PIL import Image
import io

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

def load_blueprint():
    bp_path = os.path.join(DATA_DIR, "mobile_prompt_blueprint.md")
    try:
        with open(bp_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""

def load_critical_rules(max_rules=10):
    """Load and select the most critical rules from rulebook.json."""
    rulebook_path = os.path.join(DATA_DIR, "rulebook.json")
    try:
        with open(rulebook_path, "r", encoding="utf-8") as f:
            rulebook = json.load(f)
    except Exception:
        return ""
    
    # Define priority order for critical rules (most important first)
    priority_rules = [
        "R25_password_prompt_presence",      # Password protection critical
        "R32_error_actionable_copy",         # Error handling critical
        "R29_error_over_spinner",            # UI state critical
        "R31_error_primacy",                 # UI layering critical
        "R30_state_regression_after_error",  # State management critical
        "R26_redundant_desktop_cta_under_100mb",  # File size handling
        "R34_password_label_flow",           # Complex protection scenarios
        "R35_account_mismatch_primary_secondary",  # Account handling
        "R36_account_mismatch_secondary_primary",  # Account handling
        "R37_app_precedence_when_multiple",  # App selection logic
        "R38_no_app_installed_requires_store_cta",  # Installation guidance
        "R39_xl_threshold_desktop_redirect", # Large file handling
        "R27_loader_duplication"             # UI consistency
    ]
    
    # Select top rules that exist in the rulebook
    selected_rules = []
    for rule_id in priority_rules:
        if rule_id in rulebook and len(selected_rules) < max_rules:
            selected_rules.append((rule_id, rulebook[rule_id]))
    
    # Format rules for prompt
    if not selected_rules:
        return ""
    
    rules_text = "\n\n## Critical Rules for Analysis:\n"
    for rule_id, rule_data in selected_rules:
        rules_text += f"\n**{rule_id}**: {rule_data.get('violation', 'No description')}\n"
        
        # Add key conditions if present
        if 'if' in rule_data:
            rules_text += f"  - Conditions: {json.dumps(rule_data['if'], separators=(',', ':'))}\n"
        if 'detect' in rule_data:
            rules_text += f"  - Detect: {rule_data['detect']}\n"
        if 'expect_cta_contains' in rule_data:
            rules_text += f"  - Expected CTA: {', '.join(rule_data['expect_cta_contains'])}\n"
        if 'forbid_errors' in rule_data:
            rules_text += f"  - Forbidden errors: {', '.join(rule_data['forbid_errors'])}\n"
    
    return rules_text

def build_prompt(cfg, frames):
    blueprint = load_blueprint()
    critical_rules = load_critical_rules(max_rules=10)
    
    # Convert frames to base64 and include both metadata and image content
    frames_with_images = []
    for f in frames:
        try:
            # Read and compress the image to reduce size
            with Image.open(f["path"]) as img:
                # Resize if too large (max 1024px width)
                if img.width > 1024:
                    ratio = 1024 / img.width
                    new_height = int(img.height * ratio)
                    img = img.resize((1024, new_height), Image.Resampling.LANCZOS)
                
                # Convert to RGB if needed and compress
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Save to bytes with compression
                img_buffer = io.BytesIO()
                img.save(img_buffer, format='JPEG', quality=85, optimize=True)
                img_data = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
            
            frame_data = {
                "index": f["index"], 
                "ts_ms": f["ts_ms"], 
                "rel_path": f["path"].split("static/")[-1],
                "image_base64": f"data:image/jpeg;base64,{img_data}"
            }
            frames_with_images.append(frame_data)
        except Exception as e:
            print(f"Warning: Could not encode image {f['path']}: {e}")
            # Fallback to metadata only
            frame_data = {
                "index": f["index"], 
                "ts_ms": f["ts_ms"], 
                "rel_path": f["path"].split("static/")[-1]
            }
            frames_with_images.append(frame_data)
    
    user_payload = {
        "scenario": {
            "id": cfg.scenario_id,
            "source_apps": cfg.source_apps,
            "file_size_bucket": cfg.file_size_bucket,
            "protection_level": cfg.protection_level,
            "file_type": cfg.file_type,
            "notes": cfg.notes or ""
        },
        "frames": frames_with_images,
        "instructions": {
            "return_format": {
                "bugs":[{"id":"","title":"","description":"","severity":"","category":"","evidence_frames":[],"suggestions":""}],
                "steps":[{"step_no":0,"summary":"","frames":[]}],
                "assumptions":"",
                "metadata":{"version":"v0"}
            }
        }
    }
    
    # Build system prompt with character limit management
    system = """You are a meticulous QA triage assistant for Outlook→Excel Previewer→Excel Desktop flows. 

CRITICAL: You must respond with ONLY valid JSON. No additional text, explanations, or formatting outside the JSON structure.

Analyze the provided mobile app screenshots and identify:
1. Bugs, issues, or violations in the user interface
2. Steps in the user flow
3. Any assumptions about the scenario

Return your analysis in this EXACT JSON format:
{
  "bugs": [{"id": "BUG-001", "title": "Bug title", "description": "Detailed description", "severity": "High/Medium/Low", "category": "Functional/Craft", "evidence_frames": [0, 1], "suggestions": "How to fix"}],
  "steps": [{"step_no": 1, "summary": "Step description", "frames": [0, 1]}],
  "assumptions": "Your assumptions about the scenario",
  "metadata": {"version": "v1.0"}
}"""
    
    # Add blueprint with dynamic sizing based on available space
    max_system_chars = 8000
    base_system_len = len(system)
    rules_len = len(critical_rules) if critical_rules else 0
    
    # Calculate available space for blueprint
    available_for_blueprint = max_system_chars - base_system_len - rules_len - 100  # 100 char buffer
    
    if blueprint and available_for_blueprint > 500:  # Only add if we have reasonable space
        system += "\n\n" + blueprint[:available_for_blueprint]
    
    # Add critical rules (these are prioritized)
    if critical_rules:
        system += critical_rules
    
    # Final safety check - truncate if still over limit
    if len(system) > max_system_chars:
        system = system[:max_system_chars-100] + "\n\n[Content truncated to fit limits]"
    
    return {
        "system": system,
        "user": json.dumps(user_payload, ensure_ascii=False)
    }
