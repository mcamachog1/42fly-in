import pygame
from src.model.model import Hub, Color, ZoneType

class Visualizer:

    RADIUS_HUB = 20
    RADIUS_DRONE = 8

    def __init__(self, network, width=1200, height=600, scale=60):
        self.network = network
        self.clock = pygame.time.Clock()
        self.width = width
        self.height = height
        self.scale = scale


        pygame.init()
        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        pygame.display.set_caption("Fly-in Drone Simulator")

        # VARIABLE DE ESTADO CLAVE:
        # False = Modo manual (Espera barra espaciadora)
        # True  = Modo automático (Avanza solo con el reloj)
        self.modo_automatico = False

        # Calculamos el centro de la pantalla en píxeles
        self.center_x = 0.05*width 
        self.center_y = height // 2

        # Mapeo: Asociamos cada Hub string a una coordenada de píxeles (X, Y)
        # Ejemplo: {"roof1": (100, 200), "hubA": (300, 400)}
        self.positions = self._generate_hub_positions()
        self.hubs = self._generate_hubs()

        pygame.font.init()
        self.font = pygame.font.SysFont(None, 14)

     
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

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pass
                
            elif event.type == pygame.VIDEORESIZE:
                self.width, self.height = event.w, event.h
                self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
                # Calculamos el centro de la pantalla en píxeles
                self.center_x = 0.025*self.width 
                self.center_y = self.height // 2

            elif event.type == pygame.KEYDOWN:
                # CASO A: Presiona ESPACIO -> Modo Manual / Avanzar un solo paso
                if event.key == pygame.K_SPACE:
                    self.modo_automatico = False  # Si estaba en automático, se pausa
                    # self.avanzar_logica_drones(drones)
                    # necesita_redibujar = True
                    
                # CASO B: Presiona la tecla 'A' -> Activar/Desactivar el Reloj Automático
                elif event.key == pygame.K_a or event.key == pygame.K_RETURN:
                    # Conmutamos el estado (si está apagado lo prende, y viceversa)
                    self.modo_automatico = not self.modo_automatico                

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
            hub = drone.current_zone
            positions[hub.name] = (hub.x, hub.y)
        return positions

    def draw_drone_with_text(self, center_pos: tuple[int, int], text: str) -> None:
        circle_color = Color.BLACK.value
        pygame.draw.circle(self.screen, circle_color, center_pos, self.RADIUS_DRONE)
        text_color = Color.WHITE.value
        text_surface = self.font.render(text, True, text_color)
        text_rect = text_surface.get_rect()
        text_rect.center = center_pos
        self.screen.blit(text_surface, text_rect)

    def draw_simulation(self, drones):

        self.handle_events()
        bg_color = 'gray'
        self.screen.fill(bg_color) # Fondo gris oscuro uniforme
        # 1. Dibujar conexiones (Líneas)
        for conn in self.network.connections:
            line_color = 'black'
            z1, z2 = conn.name.split('-')
            z1x, z1y = self.to_pygame_coords(*self.positions[z1])
            z2x, z2y = self.to_pygame_coords(*self.positions[z2])
            if self.hubs[z1].zone.name == ZoneType.RESTRICTED.name or self.hubs[z2].zone.name == ZoneType.RESTRICTED.name:
                line_color = 'red'
            elif self.hubs[z1].zone.name == ZoneType.PRIORITY.name or self.hubs[z2].zone.name == ZoneType.PRIORITY.name:
                line_color = 'blue'
            elif self.hubs[z1].zone.name == ZoneType.BLOCKED.name or self.hubs[z2].zone.name == ZoneType.BLOCKED.name:
                line_color = 'gray'

            pygame.draw.line(self.screen, line_color, (z1x, z1y), (z2x, z2y), 2)
        # 2. Dibujar Hubs (Círculos)not self.modo_automatico 
        for hub in self.network.hubs:
            pos = self.to_pygame_coords(*self.positions[hub.name])
            color = hub.color.value
            pygame.draw.circle(self.screen, color, pos, self.RADIUS_HUB)
        # 3. Dibujar Drones (Círculos más pequeños flotantes o imágenes)
        color = Color.BLACK.value
        for drone in drones:
            xm = (drone.current_zone.x + drone.next_zone.x) / 2
            ym = (drone.current_zone.y + drone.next_zone.y) / 2
            pos = self.to_pygame_coords(xm, ym)
            self.draw_drone_with_text(pos, str(drone.id))
        # 4. CONTROL DEL RELOJ (Crucial)
        # - Si está en automático, limitamos a 5-10 turnos por segundo para que sea legible.
        # - Si está en manual, limitamos a 60 FPS solo para que el bucle no sature la CPU al buscar eventos.
        # breakpoint()
        pygame.display.flip()
        if self.modo_automatico:
            self.clock.tick(60)  # Velocidad de la automatización (5 pasos por segundo)
        else:
            self.clock.tick(0.5) # Tas

