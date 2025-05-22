from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel, Field, ConfigDict
import httpx
import uuid
from contextlib import asynccontextmanager

API_URL = "https://economia.awesomeapi.com.br/last/{pair}"

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.client = httpx.AsyncClient(timeout=10.0)
    try:
        yield
    finally:
        await app.state.client.aclose()

app = FastAPI(title="Currency Exchange API", lifespan=lifespan)

class ExchangeResponse(BaseModel):
    sell: float
    buy: float
    date: str
    id_account: str = Field(..., alias="id-account")
    model_config = ConfigDict(populate_by_name=True)

async def fetch_rate(src: str, dst: str) -> ExchangeResponse:
    pair = f"{src.upper()}-{dst.upper()}"
    url = API_URL.format(pair=pair)
    try:
        resp = await app.state.client.get(url)
        resp.raise_for_status()
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    data = resp.json()
    key = f"{src}{dst}".upper()
    if key not in data:
        raise HTTPException(status_code=404, detail="Currency pair not supported")
    info = data[key]
    return ExchangeResponse(
        sell=float(info["ask"]),
        buy=float(info["bid"]),
        date=info["create_date"],
        id_account=str(uuid.uuid4()),
    )

@app.get("/coin/{from}/{to}", response_model=ExchangeResponse, response_model_by_alias=True)
async def exchange(
    from_currency: str = Path(..., alias="from"),
    to_currency: str = Path(..., alias="to"),
):
    return await fetch_rate(from_currency, to_currency)