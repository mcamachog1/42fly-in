# src/ui/print_map

from src.model.model import Color, Map


class TerminalInterface():
    """Manages the console text user interface for rendering simulation logs.

    Handles real-time status updates per turn, printing color-coded tracking
    identifiers for active drones based on their positioning in the map
    framework.

    Attributes:
        network (Map): Root object instance holding the active simulation map.
    """

    def __init__(self, network: Map):
        """Initializes the TerminalInterface with a target simulation
        network."""
        self.network = network

    def print_turn(self, turn: int) -> None:
        """Prints a colorized inline telemetry log detailing the state of all
        agents.

        Displays a sequential summary for the given turn step. If a drone is
        actively navigating an edge connection, it prints with a standard white
        style tracking tag containing the link identifier name. If docked at a
        node hub, it prints using the respective hub's custom color
        configuration.

        Args:
            turn (int): The current chronological clock tick number index.
        """
        print(f"TURN: {turn}    |   ", end="")
        for drone in self.network.drones:
            if drone.connection is not None:
                print(
                    f"{Color.WHITE.get_color()}"
                    f"D{drone.id}-{drone.current_zone.name=}{drone.preview_zone.name=}{drone.next_zone.name=}"
                    f"{Color.RESET.get_color()}", end=" "
                )
            else:
                print(
                    f"{drone.current_zone.color.get_color()}"
                    f"D{drone.id}-{drone.current_zone.name=}{drone.preview_zone.name=}{drone.next_zone.name=}"
                    f"{Color.RESET.get_color()}", end=" "
                )
        print()
