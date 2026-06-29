import sys
from gui.main_window import MainWindow

def main():
    try:
        # Instantiate and run main CustomTkinter window application
        app = MainWindow()
        app.mainloop()
    except Exception as e:
        print(f"Fatal error launching AI Desktop Assistant: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
