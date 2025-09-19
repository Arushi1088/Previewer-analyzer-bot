# Previewer Analyzer Bot

An AI-powered QA analysis tool that uses GPT-4o vision capabilities to analyze mobile app screenshots and identify bugs, issues, and user flow violations in Outlook→Excel Previewer→Excel Desktop workflows.

## Features

- **Vision Analysis**: Uses GPT-4o to analyze screenshots and identify UI bugs
- **Automated Bug Detection**: Detects functional and craft issues in user flows
- **Step-by-Step Analysis**: Breaks down user interactions into clear steps
- **Azure OpenAI Integration**: Leverages Azure OpenAI for scalable AI processing
- **Web Interface**: Clean, modern web UI for uploading videos and viewing reports
- **Real-time Processing**: Fast analysis with progress indicators

## Architecture

- **Backend**: FastAPI with Python
- **AI Model**: GPT-4o via Azure OpenAI
- **Frontend**: HTML/CSS/JavaScript with modern UI
- **Video Processing**: Keyframe extraction from MP4/MOV files
- **Image Processing**: Base64 encoding and compression for efficient AI analysis

## Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Arushi1088/Previewer-analyzer-bot.git
   cd Previewer-analyzer-bot
   ```

2. **Set up Azure OpenAI**:
   - Create an Azure OpenAI resource
   - Deploy GPT-4o model
   - Copy `azure_config.env.example` to `azure_config.env`
   - Fill in your Azure OpenAI credentials

3. **Install dependencies**:
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Start the server**:
   ```bash
   source .venv/bin/activate
   source ~/.zshrc  # Load environment variables
   uvicorn app:app --port 8080
   ```

5. **Open the application**:
   - Navigate to `http://localhost:8080`
   - Upload a video file (MP4/MOV) and config file
   - Click "Analyze" to start the AI-powered analysis
   - View the detailed report with bug findings and user flow steps

## Configuration

The system requires a config file (YAML/JSON/TOML/TXT) with the following structure:

```yaml
scenario_id: "test_scenario_001"
source_apps: ["Outlook", "ExcelPreviewer", "ExcelDesktop"]
file_size_bucket: "medium"  # small, medium, large, xl
protection_level: "none"    # none, password, sensitivity_label
file_type: "xlsx"          # xlsx, pdf, docx, etc.
notes: "Optional description"
```

## API Endpoints

- `GET /` - Main upload interface
- `POST /analyze` - Process video and generate analysis
- `GET /report/{run_id}` - View analysis report
- `GET /static/runs/{run_id}/llm_output.json` - Raw LLM output
- `GET /static/runs/{run_id}/eval.json` - Evaluation results

## Analysis Output

The system generates comprehensive reports including:

- **Bug Detection**: Identifies functional and craft issues with severity levels
- **User Flow Steps**: Breaks down the interaction into clear steps
- **Evidence Frames**: Links bugs to specific screenshot evidence
- **Suggestions**: Provides actionable recommendations for fixes
- **Assumptions**: Documents assumptions made during analysis

## Example Bug Categories

- **Functional Bugs**: Logic errors, incorrect behavior, missing features
- **Craft Issues**: UI/UX problems, visual inconsistencies, accessibility issues
- **Flow Violations**: Unexpected user experience, missing steps, confusing navigation

## Technology Stack

- **Backend**: FastAPI, Python 3.11+
- **AI**: Azure OpenAI GPT-4o
- **Image Processing**: PIL (Pillow)
- **Video Processing**: OpenCV
- **Web Server**: Uvicorn
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions, please open an issue on GitHub or contact the maintainers.