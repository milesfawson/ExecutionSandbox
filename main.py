import subprocess
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

app = FastAPI()

class ExecutionRequest(BaseModel):
    code: str

import uuid

@app.post("/execute")
def execute_code(req: ExecutionRequest):
    # Generate a completely unique filename for this specific request
    temp_file = f"temp_exec_{uuid.uuid4().hex}.py"
    
    try:
        # Prevent catastrophic OS commands via simple heuristics
        forbidden = ["import os", "import subprocess", "import sys", "open("]
        if any(f in req.code for f in forbidden):
            raise HTTPException(status_code=400, detail="Forbidden function call in AI code.")

        # Write the AI-generated code to the unique file
        with open(temp_file, "w") as f:
            f.write(req.code)
        
        # Execute with a strict 5-second timeout
        result = subprocess.run(
            ["python", temp_file], 
            capture_output=True, 
            text=True, 
            timeout=5
        )
        
        return {
            "success": result.returncode == 0, 
            "stdout": result.stdout, 
            "stderr": result.stderr
        }
    except subprocess.TimeoutExpired:
        raise HTTPException(
            status_code=400, 
            detail="Timeout reached. Infinite loop likely."
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup: This block always runs at the very end, whether it succeeded or crashed
        if os.path.exists(temp_file):
            os.remove(temp_file)

@app.get("/health")
def health_check():
    return {"status": "healthy"}
