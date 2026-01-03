from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import logging
import os
import joblib
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# ============================================
# load and read .env file from the root directory
# ============================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", ".env"))

load_dotenv(dotenv_path=ENV_PATH)

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
    raise EnvironmentError(
        "Database configuration is incomplete in environment variables."
    )

# ============================================
# Database engine setup
# ============================================
engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
    pool_pre_ping=True,
)

# ============================================
# Load machine learning models
# ============================================
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))

MODEL_PATHS = {
    "CatBoostRegressor": os.path.join(
        PROJECT_DIR, "notebook", "models", "catboost_model.joblib"
    ),
    "LinearRegression": os.path.join(
        PROJECT_DIR, "notebook", "models", "linear_regression_model.joblib"
    ),
    "RandomForestRegressor": os.path.join(
        PROJECT_DIR, "notebook", "models", "random_forest_model.joblib"
    ),
}

models = {}
for model_name, model in MODEL_PATHS.items():
    if os.path.exists(model):
        models[model_name] = joblib.load(model)
    else:
        logging.error(f"Model file not found: {model}")

# ============================================
# Logging configuration
# ============================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)
logger.info(f"Loaded ML models: {list(models.keys())}")

# ============================================
# FastAPI application setup
# ============================================
app = FastAPI(title="Pharmacy Sales Prediction API", version="1.0.0")


# ============================================
# Pydantic Schemas (Sales - Existing)
class SalesQueryRequest(BaseModel):
    year: int
    month: str
    product_name: str | None = None


class SalesInsertRequest(BaseModel):
    distributor: str
    product_name: str
    year: int
    month: str
    total_quantity: int
    total_sales: float


# Pydantic Schemas (Sales - Prediction)
class SalesPredictRequest(BaseModel):
    model_name: str  # catboost | LinearRegression | RandomForestRegressor

    total_sales: float
    total_quantity: int
    avg_price: float


# Global error handle
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error. Please try again later."},
    )


# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "ok"}


# Query sales data endpoint
@app.post("/sales/query")
async def query_sales(payload: SalesQueryRequest):
    try:
        query = (
            "SELECT * FROM features.sales_feature WHERE year = :year AND month = :month"
        )
        params = payload.model_dump(exclude_none=True)

        if payload.product_name:
            query += " AND product_name = :product_name"

        df = pd.read_sql(text(query), con=engine, params=params)
        return {"rows": len(df), "data": df.to_dict(orient="records")}
    except Exception as e:
        logger.error(f"Error query sales data: {e}")
        raise HTTPException(status_code=500, detail="Error querying sales data")


# Insert sales data endpoint
@app.post("/sales/insert")
def insert_sales(payload: SalesInsertRequest):
    try:
        query = """
            INSERT INTO features.sales_feature
            (distributor,
            product_name,
            year,
            month,
            total_quantity,
            total_sales)
            VALUES (
                :distributor,
                :product_name,
                :year,
                :month,
                :total_quantity,
                :total_sales
            )
            """
        with engine.begin() as conn:
            conn.execute(text(query), payload.model_dump())

        return {"message": "Sales data inserted successfully"}

    except Exception as e:
        logger.error(f"Error inserting sales data: {e}")
        raise HTTPException(status_code=500, detail="Error inserting sales data")


# Feature builder for predicting sales based on input payload (load single model and all models definitions)
@app.post("/features/build")
def build_feature_vector(payload: SalesPredictRequest):
    return np.array([[payload.total_sales, payload.total_quantity, payload.avg_price]])


# Predict sales using single model
@app.post("/sales/predict")
def predict_sales(payload: SalesPredictRequest):
    try:
        if payload.model_name not in models:
            raise HTTPException(
                status_code=400,
                detail="Invalid model name and not found in loaded models.",
            )
        feature_vector = build_feature_vector(payload=payload)
        model = models[payload.model_name]
        prediction = model.predict(feature_vector)
        return {"model": payload.model_name, "prediction": prediction.tolist()}

    except Exception as e:
        logger.error(f"Error predicting sales: {e}")
        raise HTTPException(
            status_code=500, detail="Error predicting sales trouble with loading models"
        )


# Predict sales using compare all models
@app.post("/sales/predict/compare")
def predict_compare_models(payload: SalesPredictRequest):
    try:
        feature_vector = build_feature_vector(payload=payload)
        predictions = {}
        for model_name, model in models.items():  # iterate for all loaded models
            prediction = model.predict(feature_vector)
            predictions[model_name] = prediction.tolist()
        return predictions
    except Exception as e:
        logger.error(f"Error predicting sales with all models: {e}")
        raise HTTPException(
            status_code=500, detail="Error predicting sales with all models"
        )


# Usage
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
