import carla
import random
import time

from carla import Transform

from center_camera import center_camera

# Parámetros
maps = ['Town01', 'Town02', 'Town03', 'Town04', 'Town05', 'Town10HD']
weathers = ['ClearNight', 'CloudyNoon', 'HardRainSunset', 'SoftRainNoon',
            'Default']

tiempo_transicion = 2.5

numero_vehiculos = 50
numero_peatones = 50


pausa_comienzo = 5

ticks_visuzalizacion_interseccion = 750
ticks_visualizacion_peatones = 750
ticks_visualizacion_vehiculos = 750
duracion_simulacion = ticks_visuzalizacion_interseccion + ticks_visualizacion_peatones + ticks_visuzalizacion_interseccion

ticks_cambio_seguimiento = 225

# Spawn para la demo de las fisicas de los coches cayendo del cielo
location_vehiculos = carla.Location(x=-51.038803, y=36.740517, z=25)
rotation_vehiculos = carla.Rotation(pitch=-30.146206, yaw=78.250839, roll=0.000068)
localizacion_vehiculos = carla.Transform(location_vehiculos, rotation_vehiculos)

# Cámara en la intersección de la demo
location = carla.Location(x=-46.558777, y=50.816422, z=29.995558)
rotation = carla.Rotation(pitch=-47.153709, yaw=-100.403381, roll=0.000023)
camara_intersección = carla.Transform(location, rotation)

# Variables
client = carla.Client('localhost', 2000)
world = client.get_world()

# Demo escenografia
time.sleep(pausa_comienzo)
for map in maps:
    client.load_world(map)
    time.sleep(2)
    spawn_points = world.get_map().get_spawn_points()
    vehicle_blueprints = world.get_blueprint_library().filter('*vehicle*')

    for i in range(numero_vehiculos):
        world.try_spawn_actor(random.choice(vehicle_blueprints), random.choice(spawn_points))

    for vehicle in world.get_actors().filter('*vehicle*'):
        vehicle.set_autopilot(True)

    for weather in weathers:
        world.set_weather(getattr(carla.WeatherParameters, weather))
        time.sleep(tiempo_transicion)

    actor_list = world.get_actors()
    for vehicle in actor_list.filter('vehicle.*'):
        vehicle.destroy()

# Cámara para la demo
spectator = world.get_spectator()
spectator.set_transform(camara_intersección)

# Vehiculos disponibles
vehicle_blueprints = world.get_blueprint_library().filter('*vehicle*')

for vehicle in vehicle_blueprints:
    world.try_spawn_actor(vehicle, localizacion_vehiculos)
    time.sleep(0.5)

# Limpieza
actor_list = world.get_actors()
for vehicle in actor_list.filter('vehicle.*'):
    vehicle.destroy()

# Comenzamos la demo
## Generación de vehiculos
for i in range(numero_vehiculos):
    world.try_spawn_actor(random.choice(vehicle_blueprints), random.choice(spawn_points))

for vehicle in world.get_actors().filter('*vehicle*'):
    vehicle.set_autopilot(True)

## Generación de Peatones
for i in range(numero_peatones):
    pedestrian_bp = random.choice(world.get_blueprint_library().filter('*walker.pedestrian*'))
    pedestrian = world.try_spawn_actor(pedestrian_bp, Transform(world.get_random_location_from_navigation()))
    controller_bp = world.get_blueprint_library().find('controller.ai.walker')
    try:
        controller = world.spawn_actor(controller_bp, pedestrian.get_transform(), pedestrian)
        controller.start()
        controller.go_to_location(world.get_random_location_from_navigation())
    except:
        pass

# Bucle principal para el manejo de la cámara
for i in range(duracion_simulacion):
    transicion_interseccion_peatones = ticks_visuzalizacion_interseccion
    transicion_peatones_coches = ticks_visuzalizacion_interseccion+ticks_visualizacion_peatones
    if i > ticks_visuzalizacion_interseccion and i < transicion_peatones_coches and i % ticks_cambio_seguimiento == 1:
        peaton = random.choice(world.get_actors().filter('*walker.pedestrian*'))
        camera_bp = world.get_blueprint_library().find('sensor.camera.rgb')
        camera = world.spawn_actor(camera_bp, peaton.get_transform())
        camera.set_transform(center_camera(spectator, peaton))

    if i > transicion_peatones_coches and i % ticks_cambio_seguimiento == 1:
        coche = random.choice(world.get_actors().filter('*vehicle*'))
        camera_bp = world.get_blueprint_library().find('sensor.camera.rgb')
        camera = world.spawn_actor(camera_bp, coche.get_transform())
        camera.set_transform(center_camera(spectator, coche))

    world.tick()

print('Fin')
