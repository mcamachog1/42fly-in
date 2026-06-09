# src/ui/print_map

from src.model.model import Color, Map


class TerminalInterface():
    def __init__(self, network: Map):
        self.network = network

    def print_turn(self, turn: int) -> None:
        print(f"TURN: {turn}    |   ", end="")
        for drone in self.network.drones:
            if drone.connection is not None:
                print(
                    f"{Color.WHITE.get_color()}"
                    f"D{drone.id}-{drone.connection}"
                    f"{Color.RESET.get_color()}", end=" "
                )
            else:
                print(
                    f"{drone.current_zone.color.get_color()}"
                    f"D{drone.id}-{drone.current_zone.name}"
                    f"{Color.RESET.get_color()}", end=" "
                )
        print()
