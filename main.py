import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox
from enum import Enum, auto

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

# 컨트롤러 클래스
class Controller:
    def __init__(self, view: 'AppUI'):
        self.view = view  # AppUI 인스턴스 저장
        # 컨트롤러에서 관리할 데이터나 기능 초기화
        self.directories = {
            "Work": "/Work",
            "Output": "/Output",
        }
        
        print("Controller initialized.")

    def example_action(self):
        # 예제 동작 (버튼 클릭 시 실행)
        print("Example action executed!")

    def process_action(self):
        if not self.view.validate_inputs():
            return
            
        input_values = self.view.get_input_values()
        
        # Enum을 사용한 타입 비교
        if input_values['type'] == WordbookType.ORIGINAL:
            # 원래 순서로 처리
            pass
        elif input_values['type'] == WordbookType.RANDOM:
            # 랜덤으로 처리
            pass
        elif input_values['type'] == WordbookType.ENG_KOR_RANDOM:
            # 영한랜덤으로 처리
            pass

# UI 클래스
class AppUI:
    def __init__(self, root: tk.Tk, controller: Controller):
        self.root = root
        self.controller = controller

        self.root.title("AutoTestCrafter")  # 창 제목
        self.root.geometry("400x300")    # 창 크기 설정 (너비 x 높이)

        # UI 요소 구성
        self.create_widgets()

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

    def get_input_values(self):
        """순수 입력값만 반환"""
        values = {
            'name': self.inputs['name'].get().strip(),
            'type': WordbookType.from_string(self.inputs['type'].get()),
            'version': self.inputs['version'].get().strip() if WordbookType.from_string(self.inputs['type'].get()) != WordbookType.ORIGINAL else None
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
        return True

    def get_validated_values(self):
        """편의 메서드: 검증된 값 반환"""
        if not self.validate_inputs():
            return None
        return self.get_input_values()

# 메인 코드 실행
if __name__ == "__main__":
    root = tk.Tk()  # Tkinter 메인 윈도우 생성
    controller = Controller(None)  # 컨트롤러 인스턴스 생성
    app = AppUI(root, controller)  # UI 클래스 생성 및 연결
    controller.view = app  # 컨트롤러에 UI 인스턴스 연결
    root.mainloop()  # Tkinter 이벤트 루프 실행
