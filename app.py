from dotenv import load_dotenv
load_dotenv(override=True)

import google.generativeai as genai
from openai import OpenAI
import json,os

from fastapi import FastAPI, Query, HTTPException, Depends, Body
from fastapi.responses import RedirectResponse, JSONResponse, PlainTextResponse

app = FastAPI()

class LLM:
    
    @classmethod
    def gemini(cls, prompt, usePro=False, isJson=True):
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        safety = [{"category": c, "threshold": "BLOCK_NONE"} for c in ["HARM_CATEGORY_HARASSMENT", "HARM_CATEGORY_HATE_SPEECH", "HARM_CATEGORY_SEXUALLY_EXPLICIT", "HARM_CATEGORY_DANGEROUS_CONTENT"]]
        model = 'gemini-1.5-pro' if usePro else 'gemini-1.5-flash'
        results = genai.GenerativeModel(model, safety_settings=safety).generate_content(prompt).text
        results = results.replace('```json','').replace('```','')
        
        return json.loads(results) if isJson else results
    
    @classmethod
    def openai(cls, prompt, usePro=False, isJson=True):
        model = 'gpt-4o' if usePro else 'gpt-4o-mini'
        t = OpenAI().chat.completions.create(model=model, messages=[{"role": "user", "content": prompt}]).choices[0].message.content
        results = t.replace('```json','').replace('```','')
        
        return json.loads(results) if isJson else results
    
from fastapi.security import APIKeyHeader
header_scheme = APIKeyHeader(name="x-api-key")
def isAuthorized(apiKey: str = Depends(header_scheme)) -> str:
    if os.getenv('API_KEY') and apiKey != os.getenv('API_KEY'):
        raise HTTPException(status_code=403, detail="Unauthorized")
    return apiKey
    
# @app.get("/", response_class=RedirectResponse, include_in_schema=False)
# async def index():
#     return "/docs"

@app.post("/ask", dependencies=[Depends(isAuthorized)])
async def ask(
    prompt: str = Body("How many planets are in the Solar System?", media_type="text/plain"),
    usePro: bool = False,
    isJson: bool = True,
    llm: str = Query('gemini', enum=['gemini', 'openai'])
):
    r = getattr(LLM, llm)(prompt, usePro, isJson)
    return PlainTextResponse(r) if not isJson else JSONResponse(r)