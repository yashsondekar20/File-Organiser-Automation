# File Organizer Automation

A simple Streamlit app to organize files in a folder into categorized subfolders (Images, Documents, Videos, Audio, Archives, Programs, Executables, Others).

## Quick start

1. Create and activate a virtual environment (PowerShell):

```powershell
cd "D:\Python Projects\File Organizer Automation"
python -m venv .venv
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process -Force
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

2. Run the app:

```powershell
python -m streamlit run app.py
```

3. Open the URL shown by Streamlit (usually `http://localhost:8501`).

## Notes
- The app moves files found directly in the provided folder (non-recursive).
- The app creates category subfolders inside the given folder and moves files into them. Back up important files before running.

## Files to review
- `app.py` — Streamlit application
- `requirements.txt` — pinned dependencies
- `.gitignore` — recommended ignores