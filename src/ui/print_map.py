# src/ui/print_map

from src.model.model import Color, Map

def print_map(network: Map) -> None:
    for drone in network.drones:
        if drone.current_connection is not None:
            print(
                f"D{drone.id}-{drone.current_connection}", end=" "
            )
        else:            
            print(
                f"{drone.current_zone.color.get_color()}"
                f"D{drone.id}-{drone.current_zone.name}"
                f"{Color.RESET.value}", end=" "
            )
    print()