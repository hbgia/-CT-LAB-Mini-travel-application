# Mini Travel Application

A small Streamlit-based demo application for exploring travel-related features. This repository contains the Streamlit app (`app.py`), authentication helper (`auth.py`) and backend helpers (`backend.py`).

## Prerequisites

- Python 3.9 to Python 3.13

## Setup (Windows PowerShell)

1. Open **PowerShell** and create a virtual environment in the project folder:

```
python -m venv venv
```

2. Activate the virtual environment (**PowerShell**):

```
.\\venv\\Scripts\\Activate.ps1
```
If you see an **execution policy error**, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`

3. Install the required packages from `requirements.txt`:

```
pip install --upgrade pip
pip install -r requirements.txt
```

4. Run the Streamlit app:

```
streamlit run app.py
```

5. When finished, deactivate the virtual environment:

```
deactivate
```

## Notes

- If you prefer **Command Prompt (cmd.exe)** instead of PowerShell, activate the venv with:

```
venv\\Scripts\\activate.bat
```

- To activate the virtual environment on **Linux** or **macOS**, run:

```
venv/bin/activate
```

- If you need to re-create the environment later, remove the `venv` directory and repeat steps 1–3.

## Project files

- `app.py` — Streamlit application entry point
- `auth.py` — Authentication helpers
- `backend.py` — Backend utilities
- `users.json` — User database
---
Created for a Computational Thinking LAB Practice

Author: 24127356 - Huynh Bao Gia