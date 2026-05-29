# src/ui/print_map

from src.model.model import Color, Map

def print_map(network: Map, turn: int) -> None:
    print(f"TURNO: {turn} | ", end="")
    for drone in network.drones:
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