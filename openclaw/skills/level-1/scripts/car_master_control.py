import time
import carla
import sys
import argparse

def measure_time(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} 응답시간: {end - start:.2f}초")
        return result
    return wrapper

@measure_time
def car_master_control(category: str, action: str, value: str = "0"):
\
\

    client = carla.Client('210.125.91.140', 2000)
    client.set_timeout(10.0)

    try:
        world = client.get_world()
        all_actors = world.get_actors()


        vehicle = None
        for actor in all_actors:
            if 'vehicle' in actor.type_id:
                if actor.attributes.get('role_name') in ('hero', 'ego_vehicle'):
                    vehicle = actor
                    break

        if vehicle is None:
            vehicles = list(all_actors.filter('vehicle.*'))
            if vehicles:
                vehicle = vehicles[0]

        if vehicle is None:
            return "오류: 시뮬레이터에 차량이 존재하지 않습니다."

        vehicle.set_simulate_physics(True)
        vehicle.set_autopilot(False)
        control = vehicle.get_control()
        control.hand_brake = False
        vehicle.apply_control(control)


        if category == 'drive':
            if action == 'autopilot':
                vehicle.set_autopilot(value.lower() == 'on')
                status = "활성화" if value.lower() == 'on' else "비활성화"
                return f"오토파일럿을 {status}했습니다."

            control = carla.VehicleControl()
            if action == 'throttle':
                control.throttle = float(value)
                control.brake = 0.0
                control.hand_brake = False
                control.manual_gear_shift = False
                vehicle.apply_control(control)
                return f"ID {vehicle.id} 차량: 주행 시작 (스로틀 {value})"
            elif action == 'stop':
                control.throttle = 0.0
                control.brake = 1.0
                vehicle.apply_control(control)
                return "차량을 정지시켰습니다."
            elif action == 'reverse':
                control.throttle = float(value) if value != "0" else 0.3
                control.brake = 0.0
                control.reverse = True
                control.hand_brake = False
                vehicle.apply_control(control)
                return f"후진을 시작합니다. (스로틀 {value})"


        elif category == 'ext':
            if action == 'window':
                return "창문 개폐는 CARLA 미지원 기능입니다."

            elif action == 'door':
                door_map = {
                    '0': carla.VehicleDoor.FL,
                    'fl': carla.VehicleDoor.FL,
                    '1': carla.VehicleDoor.FR,
                    'fr': carla.VehicleDoor.FR,
                    '2': carla.VehicleDoor.RL,
                    'rl': carla.VehicleDoor.RL,
                    '3': carla.VehicleDoor.RR,
                    'rr': carla.VehicleDoor.RR,
                    'all': carla.VehicleDoor.All
                }
                door = door_map.get(str(value).lower(), carla.VehicleDoor.FL)
                vehicle.open_door(door)
                return f"{value} 문을 열었습니다."

            elif action == 'close_door':
                door_map = {
                    '0': carla.VehicleDoor.FL,
                    'fl': carla.VehicleDoor.FL,
                    '1': carla.VehicleDoor.FR,
                    'fr': carla.VehicleDoor.FR,
                    '2': carla.VehicleDoor.RL,
                    'rl': carla.VehicleDoor.RL,
                    '3': carla.VehicleDoor.RR,
                    'rr': carla.VehicleDoor.RR,
                    'all': carla.VehicleDoor.All
                }
                door = door_map.get(str(value).lower(), carla.VehicleDoor.FL)
                vehicle.close_door(door)
                return f"{value} 문을 닫았습니다."

            elif action == 'light':
                ls = carla.VehicleLightState
                if value == 'hazard':
                    vehicle.set_light_state(carla.VehicleLightState(ls.LeftBlinker | ls.RightBlinker))
                    light_state = vehicle.get_light_state()
                    return f"비상등을 켰습니다. 현재 라이트 상태: {light_state}"
                elif value == 'highbeam':
                    vehicle.set_light_state(carla.VehicleLightState(ls.HighBeam))
                    return "상향등을 켰습니다."
                elif value == 'lowbeam':
                    vehicle.set_light_state(carla.VehicleLightState(ls.LowBeam))
                    return "헤드라이트를 켰습니다."
                elif value == 'leftblinker':
                    vehicle.set_light_state(carla.VehicleLightState(ls.LeftBlinker))
                    return "좌측 깜빡이를 켰습니다."
                elif value == 'rightblinker':
                    vehicle.set_light_state(carla.VehicleLightState(ls.RightBlinker))
                    return "우측 깜빡이를 켰습니다."
                elif value == 'fog':
                    vehicle.set_light_state(carla.VehicleLightState(ls.Fog))
                    return "안개등을 켰습니다."
                elif value == 'interior':
                    vehicle.set_light_state(carla.VehicleLightState(ls.Interior))
                    return "실내등을 켰습니다."
                elif value == 'brake':
                    vehicle.set_light_state(carla.VehicleLightState(ls.Brake))
                    return "브레이크등을 켰습니다."
                elif value == 'reverse':
                    vehicle.set_light_state(carla.VehicleLightState(ls.Reverse))
                    return "후진등을 켰습니다."
                elif value == 'position':
                    vehicle.set_light_state(carla.VehicleLightState(ls.Position))
                    return "포지션등(미등)을 켰습니다."
                elif value == 'off':
                    vehicle.set_light_state(carla.VehicleLightState(ls.NONE))
                    return "라이트를 껐습니다."


        elif category == 'hmi':
            if action == 'climate':
                return f"에어컨을 {value}도로 설정합니다. (CARLA 미지원 - 텍스트 응답)"
            elif action == 'media':
                return f"미디어를 재생합니다. 볼륨: {value} (CARLA 미지원 - 텍스트 응답)"


        elif category == 'weather':
            weather_map = {
                'clear': carla.WeatherParameters.ClearNoon,
                'rain': carla.WeatherParameters.WetNoon,
                'hardrain': carla.WeatherParameters.HardRainNoon,
                'cloudy': carla.WeatherParameters.CloudyNoon,
                'night': carla.WeatherParameters.ClearNight,
                'fog': carla.WeatherParameters.SoftRainNoon,
                'sunset': carla.WeatherParameters.ClearSunset,
                'wetnight': carla.WeatherParameters.WetCloudyNight,
                'hardrainnight': carla.WeatherParameters.HardRainNight,

                'darknight': carla.WeatherParameters(
                    cloudiness=80.0,
                    precipitation=0.0,
                    precipitation_deposits=0.0,
                    wind_intensity=10.0,
                    sun_azimuth_angle=-1.0,
                    sun_altitude_angle=-120.0,
                    fog_density=70.0,
                    fog_distance=100.0,
                    fog_falloff=1.0,
                    wetness=0.0,
                    scattering_intensity=1.0,
                    dust_storm=0.0,
                    mie_scattering_scale=0.03,
                    rayleigh_scattering_scale=0.0331
                )
            }
            weather = weather_map.get(value.lower(), carla.WeatherParameters.ClearNoon)
            world.set_weather(weather)
            return f"날씨를 {value}으로 변경했습니다."


        elif category == 'status':
            if action == 'check':
                v = vehicle.get_velocity()
                speed = 3.6 * (v.x**2 + v.y**2 + v.z**2)**0.5
                physics = vehicle.get_physics_control()
                wheels = physics.wheels
                result = f"현재 속도: {speed:.1f}km/h\n"
                result += "=== 타이어 상태 ===\n"
                positions = ['FL', 'FR', 'RL', 'RR']
                for i, wheel in enumerate(wheels):
                    result += f"타이어({positions[i]}): 마찰계수 {wheel.tire_friction:.2f}\n"
                return result
            elif action == 'light':
                light_state = vehicle.get_light_state()
                return f"현재 라이트 상태: {light_state}"
            elif action == 'location':
                loc = vehicle.get_location()
                return f"현재 위치: x={loc.x:.2f}, y={loc.y:.2f}, z={loc.z:.2f}"
            elif action == 'transform':
                tf = vehicle.get_transform()
                return (f"위치: x={tf.location.x:.2f}, y={tf.location.y:.2f}, z={tf.location.z:.2f} | "
                        f"회전: pitch={tf.rotation.pitch:.1f}, yaw={tf.rotation.yaw:.1f}, roll={tf.rotation.roll:.1f}")

        return "명령 수행 완료"

    except Exception as e:
        return f"제어 중 오류 발생: {str(e)}"


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--category', type=str)
    parser.add_argument('--action', type=str)
    parser.add_argument('--value', type=str, default='0')


    parser.add_argument('args', nargs='*')

    parsed = parser.parse_args()

    if parsed.category:
        category = parsed.category
        action = parsed.action
        value = parsed.value
    elif len(parsed.args) >= 3:
        category = parsed.args[0]
        action = parsed.args[1]
        value = parsed.args[2]
    elif len(parsed.args) == 2:
        category = parsed.args[0]
        action = parsed.args[1]
        value = "0"
    else:
        print("인자 부족: --category ext --action light --value hazard")
        sys.exit(1)

    result = car_master_control(category, action, value)
    print(result)
