# Overleaf Backup

Download and backup all your Overleaf projects locally with a single command.

## Overview

This script automates downloading all your Overleaf projects as ZIP files, organizing them into timestamped backup folders. It includes parallel downloads for speed, progress tracking, and detailed error reporting.

**Features:**
- ✅ Single-command backup of all Overleaf projects
- ✅ Parallel downloads (configurable, 4 threads by default)  
- ✅ Timestamped backups prevent overwrites on re-runs
- ✅ Progress bar and success/failure summary
- ✅ JSON metadata with backup statistics

## Quick Start

### Prerequisites

- Python 3.7+
- `pip` (included with Python)

### Installation

1. **Clone or download this repository**

2. **Create and activate a virtual environment:**

   ```bash
   # Linux/macOS
   python3 -m venv .venv
   source .venv/bin/activate
   
   # Windows
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure your Overleaf session cookie:**

   **Option A: Using .env file (Recommended)**

   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Open `.env` and paste your cookie value:
     ```
     OVERLEAF_SESSION_COOKIE=your_cookie_value_here
     ```
   - The script will automatically read from `.env`

   **Option B: Direct in script**

   - Edit `overleaf_backup.py` and set:
     ```python
     SESSION_COOKIE = "your_cookie_value_here"
     ```

   **Option C: Environment variable**

   ```bash
   export OVERLEAF_SESSION_COOKIE="your_cookie_value_here"
   python3 overleaf_backup.py
   ```

   **How to get your cookie:**

   - Open https://www.overleaf.com and log in
   - Open Developer Tools (F12 or Ctrl+Shift+I)
   - Go to **Application** → **Cookies** → https://www.overleaf.com
   - Copy the value of `overleaf_session2`

5. **Run the backup:**

   ```bash
   python overleaf_backup.py
   ```

That's it! Your projects will be downloaded to `overleaf_backup/backup_YYYYMMDD_HHMMSS/`

## How It Works

### What Gets Downloaded

Each Overleaf project is downloaded as a ZIP file and extracted to a folder containing:
- Source files (`.tex`, `.bib`, etc.)
- PDFs and compiled output
- Images and other assets
- Project structure preserved

### Output Format

```
overleaf_backup/
├── backup_20260312_120000/
│   ├── Project_Name_1_[project_id]/
│   │   ├── main.tex
│   │   ├── main.pdf
│   │   └── ...
│   ├── Project_Name_2_[project_id]/
│   ├── backup_summary.json
│   └── ...
├── backup_20260313_090000/
│   └── ...
```

### Backup Summary

Each backup includes a `backup_summary.json` file:

```json
{
  "timestamp": "20260312_120000",
  "total_projects": 24,
  "successful": 24,
  "failed": []
}
```

## Environment Configuration (.env)

The recommended way to store your session cookie is using a `.env` file:

1. **Copy the example file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` and add your cookie:**
   ```
   OVERLEAF_SESSION_COOKIE=s%3AyourActualCookieValueHere.moreCookieDataHere
   ```

3. **The script automatically reads from `.env`**

The `.env` file is ignored by Git (see `.gitignore`), so your cookie won't be accidentally committed to version control.

**Available environment variables:**
- `OVERLEAF_SESSION_COOKIE` - Your Overleaf session token (required)

## Configuration

Edit these variables in `overleaf_backup.py` to customize behavior:

| Variable | Default | Description |
|----------|---------|-------------|
| `SESSION_COOKIE` | `"..."` | Your Overleaf session token (required) |
| `MAX_THREADS` | `4` | Number of parallel downloads |
| `REQUEST_TIMEOUT` | `60` | Network request timeout in seconds |
| `DOWNLOAD_DIR` | `"overleaf_backup"` | Where to save backups |
| `BASE_URL` | `"https://www.overleaf.com"` | Overleaf server URL |

## Troubleshooting

### "ModuleNotFoundError: No module named 'requests'"

Ensure the virtual environment is activated and dependencies are installed:

```bash
source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
```

### "Cookie expired" or "Could not extract project state"

Your session cookie has expired. Extract a fresh cookie from your browser using the steps in Quick Start.

### "http 403" or download failures

Some projects may have restricted access. Check that you can access the project manually on Overleaf. If so, try getting a fresh cookie.

### Slow downloads

Increase `MAX_THREADS` in the script:

```python
MAX_THREADS = 8  # or higher
```

## Running on Different Systems

### Linux/macOS
```bash
python3 -m venv .venv
source .venv/bin/activate
python3 overleaf_backup.py
```

### Windows
```bash
python -m venv .venv
.venv\Scripts\activate
python overleaf_backup.py
```

## Using in PyCharm

### Open Project

1. **Open PyCharm** and select **File → Open**
2. Navigate to this folder and click **Open**
3. PyCharm will detect the `.venv` virtual environment

### Configure Python Interpreter

1. Go to **File → Settings** (Linux/Windows) or **PyCharm → Preferences** (macOS)
2. Navigate to **Project: Overleaf Backup → Python Interpreter**
3. Click the gear icon ⚙️ → **Add...**
4. Select **Existing Environment**
5. Browse to `.venv/bin/python` (Linux/macOS) or `.venv\Scripts\python.exe` (Windows)
6. Click **OK**

PyCharm will automatically install the dependencies from `requirements.txt`.

### Add Your Cookie and Run

1. Open `overleaf_backup.py` in the editor
2. Find the line `SESSION_COOKIE = "your_overleaf_session2_cookie"`
3. Replace it with your actual cookie value
4. Right-click in the editor and select **Run 'overleaf_backup'** (or press Shift+F10)

### Running from PyCharm Terminal

You can also run it from the built-in terminal:

```bash
python overleaf_backup.py
```

The virtual environment is automatically activated in PyCharm's terminal.

### View Output

- **Run results** appear in the Run tool window at the bottom
- **Backup folder** is created in `overleaf_backup/`
- **Backup summary** is saved as `backup_summary.json`

## Files

- `overleaf_backup.py` - Main backup script
- `requirements.txt` - Python dependencies
- `README.md` - This file

## License

Free to use and modify.