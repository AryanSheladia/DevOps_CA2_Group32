import sys
import os
from pathlib import Path
from functools import lru_cache

from dotenv import load_dotenv
load_dotenv()
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile, Request, HTTPException
from uvicorn import run as app_run
from fastapi.responses import Response, HTMLResponse
from starlette.responses import RedirectResponse
import pandas as pd

from networksecurity.utils.main_utils.utils import load_object

from networksecurity.utils.ml_utils.model.estimator import NetworkModel


app = FastAPI()
PROJECT_DIR = Path(__file__).resolve().parent
origins = ["*"]


@lru_cache(maxsize=1)
def get_prediction_model():
    preprocessor = load_object(PROJECT_DIR / "final_model/preprocessor.pkl")
    model = load_object(PROJECT_DIR / "final_model/model.pkl")
    return NetworkModel(preprocessor=preprocessor, model=model)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["authentication"])
async def index():
    return RedirectResponse(url="/docs")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready():
    try:
        get_prediction_model()
        return {"status": "ready"}
    except Exception:
        logging.exception("Prediction model could not be loaded")
        raise HTTPException(status_code=503, detail="Prediction model is not ready")


@app.get("/version")
def version():
    return {"commit": os.getenv("RENDER_GIT_COMMIT") or os.getenv("APP_VERSION", "local")}

@app.get("/train")
async def train_route():
    if os.getenv("ENABLE_TRAINING", "false").lower() != "true":
        raise HTTPException(status_code=403, detail="Training is disabled for the prediction demo.")
    try:
        from networksecurity.pipeline.training_pipeline import TrainingPipeline

        train_pipeline=TrainingPipeline()
        train_pipeline.run_pipeline()
        return Response("Training is successful")
    except Exception as e:
        raise NetworkSecurityException(e,sys)
    
@app.post("/predict")
async def predict_route(request: Request,file: UploadFile = File(...)):
    try:
        df=pd.read_csv(file.file)
        #print(df)
        network_model = get_prediction_model()
        y_pred = network_model.predict(df)
        df['predicted_column'] = y_pred
        #df['predicted_column'].replace(-1, 0)
        #return df.to_json()
        output_dir = PROJECT_DIR / "prediction_output"
        output_dir.mkdir(exist_ok=True)
        df.to_csv(output_dir / 'output.csv')
        table_html = df.to_html(classes='table table-striped')
        return HTMLResponse(content=table_html, status_code=200)
        
    except Exception as e:
            raise NetworkSecurityException(e,sys)

    
if __name__=="__main__":
    app_run(app,host="0.0.0.0",port=int(os.getenv("PORT", "8000")))
