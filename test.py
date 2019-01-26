import tkinter as tk
from tkinter import ttk
from scrollable import ScrollableOuter, XYFrame

root = tk.Tk()

xyframe = XYFrame(root, bg="red")
xyframe.pack(padx=10, pady=10)

for i in range(0, 30):
    tk.Label(xyframe, text=str(i)).pack()

root.mainloop()
