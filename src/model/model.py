# src/model/model.py

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
    """Enumeration defining the acceptable prefix classifiers for
    structural hubs.

    These tokens are used by text configuration parsers to distinguish
    structural roles within maps.
    """
    HUB = 'hub'
    START = 'start_hub'
    END = 'end_hub'


class ZoneType(Enum):
    """Enumeration identifying operational constraints and movement cost types
    for hubs.

    Determines graph-weight cost routing variables evaluated during automated
    agent pathfinding operations.
    """
    NORMAL = 'normal'
    BLOCKED = 'blocked'
    RESTRICTED = 'restricted'
    PRIORITY = 'priority'

    def get_cost(self) -> int:
        """Determines the discrete pathfinding numerical step penalty for
        the zone type.

        Returns:
            int: The movement cost weight value associated with this zone
            classification.
        """
        costs = {
            ZoneType.NORMAL: 1,
            ZoneType.RESTRICTED: 2,
            ZoneType.PRIORITY: 1,
            ZoneType.BLOCKED: maxsize,
        }
        return costs.get(self, 1)


class Color(Enum):
    """ANSI Escape sequence mapper matching graphical and text terminal
    viewports.

    Provides specific sequence maps for runtime log printouts or visual
    styling.
    """
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
    """Pydantic model representing a node endpoint or waypoint intersection.

    Holds spatial dimensions, validation configurations, dynamic tracking
    counters, and reference trackers mapped back to the origin text document.

    Fields:
        prefix (HubPrefix): The operational status layout designation.
        name (str): Identifier between 1 and 20 characters in length.
        x (int): Horizontal spatial configuration coordinate.
        y (int): Vertical spatial configuration coordinate.
        zone (ZoneType): Behavior model profile. Defaults to ZoneType.NORMAL.
        color (Color): UI display aesthetic tracking configuration. Defaults
            to Color.WHITE.
        max_drones (int): Concurrency agent capacity threshold.
            Must be >= 1. Defaults to 1.
        occupancy (int): Active tracking counter monitoring current agents.
            Defaults to 0.
        cost (int): Configured routing graph penalty weight. Defaults to 1.
        file_line (int, optional): Source configuration document line
            reference index.
    """
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
    """Pydantic model representing a bidirectional edge link between two hubs.

    Fields:
        name (str): Expected structural layout token formatted
            as '<zone1>-<zone2>'. Length must be between 1 and 50 characters.
        max_link_capacity (int): Concurrency payload limits for transit.
            Must be >= 1. Defaults to 1.
        occupancy (int): Dynamic simulation tracking registry counting
            current transits. Defaults to 0.
        file_line (int, optional): Source file line number for exception
            tracing context.
    """
    META_DATA_KEYS: ClassVar[set[str]] = {'max_link_capacity'}
    name: str = Field(min_length=1, max_length=50)
    max_link_capacity: int = Field(ge=1, default=1)
    occupancy: int = 0
    file_line: Optional[int]


