import sys
try:
    from pydantic import BaseModel, Field, ValidationError
except Exception as e:
    print("Pydantic Module not Found!")
    sys.exit()

class Hub(BaseModel):
    name: str = Field(ge=1, le=10)

class Map(BaseModel):
    nb_drones: int = Field(ge=1, le=10)
    # start_hub: Hub
    # hubs: list[Hub]
    # end_hub: Hub
    # connections: list[connections] 


class Connection(BaseModel):
    name: str = Field(ge=1, le=10)
