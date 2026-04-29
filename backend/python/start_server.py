import uvicorn
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

os.chdir(script_dir)

print(f"Working directory: {os.getcwd()}")
print(f"Python version: {sys.version}")
print("Starting backend server...")

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=False
    )
