from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List,Optional,Dict
import os
import shutil
from crewai import llm
from utils import create_data_analysis_crew
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryInput(BaseModel):
    query: Optional[str] = None
    messages: Optional[List[Dict]] = None

@app.post("/upload_files")
async def upload_files(files: List[UploadFile] = File(...)):
    """Endpoint to upload multiple files to the knowledge folder."""
    upload_paths = []
    for file in files:
        file_path = os.path.join("knowledge", file.filename)
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            upload_paths.append(file_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error uploading {file.filename}: {str(e)}")
    return {"filenames": [file.filename for file in files], "paths": upload_paths}

@app.post("/analyze_data")
async def analyze_data(input_data: QueryInput):
    # Prefer messages if provided, else fallback to query
    if input_data.messages and len(input_data.messages) > 0:
        user_input = {"messages": input_data.messages}
    elif input_data.query:
        user_input = {"question": input_data.query}
    else:
        raise HTTPException(status_code=400, detail="No valid input provided.")

    # Dynamically determine the CSV file path from the knowledge folder
    csv_files = [f for f in os.listdir("knowledge") if f.endswith(".csv")]

    if not csv_files:
        raise HTTPException(status_code=404, detail="No CSV file found in the knowledge folder. Please upload one.")
    else:
        csv_file_path = os.path.join("", csv_files[0])

    try:
        crew = create_data_analysis_crew(csv_file_path, user_input=user_input)
        result = crew.kickoff(inputs=user_input)
        return {"result": result.raw}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CrewAI execution failed: {str(e)}")
    

@app.get("/")
def health_check():
    """Health check endpoint to verify the service is running."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8090)
