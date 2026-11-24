name: carla-vehicle-spawner
enabled: true
description: CARLA 시뮬레이션 환경에 Lincoln MKZ 2020 차량을 스폰(생성)하고, 관전자 카메라를 차량 뒤쪽 3인칭 시점으로 설정하는 스킬입니다. CARLA 환경에 실험용 차량을 추가해야 할 때 사용하세요.

CARLA 차량 스폰 스킬

이 스킬은 CARLA 시뮬레이션 환경에 Lincoln MKZ 2020 차량(vehicle.lincoln.mkz_2020)을 스폰하고, 관전자(spectator) 카메라를 차량 뒤쪽 위에서 내려다보는 3인칭 추격 시점으로 자동 설정합니다. 스폰 전 기존에 남아있는 동일 차종 액터는 자동으로 정리(제거)됩니다.

스킬 실행 전에 CARLA 시뮬레이터가 --host와 --port에 지정된 주소로 실행 중인지 확인해야 합니다.

사용법
scripts/spawn_vehicle.py 스크립트를 exec 도구를 사용하여 실행합니다.

인자
--host <IP>: CARLA 서버의 IP 주소 (기본값: 환경변수 CARLA_HOST 또는 127.0.0.1)
--port <PORT>: CARLA 서버의 포트 번호 (기본값: 환경변수 CARLA_PORT 또는 2000)
--spawn-index <INDEX>: 사용할 스폰 포인트의 인덱스 (선택, 생략 시 사용 가능한 스폰 포인트 중 무작위로 시도)

참고
- 차량 모델은 Lincoln MKZ 2020으로 고정되어 있으며, 다른 차량 모델은 스폰할 수 없습니다.
- 맵 변경 기능은 지원하지 않습니다. 스폰 전에 원하는 맵이 이미 CARLA에 로드되어 있어야 합니다.
- 지정한 스폰 포인트가 점유된 경우, 다른 포인트로 자동 재시도합니다.

예시
기본 설정(127.0.0.1:2000)으로 Lincoln MKZ 2020 차량을 스폰합니다:
Copy
python scripts/spawn_vehicle.py

특정 CARLA 서버 주소와 스폰 포인트를 지정하여 실행합니다:
Copy
python scripts/spawn_vehicle.py --host 210.125.91.141 --port 2000 --spawn-index 5