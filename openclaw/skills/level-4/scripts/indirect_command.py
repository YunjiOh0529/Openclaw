import carla
import time

def measure_time(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} 응답시간: {end - start:.2f}초")
        return result
    return wrapper

class Level4Assistant:
    def __init__(self, vehicle, world):
        self.vehicle = vehicle
        self.world = world
        self.hud_color = carla.Color(0, 255, 0)

    def send_visual_msg(self, message):

        self.world.debug.draw_string(
            self.vehicle.get_location() + carla.Location(z=2.0),
            message,
            draw_shadow=True,
            color=self.hud_color,
            life_time=3.0
        )
        print(f"[level-4 Skill]: {message}")

    def emergency_stop(self):

        control = carla.VehicleControl()
        control.throttle = 0.0
        control.brake = 1.0
        control.hand_brake = True
        self.vehicle.set_autopilot(False)
        self.vehicle.apply_control(control)

    def activate_hazard_lights(self):

        lights = (
            carla.VehicleLightState.RightBlinker |
            carla.VehicleLightState.LeftBlinker
        )
        self.vehicle.set_light_state(carla.VehicleLightState(lights))

    def open_all_doors(self):

        for door in [
            carla.VehicleDoor.FL,
            carla.VehicleDoor.FR,
            carla.VehicleDoor.RL,
            carla.VehicleDoor.RR,
        ]:
            try:
                self.vehicle.open_door(door)
            except Exception:
                pass

    @measure_time
    def process_command(self, text):


        if "어둡" in text or "라이트" in text:
            lights = (
                carla.VehicleLightState.LowBeam |
                carla.VehicleLightState.Position
            )
            self.vehicle.set_light_state(carla.VehicleLightState(lights))
            self.send_visual_msg("주변이 어두워 헤드라이트를 켭니다.")


        elif "덥" in text or "에어컨" in text:
            self.send_visual_msg("실내 온도가 높습니다. 에어컨을 22도로 조절합니다.")


        elif "답답" in text or "창문" in text:
            self.open_all_doors()
            self.send_visual_msg("환기를 위해 창문을 개방합니다.")


        elif "피곤" in text or "마사지" in text:
            lights = carla.VehicleLightState.Interior
            self.vehicle.set_light_state(carla.VehicleLightState(lights))
            self.send_visual_msg("피로 회복을 위해 시트 마사지 기능을 시작합니다.")


        elif "졸" in text or "졸리" in text or "잠" in text:
            self.activate_hazard_lights()
            self.emergency_stop()
            time.sleep(1)
            self.open_all_doors()
            self.send_visual_msg(
                "졸음이 감지되었습니다. 안전을 위해 차량을 정지하고 문을 개방합니다."
            )


        elif "위험" in text or "멈춰" in text or "스톱" in text:
            self.activate_hazard_lights()
            self.emergency_stop()
            self.send_visual_msg("위험 상황이 감지되었습니다. 즉시 차량을 정지합니다.")


        elif any(kw in text for kw in ["도착", "내릴게", "내려", "내린다", "세워"]):
            self.open_all_doors()
            self.send_visual_msg("목적지에 도착했습니다. 문을 열겠습니다. 안녕히 가세요!")


        else:
            self.send_visual_msg("무엇을 도와드릴까요?")


@measure_time
def main():
    vehicle = None
    try:

        client = carla.Client('210.125.91.140', 2000)
        client.set_timeout(10.0)
        world = client.get_world()


        vehicles = world.get_actors().filter('vehicle.*')
        if vehicles:
            vehicle = vehicles[0]
        else:
            blueprint = world.get_blueprint_library().find('vehicle.tesla.model3')
            spawn_point = world.get_map().get_spawn_points()[0]
            vehicle = world.spawn_actor(blueprint, spawn_point)

        assistant = Level4Assistant(vehicle, world)


        scenarios = [
            (2, "밖이 어두운 것 같은데"),
            (3, "아, 좀 덥네"),
            (3, "공기가 좀 답답한 것 같아"),
            (3, "좀 졸리다"),
            (3, "위험해"),
            (3, "나 도착했어, 내릴게"),
        ]


        if len(sys.argv) > 1:
            assistant.process_command(" ".join(sys.argv[1:]))
        else:
            for delay, cmd in scenarios:
                time.sleep(delay)
                print(f"\n[입력]: {cmd}")
                assistant.process_command(cmd)

    except Exception as e:
        print(f"Error: {e}")
    finally:


        pass

if __name__ == '__main__':
    import sys
    main()
