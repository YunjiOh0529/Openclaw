import carla
import random
import argparse
import sys
import time

def spawn_vehicle(host, port, vehicle_model, map_name):
    try:
        client = carla.Client(host, port)
        client.set_timeout(60.0)

        world = client.get_world()
        current_map = world.get_map().name

        if map_name not in current_map:
            print(f'Currently in {current_map}, loading {map_name} (this might take a while)...')
            world = client.load_world(map_name)
            world.wait_for_tick(seconds=5.0)

        blueprint_library = world.get_blueprint_library()
        bp = blueprint_library.find(vehicle_model)
        bp.set_attribute('role_name', 'ego_vehicle')

        spawn_points = world.get_map().get_spawn_points()
        if not spawn_points:
            print('No spawn points found.')
            return False

        chosen_spawn_point = None
        for _ in range(10):
            sp = random.choice(spawn_points)
            if sp.location.distance(carla.Location(x=0,y=0,z=0)) > 10.0:
                chosen_spawn_point = sp
                break

        if chosen_spawn_point is None:
            chosen_spawn_point = random.choice(spawn_points)

        vehicle = world.try_spawn_actor(bp, chosen_spawn_point)

        if vehicle:
            print(f'Successfully spawned {vehicle.type_id} (ID: {vehicle.id}) at {chosen_spawn_point.location}')
            return True
        else:
            print('Failed to spawn vehicle at the chosen point.')
            return False

    except Exception as e:
        print(f'Error connecting to CARLA server or spawning vehicle: {e}')
        return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Spawn a vehicle in CARLA.')
    parser.add_argument('--carla_host', type=str, default='210.125.91.141', help='CARLA server IP address.')
    parser.add_argument('--carla_port', type=int, default=2000, help='CARLA server port number.')
    parser.add_argument('--vehicle_model', type=str, required=True, help='Vehicle blueprint name (e.g., vehicle.lincoln.mkz_2020).')
    parser.add_argument('--map_name', type=str, default='Town03', help='CARLA map name to load if not already in.')

    args = parser.parse_args()

    if not spawn_vehicle(args.carla_host, args.carla_port, args.vehicle_model, args.map_name):
        sys.exit(1)
