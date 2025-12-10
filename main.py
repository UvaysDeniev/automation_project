from .scrape_upcoming import process_upcoming_orders
from .scrape_received import process_received_orders
from .scrape_item_summary import process_item_summary
from .scrape_history import process_data_from_2024, write_weekly_by_month_table

import tkinter as tk
from tkinter import ttk, messagebox

# --------------------------------------------------
# GUI HOOKUP (options 4 & 5)
# --------------------------------------------------

def ask_user_choice():
    DARK_BG, LIGHT_FG, ACCENT, ACTIVE_BG = "#1b2838", "#c6d4df", "#2a475e", "#3e5c78"
    root = tk.Tk()
    root.title("FtinessCo PO Automation")
    root.geometry("360x300")
    root.resizable(False, False)
    root.configure(bg=DARK_BG)

    choice_var = tk.StringVar(value="0")
    def on_close():
        choice_var.set("0"); root.quit()
    root.protocol("WM_DELETE_WINDOW", on_close)

    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("TLabel", background=DARK_BG, foreground=LIGHT_FG, font=("Segoe UI",11))
    style.configure("TButton", background=ACCENT, foreground=LIGHT_FG,
                    font=("Segoe UI",10), borderwidth=0, padding=6)
    style.map("TButton", background=[("active",ACTIVE_BG)])

    ttk.Label(root, text="Select an action to run:", background=DARK_BG, foreground=LIGHT_FG).pack(pady=(20,10))

    options = [
      ("📥 Upcoming → WAITING ON",   "1"),
      ("📦 Received → CAME IN",      "2"),
      ("📊 Item Summary",            "3"),
      ("📅 Past 2024",               "4"),
      ("📅 Trend Chart Table",       "5"),
      ("⚡ Quick Update",            "6"),
      ("⚡⚡⚡ Full Update",         "7"),
      ("❌ Exit",                    "0"),
    ]
    for txt,val in options:
        rb = tk.Radiobutton(root, text=txt, variable=choice_var, value=val,
                            bg=DARK_BG, fg=LIGHT_FG, selectcolor=ACCENT,
                            activebackground=DARK_BG, activeforeground=LIGHT_FG,
                            highlightthickness=0, bd=0, font=("Segoe UI",10))
        rb.pack(anchor="w", padx=30, pady=2)

    ttk.Button(root, text="OK", command=root.quit).pack(pady=(5,10))

    root.update_idletasks()
    w,h = root.winfo_width(), root.winfo_height()
    x = (root.winfo_screenwidth()-w)//2
    y = (root.winfo_screenheight()-h)//2
    root.geometry(f"{w}x{h}+{x}+{y}")

    root.mainloop()
    choice = choice_var.get()
    root.destroy()
    return choice

if __name__ == "__main__":
    while True:
        ch = ask_user_choice()
        if ch in (None,"0"):
            break
        if   ch=="1": process_upcoming_orders()
        elif ch=="2": process_received_orders()
        elif ch=="3": process_item_summary()
        elif ch=="4": process_data_from_2024()
        elif ch=="5": write_weekly_by_month_table()
        elif ch == "6":
            process_item_summary()
            process_data_from_2024()
            write_weekly_by_month_table()
            messagebox.showinfo("Quick Update", "All summaries/tables refreshed from Sheets only.")
        elif ch == "7":
            process_received_orders()
            process_upcoming_orders()
            process_item_summary()
            process_data_from_2024()
            write_weekly_by_month_table()
            messagebox.showinfo("Full Update", "All summaries/tables are completed.")
        else:
            tk.Tk().withdraw()
            messagebox.showerror("Invalid choice", f"'{ch}' is not an option.")
