import sys
import time

import carla

HOST = "210.125.91.140"
PORT = 2000
MODEL = "vehicle.lincoln.mkz_2020"
SPAWN_INDEX = 0


def main():
    client = carla.Client(HOST, PORT)
    client.set_timeout(60.0)
    world = client.get_world()

    old = list(world.get_actors().filter("vehicle.*"))
    if old:
        client.apply_batch_sync([carla.command.DestroyActor(a) for a in old])
    world.wait_for_tick(seconds=10.0)

    bp = world.get_blueprint_library().find(MODEL)
    bp.set_attribute("role_name", "ego_vehicle")
    points = world.get_map().get_spawn_points()
    if not points:
        sys.exit("No spawn points found.")

    vehicle = None
    for i in range(len(points)):
        sp = points[(SPAWN_INDEX + i) % len(points)]
        vehicle = world.try_spawn_actor(bp, sp)
        if vehicle is not None:
            break
    if vehicle is None:
        sys.exit("Could not spawn the vehicle.")

    world.wait_for_tick(seconds=10.0)
    tf = vehicle.get_transform()
    back = tf.get_forward_vector() * -8.0
    cam = carla.Transform(
        carla.Location(x=tf.location.x + back.x, y=tf.location.y + back.y, z=tf.location.z + 4.0),
        carla.Rotation(pitch=-20.0, yaw=tf.rotation.yaw),
    )
    world.get_spectator().set_transform(cam)
    time.sleep(1.0)
    print(f"reset ok: removed {len(old)} vehicle(s), spawned {MODEL} (id {vehicle.id})")


if __name__ == "__main__":
    main()
