import sys
import traceback
import tkinter as tk

try:
    from tkinterdnd2 import TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    TkinterDnD = None
    DND_AVAILABLE = False

from app import FM26ModManagerApp
from ui.dialogs import show_error, ask_yes_no


def handle_exception(exc_type, exc_value, exc_traceback):
    """
    Global exception handler to prevent crashes.

    Shows user-friendly error dialog while allowing application to continue.
    """
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    try:
        root = tk._default_root
        if root:
            show_error(
                root,
                "Unexpected Error",
                f"An unexpected error occurred:\n\n{exc_value}\n\n"
                f"The application will continue running, but you may want to restart it.\n\n"
                f"If this problem persists, please report it to the developer.",
                ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            )
    except:
        print(f"Fatal error: {exc_value}")
        traceback.print_exception(exc_type, exc_value, exc_traceback)


def main():
    """Application entry point."""
    try:
        sys.excepthook = handle_exception

        # Use TkinterDnD if available, otherwise fallback to regular Tk
        if DND_AVAILABLE:
            root = TkinterDnD.Tk()
        else:
            root = tk.Tk()

        def on_closing():
            """Handle window close event."""
            if ask_yes_no(root, "Quit", "Are you sure you want to exit?"):
                root.destroy()

        root.protocol("WM_DELETE_WINDOW", on_closing)

        app = FM26ModManagerApp(root, dnd_available=DND_AVAILABLE)
        root.mainloop()

    except Exception as e:
        temp_root = tk.Tk()
        temp_root.withdraw()
        show_error(
            temp_root,
            "Fatal Error",
            f"A fatal error occurred during startup:\n\n{str(e)}\n\n"
            f"The application cannot continue.",
            traceback.format_exc()
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
