import tkinter as tk
from tkinter import ttk, scrolledtext
import tkinter.messagebox as messagebox
import pygetwindow as gw
from datetime import datetime
from enum import Enum, auto
import pyautogui, json, time, os, shutil, re, pyperclip

class WordbookType(Enum):
    ORIGINAL = "원래 순서"
    RANDOM = "랜덤"
    ENG_KOR_RANDOM = "영한랜덤"
    
    @classmethod
    def get_values(cls):
        return [type.value for type in cls]
    
    @classmethod
    def from_string(cls, value):
        for type in cls:
            if type.value == value:
                return type
        raise ValueError(f"Invalid type value: {value}")

# 기존의 WordbookType Enum 아래에 추가
class ProgramState(Enum):
    IDLE = auto()      # 초기 상태 또는 중단 후
    RUNNING = auto()   # 실행 중
    PAUSED = auto()    # 일시정지

# 컨트롤러 클래스
class Controller:
    def __init__(self, root: tk.Tk):
        self.state = ProgramState.IDLE
        
        # 자식 컴포넌트 초기화
        self.debug_window = DebugWindow(self) if Config.is_debug_mode() else None            
        self.view = AppUI(root, self)
        self.macro = MacroController(self)
        
        print("Controller initialized.")
        
        appdata_path = os.getenv('APPDATA')
        
        # 컨트롤러에서 관리할 데이터나 기능 초기화
        self.directories = {
            "Work": "/work",
            "Output": "/output",
            "Answer": os.path.join(appdata_path, 'FactoryVoca Pro', '정답')
        }
                
        self.initialize_directories()
        self.delete_work_contents()
        self.delete_answer_sheet_contents()

    def initialize_directories(self):
        """폴더가 없으면 생성하는 메서드"""
        for dir_name, dir_path in self.directories.items():
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                self.log(f"{dir_name} 폴더가 생성되었습니다: {dir_path}")
            else:
                self.log(f"{dir_name} 폴더가 이미 존재합니다: {dir_path}")
                
    def delete_work_contents(self):
        """작업 폴더 내의 모든 내용물을 삭제 (폴더는 유지)"""
        if not os.path.exists(self.directories['Work']):
            self.log(f"작업 폴더가 존재하지 않습니다: {self.directories['Work']}")
            return
        
        # 폴더 내 파일 및 하위 폴더 목록 가져오기
        items = os.listdir(self.directories['Work'])
        if not items:
            self.log("작업 폴더가 이미 비어 있습니다.")
            return
        
        # 사용자에게 삭제 확인
        confirm = messagebox.askyesno("경고", "작업 폴더 내 모든 내용물을 삭제하시겠습니까?")
        if not confirm:
            self.log("삭제가 취소되었습니다.")
            return
        
        # 파일 및 폴더 삭제
        for item_name in items:
            item_path = os.path.join(self.directories['Work'], item_name)
            try:
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.remove(item_path)  # 파일 또는 심볼릭 링크 삭제
                    self.log(f"파일 삭제: {item_path}")
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)  # 하위 폴더 및 파일 모두 삭제
                    self.log(f"폴더 삭제: {item_path}")
            except Exception as e:
                self.log(f"삭제 중 오류 발생: {item_path} - {str(e)}")
        
        self.log("작업 폴더 내 모든 내용물이 삭제되었습니다.")
        messagebox.showinfo("완료", "작업 폴더 내 모든 내용물이 삭제되었습니다.")
                
    def delete_answer_sheet_contents(self):
        """정답지 폴더 내의 모든 내용물을 삭제 (폴더는 유지)"""
        if not os.path.exists(self.directories['Answer']):
            self.log(f"정답지 폴더가 존재하지 않습니다: {self.directories['Answer']}")
            return
        
        # 폴더 내 파일 및 하위 폴더 목록 가져오기
        items = os.listdir(self.directories['Answer'])
        if not items:
            self.log("정답지 폴더가 이미 비어 있습니다.")
            return
        
        # 사용자에게 삭제 확인
        confirm = messagebox.askyesno("경고", "정답지 폴더 내 모든 내용물을 삭제하시겠습니까?")
        if not confirm:
            self.log("삭제가 취소되었습니다.")
            return
        
        # 파일 및 폴더 삭제
        for item_name in items:
            item_path = os.path.join(self.directories['Answer'], item_name)
            try:
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.remove(item_path)  # 파일 또는 심볼릭 링크 삭제
                    self.log(f"파일 삭제: {item_path}")
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)  # 하위 폴더 및 파일 모두 삭제
                    self.log(f"폴더 삭제: {item_path}")
            except Exception as e:
                self.log(f"삭제 중 오류 발생: {item_path} - {str(e)}")
        
        self.log("정답지 폴더 내 모든 내용물이 삭제되었습니다.")
        messagebox.showinfo("완료", "정답지 폴더 내 모든 내용물이 삭제되었습니다.")            

    def log(self, message: str):
        """로그 메시지를 출력"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{current_time}] {message}"
        print(log_message)  # 항상 콘솔에 출력
        if self.debug_window:  # 디버그 모드일 경우 디버그 콘솔에도 출력
            self.debug_window.log(message)

    # def process_action(self):
    #     if not self.view.validate_inputs():
    #         return
            
    #     input_values = self.view.get_input_values()
        
    #     # Enum을 사용한 타입 비교
    #     if input_values['type'] == WordbookType.ORIGINAL:
    #         # 원래 순서로 처리
    #         pass
    #     elif input_values['type'] == WordbookType.RANDOM:
    #         # 랜덤으로 처리
    #         pass
    #     elif input_values['type'] == WordbookType.ENG_KOR_RANDOM:
    #         # 영한랜덤으로 처리
    #         pass

    def set_state(self, new_state: ProgramState):
        """상태 변경 및 UI 업데이트"""
        self.state = new_state
        self.update_ui_for_state()

    def update_ui_for_state(self):
        """현재 상태에 따라 UI 업데이트"""
        if not self.view:
            return
            
        if self.state == ProgramState.IDLE:
            self.view.buttons['start'].configure(state='normal')
            self.view.buttons['pause'].configure(state='disabled')
            self.view.buttons['stop'].configure(state='disabled')
            
        elif self.state == ProgramState.RUNNING:
            self.view.buttons['start'].configure(state='disabled')
            self.view.buttons['pause'].configure(state='normal')
            self.view.buttons['stop'].configure(state='normal')
            
        elif self.state == ProgramState.PAUSED:
            self.view.buttons['start'].configure(state='normal')
            self.view.buttons['pause'].configure(state='disabled')
            self.view.buttons['stop'].configure(state='normal')

        # 상태 레이블 업데이트
        status_texts = {
            ProgramState.IDLE: "상태: 대기 중",
            ProgramState.RUNNING: "상태: 실행 중",
            ProgramState.PAUSED: "상태: 일시정지"
        }
        self.view.status_label.configure(text=status_texts[self.state])

# UI 클래스
class AppUI:
    def __init__(self, root: tk.Tk, controller: Controller):
        self.root = root
        self.controller = controller

        self.root.title("AutoTestCrafter")  # 창 제목
        self.root.geometry("400x500")    # 창 크기 설정 (너비 x 높이)

        # UI 요소 구성
        self.create_widgets()
        
    def log(self, message):
        """컨트롤러의 로그 기능 사용"""
        self.controller.log(message)

    def create_widgets(self):
        # Label (레이블: 텍스트 표시)
        self.label = tk.Label(self.root, text="단어장 제작 자동화 프로그램")
        self.label.pack(pady=20)  # 위아래 여백
        
        # Frame을 사용하여 입력 필드들을 구조화
        self.input_frame = ttk.LabelFrame(self.root, text="단어장 설정")
        self.input_frame.pack(pady=10, padx=20, fill="x")

        # 입력 필드들을 담을 딕셔너리 생성
        self.inputs = {}
        
        # 단어장 이름 입력
        name_frame = ttk.Frame(self.input_frame)
        name_frame.pack(fill="x", pady=5)
        ttk.Label(name_frame, text="단어장 이름:").pack(side="left")
        self.inputs['name'] = ttk.Entry(name_frame)
        self.inputs['name'].pack(side="left", padx=5, fill="x", expand=True)
        
        # 유형 선택 콤보박스
        type_frame = ttk.Frame(self.input_frame)
        type_frame.pack(fill="x", pady=5)
        ttk.Label(type_frame, text="출제 유형:").pack(side="left")
        self.inputs['type'] = ttk.Combobox(type_frame, 
            values=WordbookType.get_values(),
            state="readonly")
        self.inputs['type'].set(WordbookType.ORIGINAL.value)  # 기본값 설정
        self.inputs['type'].pack(side="left", padx=5, fill="x", expand=True)
        
        # 콤보박스 선택 변경 이벤트 핸들러 수정
        def on_type_changed(event):
            selected_type = WordbookType.from_string(self.inputs['type'].get())
            if selected_type == WordbookType.ORIGINAL:
                self.inputs['version'].configure(state="readonly")
                self.inputs['version'].delete(0, tk.END)
            else:
                self.inputs['version'].configure(state="normal")
        
        self.inputs['type'].bind('<<ComboboxSelected>>', on_type_changed)
        
        # 버전 입력 (숫자만)
        version_frame = ttk.Frame(self.input_frame)
        version_frame.pack(fill="x", pady=5)
        ttk.Label(version_frame, text="버전:").pack(side="left")
        self.inputs['version'] = ttk.Entry(version_frame)
        self.inputs['version'].pack(side="left", padx=5, fill="x", expand=True)
        
        # 초기 상태 설정 (기본값이 "원래 순서"이므로 버전 입력 비활성화)
        self.inputs['version'].configure(state="readonly")

        # 숫자만 입력 가능하도록 검증 함수 추가
        def validate_number(P):
            if P == "": return True
            return P.isdigit()
        vcmd = (self.root.register(validate_number), '%P')
        self.inputs['version'].configure(validate="key", validatecommand=vcmd)

        # Day 범위 입력 (숫자만)
        day_frame = ttk.Frame(self.input_frame)
        day_frame.pack(fill="x", pady=5)
        ttk.Label(day_frame, text="범위: Day").pack(side="left")
        
        # 시작 Day 입력
        self.inputs['day_start'] = ttk.Entry(day_frame, width=5)
        self.inputs['day_start'].pack(side="left", padx=2)
        self.inputs['day_start'].insert(0, "1")  # 기본값 1 설정
        
        ttk.Label(day_frame, text="~").pack(side="left", padx=2)
        
        ttk.Label(day_frame, text="Day").pack(side="left")
        
        # 끝 Day 입력
        self.inputs['day_end'] = ttk.Entry(day_frame, width=5)
        self.inputs['day_end'].pack(side="left", padx=2)
        
        # Day 입력 필드들에 숫자 검증 적용
        self.inputs['day_start'].configure(validate="key", validatecommand=vcmd)
        self.inputs['day_end'].configure(validate="key", validatecommand=vcmd)

        # 수동 체크리스트 프레임
        self.checklist_frame = ttk.LabelFrame(self.root, text="확인사항")
        self.checklist_frame.pack(pady=10, padx=20, fill="x")

        # 체크박스들을 저장할 딕셔너리
        self.checkboxes = {}
        
        # 체크리스트 항목들
        checklist_items = [
            "첫페이지 제목(ex. 랜덤ver1) 설정하기",
            "기본 프린터 PDF로 설정하기",
            "추가기능 -> 날짜 설정에서 빈칸으로 설정하기",
            "엑셀 인쇄 페이지 크기 맞추기",
            "단어장 검색해서 설정하기",
            "'첫단어에 유닛이름 표시' 해제하기"
        ]
        
        # 체크박스 변수들을 저장할 딕셔너리
        self.checkbox_vars = {}
        
        # 체크박스 생성
        for item in checklist_items:
            # 각 체크박스의 상태를 저장할 변수
            self.checkbox_vars[item] = tk.BooleanVar()
            
            # 체크박스 생성
            checkbox = ttk.Checkbutton(
                self.checklist_frame,
                text=item,
                variable=self.checkbox_vars[item],
                onvalue=True,
                offvalue=False
            )
            checkbox.pack(anchor="w", padx=10, pady=2)
            self.checkboxes[item] = checkbox

        

        # 버튼 프레임
        self.button_frame = ttk.LabelFrame(self.root, text="제어")
        self.button_frame.pack(pady=10, padx=20, fill="x")

        # 버튼들을 담을 딕셔너리
        self.buttons = {}
        
        # 버튼 생성
        button_configs = [
            {
                'name': 'start',
                'text': '시작',
                'command': self.on_start_click,
                'width': 10
            },
            {
                'name': 'pause',
                'text': '일시정지',
                'command': self.on_pause_click,
                'width': 10
            },
            {
                'name': 'stop',
                'text': '중단',
                'command': self.on_stop_click,
                'width': 10
            },
            {
                'name': 'exit',
                'text': '종료',
                'command': self.root.quit,
                'width': 10
            }
        ]
        
        # 버튼 프레임 내부에 버튼들을 담을 하위 프레임
        button_container = ttk.Frame(self.button_frame)
        button_container.pack(pady=5, padx=5)
        
        # 버튼 생성 및 배치
        for config in button_configs:
            btn = ttk.Button(
                button_container,
                text=config['text'],
                command=config['command'],
                width=config['width']
            )
            btn.pack(side='left', padx=5)
            self.buttons[config['name']] = btn
        
        # 초기 버튼 상태 설정
        self.buttons['pause'].configure(state='disabled')
        self.buttons['stop'].configure(state='disabled')

        # 상태 표시 레이블
        self.status_label = ttk.Label(self.root, text="상태: 대기 중")
        self.status_label.pack(pady=5)

    def get_input_values(self):
        """순수 입력값만 반환"""
        values = {
            'name': self.inputs['name'].get().strip(),
            'type': WordbookType.from_string(self.inputs['type'].get()),
            'version': self.inputs['version'].get().strip() if WordbookType.from_string(self.inputs['type'].get()) != WordbookType.ORIGINAL else None,
            'day_start': self.inputs['day_start'].get().strip(),
            'day_end': self.inputs['day_end'].get().strip()
        }
        return values

    def validate_inputs(self):
        """검증 로직"""
        values = self.get_input_values()
        
        if not values['name']:
            messagebox.showerror("오류", "단어장 이름을 입력해주세요.")
            return False
        
        if values['type'] != WordbookType.ORIGINAL and not values['version']:
            messagebox.showerror("오류", "버전을 입력해주세요.")
            return False
        
        # Day 범위 검증
        if not values['day_start'] or not values['day_end']:
            messagebox.showerror("오류", "Day 범위를 모두 입력해주세요.")
            return False
        
        try:
            day_start = int(values['day_start'])
            day_end = int(values['day_end'])
            
            if day_start < 1:
                messagebox.showerror("오류", "시작 Day는 1 이상이어야 합니다.")
                return False
            
            if day_end < day_start:
                messagebox.showerror("오류", "종료 Day는 시작 Day보다 크거나 같아야 합니다.")
                return False
            
        except ValueError:
            messagebox.showerror("오류", "Day 범위에는 숫자만 입력 가능합니다.")
            return False
        
        return True

    # def get_checklist_status(self):
    #         """체크리스트 상태를 딕셔너리로 반환"""
    #         return {item: var.get() for item, var in self.checkbox_vars.items()}
    def disable_inputs(self):
        """입력 필드와 콤보박스를 비활성화"""
        for input_field in self.inputs.values():
            input_field.configure(state="disabled")
        self.inputs['type'].configure(state="disabled")  # 콤보박스도 비활성화
        
    def enable_inputs(self):
        """입력 필드와 콤보박스를 활성화"""
        for input_field in self.inputs.values():
            input_field.configure(state="normal")
        
        # 콤보박스는 다시 readonly로 설정
        self.inputs['type'].configure(state="readonly")
        
        # type이 "원래 순서"인 경우 버전 입력 필드 비활성화
        selected_type = WordbookType.from_string(self.inputs['type'].get())
        if selected_type == WordbookType.ORIGINAL:
            self.inputs['version'].configure(state="disabled")
        else:
            self.inputs['version'].configure(state="normal")
    

    def validate_checklist(self):
        """모든 항목이 체크되었는지 확인"""
        unchecked = [item for item, var in self.checkbox_vars.items() if not var.get()]
        if unchecked:
            messagebox.showwarning(
                "미완료 항목",
                "다음 항목들이 체크되지 않았습니다:\n\n" + "\n".join(f"- {item}" for item in unchecked)
            )
            return False
        return True

    def get_validated_values(self):
        """편의 메서드: 검증된 값 반환"""
        if not self.validate_inputs():
            return None
        return self.get_input_values()
    

    def on_start_click(self):
        """시작 버튼 클릭 시 실행될 메서드"""
        
        # 데이터 값 검증
        if not self.validate_inputs():
            return
        
        # 확인사항 검증
        if not self.validate_checklist():
            return
        
        # 입력 필드 비활성화
        self.disable_inputs()
        
        # 상태 변경
        self.controller.set_state(ProgramState.RUNNING)
        
        # 매크로 시작
        self.controller.macro.start_macro()
        self.log("작업 시작")

    def on_pause_click(self):
        """일시정지 버튼 클릭 시 실행될 메서드"""
        self.controller.set_state(ProgramState.PAUSED)
        # TODO: 실제 일시정지 로직 구현
        self.log("작업 일시정지")


    def on_stop_click(self):
        """중단 버튼 클릭 시 실행될 메서드"""
        self.controller.set_state(ProgramState.IDLE)
        # 입력 필드 활성화
        self.enable_inputs()
        
        # TODO: 실제 중단 로직 구현
        self.log("작업 중단")

class PDFManager:
    def __init__(self, controller: Controller):
        self.controller = controller

# 매크로 클래스
class DebugWindow:
    def __init__(self, controller: Controller):
        self.controller = controller
        
        self.window = tk.Toplevel()
        self.window.title("Debug Console")
        self.window.geometry("600x400")
        
        # 키보드 이벤트 바인딩
        self.window.bind('<F2>', self._get_mouse_position)
        
        # 로그 출력을 위한 텍스트 영역
        self.log_area = scrolledtext.ScrolledText(self.window, wrap=tk.WORD, height=15)
        self.log_area.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        # 테스트 버튼들을 위한 프레임
        self.button_frame = ttk.LabelFrame(self.window, text="디버그 도구")
        self.button_frame.pack(padx=10, pady=5, fill=tk.X)
        
        # 창 제목 입력 필드 추가
        self.window_title_frame = ttk.Frame(self.button_frame)
        self.window_title_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(self.window_title_frame, text="창 제목:").pack(side="left", padx=5)
        self.window_title_entry = ttk.Entry(self.window_title_frame)
        self.window_title_entry.pack(side="left", padx=5, fill="x", expand=True)
        self.window_title_entry.insert(0, "FactoryVoca(")  # 기본값 설정
        
        # 테스트 버튼들
        ttk.Button(self.button_frame, text="창 감지 테스트", 
                  command=self.test_window_detection).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(self.button_frame, text="좌표 측정 (F2)", 
                  command=self.measure_position).pack(side=tk.LEFT, padx=5, pady=5)
        
        # 위치 테스트 프레임
        test_frame = ttk.LabelFrame(self.window, text="위치 테스트")
        test_frame.pack(padx=10, pady=5, fill=tk.X)
        
        # 위치 테스트 버튼들
        ttk.Button(test_frame, text="전체 위치 순차 이동", 
                  command=lambda: self.test_all_positions(move_only=True)).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(test_frame, text="전체 위치 순차 클릭", 
                  command=lambda: self.test_all_positions(move_only=False)).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(test_frame, text="개별 위치 테스트", 
                  command=self.show_position_test_window).pack(side=tk.LEFT, padx=5, pady=5)
        
        # 모든 창 개수 감지 버튼 추가
        ttk.Button(self.button_frame, text="모든 창 개수 감지", 
                  command=self.detect_all_windows).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(self.button_frame, text="로그 지우기", 
                  command=self.clear_log).pack(side=tk.RIGHT, padx=5, pady=5)
        
        self.log("디버그 모드가 활성화되었습니다.")
        
    def detect_all_windows(self):
        """모든 창의 개수를 감지하여 로그에 출력"""
        try:
            windows = pyautogui.getAllWindows()
            self.log(f"현재 열려 있는 모든 창의 개수: {len(windows)}")
            # for i, window in enumerate(windows):
            #     self.log(f"창 {i + 1}: {window.title}")
        except Exception as e:
            self.log(f"창 개수 감지 중 오류 발생: {str(e)}")
        
    def get_window_title(self):
        """입력된 창 제목을 반환 (기본값: FactoryVoca()"""
        return self.window_title_entry.get().strip() or "FactoryVoca("

    def show_position_test_window(self):
        """개별 위치 테스트 창 표시"""
        test_window = tk.Toplevel(self.window)
        test_window.title("개별 위치 테스트")
        test_window.geometry("300x400")
        
        # 모든 위치 정보 가져오기
        positions = self._get_all_positions()
        
        # 스크롤 가능한 프레임 생성
        canvas = tk.Canvas(test_window)
        scrollbar = ttk.Scrollbar(test_window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 각 위치에 대한 테스트 버튼 생성
        for pos_name in positions:
            frame = ttk.Frame(scrollable_frame)
            frame.pack(fill="x", padx=5, pady=2)
            
            ttk.Label(frame, text=pos_name).pack(side="left", padx=5)
            ttk.Button(frame, text="이동", 
                      command=lambda n=pos_name: self.test_single_position(n, True)).pack(side="right", padx=2)
            ttk.Button(frame, text="클릭", 
                      command=lambda n=pos_name: self.test_single_position(n, False)).pack(side="right", padx=2)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _get_all_positions(self):
        """config에서 모든 위치 정보 가져오기"""
        return Config.get_all_positions()

    def test_single_position(self, position_key, move_only=True):
        """단일 위치 테스트"""
        self.log(f"테스트 위치: {position_key}")
        
        try:
            # 창 찾기
            windows = pyautogui.getWindowsWithTitle("FactoryVoca")
            target_window = None
            for window in windows:
                if Config.get_window_title() == window.title:
                    target_window = window
                    break

            if not target_window:
                self.log("창을 찾을 수 없습니다.")
                return
                
            # 좌표 가져오기
            coords = Config.get_position(position_key)
            if not coords:
                self.log(f"좌표를 찾을 수 없습니다: {position_key}")
                return
            
            abs_x = target_window.left + coords[0]
            abs_y = target_window.top + coords[1]
            
            if move_only:
                pyautogui.moveTo(abs_x, abs_y)
                self.log(f"이동 완료: {position_key} ({coords[0]}, {coords[1]})")
            else:
                pyautogui.click(abs_x, abs_y)
                self.log(f"클릭 완료: {position_key} ({coords[0]}, {coords[1]})")
                
        except Exception as e:
            self.log(f"테스트 중 오류 발생: {str(e)}")

    def test_all_positions(self, move_only=True):
        """모든 위치 순차 테스트"""
        positions = self._get_all_positions()
        
        self.log("전체 위치 테스트 시작...")
        
        def test_next_position(index):
            if index < len(positions):
                position_key = positions[index]
                self.test_single_position(position_key, move_only)
                self.window.after(1000, test_next_position, index + 1)
            else:
                self.log("전체 위치 테스트 완료")
        
        test_next_position(0)

    def log(self, message):
        """로그 메시지를 콘솔과 디버그 콘솔에 출력"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{current_time}] {message}"
        self.log_area.insert(tk.END, f"{log_message}\n")
        self.log_area.see(tk.END) # 자동 스크롤

    def clear_log(self):
        """로그 지우기"""
        self.log_area.delete(1.0, tk.END)

    def test_window_detection(self):
        """창 감지 테스트"""
        self.log("창 감지 테스트 시작...")
        try:
            window_title = self.get_window_title()
            windows = pyautogui.getWindowsWithTitle(window_title)
            self.log(f"'{window_title}' 관련 창 개수: {len(windows)}")
            for window in windows:
                self.log(f"찾은 창: {window.title}")
                self.log(f"위치: ({window.left}, {window.top})")
                self.log(f"크기: {window.width} x {window.height}")
                self.log("---")
        except Exception as e:
            self.log(f"오류 발생: {str(e)}")

    def measure_position(self):
        """좌표 측정 시작"""
        self.log("F2 키를 눌러 현재 마우스 위치를 측정합니다...")
        self.window.focus_force()  # 디버그 창에 포커스 주기

    def _get_mouse_position(self, event=None):
        """현재 마우스 위치 측정"""
        try:
            # 현재 마우스 위치 가져오기
            x, y = pyautogui.position()
            
            # 입력된 창 제목으로 창 찾기
            window_title = self.get_window_title()
            windows = pyautogui.getWindowsWithTitle(window_title)
            
            if not windows:
                self.log(f"'{window_title}' 제목의 창을 찾을 수 없습니다.")
                return
            
            # 첫 번째 창만 취급
            target_window = windows[0]
            
            # 상대 좌표 계산
            rel_x = x - target_window.left
            rel_y = y - target_window.top
            
            self.log("---")
            self.log(f"창 정보:")
            self.log(f"- 창 위치: ({target_window.left}, {target_window.top})")
            self.log(f"- 창 크기: {target_window.width} x {target_window.height}")
            self.log(f"- 창 제목: {target_window.title}")
            
            self.log(f"절대 좌표: ({x}, {y})")
            self.log(f"창 기준 상대 좌표: ({rel_x}, {rel_y})")
            
        except Exception as e:
            self.log(f"오류 발생: {str(e)}")

class MacroController:
    def __init__(self, controller: Controller):
        self.controller = controller
        
        self.auto_answer_save = False
        self.print_output_path_set = False

    def log(self, message):
        """컨트롤러의 로그 기능 사용"""
        self.controller.log(message)
        
    def debug_log(self, message):
        """디버그 로그 출력"""
        if Config.is_debug_mode():
            self.log(message)

    def start_macro(self):
        """매크로 시작"""
        self.debug_log("매크로 시작")
        
        self.input_values = self.controller.view.get_input_values()
        if self.input_values is None:
            self.log("입력 값이 유효하지 않습니다. 매크로를 중단합니다.")
            return
        try:
            day_start = int(self.input_values['day_start'])
            day_end = int(self.input_values['day_end'])
        except ValueError:
            messagebox.showerror("치명적인 오류", "Day 범위에는 숫자만 입력 가능합니다.")
            self.stop_macro(f"Day 범위에는 숫자만 입력 가능합니다.")
            return
        


        
        for day in range(day_start, day_end + 1):
            self.current_day = day
            
            if self.input_values['type'] == WordbookType.ORIGINAL:
                self.click_selected_day()
                
                self.remove_selected_day()
                
                # 단어 선택
                if not self.select_day(day):
                    self.stop_macro(f"Day {day} 선택 실패")
                    return
                
                self.add_selected_day()
                
                self.load_day()
                
                pyautogui.sleep(3)
                
                self.print_wordbook()
                
            
    def stop_macro(self, e = None):
        """매크로 중단 (에러 등)"""
        self.log("매크로 중단")
        if e:
            self.log("원인: " + str(e))
        self.controller.view.on_stop_click()
        pass
    
    def find_and_activate_window(self, title: str, title_key: str = "window_title"):
        """정확한 창 제목으로 창을 찾아서 활성화"""
        try:
            start_time = time.time()
            windows = pyautogui.getWindowsWithTitle(title)
            
            for window in windows:
                if window.title == Config.get_value(title_key):
                    window.activate()
                    end_time = time.time()
                    self.debug_log(f"{window.title} 창 찾기 소요 시간: {end_time - start_time}초")
                    pyautogui.sleep(0.1)  # 활성화 대기
                    return window
        except Exception as e:
            messagebox.showerror("오류", f"창을 찾는 중 오류가 발생했습니다: {str(e)}")
            return None

        
    def click_position(self, position_key, title = "Factoryvoca", title_key = "window_title"):
        """설정된 위치 클릭"""
        try:
            # 창 찾고 활성화
            window = self.find_and_activate_window(title, title_key)
            if not window:
                return False
                
            # position_key에 해당하는 좌표 찾기 (예: 'buttons.add_day')
            coords = self.get_position_from_config(position_key)
            if not coords:
                self.log(f"좌표를 찾을 수 없습니다: {position_key}")
                return False
                
            # 상대 좌표를 절대 좌표로 변환
            abs_x = window.left + coords[0]
            abs_y = window.top + coords[1]
            
            # 클릭
            pyautogui.click(abs_x, abs_y)
            pyautogui.sleep(Config.get_delay('click'))  # 약간의 딜레이
            return True
            
        except Exception as e:
            self.log(f"클릭 중 오류 발생: {str(e)}")
            return False

    def get_position_from_config(self, position_key):
        """config에서 위치 정보 가져오기"""
        try:
            # 키를 점(.)으로 분리하여 딕셔너리 탐색
            keys = position_key.split('.')
            value = Config._config['ui_positions']
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return None

    def select_day(self, day_number: int):
        """특정 Day 선택 (PageDown 및 PageUp 활용)"""
        try:
            # Day 리스트 첫 위치 클릭
            if not self.click_position('day_list.first_day'):
                return False
                
            # Home 키로 맨 위로 이동
            pyautogui.press('home')
            pyautogui.sleep(0.1)
            
            # PageDown 한 번에 이동하는 Day 수
            page_size = Config.get_value('page_down_size')  # 예: 16
        
            # 전체 페이지 수 계산
            total_pages = (day_number - 1) // page_size
            
            # 현재 페이지의 중간 지점 계산
            mid_point = page_size // 2
            
            # 현재 페이지에서의 위치 계산
            current_position = (day_number - 1) % page_size

            if current_position > mid_point:
                # Page Down을 사용하여 다음 페이지로 이동
                for _ in range(total_pages + 1):
                    pyautogui.press('pagedown')
                    pyautogui.sleep(pyautogui.sleep(Config.get_delay('page_down')))
                
                # 남은 Day는 위 화살표로 이동
                remaining_days = page_size - current_position
                for _ in range(remaining_days):
                    pyautogui.press('up')
                    pyautogui.sleep(Config.get_delay('arrow_key'))
            else:
                # Page Down을 사용하여 대략적인 위치로 이동
                for _ in range(total_pages):
                    pyautogui.press('pagedown')
                    pyautogui.sleep(pyautogui.sleep(Config.get_delay('page_down')))
                
                # 남은 Day는 아래 화살표로 이동
                for _ in range(current_position):
                    pyautogui.press('down')
                    pyautogui.sleep(Config.get_delay('arrow_key'))

            return True
            
        except Exception as e:
            self.log(f"Day 선택 중 오류 발생: {str(e)}")
            return False

    def set_word_count(self, count):
        """출제 단어 수 설정"""
        try:
            if not self.click_position('inputs.word_count'):
                return False
            
            pyautogui.write(str(count))
            return True
            
        except Exception as e:
            self.log(f"단어 수 설정 중 오류 발생: {str(e)}")
            return False

    def set_eng_to_kor(self, value):
        """영한 비율 설정"""
        try:
            if not self.click_position('inputs.eng_to_kor'):
                return False
            
            pyautogui.write(str(value))
            return True
            
        except Exception as e:
            self.log(f"영한 비율 설정 중 오류 발생: {str(e)}")
            return False
        
    def toggle_auto_answer_save(self):
        """자동 저장 토글"""
        self.auto_answer_save = not self.auto_answer_save
        self.debug_log("자동 저장 토글")
        return self.click_position('checkboxes.auto_answer_save')

    def toggle_first_letter(self):
        """첫글자 보여주기 토글"""
        return self.click_position('checkboxes.show_first_letter')

    def add_selected_day(self):
        """Day 추가"""
        return self.click_position('buttons.add_day')

    def remove_selected_day(self):
        """Day 제거"""
        return self.click_position('buttons.remove_day')

    def load_day(self):
        """Day 불러오기"""
        if not self.click_position('buttons.load_day'):
            return False
        pyautogui.sleep(Config.get_delay('load_day'))  # Day 불러오기 딜레이
        return True

    def apply_settings(self):
        """설정 적용"""
        return self.click_position('buttons.apply')

    def apply_random_settings(self):
        """무작위 설정 적용"""
        return self.click_position('buttons.random_apply')
    
    def click_selected_day(self):
        """선택된 Day 클릭"""
        return self.click_position('selected_day.position')

    def print_wordbook(self):
        """단어장 출력"""
        if not self.auto_answer_save:
            self.toggle_auto_answer_save()
        
        start_window_count = len(pyautogui.getAllWindows())
        self.debug_log(f"출력 전 창 개수: {start_window_count}")
        
        if not self.click_position('buttons.print'): # 출력 버튼 누르기
            return False
        
        
        
        pyautogui.sleep(Config.get_delay('print_btn'))  # 단어장 출력버튼 딜레이
        
        if not self.print_output_path_set:
            self.set_print_output_path()
        
        self.debug_log(f"출력 버튼 누른 후 창 개수: {len(pyautogui.getAllWindows())}")
            # 파일이름 입력
        pyperclip.copy(self.get_filename())
        pyautogui.hotkey('ctrl', 'v')  # 파일이름 입력


        pyautogui.sleep(Config.get_delay('input_filename'))  # 파일이름 입력 딜레이
        pyautogui.press('enter')  # 엔터로 출력 시작
        
    
        pyautogui.sleep(Config.get_delay('print_duration'))  # 단어장 출력 완료까지 딜레이
        
        while True:
            self.debug_log(f"현재 창 개수: {len(pyautogui.getAllWindows())}")
            if len(pyautogui.getAllWindows()) <= start_window_count:
                break
            pyautogui.sleep(0.5)
            time.sleep(0.5)
        # 단어장 출력 딜레이
        return True
    
    def get_filename(self):
        """파일이름을 생성"""
        filename = f"{self.input_values['name']}"
        
        if self.input_values['type'] == WordbookType.ORIGINAL:
            filename += f" {WordbookType.ORIGINAL.value}"
        elif self.input_values['type'] == WordbookType.RANDOM:
            filename += f" {WordbookType.RANDOM.value}"
        else:
            filename += f" {WordbookType.ENG_KOR_RANDOM.value}"
        
        if self.input_values['type'] != WordbookType.ORIGINAL and self.input_values['version']:
            filename += f"ver{self.input_values['version']}"
            
        filename += f" Day {self.current_day}"
                
        return re.sub(r'[\\/:*?"<>|]', '_', filename)
        
    
    def set_print_output_path(self):
        """출력 경로 설정"""
        try:
            # 출력 경로 설정 버튼 클릭
            if not self.click_position('buttons.set_output_path', Config.get_value('print_title'), "print_title"):
                return False
            
            # 경로 입력
            pyautogui.write(os.path.join(os.getcwd(), "work"))
            pyautogui.sleep(Config.get_delay('output_path'))  # 출력 경로 입력 딜레이
            pyautogui.press('enter')
            
            if not self.click_position('inputs.input_filename', Config.get_value('print_title'), "print_title"):
                return False
            
            self.print_output_path_set = True
            return True
            
        except Exception as e:
            self.log(f"출력 경로 설정 중 오류 발생: {str(e)}")
            return False

class Config:
    # 클래스 변수로 설정
    _config = {
        'window_title': "FactoryVoca(http://cafe.naver.com/factoryvoca)",
        'debug': True,
        'ui_positions': {
            'day_list': {
                'first_day': [50, 150]
            },
            'selected_day': {
                'position': [400, 150]
            },
            'buttons': {
                'add_day': [450, 200],
                'remove_day': [450, 230],
                'load_day': [450, 260],
                'apply': [800, 300],
                'random_apply': [800, 330],
                'print': [800, 360]
            },
            'inputs': {
                'word_count': [700, 150],
                'eng_to_kor': [700, 200]
            },
            'checkboxes': {
                'show_first_letter': [700, 250]
            }
        }
    }

    @classmethod
    def load(cls):
        """config.json 파일에서 설정 로드"""
        config_path = 'config.json'
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    cls._config = json.load(f)
            else:
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(cls._config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"설정 로드 오류: {str(e)}")

    @classmethod
    def get_value(cls, key):
        """key에 해당하는 값 반환"""
        return cls._config.get(key)
    
    @classmethod
    def get_delay(cls, key):
        """key에 해당하는 딜레이 값을 반환"""
        return cls._config['delays'].get(key, cls._config['delays']['default'])

    @classmethod
    def get_position(cls, position_key):
        """position_key에 해당하는 좌표 반환"""
        try:
            keys = position_key.split('.')
            value = cls._config['ui_positions']
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return None

    @classmethod
    def get_all_positions(cls):
        """모든 위치 정보 반환"""
        positions = []
        
        def collect_positions(data, prefix=''):
            for key, value in data.items():
                if isinstance(value, dict):
                    collect_positions(value, f"{prefix}{key}.")
                elif isinstance(value, list):
                    positions.append(f"{prefix}{key}")
        
        collect_positions(cls._config['ui_positions'])
        return positions

    @classmethod
    def is_debug_mode(cls) -> bool:
        """디버그 모드 여부 반환"""
        return cls._config.get('debug', False)

# 메인 코드 실행
if __name__ == "__main__":
    root = tk.Tk()  # Tkinter 메인 윈도우 생성
    Config.load()  # 설정 파일 로드
        
    controller = Controller(root)  # 컨트롤러 인스턴스 생성 UI 클래스 생성 및 연결
    root.mainloop()  # Tkinter 이벤트 루프 실행