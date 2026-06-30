from tkinter import Tk, Frame
from MainApp import MainApp

#main (top-level) startup
if __name__ == '__main__':

    main_window = MainApp()
    main_window.ui.after(1000, lambda: main_window.initCMD(startup=True))
    main_window.ui.mainloop()





# [ 0  |  1 | 2  | 3  | 4  | 5  | 6  | 7  | 8  | 9  | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 23 | 24 | 25 | 26 | 27 | 28 | 29 | 30 ]
# [ 85 | 170|  gate-V |  set-V  |  set-T  |  delay  |  R1-V   |  R1-T   | reset-V | reset-T |  R2-V   |  R2 T   | r  | c  |  cyl    |  stp    | M  | 170| 85 ]
#-------------------------------------------------------------------------------------------------------------------------------------------------------------
# [ 55 | AA | 07 | D0 | 00 | 00 | 00 | 00 | 01 | F4 | 00 | 00 | 00 | 00 | 00 | 00 | 00 | 00 | 00 | 00 | 01 | F4 | 00 | 00 | 00 | 01 | 00 | 00 | 00 | AA | 55 ]
# [ 55 | AA | 07 | D0 | 00 | 00 | 00 | 00 | 01 | F4 | 00 | 00 | 00 | 00 | 00 | 00 | 00 | 00 | 00 | C8 | 01 | F4 | 05 | 02 | 00 | 01 | 00 | 00 | 00 | AA | 55 ]





# [ 55 | AA | 07 | D0 | 07 | D0 | 00 | 64 | 01 | F4 | 00 | 00 | 00 | 00 | 07 | 08 | 00 | 64 | 00 | C8 | 01 | F4 | 00 | 00 | 00 | 01 | 00 | 00 | 00 | AA | 55 ]



# [ 55 | AA | 05 | DC | 07 | D0 | 00 | 64 | 01 | F4 | 00 | C8 | 01 | F4 | 00 | 00 | 00 | 64 | 00 | 00 | 01 | F4 | 00 | 00 | 00 | 01 | 00 | 00 | 00 | AA | 55 ]
# [ 55 | AA | 05 | DC | 07 | D0 | 00 | 64 | 01 | F4 | 00 | C8 | 01 | F4 | 00 | 00 | 00 | 64 | 00 | 00 | 01 | F4 | 00 | 01 | 00 | 01 | 00 | 00 | 00 | AA | 55 ]
# [ 55 | AA | 05 | DC | 07 | D0 | 00 | 64 | 01 | F4 | 00 | C8 | 01 | F4 | 00 | 00 | 00 | 64 | 00 | 00 | 01 | F4 | 00 | 02 | 00 | 01 | 00 | 00 | 00 | AA | 55 ]

#[85, 170, 5, 220, 7, 208, 0, 100, 1, 244, 0, 200, 1, 244, 0, 0, 0, 100, 0, 0, 1, 244, 30, 10, 0, 1, 0, 0, 0, 170, 85]


# import tkinter as tk 


# def create_app():
#     root = tk.Tk()
#     root.title("3 Labels and Entries")
#     root.geometry("400x200")  # Wider for better resizing

#     root.resizable(True, True)  # Enable window resizing

#     # Tell root grid: column 1 (where frames with entries are) should expand
#     root.grid_columnconfigure(1, weight=1)

#     labels_text = ["First Name:", "Last Name:", "Email:"]

#     for i, text in enumerate(labels_text):
#         label = tk.Label(root, text=text, anchor='w')
#         label.grid(row=i, column=0, padx=10, pady=5, sticky='w')

#         frame = tk.Frame(root)
#         frame.grid(row=i, column=1, padx=10, pady=10, sticky='ew')  # Let frame stretch horizontally

#         # Tell frame grid: column 0 (entry) should expand
#         frame.grid_columnconfigure(0, weight=1)

#         entry = tk.Entry(frame)
#         entry.grid(row=0, column=0, padx=5, pady=5, sticky='ew')  # Entry stretches in frame

#         unit = tk.Label(frame, text='us', anchor='w')
#         unit.grid(row=0, column=1, padx=5, pady=5, sticky='w')  # Unit stays to the right

#     return root

# if __name__ == "__main__":
#     app = create_app()
#     app.mainloop()