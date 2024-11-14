from typing import List, Dict, Any, Set, Tuple, Optional
import httpx
from fastapi import FastAPI, HTTPException, Path, Query, Depends, Body
from snowflake_utils import *
try:
    from myFastapi.funtions import convert_time, fetch_all_telemetry
except:
    from funtions import convert_time, fetch_all_telemetry

import os
from pydantic import BaseModel
from s3 import S3Client

try:
    from s3 import *
except:
    from s3 import *

token_global = ""
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

base_url = os.getenv('BASE_URL')




AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
S3_ENDPOINT_URL = os.getenv('S3_ENDPOINT_URL')



app = FastAPI()

if not base_url:
    raise ValueError("BASE_URL environment variable is not set")
login_url = f"{base_url}/api/auth/login"

class CustomLoginForm(BaseModel):
    username: str
    password: str

@app.post("/login")
async def login(form_data: CustomLoginForm = Depends()):
    global token_global
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(login_url, json={
                "username": form_data.username,
                "password": form_data.password
            })
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=exc.response.status_code if exc.response else 500,
                                detail=str(exc)) from exc
        data = response.json()
        token = data.get("token")
        if not token:
            raise HTTPException(status_code=500, detail="Token not found in response")
        token_global = token
        return {"token": token_global}
    



# Instantiate the MinIOClient
s3_client = S3Client(
    bucket_name='fastapi-snowflake',
    region='eu-central-1',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    endpoint_url=S3_ENDPOINT_URL  
)


@app.get("/get-elements")

async def get_elements_by_id(
    entityType: str = Query(..., description="String value representing the entity type. For example, 'DEVICE'"),
    entityId: str = Query(..., description="A string value representing the entity id. For example, '784f394c-42b6-435a-983c-b7beff2784f9'"),
    start_date: str = Query(..., description="Start time/date in UTC format, e.g., '2023-04-23T17:25:43.511Z'", alias="start-date"),
    end_date: str = Query(..., description="End time/date in UTC format, e.g., '2023-04-23T17:25:43.511Z'", alias="end-date"),
    telemetry_keys: Optional[str] = Query(None, description="Comma-separated list of telemetry keys."),
    table_name:  Optional[str] = Query(None, description="The table name for the telemetry data"),
    savebase: bool = Query(False, description="Whether to save data to S3")
):
    global token_global 
    if not token_global:
        raise HTTPException(status_code=401, detail="User not authenticated. Please login. There is no token_global.")

    # Convert start_date and end_date to milliseconds
    start_time_millis, end_time_millis = convert_time(start_date, end_date)

    # Convert telemetry_keys to a list
    telemetry_keys_list = telemetry_keys.split(",") if telemetry_keys else None

    async with httpx.AsyncClient() as client:
        telemetry = await fetch_all_telemetry(
            entityType=entityType,
            client=client,
            entityId=entityId,
            start_time_millis=start_time_millis,
            end_time_millis=end_time_millis,
            telemetry_keys=telemetry_keys_list,
            token=token_global
        )
        if savebase:
            success = s3_client.save_telemetry(telemetry, table_name)
            if not success:
                raise HTTPException(status_code=500, detail="Failed to save data to S3")


     
    return telemetry 





# @app.get(
#     "/elements/{entityType}/{entityId}",
#     responses={
#         400: {"description": "Invalid parameter supplied"},
#         401: {"description": "Unauthorized. Please login."},
#         404: {"description": "No element(s) found"},
#     },
#     tags=["Elements"],
#     summary="Get all element_uid's between start and end date",
# )

# async def get_elements_route(
#     entityType: str = Path(..., description="String value representing the entity type. For example, 'DEVICE'"),
#     entityId: str = Path(..., description="A string value representing the entity id. For example, '784f394c-42b6-435a-983c-b7beff2784f9'"),
#     start_date: str = Query(..., description="Start time/date in UTC format, e.g., '2023-04-23T17:25:43.511Z'", alias="start-date"),
#     end_date: str = Query(..., description="End time/date in UTC format, e.g., '2023-04-23T17:25:43.511Z'", alias="end-date"),
#     telemetry_keys: Optional[str] = Query(None, description="Comma-separated list of telemetry keys.")
# ):
#     global token_global 
#     if not token_global:
#         raise HTTPException(status_code=401, detail="User not authenticated. Please login. There is no token_global.")

#     # Convert start_date and end_date to milliseconds
#     start_time_millis, end_time_millis = convert_time(start_date, end_date)

#     # Convert telemetry_keys to a list
#     telemetry_keys_list = telemetry_keys.split(",") if telemetry_keys else None

#     async with httpx.AsyncClient() as client:
#         telemetry = await fetch_all_telemetry(
#             entityType=entityType,
#             client=client,
#             entityId=entityId,
#             start_time_millis=start_time_millis,
#             end_time_millis=end_time_millis,
#             telemetry_keys=telemetry_keys_list,
#             token=token_global
#         )
     
#     return telemetry 