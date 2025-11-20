"""
RAG 시스템 GUI
사용자 입력 받아서 최종 프롬프트를 생성하고 복사 가능하게 표시
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox
import pyperclip
from rag_system import MapRAG


class RagGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SUMO 맵 RAG 시스템")
        self.root.geometry("900x700")

        # RAG 시스템 초기화
        self.rag = MapRAG()

        # 제목
        title = tk.Label(root, text="SUMO 맵 생성기 (RAG)", font=("Arial", 18, "bold"))
        title.pack(pady=10)

        # 입력 섹션
        input_frame = tk.Frame(root)
        input_frame.pack(pady=10, padx=20, fill=tk.X)

        input_label = tk.Label(input_frame, text="맵 요청 입력:", font=("Arial", 12))
        input_label.pack(anchor=tk.W)

        self.input_text = tk.Entry(input_frame, font=("Arial", 11), width=80)
        self.input_text.pack(pady=5, fill=tk.X)
        self.input_text.insert(0, "고속도로 진입로가 있는 램프")

        # 버튼
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)

        generate_btn = tk.Button(
            button_frame,
            text="프롬프트 생성",
            command=self.generate_prompt,
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            padx=20,
            pady=10
        )
        generate_btn.pack(side=tk.LEFT, padx=5)

        copy_btn = tk.Button(
            button_frame,
            text="프롬프트 복사",
            command=self.copy_prompt,
            font=("Arial", 12),
            bg="#2196F3",
            fg="white",
            padx=20,
            pady=10
        )
        copy_btn.pack(side=tk.LEFT, padx=5)

        clear_btn = tk.Button(
            button_frame,
            text="지우기",
            command=self.clear_output,
            font=("Arial", 12),
            bg="#f44336",
            fg="white",
            padx=20,
            pady=10
        )
        clear_btn.pack(side=tk.LEFT, padx=5)

        # 출력 섹션
        output_label = tk.Label(root, text="생성된 프롬프트:", font=("Arial", 12, "bold"))
        output_label.pack(anchor=tk.W, padx=20, pady=(10, 0))

        self.output_text = scrolledtext.ScrolledText(
            root,
            font=("Courier", 9),
            width=100,
            height=30,
            wrap=tk.WORD
        )
        self.output_text.pack(pady=5, padx=20, fill=tk.BOTH, expand=True)

        # 상태바
        self.status_label = tk.Label(
            root,
            text="준비됨",
            font=("Arial", 10),
            bg="#e0e0e0",
            anchor=tk.W
        )
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def generate_prompt(self):
        """프롬프트 생성"""
        user_query = self.input_text.get().strip()

        if not user_query:
            messagebox.showwarning("경고", "맵 요청을 입력해주세요!")
            return

        try:
            self.status_label.config(text="프롬프트 생성 중...", bg="#FFC107")
            self.root.update()

            # RAG로 프롬프트 생성
            prompt = self.rag.generate_map_with_ai(user_query, top_k=2)

            # 출력창에 표시
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, prompt)

            self.status_label.config(text=f"완료! (쿼리: {user_query})", bg="#4CAF50")

        except Exception as e:
            messagebox.showerror("오류", f"프롬프트 생성 실패:\n{str(e)}")
            self.status_label.config(text="오류 발생", bg="#f44336")

    def copy_prompt(self):
        """프롬프트를 클립보드에 복사"""
        prompt = self.output_text.get(1.0, tk.END).strip()

        if not prompt:
            messagebox.showwarning("경고", "복사할 프롬프트가 없습니다!")
            return

        try:
            pyperclip.copy(prompt)
            self.status_label.config(text="클립보드에 복사됨!", bg="#2196F3")
            messagebox.showinfo("성공", "프롬프트가 클립보드에 복사되었습니다!")
        except Exception as e:
            messagebox.showerror("오류", f"복사 실패:\n{str(e)}")

    def clear_output(self):
        """출력창 지우기"""
        self.output_text.delete(1.0, tk.END)
        self.status_label.config(text="지워짐", bg="#e0e0e0")


def main():
    root = tk.Tk()
    app = RagGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
