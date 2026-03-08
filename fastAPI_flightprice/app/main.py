from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from model_flight_price import get_price
from fastapi.templating import Jinja2Templates
import re
import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# fillin a flight number in a box 
@app.get("/", response_class=HTMLResponse)
def get_flight(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# get the filled flight number and get the price
@app.post("/check")
def flight_num_val(flight_num: str = Form(...)):
    # a alphabet and 3 digits
    if re.match(r"^[A-Za-z]\d{3}$", flight_num):
        return get_price(flight_num)
    else:
        return "Please input in right format"
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)