from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supabase import create_client, Client
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Supabase configuration
supabase_url = os.getenv("https://zeolkmdajtsxzbgcsobi.supabase.co")
supabase_key = os.getenv("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inplb2xrbWRhanRzeHpiZ2Nzb2JpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTY2NTI3ODUsImV4cCI6MjAzMjIyODc4NX0.WNyYHL3Yf5pYM0iSQPgQcgpDZvO6vQE-qs6xmJIIqU8")
supabase: Client = create_client(supabase_url, supabase_key)

# OpenAI API key configuration
openai.api_key = os.getenv("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")


# Character model
class Character(BaseModel):
    name: str
    details: str


# Endpoint to create a character
@app.post("/api/create_character", response_model=Character, status_code=201)
async def create_character(character: Character):
    response = supabase.table('characters').insert({
        "name": character.name,
        "details": character.details
    }).execute()

    if response.get("status_code") != 201:
        raise HTTPException(status_code=500, detail="Failed to create character")

    return character


# Endpoint to generate a story
@app.post("/api/generate_story", status_code=201)
async def generate_story(character_name: str):
    response = supabase.table('characters').select("*").eq("name", character_name).execute()

    if not response.get("data"):
        raise HTTPException(status_code=404, detail="Character not found")

    character = response.get("data")[0]
    story_prompt = f"{character['name']}, a {character['details']}, lived a quiet life. However, something unexpected happened..."

    openai_response = openai.Completion.create(
        engine="davinci",
        prompt=story_prompt,
        max_tokens=150
    )

    story = openai_response.choices[0].text.strip()

    return {"story": story}
