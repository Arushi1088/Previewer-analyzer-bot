# Config File Schema Documentation

The analyzer bot accepts configuration files in three formats: **YAML**, **JSON**, or **simple text**. Upload this alongside your video file to provide context for the analysis.

## Schema Fields

| Field | Type | Required | Options | Description |
|-------|------|----------|---------|-------------|
| `scenario_id` | string | ✅ | Any | Unique identifier for this test scenario |
| `source_apps` | array | ✅ | App names | List of apps involved in the flow (e.g., ["Outlook", "ExcelPreviewer"]) |
| `file_size_bucket` | string | ✅ | `small`, `medium`, `large` | Size category of the file being processed |
| `protection_level` | string | ✅ | `none`, `password`, `confidential`, `highly_confidential` | File protection/security level |
| `file_type` | string | ❌ | `xlsx`, `xls`, `csv`, `other` | File type (defaults to "xlsx") |
| `notes` | string | ❌ | Any | Additional context or description of the scenario |

## Format Examples

### YAML Format
```yaml
scenario_id: "outlook_preview_to_excel_001"
source_apps: 
  - "Outlook"
  - "ExcelPreviewer" 
  - "ExcelDesktop"
file_size_bucket: "medium"
protection_level: "confidential"
file_type: "xlsx"
notes: "Open attachment in Previewer → Open in Desktop → edit."
```

### JSON Format
```json
{
  "scenario_id": "outlook_preview_to_excel_001",
  "source_apps": ["Outlook", "ExcelPreviewer", "ExcelDesktop"],
  "file_size_bucket": "medium",
  "protection_level": "confidential",
  "file_type": "xlsx",
  "notes": "Open attachment in Previewer → Open in Desktop → edit."
}
```

### Simple Text Format
```
scenario_id: outlook_preview_to_excel_001
source_apps: Outlook,ExcelPreviewer,ExcelDesktop
file_size_bucket: medium
protection_level: confidential
file_type: xlsx
notes: Open attachment in Previewer → Open in Desktop → edit.
```

## Common Scenarios

### Password-Protected File
```yaml
scenario_id: "password_protected_large_file_002"
source_apps: ["Outlook", "ExcelPreviewer", "ExcelDesktop"]
file_size_bucket: "large"
protection_level: "password"
file_type: "xlsx"
notes: "Large password-protected file should prompt for password before opening."
```

### No App Installed
```
scenario_id: no_app_install_required_003
source_apps: Outlook,ExcelPreviewer
file_size_bucket: small
protection_level: none
file_type: xlsx
notes: No Excel app installed - should show install guidance
```

### Account Mismatch
```json
{
  "scenario_id": "account_mismatch_secondary_primary_004",
  "source_apps": ["Outlook", "ExcelPreviewer", "ExcelDesktop"],
  "file_size_bucket": "medium",
  "protection_level": "confidential",
  "file_type": "xlsx",
  "notes": "Secondary account in Outlook, Primary in Excel - should handle account switching gracefully"
}
```

## Usage

1. Create a config file in your preferred format
2. Upload both the video file and config file to http://localhost:8080
3. The system will parse the config and use it to provide context-aware analysis

## Validation

The system automatically validates:
- Required fields are present
- Enum values are valid (e.g., `file_size_bucket` must be one of the allowed options)
- Data types are correct
- Provides helpful error messages for invalid configurations

## Tips

- Use descriptive `scenario_id` values for easy identification
- Include relevant apps in `source_apps` for accurate flow analysis
- Add detailed `notes` to help the LLM understand the expected behavior
- Choose appropriate `protection_level` and `file_size_bucket` for realistic testing scenarios




