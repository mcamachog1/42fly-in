
import sys
from typing import Optional

try:
    from pydantic import BaseModel, Field, ValidationError
except Exception as e:
    print("Pydantic Module not Found!")
    sys.exit()

class Hub(BaseModel):
    name: str = Field(min_length=1, max_length=10)
    coord_x: int
    coord_y: int
    optionals: Optional[str] = Field(default=None) 

class Map(BaseModel):
    nb_drones: int = Field(ge=1, le=10)
    # start_hub: Hub
    # hubs: list[Hub]
    # end_hub: Hub
    # connections: list[connections] 


class Connection(BaseModel):
    name: str = Field(min_length=1, max_length=10)
