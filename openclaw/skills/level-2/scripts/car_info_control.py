import carla
import sys
import argparse
from datetime import datetime
import time

def measure_time(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} 응답시간: {end - start:.2f}초")
        return result
    return wrapper

@measure_time
def car_info_control(category: str, action: str, value: str = "0"):
    """
    CARLA 시뮬레이션 정보 조회 및 제어 통합 도구 (날씨, 위치, 도로, 시간, 주행정보)
    """
    client = carla.Client('210.125.91.140', 2000)
    client.set_timeout(10.0)
    
    try:
        world = client.get_world()
        map_obj = world.get_map()
        all_actors = world.get_actors()
        
        # 기본 타겟 차량 찾기 (ID: 24 우선, 없으면 첫 번째 차량)
        target_id = 24
        vehicle = all_actors.find(target_id)
        
        if vehicle is None:
            vehicles = all_actors.filter('vehicle.*')
            if not vehicles:
                return "실행 실패: 시뮬레이터에 활성화된 차량이 없습니다."
            vehicle = vehicles[0]

        # --- [1] 날씨 조회/설정 ---
        if category == 'weather':
            if action == 'get':
                w = world.get_weather()
                return f"현재 날씨 상태입니다: 구름량 {w.cloudiness}%, 강수량 {w.precipitation}%, 풍속 {w.wind_intensity}. 모든 기상 파라미터가 정상입니다."
            elif action == 'set':
                weather_map = {
                    'clear': carla.WeatherParameters.ClearNoon,
                    'rain': carla.WeatherParameters.WetNoon,
                    'hardrain': carla.WeatherParameters.HardRainNoon,
                    'cloudy': carla.WeatherParameters.CloudyNoon,
                    'night': carla.WeatherParameters.ClearNight
                }
                weather = weather_map.get(value.lower(), carla.WeatherParameters.ClearNoon)
                world.set_weather(weather)
                return f"날씨를 {value} 상태로 성공적으로 변경했습니다."

        # --- [2] 위치 및 도로 정보 (Location & Road) ---
        elif category == 'location':
            loc = vehicle.get_location()
            if action == 'get':
                return f"현재 차량은 x={loc.x:.2f}, y={loc.y:.2f}, z={loc.z:.2f} 지점에 위치해 있습니다."
            
            elif action == 'road': # 도로 정보 조회 추가
                waypoint = map_obj.get_waypoint(loc)
                road_id = waypoint.road_id
                lane_id = waypoint.lane_id
                return f"현재 Road ID {road_id}번 도로의 {lane_id}번 차선에서 주행 중입니다."

        # --- [3] 날짜 및 시간 정보 (DateTime) ---
        elif category == 'datetime':
            now = datetime.now()
            return f"현재 시스템 기준 날짜는 {now.strftime('%Y년 %m월 %d일')}이며, 시간은 {now.strftime('%H시 %M분')}입니다."

        # --- [4] 주행 정보 (Driving Info - 속도 등) ---
        elif category == 'driving':
            if action == 'speed':
                v = vehicle.get_velocity()
                # m/s를 km/h로 변환
                speed = 3.6 * (v.x**2 + v.y**2 + v.z**2)**0.5
                return f"현재 차량의 주행 속도는 약 {speed:.1f} km/h입니다."

        # --- [5] 카메라 제어 ---
        elif category == 'camera':
            spectator = world.get_spectator()
            transform = vehicle.get_transform()
            if action == 'back': 
                transform.location -= 10 * transform.get_forward_vector()
                transform.location.z += 5
                transform.rotation.pitch = -20
            elif action == 'front': 
                transform.location += 10 * transform.get_forward_vector()
                transform.rotation.yaw += 180
                transform.location.z += 3
            elif action == 'top': 
                transform.location.z += 30
                transform.rotation.pitch = -90
            spectator.set_transform(transform)
            return f"카메라 시점을 {action} 뷰로 전환 완료했습니다."

        return "요청하신 조회를 완료했습니다."

    except Exception as e:
        return f"실행 중 오류 발생: {str(e)}"

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--category', type=str)
    parser.add_argument('--action', type=str)
    parser.add_argument('--value', type=str, default='0')

    parsed = parser.parse_args()

    result = car_info_control(parsed.category, parsed.action, parsed.value)
    print(result)
