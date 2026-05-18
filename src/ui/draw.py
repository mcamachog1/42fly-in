from turtle import Turtle
from random import random
from math import sqrt, atan2

from src.model.model import Map, Connection, Hub, Drone

RADIO: int = 20
SCALE: int = 100

def draw_map(network: Map) -> None:
    hubs: list[Hub] = network.hubs
    connections: list[Connection] = network.connections
    t = Turtle()
    t.radians()
    t.screen.title(f"Simulation with {network.nb_drones} drones")
    t.screen.bgcolor("white")    
    hub_center: dict[str, tuple[int, int]] = {}

    def draw_hubs() -> None:
        # t.screen.setup(width=0.5, height=0.5, startx=None, starty=None)
        t.color('black')
        for hub in hubs:
            t.up()
            t.setpos(hub.x * SCALE, hub.y * SCALE)
            hub_center[hub.name] = (hub.x * SCALE, hub.y * SCALE + RADIO) 
            t.down()
            t.fillcolor(hub.color.value)
            t.begin_fill()
            t.circle(RADIO)
            t.end_fill()

    def hubs_distance(h1: tuple[int,int], h2: tuple[int, int]) -> float:
        x1, y1 = h1
        x2, y2 = h2
        return sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)

    def draw_connections() -> None:

        for con in connections:
            name_h1, name_h2 = con.name.split('-')
            h1: Hub = [ hub for hub in hubs if hub.name == name_h1][0]
            h2: Hub = [ hub for hub in hubs if hub.name == name_h2][0]
            x1, y1 = hub_center[h1.name]
            x2, y2 = hub_center[h2.name]
            d: float = hubs_distance(
                            (x1, y1), 
                            (x2, y2), 
                        )
            angle: float = atan2(
                        (y2 - y1),
                        (x2 - x1))
            t.up()
            t.setpos(x1, y1)
            t.setheading(0)
            # print(f"color1: {h1.color}, hub1: {name_h1}, x:{x1}, y:{y1}")
            # print(f"color2: {h2.color}, hub2: {name_h2}, x:{x2}, y:{y2}")
            # print(f"angle: {angle}, distance: {d}")
#            if angle >= 0:
            t.left(angle)
            t.down()
            t.forward(d)

    draw_hubs()
    draw_connections()
    t.hideturtle() 
    t.screen.mainloop()

# pos1 = (20, 80)
# pos2 = (30, 90)

# t.up()
# t.setpos(pos1)
# t.down()
# t.fd(100)
# # t.setpos(pos2)
# # t.fd(100)


