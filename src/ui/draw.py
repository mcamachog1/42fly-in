import turtle as t
from random import random
from math import sqrt

from src.model.model import Map, Connection, Hub, Drone

RADIO: int = 20

def draw_hubs(hubs: list[Hub]) -> None:
    coords: list[tuple[int, int]] = []
    for hub in hubs:
        coord = (hub.x * 150, hub.y * 150)
        coords.append(coord)
    for c in coords:
        t.up()
        t.setpos(c)
        t.down()
        t.circle(RADIO)     
    t.mainloop()

def hubs_distance(h1: tuple[int,int], h2: tuple[int, int]) -> float:
    x1, y1 = h1
    x2, y2 = h2
    return sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)

def draw_connections(connections: list[Connection], hubs: list[Hub]) -> None:
    coords: list[tuple[int, int]] = []
    for con in connections:
        name_h1, name_h2 = con.name.split('-')
        h1 = [(hub.x, hub.y) for hub in hubs if hub.name == name_h1][0]
        h2 = [(hub.x, hub.y) for hub in hubs if hub.name == name_h2][0]
        
    for c in coords:
        t.up()
        t.setpos(c)
        t.down()
        t.circle(RADIO)     
    t.mainloop()


# pos1 = (20, 80)
# pos2 = (30, 90)

# t.up()
# t.setpos(pos1)
# t.down()
# t.fd(100)
# # t.setpos(pos2)
# # t.fd(100)


