from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from database import get_db
from models import Agent
import anthropic

router = APIRouter(prefix="/api", tags=["gherkin"])

class GherkinRequest(BaseModel):
    agentId: str
    scenario: str

@router.post("/generate-gherkin")
async def generate_gherkin(request: GherkinRequest, db = get_db()):
    try:
        # Fetch agent from database
        agent = db.execute(select(Agent).where(Agent.id == request.agentId)).scalar_one_or_none()
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")

        # Initialize LLM client with agent's API key
        client = anthropic.Anthropic(api_key=agent.api_key)

        # Generate Gherkin using LLM
        prompt = f"""Convert the following manual scenario description into Cucumber Gherkin format.
Include: Feature, Scenario, Given, When, Then steps.

Scenario: {request.scenario}

Generate valid Gherkin syntax:"""

        message = client.messages.create(
            model=agent.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )

        gherkin_output = message.content[0].text

        return {"gherkin": gherkin_output}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
