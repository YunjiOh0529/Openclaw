---
name: level-1
enabled: true
description: CARLA 시뮬레이션 환경 내에서 차량의 주행, 문/라이트, 날씨, 상태 진단을 제어하는 통합 비서 스킬
---

# Level 1 Car Master Control

CARLA 시뮬레이션 차량을 제어한다. car_master_control 함수를 호출하여 사용한다.

## 문 열기
- "운전석 문 열어줘" → car_master_control(category='ext', action='door', value='fl')
- "조수석 문 열어줘" → car_master_control(category='ext', action='door', value='fr')
- "뒷좌석 왼쪽 문 열어줘" → car_master_control(category='ext', action='door', value='rl')
- "뒷좌석 오른쪽 문 열어줘" → car_master_control(category='ext', action='door', value='rr')
- "모든 문 열어줘" → car_master_control(category='ext', action='door', value='all')

## 문 닫기
- "운전석 문 닫아줘" → car_master_control(category='ext', action='close_door', value='fl')
- "모든 문 닫아줘" → car_master_control(category='ext', action='close_door', value='all')

## 라이트 제어
- "헤드라이트 켜줘" → car_master_control(category='ext', action='light', value='lowbeam')
- "상향등 켜줘" → car_master_control(category='ext', action='light', value='highbeam')
- "비상등 켜줘" → car_master_control(category='ext', action='light', value='hazard')
- "좌측 깜빡이 켜줘" → car_master_control(category='ext', action='light', value='leftblinker')
- "우측 깜빡이 켜줘" → car_master_control(category='ext', action='light', value='rightblinker')
- "안개등 켜줘" → car_master_control(category='ext', action='light', value='fog')
- "라이트 꺼줘" → car_master_control(category='ext', action='light', value='off')

## 날씨 변경
- "비 내리게 해줘" → car_master_control(category='weather', action='set', value='rain')
- "날씨 맑게 해줘" → car_master_control(category='weather', action='set', value='clear')
- "폭우로 바꿔줘" → car_master_control(category='weather', action='set', value='hardrain')
- "흐리게 해줘" → car_master_control(category='weather', action='set', value='cloudy')

## 창문
- 창문 개폐는 CARLA 미지원 기능이므로 "창문은 CARLA에서 지원하지 않습니다"라고 응답한다.

## 차량 상태 확인
- "차량 상태 알려줘" → car_master_control(category='status', action='check')
- "타이어 공기압 확인해줘" → car_master_control(category='status', action='check')
- "현재 속도 알려줘" → car_master_control(category='status', action='check')

## 에어컨/미디어
- CARLA 미지원 기능이므로 텍스트로만 응답한다.
- "에어컨 22도로 설정해줘" → car_master_control(category='hmi', action='climate', value='22')
- "음악 틀어줘" → car_master_control(category='hmi', action='media', value='50')
