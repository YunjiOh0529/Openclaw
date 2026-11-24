---
name: level-2
enabled: true
description: CARLA 시뮬레이션 차량의 날씨 조회/변경, 위치 조회, 간접 명령 처리 스킬
---

# Level 2 정보 제공

CARLA 시뮬레이션 차량에서 실시간 정보를 읽어오거나 날씨를 변경한다.
car_info_control 함수를 호출하여 사용한다.

## 날씨 조회
- "지금 날씨 어때?" → car_info_control(category='weather', action='get')

## 날씨 변경
- "비로 바꿔줘" → car_info_control(category='weather', action='set', value='rain')
- "날씨 맑게 해줘" → car_info_control(category='weather', action='set', value='clear')
- "폭우로 바꿔줘" → car_info_control(category='weather', action='set', value='hardrain')
- "흐리게 해줘" → car_info_control(category='weather', action='set', value='cloudy')
- "밤으로 바꿔줘" → car_info_control(category='weather', action='set', value='night')

## 위치 조회
- "지금 내 차 어디 있어?" → car_info_control(category='location', action='get')
- "현재 위치 알려줘" → car_info_control(category='location', action='get')

## 차량 스폰
- "링컨 차량 스폰해줘" → car_info_control(category='vehicle', action='spawn', value='lincoln')

## 카메라 시점 제어
- "차 앞에서 봐줘" → car_info_control(category='camera', action='front')
- "차 뒤에서 봐줘" → car_info_control(category='camera', action='back')
- "차 옆에서 봐줘" → car_info_control(category='camera', action='side')
- "차 위에서 봐줘" → car_info_control(category='camera', action='top')

## 간접 명령 처리
- "밖이 어두운 것 같은데" → car_info_control(category='light', action='set', value='lowbeam')
- "날씨가 안 좋은 것 같은데" → car_info_control(category='weather', action='get')
- "비가 오는 것 같은데" → car_info_control(category='weather', action='get')