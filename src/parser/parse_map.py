# src/parser/parse_map.py

import re
import sys
from typing import Any
from src.model.model import Hub, Connection, Color, Map
from pydantic import ValidationError


class MapParsingError(Exception):
    """Custom exception raised for syntax or constraint violations during
    map parsing."""
    pass


class MapParser():
    """Parses structural layout configuration files into fully
    validated Map domains.

    Handles continuous stream reading, syntactic isolation, attribute checking,
    regex-based metadata parsing, and instance loading of unified
    Pydantic maps.

    Attributes:
        filename (str): Path targeting the map specification source file.
        raw_data (list[tuple[str, str, int]]): Isolated string fragments
            extracted from the file containing keys, raw text parameters,
            and line numbers.
        valid_colors (set[str]): Collection of text string color
            literals supported by the system.
    """
    def __init__(self, filename: str) -> None:
        """Initializes the MapParser and automatically reads the target
        raw map data."""
        self.filename = filename
        self.raw_data: list[tuple[str, str, int]] = self._read_map()
        self.valid_colors = {c.value for c in Color}

    def _get_numbers_of_drones(self) -> int:
        """Extracts and validates the initial 'nb_drones' parameter
        from memory.

        Raises:
            MapParsingError: If 'nb_drones' is absent from the primary dataset
                space, contains non-integer characters, or evaluates to
                less than or equal to 0.

        Returns:
            int: Total headcount volume parameters of operational simulation
                agents.
        """
        key, value, line_n = self.raw_data[0]
        if key == 'nb_drones':
            try:
                nb_drones: int = int(value)
            except ValueError as e:
                raise MapParsingError(
                    f"Error in line: {line_n} Invalid nb_drones "
                    f"value: {value}") from e
            if nb_drones <= 0:
                raise MapParsingError(
                    f"Error in line: {line_n} nb_drones must "
                    f"be greater than 0")
            return nb_drones
        else:
            raise MapParsingError(
                "There is not value for 'nb_drones' "
                "in the first line"
            )

    def _get_metadata(
            self,
            string: str,
            prefix: str,
            line_n: int
    ) -> dict[str, str]:
        """Decodes localized configuration metadata string brackets
        via regex matching.

        Processes option entries declared inside brackets like
        `[zone=priority color=red]`.

        Args:
            string (str): Raw target metadata parameter string.
            prefix (str): Structural type identifier ('hub' or 'connection')
                used to validate options.
            line_n (int): Source reference line tracking index used for error
                context.

        Raises:
            MapParsingError: If the syntax format violates standard rules,
                an illegal key option parameter is passed, or color literal
                parameters are corrupt.

        Returns:
            dict[str, str]: Dictionary mapping isolated key variables to
            property values.
        """
        result: dict[str, str] = {}
        if string == "":
            return result
        pattern = r"\[([a-z_0-9]+=[a-z_0-9]+\s*)*\]"
        if not re.search(pattern, string):
            raise MapParsingError(
                f"Error in line {line_n} Invalid format "
                f"for metadata '{string}'")
        optionals: list[str] = string.strip("[]").split()
        pattern_color = r"^[a-z]{3,8}$"
        for values in optionals:
            key, value = values.split("=")
            if prefix.lower() == 'hub' and key not in Hub.META_DATA_KEYS:
                raise MapParsingError(
                    f"Error in line {line_n} Invalid key "
                    f"'{key}' for hub metadata '{string}'"
                )
            if (
                prefix.lower() == 'connection' and
                key not in Connection.META_DATA_KEYS
            ):
                raise MapParsingError(
                    f"Error in line {line_n} Invalid key "
                    f"'{key}' for connection metadata '{string}'"
                )
            if key == 'color' and value not in self.valid_colors:
                if not re.search(pattern_color, value):
                    raise MapParsingError(
                        f"Error in line {line_n} Invalid color "
                        f"for metadata '{string}'")
                value = 'white'
            result[key] = value
        return result

    def _get_zones(
        self,
        zones: list[tuple[str, str, int]]
    ) -> list[dict[str, Any]]:
        """Validates layout rules and processes property models for hub
        map items.

        Enforces uniqueness boundaries limiting the network layout to exactly
        one start hub and one end hub node.

        Args:
            zones (list[tuple[str, str, int]]): Isolated raw hub data lines.

        Raises:
            MapParsingError: If multiple start or end hubs are detected,
                argument counts are mismatching, or coordinates are
                non-numeric.

        Returns:
            list[dict[str, Any]]: Raw dictionary collection containing hub
                records ready for class instantiation.
        """
        # Validate unique start_hub
        start_hubs: list[str] = [
            str(line)
            for key, value, line in zones if key == 'start_hub']
        if len(start_hubs) > 1:
            raise MapParsingError(
                f"Error in lines {', '.join(start_hubs)} "
                "There must be exactly one start_hub: zone")
        # Validate unique end_hub
        end_hubs: list[str] = [
            str(line)
            for key, value, line in zones if key == 'end_hub']
        if len(end_hubs) > 1:
            raise MapParsingError(
                f"Error in lines {', '.join(end_hubs)} "
                "There must be exactly one end_hub: zone")

        results: list[dict[str, Any]] = []
        for hub, values, line_n in zones:

            metadata: str = ""
            attributes = values.split(maxsplit=3)
            if len(attributes) > 4:
                raise MapParsingError(
                        f"Error in line {line_n} To many arguments "
                        f"for zone: '{hub}': "
                        f"'{attributes}'"
                )
            if len(attributes) < 3:
                raise MapParsingError(
                    f"Error in line {line_n} "
                    "To few arguments for zone: '{hub}': "
                    f"'{attributes}'"
                )
            if len(attributes) == 3:
                name, coord_x, coord_y = attributes
            if len(attributes) == 4:
                name, coord_x, coord_y, metadata = attributes
            try:
                x = int(coord_x)
                y = int(coord_y)
            except ValueError:
                raise MapParsingError(
                    f"Error in line {line_n} "
                    "Invalid values or format in zone: "
                    f"{hub}, name: {name}, x: {coord_x}, y: {coord_y}, "
                    f"metadata: {metadata}"
                )
            parsed_metadata: dict[str, str] = self._get_metadata(
                metadata, 'hub', line_n)
            results.append({
                'prefix': hub,
                'name': name,
                'x': x,
                'y': y,
                'zone': parsed_metadata.get('zone', 'normal'),
                'color': parsed_metadata.get('color', 'white'),
                'max_drones': parsed_metadata.get('max_drones', 1),
                'file_line': line_n
            })
        return results

    def _get_connections(
            self,
            connections: list[tuple[str, str, int]]) -> list[dict[str, Any]]:
        """Processes and validates layout schema structures for route edge
        links.

        Ensures connection names correctly fit the mandatory '<zone1>-<zone2>'
        format.

        Args:
            connections (list[tuple[str, str, int]]): Isolated raw link
                connection data lines.

        Raises:
            MapParsingError: If attribute parameter quantities are incorrect
            or the naming style misses the single dash delimiter pattern
            layout.

        Returns:
            list[dict[str, Any]]: Raw dictionary mappings outlining connection
                variables.
        """
        results: list[dict[str, Any]] = []
        for connection, values, line_n in connections:
            metadata: str = ""
            attributes = values.split(maxsplit=1)
            if len(attributes) > 2:
                raise MapParsingError(
                    f"Error in line {line_n} "
                    "To many arguments for connection: "
                    f"{connection}: {attributes}"
                )
            if len(attributes) < 1:
                raise MapParsingError(
                    f"Error in line {line_n} To few arguments for connection: "
                    f"{connection}: {attributes}"
                )
            if len(attributes) == 1:
                name = attributes[0]
            if len(attributes) == 2:
                name, metadata = attributes
            # Validate <zone1>-<zone2> format
            if (
                name.count('-') != 1 or
                name.startswith('-') or
                name.endswith('-')
            ):
                raise MapParsingError(
                    f"Error in line {line_n} "
                    f"Invalid name for connection: '{name}' "
                    "expected: <zone1>-<zone2>"
                )
            parsed_metadata: dict[str, str] = self._get_metadata(
                metadata, 'connection', line_n
            )
            results.append({
                'prefix': connection,
                'name': name,
                'max_link_capacity': parsed_metadata.get(
                    'max_link_capacity', 1),
                'file_line': line_n
            })
        return results

    def _parse(self) -> dict[str, Any]:
        """Orchestrates internal sub-parsing operations to aggregate
        components.

        Segregates components using line header keys into isolated category
        maps.

        Raises:
            SystemExit: If an internal parsing routing error is captured.

        Returns:
            dict[str, Any]: Aggregated raw components describing the system
            state.
        """

        data: dict[str, Any] = {}

        try:
            # nb_drones
            data['nb_drones'] = self._get_numbers_of_drones()

            # zones
            zones = [
                line for line in self.raw_data
                if line[0] in ('hub', 'start_hub', 'end_hub')
            ]
            data['zones'] = self._get_zones(zones)

            # connections
            connections = [
                line for line in self.raw_data
                if line[0] == 'connection'
            ]
            data['connections'] = self._get_connections(connections)

            return data

        except MapParsingError as e:
            print(f"PARSING ERROR {e}")
            exit(1)

    def _read_map(self) -> list[tuple[str, str, int]]:
        """Reads the file line-by-line, stripping comments and isolating map
        tokens.

        Raises:
            SystemExit: If file access is denied, the path does not exist,
                syntax is invalid, or mandatory layout block keys are missing.

        Returns:
            list[tuple[str, str, int]]: Collection of sanitized configuration
            data.
        """
        valid_keys: list[str] = [
            'nb_drones',
            'start_hub',
            'hub',
            'end_hub',
            'connection',
            ]
        # Each line is a tuple (key, value(s), line_number)
        file_lines: list[tuple[str, str, int]] = []
        try:
            with open(self.filename) as file:
                for line_num, line in enumerate(file, 1):
                    line = line.strip().lower()
                    if not line or line.startswith("#"):
                        continue
                    key, value = line.split(":")
                    if key not in valid_keys:
                        raise ValueError(f"Invalid key '{key}'.")
                    file_lines.append((key, value, line_num))
                for key in valid_keys:
                    if key not in {line[0] for line in file_lines}:
                        raise ValueError(f"'{key}' is missing")
        except FileNotFoundError:
            print(
                f"READING FILE ERROR: Archive not found "
                f"{self.filename}", file=sys.stderr)
            sys.exit()
        except PermissionError:
            print(
                f"READING FILE ERROR: Archive deny access "
                f"{self.filename}", file=sys.stderr)
            sys.exit()
        except ValueError as error:
            print(
                f"READING FILE ERROR: {error} in '{self.filename}' "
                f"Error in line {line_num} ",
                file=sys.stderr
            )
            sys.exit()
        except Exception as error:
            print(
                f"READING FILE ERROR:  Unexpected error: {error} "
                f"Error in line {line_num} "
                f"- Type: {type(error).__name__}", file=sys.stderr)
            sys.exit()
        return file_lines

    def load_map(self) -> Map:
        """Assembles data components into a fully validated Map object model.

        Injects capacity rules (infinite limits for endpoints) and formats
        initial inputs before performing the final Pydantic verification step.

        Raises:
            SystemExit: If model validation checks flag constraint failures.

        Returns:
            Map: A fully instantiated and validated ecosystem network Map
            object.
        """
        data = self._parse()
        # Format input for zone objects
        zones: list[dict[str, Any]] = data['zones']
        hubs: list[Hub] = []
        for zone in zones:
            if zone['prefix'] == 'start_hub':
                zone['max_drones'] = sys.maxsize
                zone['occupancy'] = data['nb_drones']
                start_hub: str = zone['name']
            if zone['prefix'] == 'end_hub':
                zone['max_drones'] = sys.maxsize
                end_hub: str = zone['name']
            try:
                hubs.append(Hub(**zone))
            except ValidationError as e:
                for error in e.errors():
                    print(
                        "CONSTRAINT ERROR: "
                        f"{error['msg'].removeprefix('Value error, ')}"
                    )
                exit(1)                

        # Format input for connections objects
        connections: list[dict[str, Any]] = data['connections']
        connection_objects: list[Connection] = []
        for connection in connections:
            try:
                connection_objects.append(Connection(**connection))
            except ValidationError as e:
                for error in e.errors():
                    print(
                        "CONSTRAINT ERROR: "
                        f"{error['msg'].removeprefix('Value error, ')}"
                    )
                exit(1)                

        # Format input for map object
        map_input: dict[str, Any] = {}
        map_input['nb_drones'] = data['nb_drones']
        map_input['start_hub'] = start_hub
        map_input['end_hub'] = end_hub
        map_input['hubs'] = hubs
        map_input['connections'] = connection_objects
        try:
            fly_map = Map(**map_input)
        except ValidationError as e:
            for error in e.errors():
                print(
                    "CONSTRAINT ERROR: "
                    f"{error['msg'].removeprefix('Value error, ')}"
                )
            exit(1)

        return fly_map
