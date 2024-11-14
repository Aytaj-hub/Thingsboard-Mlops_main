from typing import List, Dict, Any, Set, Tuple, Optional
import httpx
from fastapi import FastAPI, HTTPException, Path, Query, Depends, Body
from snowflake_utils import *
# Correct the import below. Assuming you have a `functions` module.
# Replace 'functions' with the actual module name if different.
try:
    from myFastapi.funtions import convert_time, fetch_all_telemetry
except:
    from funtions import convert_time, fetch_all_telemetry

import os
from pydantic import BaseModel

token_global = ""

app = FastAPI()
login_url = os.getenv('LOGIN_URL', "https://dacs.site/api/auth/login")

class CustomLoginForm(BaseModel):
    username: str
    password: str

@app.post("/login")
async def login(form_data: CustomLoginForm = Depends()):
    global token_global  # Corrected variable name
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(login_url, json={
                "username": form_data.username,
                "password": form_data.password
            })
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=exc.response.status_code if exc.response else 500,
                detail=str(exc)
            ) from exc

        data = response.json()
        token = data.get("token")
        if not token:
            raise HTTPException(status_code=500, detail="Token not found in response")

        token_global = token  # Corrected variable name
        return {"token": token_global}

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


@app.get(
    "/elements/{entityType}/{entityId}",
    responses={
        400: {"description": "Invalid parameter supplied"},
        401: {"description": "Unauthorized. Please login."},
        404: {"description": "No element(s) found"},
    },
    tags=["Elements"],
    summary="Get all element_uid's between start and end date",
)
async def get_elements_route(
    entityType: str = Path(..., description="String value representing the entity type. For example, 'DEVICE'"),
    entityId: str = Path(..., description="A string value representing the entity id. For example, '784f394c-42b6-435a-983c-b7beff2784f9'"),
    start_date: str = Query(..., description="Start time/date in UTC format, e.g., '2023-04-23T17:25:43.511Z'", alias="start-date"),
    end_date: str = Query(..., description="End time/date in UTC format, e.g., '2023-04-23T17:25:43.511Z'", alias="end-date"),
    telemetry_keys: Optional[str] = Query(None, description="Comma-separated list of telemetry keys."),
    table_name: str = Query(..., description="The table name for the telemetry data")
    
):
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

    # Pass the telemetry data and table_name to the save_telemetry_to_snowflake function
    await save_telemetry_to_snowflake(table_name=table_name, telemetry=telemetry)

    return telemetry


@app.post(
    "/save-telemetry/{table_name}",
    responses={
        400: {"description": "Invalid data format"},
        401: {"description": "Unauthorized. Please login."},
        500: {"description": "Database error"},
    },
    tags=["Database"],
    summary="Save telemetry data to Snowflake database"
)
async def save_telemetry_to_snowflake(
    table_name: str = Path(..., description="The table name for the telemetry data"),
    telemetry: Dict[str, List[Dict[str, Any]]] = Body(..., description="Telemetry data to save")
):
    if not token_global:
        raise HTTPException(status_code=401, detail="User not authenticated. Please login.")
    
    try:
        # Run the blocking save_telemetry_data in a separate thread
        await asyncio.to_thread(save_telemetry_data, table_name, telemetry)
        return {"status": "success", "message": "Telemetry data saved successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")