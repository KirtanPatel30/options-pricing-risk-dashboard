"""api/main.py — FastAPI REST API for options pricing."""
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Literal, Optional

app = FastAPI(title="Options Pricing & Risk API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])


class OptionRequest(BaseModel):
    S: float = Field(..., example=100.0)
    K: float = Field(..., example=100.0)
    T: float = Field(..., example=1.0)
    r: float = Field(..., example=0.05)
    sigma: float = Field(..., example=0.20)
    option_type: Literal["call","put"] = "call"
    q: float = 0.0


class MCRequest(OptionRequest):
    n_paths: int = Field(10000, ge=1000, le=100000)
    model: Literal["european","asian","barrier"] = "european"
    barrier: Optional[float] = None
    barrier_type: str = "down-and-out"


@app.get("/health")
def health():
    return {"status": "healthy", "models": ["black-scholes","monte-carlo"]}


@app.post("/price/bs")
def price_bs(req: OptionRequest):
    from pricing.black_scholes import BlackScholes, OptionParams
    bs = BlackScholes(OptionParams(**req.dict()))
    return {"model": "black-scholes", **bs.all_greeks()}


@app.post("/price/mc")
def price_mc(req: MCRequest):
    from pricing.monte_carlo import price_european, price_asian, price_barrier
    kw = dict(S=req.S, K=req.K, T=req.T, r=req.r, sigma=req.sigma,
              option_type=req.option_type, n_paths=req.n_paths)
    if   req.model == "european": result = price_european(**kw)
    elif req.model == "asian":    result = price_asian(**kw)
    else:
        result = price_barrier(**kw, barrier=req.barrier or req.S*0.9,
                               barrier_type=req.barrier_type)
    return {"model": f"monte-carlo-{req.model}", "price": result.price,
            "std_error": result.std_error,
            "confidence_95": [result.confidence_low, result.confidence_high]}


@app.post("/implied-vol")
def implied_vol(req: OptionRequest, market_price: float):
    from pricing.black_scholes import implied_volatility, OptionParams
    iv = implied_volatility(market_price, OptionParams(**req.dict()))
    if np.isnan(iv):
        raise HTTPException(400, "Could not compute implied volatility.")
    return {"implied_volatility": iv, "implied_vol_pct": round(iv*100, 4)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
