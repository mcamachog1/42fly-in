import pygame
from src.model.model import Hub, Color

class Visualizer:
    def __init__(self, network, width=1200, height=600, scale=45):
        self.network = network
        self.clock = pygame.time.Clock()
        self.width = width
        self.height = height
        self.scale = scale         

        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Fly-in Drone Simulator")
        
        # Calculamos el centro de la pantalla en píxeles
        self.center_x = 0.05*width 
        self.center_y = height // 2

        # Mapeo: Asociamos cada Hub string a una coordenada de píxeles (X, Y)
        # Ejemplo: {"roof1": (100, 200), "hubA": (300, 400)}
        self.positions = self._generate_hub_positions()
        self.hubs = self._generate_hubs()

        # try
        drone_original = pygame.image.load("src/ui/img/drone.png").convert_alpha()
        self.drone_image = pygame.transform.scale(drone_original, (30,30))

    def to_pygame_coords(self, model_x: float, model_y: float) -> tuple[int, int]:
            """
            Convierte coordenadas cartesianas (centro 0,0) al sistema 
            de píxeles de Pygame (esquina superior izquierda 0,0) aplicando escala.
            """
            # 1. Aplicamos el factor de escala (Zoom)
            scaled_x = model_x * self.scale
            scaled_y = model_y * self.scale
            
            # 2. Trasladamos el origen al centro e invertimos el eje Y
            pygame_x = int(self.center_x + scaled_x)
            pygame_y = int(self.center_y - scaled_y)
            
            return pygame_x, pygame_y


    def _generate_hubs(self) -> dict[str, Hub]:
        hubs: dict[str, Hub] = {h.name: h for h in self.network.hubs}
        return hubs

    def _generate_hub_positions(self) -> dict:
        # Aquí puedes asignar coordenadas fijas a tus Hubs para que se dibujen
        # en forma de cuadrícula o grafo ordenado en la pantalla.
        positions = {}
        for hub in self.network.hubs:
            positions[hub.name] = (hub.x, hub.y)
        return positions

    def _generate_drone_positions(self) -> dict:
        # Aquí puedes asignar coordenadas to the drones para que se dibujen
        # en forma de cuadrícula o grafo ordenado en la pantalla.
        positions = {}
        for drone in self.network.drones:
            positions[hub.name] = (hub.x, hub.y)
        return positions

    def draw_simulation(self, drones):
        self.screen.fill((20, 20, 20)) # Fondo gris oscuro uniforme
        
        # 1. Dibujar conexiones (Líneas)
        for conn in self.network.connections:
            z1, z2 = conn.name.split('-')
            z1x, z1y = self.to_pygame_coords(*self.positions[z1])
            z2x, z2y = self.to_pygame_coords(*self.positions[z2])
            pygame.draw.line(self.screen, (100, 100, 100), (z1x, z1y), (z2x, z2y), 2)
            
        # 2. Dibujar Hubs (Círculos)
        for hub in self.network.hubs:
            pos = self.to_pygame_coords(*self.positions[hub.name])
            color = hub.color.value
            pygame.draw.circle(self.screen, color, pos, 15)
            
        # 3. Dibujar Drones (Círculos más pequeños flotantes o imágenes)
        color = Color.BLACK.value
        for drone in drones:
            xm = (drone.current_zone.x + drone.next_zone.x) / 2
            ym = (drone.current_zone.y + drone.next_zone.y) / 2
            pos = self.to_pygame_coords(xm, ym)

            drone_rect = self.drone_image.get_rect()
            drone_rect.center = pos
            self.screen.blit(self.drone_image, drone_rect)
            # pygame.draw.circle(self.screen, color, pos, 5)

        pygame.display.flip()
        self.clock.tick(1) # Forzar 60 fotogramas por segundo