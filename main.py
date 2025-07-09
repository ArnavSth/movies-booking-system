from system import initialize_db
import tkinter as tk
from gui import MovieBookingGUI

def main():
    initialize_db()  # Ensure database and sample data are ready
    root = tk.Tk()
    app = MovieBookingGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()