# src/ui/print_map

import pygame
from src.model.model import Color, ZoneType, Map, Hub


class Visualizer:
    """Manages the graphical interface and simulation rendering using Pygame.

        This class translates the abstract mathematical drone network model
        (graph) into a visual display, handling coordinate scaling, map
        translations, and drawing operations for hubs, connections, and active
        drones.

        Attributes:
            RADIUS_HUB (int): Pixel radius used to draw network hubs.
            RADIUS_DRONE (int): Pixel radius used to draw active drones.
            network (Map): The core drone network model containing logical
                data.
            clock (pygame.time.Clock): Pygame clock object to regulate frame
                rates.
            width (int): Width of the display window in pixels.
            height (int): Height of the display window in pixels.
            scale (int): Multiplication factor to transform model units to
                pixels.
            center_x (float): Dynamic X offset to position the map origin.
            center_y (int): Dynamic Y offset to center the map vertically.
            hub_coords (dict[str, tuple[int, int]]): Mapping of hub names to
                their raw numerical model coordinates.
            hubs (dict[str, Hub]): Mapping of hub names to their respective Hub
                objects.
            conns (dict[str, Connection]): Mapping of connection strings to
                their respective Connection objects.
            autoplay (bool): Flag indicating if the display is in autoplay
                mode or manual step-by-step mode.
            screen (pygame.Surface): The active Pygame window surface.
            font (pygame.font.Font): Font configuration used for drawing
                overlay text.
        """

    RADIUS_HUB = 22
    RADIUS_DRONE = 8

    def __init__(
        self,
        network: Map,
        filename: str,
        width: int = 1200,
        height: int = 600,
        scale: int = 55
    ) -> None:
        """Initializes the Visualizer window and properties.

        Args:
            network (Map): The drone network model object to simulate.
            filename (str): Name of the map file used to set the window title.
            width (int, optional): Initial window width in pixels.
                Defaults to 1200.
            height (int, optional): Initial window height in pixels.
                Defaults to 600.
            scale (int, optional): Scale factor mapping 1 model unit to pixels.
                Defaults to 55.
        """
        # Graphic properties
        self.clock = pygame.time.Clock()
        self.width = width
        self.height = height
        self.scale = scale
        self.center_x = 0.05 * width
        self.center_y = height // 2

        # Model properties
        self.network = network
        self.hub_coords = self.network.lookup_hub_coords
        self.hubs = self.network.lookup_hubs
        self.conns = self.network.lookup_connections

        # Display mode autoplay vs step by step
        self.autoplay = False

        pygame.init()
        self.screen = pygame.display.set_mode(
            (width, height),
            pygame.RESIZABLE
        )
        pygame.display.set_caption(filename)
        pygame.font.init()
        self.font = pygame.font.SysFont(None, 14)

    def to_pygame_coords(
        self,
        model_x: float,
        model_y: float
    ) -> tuple[int, int]:
        """Translates Cartesian model coordinates to Pygame screen coordinates.

        Applies the zoom scale multiplier, centers the representation around
        the internal pixel offsets, and inverts the Y-axis since Pygame's
        vertical origin grows downwards.

        Args:
            model_x (float): Abstract X coordinate from the backend model.
            model_y (float): Abstract Y coordinate from the backend model.

        Returns:
            tuple[int, int]: A tuple containing the corresponding (x, y)
                pixel values on the Pygame window.
        """
        scaled_x = model_x * self.scale
        scaled_y = model_y * self.scale
        pygame_x = int(self.center_x + scaled_x)
        pygame_y = int(self.center_y - scaled_y)
        return pygame_x, pygame_y

    def draw_drone_with_text(
        self,
        center_pos: tuple[int, int],
        text: str
    ) -> None:
        """Draws a drone as a circle containing its identifying ID text.

            Args:
                center_pos (tuple[int, int]): Screen pixel position (x, y)
                    where the drone will be rendered.
                text (str): The identification label (e.g., drone ID) to
                    display inside the circle.
            """
        circle_color = Color.BLACK.value
        pygame.draw.circle(
            self.screen,
            circle_color,
            center_pos,
            self.RADIUS_DRONE
        )
        text_surface = self.font.render(text, True, Color.WHITE.value)
        text_rect = text_surface.get_rect()
        text_rect.center = center_pos
        self.screen.blit(text_surface, text_rect)

    def draw_connections(self) -> None:
        """Renders structural paths connecting hubs on the display surface.

        Colors lines dynamically depending on whether either connecting hub
        is classified under a restricted, priority, or blocked zone.
        """
        for conn in self.network.connections:
            line_color = 'black'
            z1, z2 = conn.name.split('-')
            z1x, z1y = self.to_pygame_coords(*self.hub_coords[z1])
            z2x, z2y = self.to_pygame_coords(*self.hub_coords[z2])
            if (
                # self.hubs[z1].zone.name == ZoneType.RESTRICTED.name or
                self.hubs[z2].zone.name == ZoneType.RESTRICTED.name
            ):
                line_color = 'red'
            elif (
                # self.hubs[z1].zone.name == ZoneType.PRIORITY.name or
                self.hubs[z2].zone.name == ZoneType.PRIORITY.name
            ):
                line_color = 'blue'
            elif (
                # self.hubs[z1].zone.name == ZoneType.BLOCKED.name or
                self.hubs[z2].zone.name == ZoneType.BLOCKED.name
            ):
                line_color = 'gray'
            pygame.draw.line(
                self.screen,
                line_color,
                (z1x, z1y),
                (z2x, z2y),
                2
            )

    def draw_hub_text(
        self,
        center_pos: tuple[int, int],
        zone: Hub
    ) -> None:
        """Overlays the identification name text onto a rendered node hub area.

        Dynamically checks the contrast safety margins of background nodes,
        switching text color to black if rendering over white or yellow hubs.

        Args:
            center_pos (tuple[int, int]): Screen pixel position (x, y) where
                the text rect will center.
            zone (Hub): The data model instance representing the current
                hub node.
        """
        transparent_surface = pygame.Surface(center_pos, pygame.SRCALPHA)
        circle_color = (0, 0, 0, 0)
        pygame.draw.circle(
            transparent_surface,
            circle_color,
            center_pos,
            self.RADIUS_HUB
        )
        font_color = Color.WHITE.value
        # breakpoint()
        if zone.color.name in [Color.WHITE.name, Color.YELLOW.name]:
            font_color = Color.BLACK.value
        text_surface = self.font.render(zone.name, True, font_color)
        text_rect = text_surface.get_rect()
        text_rect.center = center_pos
        self.screen.blit(text_surface, text_rect)

    def draw_hubs(self) -> None:
        """Renders all operational network hubs as distinct colored circles."""
        for hub in self.network.hubs:
            pos = self.to_pygame_coords(*self.hub_coords[hub.name])
            color = hub.color.value
            pygame.draw.circle(self.screen, color, pos, self.RADIUS_HUB)
            pygame.draw.circle(
                self.screen,
                (0, 0, 0),
                pos,
                self.RADIUS_HUB,
                width=2
            )
            self.draw_hub_text(pos, hub)

    def draw_drones(self) -> None:
        """Calculates drone offsets and plots active agents on the display map.

        Applies dynamic delta displacement formulas based on node/connection
        occupancy counts to separate overlapping drones when stacked at the
        same structural coordinates.
        """
        # delta is for move drones inside the same hub a little distance
        delta: dict[str, float] = {h.name: 0 for h in self.network.hubs}
        for c in self.network.connections:
            delta[c.name] = 0
        for drone in self.network.drones:
            # When drone stay in one connection (restricted zone)
            if drone.connection is not None:
                xm = (drone.current_zone.x + drone.next_zone.x) / 2
                ym = (drone.current_zone.y + drone.next_zone.y) / 2
                if self.conns[drone.connection].occupancy > 1:
                    delta[drone.connection] += 0.15
                    xm -= delta[drone.connection]
                elif self.conns[drone.connection].occupancy == 1:
                    delta[drone.connection] = 0
            # Normal zones
            else:
                xm = drone.current_zone.x
                ym = drone.current_zone.y
                if (
                    drone.current_zone.name != self.network.start_hub and
                    drone.current_zone.name != self.network.end_hub
                ):
                    if drone.current_zone.occupancy > 1:
                        delta[drone.current_zone.name] += 0.15
                        xm -= delta[drone.current_zone.name]
                    elif drone.current_zone.occupancy == 1:
                        delta[drone.current_zone.name] = 0

            pos = self.to_pygame_coords(xm, ym)
            self.draw_drone_with_text(pos, str(drone.id))

    def event_action(self, event: pygame.event.Event, bg_color: str) -> None:
        """Handles core window events such as resizing and closing requests.

        Args:
            event (pygame.event.Event): The Pygame event object to evaluate.
            bg_color (str): The background color name or RGB tuple to fill
                the screen.
        """
        # Close window event
        if event.type == pygame.QUIT:
            pygame.quit()
            exit(0)

        # Resize window
        if event.type == pygame.VIDEORESIZE:
            self.width, self.height = event.w, event.h
            self.screen = pygame.display.set_mode(
                (self.width, self.height),
                pygame.RESIZABLE
            )
            self.center_x = 0.025 * self.width
            self.center_y = self.height // 2
            # Re-draw
            self.screen.fill(bg_color)
            self.draw_connections()
            self.draw_hubs()
            self.draw_drones()
            pygame.display.flip()

    def close(self) -> None:
        """Uninitializes Pygame core frameworks and closes standard
        visual windows."""
        pygame.quit()

    def draw_simulation(self) -> None:
        """Refreshes and paints the current frame of the live simulation.

        Draws connections, updates hub availability colors, plots drone
        midpoint transitions, and triggers a physical frame update to
        the screen display.
        """
        bg_color = 'gray'
        self.screen.fill(bg_color)
        self.draw_connections()
        self.draw_hubs()
        self.draw_drones()
        pygame.display.flip()

        if self.autoplay:
            for event in pygame.event.get():
                self.event_action(event, bg_color)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.autoplay = False
            self.clock.tick(0.5)
        else:
            waiting_for_input = True
            while waiting_for_input:
                # Freeze everything until an event occurs
                event = pygame.event.wait()
                self.event_action(event, bg_color)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        waiting_for_input = False
                    elif event.key == pygame.K_RETURN:
                        self.autoplay = True
                        waiting_for_input = False
