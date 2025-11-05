# ai_agents/tools.py
from langchain.agents import Tool
from langchain.tools import StructuredTool 
from langchain_community.tools import DuckDuckGoSearchRun
from pydantic import BaseModel, Field
from api.models import Users
from ships.models import Ship

# --- DuckDuckGo Search (no API key required) ---
duckduckgo = DuckDuckGoSearchRun()

search_tool = Tool(
    name="WebSearch",
    func=duckduckgo.run,
    description="Search the web for validating vessel details, IMO numbers, or shipping routes"
)

# --- Pydantic Schemas for Structured Tools ---

class AddShipInput(BaseModel):
    ship_name: str = Field(..., description="Name of the ship")
    imo_number: str = Field(..., description="IMO number of the ship")
    company_id: int = Field(..., description="Company ID that owns the ship")
    flag_id: int | None = Field(None, description="Flag ID of the ship")
    vessel_type_id: int | None = Field(None, description="Vessel type ID of the ship")

def add_ship(ship_name: str, imo_number: str, company_id: int, flag_id=None, vessel_type_id=None):
    """Create a new ship record."""
    ship, created = Ship.objects.get_or_create(
        imo_number=imo_number,
        defaults={
            "ship_name": ship_name,
            "company_id": company_id,
            "flag_id": flag_id,
            "ship_type_id": vessel_type_id,
        },
    )
    return {"ship_id": ship.id, "action": "created" if created else "exists"}

add_ship_tool = StructuredTool.from_function(
    func=add_ship,
    args_schema=AddShipInput,
    description="Create a new ship in the database. Requires ship_name, imo_number, and company_id."
)

# --- Assign User to Ship ---

class AssignUserInput(BaseModel):
    user_email: str = Field(..., description="Email of the user")
    imo_number: str = Field(..., description="IMO number of the ship")

def assign_user_to_ship(user_email: str, imo_number: str):
    """Assign a crew member (user) to a ship by IMO number."""
    user = Users.objects.get(email=user_email)
    ship = Ship.objects.get(imo_number=imo_number)
    ship.crew.add(user)
    return {"ship_id": ship.id, "user_id": user.id, "action": "assigned"}

assign_user_tool = StructuredTool.from_function(
    func=assign_user_to_ship,
    args_schema=AssignUserInput,
    description="Assign a user to a ship’s crew using the ship's IMO number."
)

# --- Update Ship Status ---

class UpdateStatusInput(BaseModel):
    imo_number: str = Field(..., description="IMO number of the ship")
    status: str = Field(..., description="New status: Active, Under Maintenance, Inactive")

def update_ship_status(imo_number: str, status: str):
    """Update a ship's operational status."""
    ship = Ship.objects.get(imo_number=imo_number)
    ship.status = status
    ship.save()
    return {"ship_id": ship.id, "action": "status_updated", "status": status}

update_status_tool = StructuredTool.from_function(
    func=update_ship_status,
    args_schema=UpdateStatusInput,
    description="Update the operational status of a ship."
)

# --- Tools list ---
tools = [
    search_tool,
    add_ship_tool,
    assign_user_tool,
    update_status_tool,
]
