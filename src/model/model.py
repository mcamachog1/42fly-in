# model.py

from sys import maxsize
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
            ZoneType.BLOCKED: maxsize,
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
    CYAN = 'cyan'
    PURPLE = 'purple'
    BROWN = 'brown'
    GOLD = 'gold'
    MAROON = 'maroon'
    DARKRED = 'darkred'
    CRIMSON = 'crimson'
    LIME = 'lime'
    MAGENTA = 'magenta'
    RESET = '\033[0m'

    def get_color(self) -> str:
        cls = type(self)
        colors = {
            cls.RED: '\033[31m',
            cls.GREEN: '\033[32m',
            cls.BLUE: '\033[34m',
            cls.YELLOW: '\033[93m',
            cls.BLACK: '\033[30m',
            cls.WHITE: '\033[37m',
            cls.GRAY: '\033[90m',
            cls.ORANGE: '\033[38;5;208m',
            cls.CYAN: '\033[36m',
            cls.PURPLE: '\033[35m',
            cls.BROWN: '\033[38;5;94m',
            cls.GOLD: '\033[38;5;220m',
            cls.MAROON: '\033[31;1m',
            cls.DARKRED: '\033[38;5;124m',
            cls.CRIMSON: '\033[38;5;196m',
            cls.LIME: '\033[92m',
            cls.MAGENTA: '\033[38;5;201m',
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
    cost: int = 1
    file_line: Optional[int]


class Connection(BaseModel):
    META_DATA_KEYS: ClassVar[set[str]] = {'max_link_capacity'}
    name: str = Field(min_length=1, max_length=50)
    max_link_capacity: int = Field(ge=1, default=1)
    occupancy: int = 0
    file_line: Optional[int]    


class Drone(BaseModel):
    id: int = Field(ge=1)
    current_zone: Hub
    next_zone: Hub
    preview_zone: Hub
    connection: None | str = None
    path: list[str] = []
    cost: int = 0
    accum_cost: int = 0
    move: bool = False
    travel_duration: int = 1  # cost in turns for next movement


class Map(BaseModel):
    nb_drones: int = Field(ge=1, le=50)
    start_hub: str
    hubs: list[Hub]
    end_hub: str
    connections: list[Connection]
    drones: list[Drone] = []
    lookup_hubs: dict[str, Hub] = {}
    lookup_hub_coords: dict[str, tuple[int, int]] = {}
    lookup_connections: dict[str, Connection] = {}

    @model_validator(mode='after')
    def validate_hub_names(self) -> Self:
        used_names: set[str] = set()
        for hub in self.hubs:
            if hub.name in used_names:
                raise ValueError(f"Duplicated zone name: '{hub.name}' Error in line {hub.file_line}")
            if '-' in hub.name:
                raise ValueError(
                    f"zone name: '{hub.name}' can not contain symbol '-' Error in line {hub.file_line}"
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
                    f"Duplicated coordinates in zone: '{hub.name}' Error in line {hub.file_line}"
                )
            used_coordinates.add(coordinates)
        return self

    @model_validator(mode='after')
    def validate_connection(self) -> Self:
        used_connections: set[str] = set()
        valid_names: set[str] = {hub.name for hub in self.hubs}
        for connection in self.connections:
            if connection.name in used_connections:
                raise ValueError(f"Duplicated connection: '{connection.name}' Error in line {connection.file_line}")
            zone1, zone2 = connection.name.split('-')
            rev_connection = f"{zone2}-{zone1}"
            if rev_connection in used_connections:
                raise ValueError(f"Duplicated connection: '{connection.name}' Error in line {connection.file_line}")
            if zone1 not in valid_names or zone2 not in valid_names:
                raise ValueError(f"Invalid connection, one or more invalid zones: '{connection.name}' Error in line {connection.file_line}")
            used_connections.add(connection.name)
        return self

    @model_validator(mode='after')
    def initialize_cost_zone(self) -> Self:
        for zone in self.hubs:
            if zone.zone == ZoneType.NORMAL:
                zone.cost = 1
            if zone.zone == ZoneType.PRIORITY:
                zone.cost = 1
            elif zone.zone == ZoneType.RESTRICTED:
                zone.cost = 2
            elif zone.zone == ZoneType.BLOCKED:
                zone.cost = maxsize
        return self

    @model_validator(mode='after')
    def initialize_lookups(self) -> Self:
        self.lookup_hubs = self._lookup_hubs()
        self.lookup_hub_coords = self._lookup_hub_coords()
        self.lookup_connections = self._lookup_connections()
        return self

    def _lookup_connections(self) -> dict[str, Connection]:
        conn_objects: dict[str, Connection] = {
            c.name: c for c in self.connections
        }
        # Make conmmutative names
        swap_names: dict[str, Connection] = {}
        for name, obj in conn_objects.items():
            z1, z2 = name.split('-')
            swap_names[f"{z2}-{z1}"] = obj
        conn_total = conn_objects | swap_names
        return conn_total

    def _lookup_hubs(self) -> dict[str, Hub]:
        """Creates an easy-lookup dictionary linking hub names to Hub objects.

        Returns:
            dict[str, Hub]: Dictionary where keys are hub names (strings) and
            values are Hub object references.
        """
        hubs: dict[str, Hub] = {h.name: h for h in self.hubs}
        return hubs

    def _lookup_hub_coords(self) -> dict[str, tuple[int, int]]:
        """Extracts the abstract model coordinates for all existing hubs.

        Returns:
            dict[str, tuple[float, float]]: Dictionary mapping hub names to
            their raw (x, y) positions.
        """
        coords = {}
        for hub in self.hubs:
            coords[hub.name] = (hub.x, hub.y)
        return coords