class Drone(BaseModel):
    """Pydantic model defining operational attributes of an individual
    mobile agent.

        Fields:
            id (int): Positive unique key identifying the drone asset.
                Must be >= 1.
            current_zone (Hub): The current hub where the drone is located.
            next_zone (Hub): Target destination step along the active
                route sequence.
            preview_zone (Hub): Previous layout step intersection location
                marker.
            connection (str, optional): Target connection edge ID name if
                actively transiting. Defaults to None.
            path (list[str]): Sequential sequence of future hub names to be
                visited. Defaults to [].
            cost (int): Estimated movement turn calculation metrics.
                Defaults to 0.
            accum_cost (int): Historical record tracking total turns consumed.
                Defaults to 0.
            move (bool): Status flag tracking if routing space is reserved
                for a step. Defaults to False.
            travel_duration (int): Chronological turn count delay steps
                remaining to complete the current link navigation.
                Defaults to 1.
        """
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
    """Root model holding the entire layout environment state data collection.

    Orchestrates initial entity group allocations, cross-links lookups,
    and registers Pydantic lifecycle data-integrity assertion validators.

    Fields:
        nb_drones (int): Complete agent population quantity limit parameters
            (1 to 50).
        start_hub (str): Core node entry name marking origin coordinates.
        hubs (list[Hub]): Full dataset listing specifying active map node
            elements.
        end_hub (str): Target final destination layout node criteria string.
        connections (list[Connection]): Structural pathway layout array.
        drones (list[Drone]): Collection tracking processing active simulation
            agents.
        lookup_hubs (dict[str, Hub]): Optimization map linking keys to objects.
        lookup_hub_coords (dict[str, tuple[int, int]]): Map tracking localized
            node points.
        lookup_connections (dict[str, Connection]): Bidirectional edge
            cross-referencing maps.
    """
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
        """Enforces entity name uniqueness and bans illegal token formats.

        Raises:
            ValueError: If duplicate zone names exist or name strings contain
                the reserved hyphen '-' character.

        Returns:
            Self: The validated Map instance.
        """
        used_names: set[str] = set()
        for hub in self.hubs:
            if hub.name in used_names:
                raise ValueError(
                    f"Duplicated zone name: '{hub.name}' "
                    f"Error in line {hub.file_line}")
            if '-' in hub.name:
                raise ValueError(
                    f"zone name: '{hub.name}' can not contain symbol "
                    f"'-' Error in line {hub.file_line}"
                )
            used_names.add(hub.name)
        return self

    @model_validator(mode='after')
    def validate_coordinates(self) -> Self:
        """Validates that no two hubs share identical spatial coordinate
            configurations.

        Raises:
            ValueError: If multiple hubs share overlapping (x, y) coordinates.

        Returns:
            Self: The validated Map instance.
        """
        used_coordinates: set[tuple[int, int]] = set()
        for hub in self.hubs:
            coordinates = (hub.x, hub.y)
            if coordinates in used_coordinates:
                raise ValueError(
                    f"Duplicated coordinates in zone: '{hub.name}' "
                    f"Error in line {hub.file_line}"
                )
            used_coordinates.add(coordinates)
        return self

    @model_validator(mode='after')
    def validate_connection(self) -> Self:
        """Validates structural correctness and uniqueness of edge connection
        schemas.

        Ensures that connections are not duplicated in either direction
        and that the endpoint hubs exist.

        Raises:
            ValueError: If duplicates/inverse matches are found or if
                an endpoint references an undefined hub.

        Returns:
            Self: The validated Map instance.
        """
        used_connections: set[str] = set()
        valid_names: set[str] = {hub.name for hub in self.hubs}
        for connection in self.connections:
            if connection.name in used_connections:
                raise ValueError(
                    f"Duplicated connection: '{connection.name}' "
                    f"Error in line {connection.file_line}")
            zone1, zone2 = connection.name.split('-')
            rev_connection = f"{zone2}-{zone1}"
            if rev_connection in used_connections:
                raise ValueError(
                    f"Duplicated connection: '{connection.name}' "
                    f"Error in line {connection.file_line}")
            if zone1 not in valid_names or zone2 not in valid_names:
                raise ValueError(
                    f"Invalid connection, one or more "
                    f"invalid zones: '{connection.name}' "
                    f"Error in line {connection.file_line}")
            used_connections.add(connection.name)
        return self

    @model_validator(mode='after')
    def initialize_cost_zone(self) -> Self:
        """Sets internal route-weight properties across elements using
        ZoneType rules.

        Returns:
            Self: The updated Map instance.
        """
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
        """Orchestrates tracking setup steps to compile structural
        mapping lookups.

        Returns:
            Self: The Map instance with fully populated lookup dictionaries.
        """
        self.lookup_hubs = self._lookup_hubs()
        self.lookup_hub_coords = self._lookup_hub_coords()
        self.lookup_connections = self._lookup_connections()
        return self

    def _lookup_connections(self) -> dict[str, Connection]:
        """Generates a lookup map containing commutative bidirectional
        edge entries.

        Maps both forward ('A-B') and reverse ('B-A') configurations
        to the same underlying Connection reference to support simplified
        graph routing logic.

        Returns:
            dict[str, Connection]: Dictionary mapping connection string
                identifiers to their Connection objects.
        """
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
