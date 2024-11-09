



app = FastAPI()
login_url = os.getenv('login_url')

class CustomLoginForm(BaseModel):
    username: str
    password: str

@router.post("/login")
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


@app.get(
    "Load the data from Thinksbaord",
    responses={
        400: {"description": "Invalid parameter supplied"},
        404: {"description": "No element(s) found"},
    },
    tags=["Elements"],
    summary="Get all element_uid's between start and end date",
    response_model_by_alias=True,
)
async def get_elements_route(
    oemISOidentifier: str = Path(..., description="OEM ISO identifier, as defined in ISO 15143-3"),
    start_date: str = Query(None, description="Start time/date in UTC format, e.g., '2023-04-23T17:25:43.511Z'", alias="start-date"),
    end_date: str = Query(None, description="End time/date in UTC format, e.g., '2023-04-23T17:25:43.511Z'", alias="end-date"),
    page_number: int = Query(1, description="Page number, starting from 1", alias="page-number"),
    token_bearer: dict = Security(get_token_bearer),
    )):
    
        return await get_elements_by_startdate_and_enddate_short_list(
            oemISOidentifier=oemISOidentifier, start_date=start_date, end_date=end_date, page_number=page_number, token_bearer=token_bearer
        )

