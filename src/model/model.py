
from enum import Enum
from typing import Optional
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


class Hub(BaseModel):
    prefix: HubPrefix
    name: str = Field(min_length=1, max_length=20)
    x: int
    y: int
    metadata: Optional[dict[str, str]] = Field(default=None)


class Connection(BaseModel):
    name: str = Field(min_length=1, max_length=20)
    metadata: Optional[dict[str, str]] = Field(default=None)


class Map(BaseModel):
    nb_drones: int = Field(ge=1, le=50)
    start_hub: Hub
    hubs: list[Hub]
    end_hub: Hub
    connections: list[Connection]

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
