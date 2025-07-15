import tkinter as tk

def spawn():
    print("spawning")              # 1. 버튼 클릭 시 호출 확인
    c.create_rectangle(50,50,150,100, fill='red')  # 2. 캔버스 위에 사각형 그리기

win = tk.Tk()
win.title("테스트")
c = tk.Canvas(win, width=200, height=200, bg='white')
c.pack(padx=10, pady=10)

btn = tk.Button(win, text="Spawn", command=spawn)
btn.pack(pady=5)

win.mainloop()
