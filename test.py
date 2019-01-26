import tkinter as tk
from tkinter import ttk
from scrollable import ScrollableOuter, XYFrame

root = tk.Tk()

scr_outer = ScrollableOuter(root, scroll=tk.Y)
xyframe = XYFrame(scr_outer, bg='red', relief=tk.SUNKEN, bd=4)
scr_outer.set_interior(xyframe)
scr_outer.pack(padx=10, pady=10)

for i in range(0, 30):
    label = tk.Label(xyframe, text=str(i))
    label.bind('<MouseWheel>', xyframe.on_scroll)
    label.pack()

root.mainloop()
