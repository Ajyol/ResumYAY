
## Installation Guide

### Step 1: Install Ollama

**For macOS:**
```bash
# Download and install from official website
curl -fsSL https://ollama.com/install.sh | sh

# Or using Homebrew
brew install ollama
```

**For Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**For Windows:**
- Download the installer from [ollama.com](https://ollama.com)
- Run the installer and follow instructions

### Step 2: Start Ollama Service

```bash
# Start Ollama service (this runs in the background)
ollama serve
```

Leave this terminal open or run it as a background service.

### Step 3: Download AI Model

In a new terminal, download the required AI model:

```bash
# Download the Llama 3.2 3B model (recommended for this project)
ollama pull llama3.2:3b

# Alternative: For better accuracy but slower processing
ollama pull llama3.2:7b
```

**Model Options:**
- `llama3.2:3b` - Faster, lower memory usage (4GB RAM)
- `llama3.2:7b` - Better accuracy, higher memory usage (8GB RAM)
- `llama3.2:1b` - Fastest, lowest accuracy (2GB RAM)

### Step 4: Set Up Python Environment

```bash
# Create a virtual environment
python3 -m venv resume_parser_env

# Activate the virtual environment
# On macOS/Linux:
source resume_parser_env/bin/activate

# On Windows:
resume_parser_env\Scripts\activate
```

### Step 5: Install Python Dependencies

```bash
# Install required packages
pip install requests PyPDF2
```

**Required Python Packages:**
- `requests` - For communicating with Ollama API
- `PyPDF2` - For extracting text from PDF files
- `json` - Built-in Python module for JSON handling
- `re` - Built-in Python module for regex operations
- `sys` - Built-in Python module for system operations

## Project Setup

### Step 6: Download the Code

Save the resume parser code as `resume_parser.py` in your project directory.

### Step 7: Verify Installation

Test that everything is working:

```bash
# Check if Ollama is running
curl http://localhost:11434/api/version

# Check if the model is installed
ollama list
```

You should see your downloaded model in the list.

## Usage

### Basic Usage

```bash
# Make sure your virtual environment is activated
source resume_parser_env/bin/activate  # On macOS/Linux
# resume_parser_env\Scripts\activate    # On Windows

# Parse a resume
python resume_parser.py sample_resume.pdf
```

### Expected Output

The script will:
1. Extract text from the PDF
2. Send it to the local AI model for parsing
3. Save the results as `sample_resume_parsed.json`

### Sample Output Structure

```json
{
  "personal_info": {
    "name": "John Doe",
    "email": "john.doe@email.com",
    "phone": "(555) 123-4567",
    "location": "New York, NY",
    "linkedin": "linkedin.com/in/johndoe",
    "github": "github.com/johndoe",
    "portfolio": "johndoe.dev"
  },
  "skills": {
    "technical_skills": ["Machine Learning", "Data Analysis"],
    "programming_languages": ["Python", "JavaScript", "SQL"],
    "frameworks": ["React", "Django", "TensorFlow"],
    "tools": ["Git", "Docker", "AWS"],
    "databases": ["PostgreSQL", "MongoDB"]
  },
  "experience": [...],
  "education": [...],
  "projects": [...],
  "certifications": [...],
  "honors_achievements": [...]
}
```

## Troubleshooting

### Common Issues

**Error: "Connection refused"**
- Make sure Ollama is running: `ollama serve`
- Check if the service is accessible: `curl http://localhost:11434/api/version`

**Error: "Model not found"**
- Ensure you've downloaded the model: `ollama pull llama3.2:3b`
- Check available models: `ollama list`

**Error: "'NoneType' object has no attribute 'group'"**
- The AI model might not be generating valid JSON
- Try a different model or check the debug output
- Ensure your PDF has readable text

**Poor parsing results**
- Try a larger model like `llama3.2:7b`
- Ensure your PDF has clear, readable text
- Check if the PDF text extraction is working properly

### Performance Tips

**For faster processing:**
- Use `llama3.2:1b` or `llama3.2:3b` models
- Ensure sufficient RAM is available
- Close other memory-intensive applications

**For better accuracy:**
- Use `llama3.2:7b` or larger models
- Ensure PDFs have clear, well-formatted text
- Review and adjust the parsing prompt if needed

