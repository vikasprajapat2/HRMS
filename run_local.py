"""Run the Flask app without the reloader (useful for debugging runtime errors).

Usage (PowerShell):
    .\venv\Scripts\activate
    python run_local.py
"""
from app import app

if __name__ == '__main__':
    # Run without debug/reloader so we see tracebacks in this process
    app.run(debug=False, host='0.0.0.0', port=5000)
