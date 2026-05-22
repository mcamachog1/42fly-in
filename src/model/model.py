# model.py

from enum import Enum
from typing import ClassVar, Optional
from typing_extensions import Self

try:
    from pydantic import (
            BaseModel,
            Field,
            model_validator,
    )
except ImportError:
    print("Import Pydantic")
    exit(1)


class HubPrefix(Enum):
    HUB = 'hub'
    START = 'start_hub'
    END = 'end_hub'


class ZoneType(Enum):
    NORMAL = 'normal'
    BLOCKED = 'blocked'
    RESTRICTED = 'restricted'
    PRIORITY = 'priority'

    def get_cost(self) -> int:
        costs = {
            ZoneType.NORMAL: 1,
            ZoneType.RESTRICTED: 2,
            ZoneType.PRIORITY: 1,
            ZoneType.BLOCKED: float('inf'),       
        }
        return costs.get(self, 1)

class Color(Enum):
    RED = 'red'
    GREEN = 'green'
    BLUE = 'blue'
    YELLOW = 'yellow'
    BLACK = 'black'
    WHITE = 'white'
    GRAY = 'gray'
    ORANGE = 'orange'
    RESET = '\033[0m'    

    def get_color(self) -> str:
        cls = type(self)
        colors = {
            cls.RED: '\033[31m',
            cls.GREEN: '\033[32m',
            cls.BLUE: '\033[34m',
            cls.YELLOW: '\033[43m',
            cls.BLACK: '\033[40m',
            cls.WHITE: '\033[47m',
            cls.GRAY: '\033[100m',
            cls.ORANGE: '\033[38;5;208m',
            cls.RESET: '\033[0m'
            # BG colors begin with 4 or 10
            # TEXT colors begin with 3 or 9                      
        }
        return colors.get(self, '\033[0m')    


class Hub(BaseModel):
    META_DATA_KEYS: ClassVar[set[str]] = {'zone', 'color', 'max_drones'}
    prefix: HubPrefix
    name: str = Field(min_length=1, max_length=20)
    x: int
    y: int
    zone: ZoneType = Field(default=ZoneType.NORMAL)
    color: Color = Field(default=Color.WHITE)
    max_drones: int = Field(ge=1, default=1)
    occupancy: int = 0


class Connection(BaseModel):
    META_DATA_KEYS: ClassVar[set[str]] = {'max_link_capacity'}    
    name: str = Field(min_length=1, max_length=50)
    max_link_capacity: int = Field(ge=1, default=1)
    occupancy: int = 0


class Drone(BaseModel):
    id: int = Field(ge=1)
    current_zone: Hub
    next_zone: Hub
    preview_zone: Hub
    connection: None | Connection = None
    path: list[str] = []
    cost: int = 0
    move: bool = False


class Map(BaseModel):
    nb_drones: int = Field(ge=1, le=50)
    start_hub: Hub
    hubs: list[Hub]
    end_hub: Hub
    connections: list[Connection]
    drones: list[Drone] = []


    @model_validator(mode='after')
    def validate_hub_names(self) -> Self:
        used_names: set[str] = set()
        for hub in self.hubs:
            if hub.name in used_names:
                raise ValueError(f"Duplicated zone name: '{hub.name}'")
            if '-' in hub.name:
                raise ValueError(
                    f"zone name: '{hub.name}' can not contain symbol '-'"
                )
            used_names.add(hub.name)
        return self


    @model_validator(mode='after')
    def validate_coordinates(self) -> Self:
        used_coordinates: set[tuple[int, int]] = set()
        for hub in self.hubs:
            coordinates = (hub.x, hub.y)
            if coordinates in used_coordinates:
                raise ValueError(
                    f"Duplicated coordinates in zone: '{hub.name}'"
                )
            used_coordinates.add(coordinates)
        return self

    @model_validator(mode='after')
    def validate_connection(self) -> Self:
        used_connections: set[str] = set()
        valid_names: set[str] = {hub.name for hub in self.hubs}
        for connection in self.connections:
            if connection.name in used_connections:
                raise ValueError(f"Duplicated connection: '{connection.name}'")
            zone1, zone2 = connection.name.split('-')
            rev_connection = f"{zone2}-{zone1}"
            if rev_connection in used_connections:
                raise ValueError(f"Duplicated connection: '{connection.name}'")
            if zone1 not in valid_names or zone2 not in valid_names:
                raise ValueError(f"Invalid connection: '{connection.name}'")
            used_connections.add(connection.name)
        return self
    

