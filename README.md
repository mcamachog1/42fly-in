*This project has been created as part of the 42 curriculum by macamach*

# Description

The **Fly-In** project is a simulation system designed to evaluate and optimize a **Multi-Agent Pathfinding (MAPF)** problem. 

The objective is to safely coordinate a fleet of autonomous drones across a network of zones (hubs) and interconnecting links (connections). The system must guide all drones from a designated **Start Hub** to an **End Hub** in the minimum number of simulation turns possible, while strictly adhering to real-time spatial constraints (such as zone capacities and maximum link occupancy).

The main requirements are:
- Drones may move simultaneously
- Path conflicts and deadlocks are not allowed
- The simulation needs to meet zone and connection capacity constraints

## Zone Types and costs

| Zone Type  |   Cost   |
| ---------- | -------- |
| NORMAL     |    1     |
| PRIORITY   |    1     |
| RESTRICTED |    2     |
| BLOCKED    | infinity |

Zones must respect the *max_drones* constraint  
**tie-breaking rule**: Even though NORMAL and PRIORITY have the same cost, PRIORITY must take precedence over NORMAL whenever possible.

## Connections

Connections are bidirectional and must respect the *max_link_capacity* constraint.

## Visual Representation

The network topology and real-time drone movements are rendered graphically. Components are color-coded based on the input configuration file and the following state rules:

- **Zones:** Each zone (Hub) is rendered using the custom color assigned within the network configuration file.
- **Connections:** Connections are rendered dynamically based on the type of the **destination zone**:

  - `BLACK`: When the next zone is a **NORMAL** zone.
  - `BLUE`: When the next zone is a **PRIORITY** zone.
  - `RED`: When the next zone is a **RESTRICTED** zone.
  - `GRAY`: When the next zone is a **BLOCKED** zone.

## Input file example

This is an example of a graphic network and the corresponding input network file configuration (.txt)

![Simple linear path network](assets/images/01_easy.png)



    nb_drones: 2

    start_hub:  start       0 0 [color=green]
    hub:        waypoint1   1 0 [color=blue]
    hub:        waypoint2   2 0 [color=blue]
    end_hub:    goal        3 0 [color=red]

    connection: start-waypoint1
    connection: waypoint1-waypoint2
    connection: waypoint2-goal
  

## Running Simulation

### Terminal

 A line list all the drone movements that occur during each turn, spaceseparated. Each movement follow the format: D`<ID>-<zone>`, or D`<ID>-<connection>` in case of drones still in flight toward restricted zones.

- D`<ID>` refers to the unique drone identifier (e.g., D1, D2).
- `<zone>` is the name of the destination zone.
- `<connection>` is the name of the connection toward a restricted zone (RESTRICTED zones cost 2 turns)
<br>

![Terminal simulation](assets/videos/01_easy_terminal.gif)

### GUI (pygame)

![GUI simulation](assets/videos/01_easy.gif)

# Instructions

- Clone the repo
- Execute
    ```
        make install
        make run
    ```
# Resources