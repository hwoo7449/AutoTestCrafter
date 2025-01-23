# FactoryVoca 매크로

## 설정 파일 (config.json) 설명

### 창 제목
- `window_title`: "FactoryVoca(http://cafe.naver.com/factoryvoca)"
  - 매크로가 제어할 FactoryVoca 제어판 창의 정확한 이름

### UI 위치 설정 (`ui_positions`)

#### Day 리스트 영역 (`day_list`)
- `first_day`: Day 리스트의 첫 번째 항목(Day01)의 위치
  - 이 위치를 클릭한 후 Home키와 화살표키로 원하는 Day로 이동

#### 선택된 Day 영역 (`selected_day`)
- `position`: 오른쪽에 추가된 Day 항목이 표시되는 영역의 위치

#### 버튼 위치 (`buttons`)
- `add_day`: Day 추가 버튼(▶) 위치
- `remove_day`: Day 삭제 버튼(◀) 위치
- `load_day`: 불러오기 버튼 위치
- `apply`: 적용 버튼 위치
- `random_apply`: 무작위계속적용 버튼 위치
- `print`: 출력 버튼 위치

#### 입력 필드 (`inputs`)
- `word_count`: 출제 단어 수를 입력하는 텍스트 필드 위치
- `eng_to_kor`: 영->한 비율을 입력하는 필드 위치

#### 체크박스 (`checkboxes`)
- `show_first_letter`: "첫글자만 보여주기" 체크박스 위치

## 좌표 측정 방법
1. 디버그 모드에서 F2 키를 눌러 마우스 커서 위치 측정
2. 측정된 상대 좌표를 config.json의 해당 위치에 입력
3. 좌표는 [x, y] 형식의 배열로 입력

## 주의사항
- 모든 좌표는 FactoryVoca 창의 왼쪽 위 모서리를 기준으로 한 상대 좌표입니다
- 창 크기가 변경되면 좌표값도 다시 측정해야 할 수 있습니다
- 좌표 측정 시 마우스 커서의 끝부분(화살표 끝)이 기준점입니다 