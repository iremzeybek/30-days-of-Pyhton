```python
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import platform
import os
import hashlib
from datetime import datetime


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

APP_TITLE = "Python Executable Utility"
APP_VERSION = "1.0.0"


# ============================================================
# SYSTEM INFORMATION
# ============================================================

def get_system_information():
    """Return basic information about the current computer."""

    information = {
        "Operating System": platform.system(),
        "OS Version": platform.version(),
        "Architecture": platform.machine(),
        "Processor": platform.processor() or "Unknown",
        "Computer Name": platform.node(),
        "Python Version": platform.python_version(),
        "Current User": os.getlogin(),
    }

    return information


# ============================================================
# FILE HASHING
# ============================================================

def calculate_file_hash(file_path, algorithm="sha256"):
    """
    Calculate the hash of a file.

    The file is read in chunks so large files can be processed
    without loading the entire file into memory.
    """

    hash_object = hashlib.new(algorithm)

    try:
        with open(file_path, "rb") as file:
            while True:
                chunk = file.read(8192)

                if not chunk:
                    break

                hash_object.update(chunk)

        return hash_object.hexdigest()

    except (OSError, PermissionError) as error:
        raise RuntimeError(f"Could not read the file:\n{error}")


# ============================================================
# TEXT FILE ANALYSIS
# ============================================================

def analyze_text_file(file_path):
    """Count lines, words, and characters in a text file."""

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        lines = content.splitlines()
        words = content.split()
        characters = len(content)

        return {
            "Lines": len(lines),
            "Words": len(words),
            "Characters": characters,
        }

    except UnicodeDecodeError:
        raise RuntimeError(
            "This file does not appear to be a UTF-8 text file."
        )

    except (OSError, PermissionError) as error:
        raise RuntimeError(f"Could not read the file:\n{error}")


# ============================================================
# FILE INFORMATION
# ============================================================

def get_file_information(file_path):
    """Return basic information about a selected file."""

    try:
        file_size = os.path.getsize(file_path)
        modified_time = os.path.getmtime(file_path)

        return {
            "File Name": os.path.basename(file_path),
            "Full Path": os.path.abspath(file_path),
            "File Size": f"{file_size:,} bytes",
            "Modified": datetime.fromtimestamp(
                modified_time
            ).strftime("%Y-%m-%d %H:%M:%S"),
        }

    except (OSError, PermissionError) as error:
        raise RuntimeError(f"Could not inspect the file:\n{error}")


# ============================================================
# MAIN APPLICATION
# ============================================================

class UtilityApp:

    def __init__(self, root):
        self.root = root

        self.root.title(f"{APP_TITLE} v{APP_VERSION}")
        self.root.geometry("850x650")
        self.root.minsize(750, 550)

        self.selected_file = None

        self.create_styles()
        self.create_interface()

    # ========================================================
    # STYLING
    # ========================================================

    def create_styles(self):
        """Configure ttk widget styles."""

        style = ttk.Style()

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Title.TLabel",
            font=("Segoe UI", 20, "bold")
        )

        style.configure(
            "Subtitle.TLabel",
            font=("Segoe UI", 10)
        )

        style.configure(
            "Section.TLabelframe",
            padding=10
        )

        style.configure(
            "Section.TLabelframe.Label",
            font=("Segoe UI", 11, "bold")
        )

        style.configure(
            "Action.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=8
        )

    # ========================================================
    # USER INTERFACE
    # ========================================================

    def create_interface(self):
        """Create all GUI components."""

        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill="both", expand=True)

        # ----------------------------------------------------
        # Header
        # ----------------------------------------------------

        title = ttk.Label(
            main_frame,
            text=APP_TITLE,
            style="Title.TLabel"
        )
        title.pack(anchor="w")

        subtitle = ttk.Label(
            main_frame,
            text="A Python application packaged as a standalone executable",
            style="Subtitle.TLabel"
        )
        subtitle.pack(anchor="w", pady=(0, 15))

        # ----------------------------------------------------
        # Notebook
        # ----------------------------------------------------

        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill="both", expand=True)

        self.system_tab = ttk.Frame(notebook, padding=15)
        self.file_tab = ttk.Frame(notebook, padding=15)
        self.about_tab = ttk.Frame(notebook, padding=15)

        notebook.add(
            self.system_tab,
            text="System Information"
        )

        notebook.add(
            self.file_tab,
            text="File Utility"
        )

        notebook.add(
            self.about_tab,
            text="About"
        )

        self.create_system_tab()
        self.create_file_tab()
        self.create_about_tab()

    # ========================================================
    # SYSTEM TAB
    # ========================================================

    def create_system_tab(self):
        """Create system information interface."""

        frame = ttk.LabelFrame(
            self.system_tab,
            text="Computer Information",
            style="Section.TLabelframe"
        )
        frame.pack(fill="both", expand=True)

        columns = ("Property", "Value")

        self.system_tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings"
        )

        self.system_tree.heading(
            "Property",
            text="Property"
        )

        self.system_tree.heading(
            "Value",
            text="Value"
        )

        self.system_tree.column(
            "Property",
            width=200,
            anchor="w"
        )

        self.system_tree.column(
            "Value",
            width=450,
            anchor="w"
        )

        scrollbar = ttk.Scrollbar(
            frame,
            orient="vertical",
            command=self.system_tree.yview
        )

        self.system_tree.configure(
            yscrollcommand=scrollbar.set
        )

        self.system_tree.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        button_frame = ttk.Frame(self.system_tab)
        button_frame.pack(fill="x", pady=(10, 0))

        refresh_button = ttk.Button(
            button_frame,
            text="Refresh Information",
            command=self.show_system_information,
            style="Action.TButton"
        )

        refresh_button.pack(side="left")

        export_button = ttk.Button(
            button_frame,
            text="Export Information",
            command=self.export_system_information,
            style="Action.TButton"
        )

        export_button.pack(side="left", padx=10)

        self.show_system_information()

    # ========================================================
    # SHOW SYSTEM INFORMATION
    # ========================================================

    def show_system_information(self):
        """Display system information in the Treeview."""

        for item in self.system_tree.get_children():
            self.system_tree.delete(item)

        information = get_system_information()

        for property_name, value in information.items():
            self.system_tree.insert(
                "",
                "end",
                values=(property_name, value)
            )

    # ========================================================
    # EXPORT SYSTEM INFORMATION
    # ========================================================

    def export_system_information(self):
        """Save system information to a text file."""

        information = get_system_information()

        file_path = filedialog.asksaveasfilename(
            title="Save System Information",
            defaultextension=".txt",
            filetypes=[
                ("Text Files", "*.txt"),
                ("All Files", "*.*")
            ]
        )

        if not file_path:
            return

        try:
            with open(
                file_path,
                "w",
                encoding="utf-8"
            ) as file:

                file.write(
                    f"{APP_TITLE} - System Information\n"
                )

                file.write("=" * 50 + "\n\n")

                for key, value in information.items():
                    file.write(
                        f"{key}: {value}\n"
                    )

            messagebox.showinfo(
                "Export Complete",
                f"Information saved to:\n{file_path}"
            )

        except OSError as error:
            messagebox.showerror(
                "Export Error",
                f"Could not save the file:\n{error}"
            )

    # ========================================================
    # FILE TAB
    # ========================================================

    def create_file_tab(self):
        """Create file utility interface."""

        selection_frame = ttk.LabelFrame(
            self.file_tab,
            text="File Selection",
            style="Section.TLabelframe"
        )

        selection_frame.pack(
            fill="x",
            pady=(0, 10)
        )

        self.file_label = ttk.Label(
            selection_frame,
            text="No file selected"
        )

        self.file_label.pack(
            side="left",
            fill="x",
            expand=True,
            padx=5
        )

        select_button = ttk.Button(
            selection_frame,
            text="Select File",
            command=self.select_file,
            style="Action.TButton"
        )

        select_button.pack(
            side="right"
        )

        # ----------------------------------------------------
        # File Information
        # ----------------------------------------------------

        info_frame = ttk.LabelFrame(
            self.file_tab,
            text="File Information",
            style="Section.TLabelframe"
        )

        info_frame.pack(
            fill="x",
            pady=(0, 10)
        )

        self.file_info_text = tk.Text(
            info_frame,
            height=8,
            wrap="word",
            state="disabled"
        )

        self.file_info_text.pack(
            fill="both",
            expand=True
        )

        # ----------------------------------------------------
        # Hash
        # ----------------------------------------------------

        hash_frame = ttk.LabelFrame(
            self.file_tab,
            text="SHA-256 Hash",
            style="Section.TLabelframe"
        )

        hash_frame.pack(
            fill="x",
            pady=(0, 10)
        )

        self.hash_entry = ttk.Entry(
            hash_frame
        )

        self.hash_entry.pack(
            fill="x",
            padx=5,
            pady=5
        )

        # ----------------------------------------------------
        # Text Analysis
        # ----------------------------------------------------

        analysis_frame = ttk.LabelFrame(
            self.file_tab,
            text="Text File Analysis",
            style="Section.TLabelframe"
        )

        analysis_frame.pack(
            fill="x"
        )

        analyze_button = ttk.Button(
            analysis_frame,
            text="Analyze Text File",
            command=self.analyze_selected_file,
            style="Action.TButton"
        )

        analyze_button.pack(
            side="left",
            padx=5,
            pady=5
        )

        clear_button = ttk.Button(
            analysis_frame,
            text="Clear",
            command=self.clear_file_results,
            style="Action.TButton"
        )

        clear_button.pack(
            side="left",
            padx=5,
            pady=5
        )

    # ========================================================
    # SELECT FILE
    # ========================================================

    def select_file(self):
        """Open file selection dialog."""

        file_path = filedialog.askopenfilename(
            title="Select a File"
        )

        if not file_path:
            return

        self.selected_file = file_path

        self.file_label.config(
            text=file_path
        )

        try:
            information = get_file_information(
                file_path
            )

            self.update_file_information(
                information
            )

            file_hash = calculate_file_hash(
                file_path
            )

            self.hash_entry.delete(
                0,
                tk.END
            )

            self.hash_entry.insert(
                0,
                file_hash
            )

        except RuntimeError as error:
            messagebox.showerror(
                "File Error",
                str(error)
            )

    # ========================================================
    # UPDATE FILE INFORMATION
    # ========================================================

    def update_file_information(self, information):
        """Display selected file information."""

        self.file_info_text.config(
            state="normal"
        )

        self.file_info_text.delete(
            "1.0",
            tk.END
        )

        for key, value in information.items():
            self.file_info_text.insert(
                tk.END,
                f"{key}: {value}\n"
            )

        self.file_info_text.config(
            state="disabled"
        )

    # ========================================================
    # ANALYZE FILE
    # ========================================================

    def analyze_selected_file(self):
        """Analyze selected file as a text file."""

        if not self.selected_file:
            messagebox.showwarning(
                "No File",
                "Please select a file first."
            )
            return

        try:
            result = analyze_text_file(
                self.selected_file
            )

            message = (
                f"Lines: {result['Lines']:,}\n"
                f"Words: {result['Words']:,}\n"
                f"Characters: {result['Characters']:,}"
            )

            messagebox.showinfo(
                "Text File Analysis",
                message
            )

        except RuntimeError as error:
            messagebox.showerror(
                "Analysis Error",
                str(error)
            )

    # ========================================================
    # CLEAR FILE RESULTS
    # ========================================================

    def clear_file_results(self):
        """Clear all file-related information."""

        self.selected_file = None

        self.file_label.config(
            text="No file selected"
        )

        self.file_info_text.config(
            state="normal"
        )

        self.file_info_text.delete(
            "1.0",
            tk.END
        )

        self.file_info_text.config(
            state="disabled"
        )

        self.hash_entry.delete(
            0,
            tk.END
        )

    # ========================================================
    # ABOUT TAB
    # ========================================================

    def create_about_tab(self):
        """Create the About page."""

        container = ttk.Frame(
            self.about_tab
        )

        container.pack(
            expand=True
        )

        title = ttk.Label(
            container,
            text=APP_TITLE,
            style="Title.TLabel"
        )

        title.pack(
            pady=(30, 10)
        )

        version = ttk.Label(
            container,
            text=f"Version {APP_VERSION}"
        )

        version.pack(
            pady=5
        )

        description = ttk.Label(
            container,
            text=(
                "This project demonstrates how to create a "
                "Python desktop application and package it "
                "as a standalone executable using PyInstaller."
            ),
            justify="center",
            wraplength=500
        )

        description.pack(
            pady=20
        )

        technologies = ttk.Label(
            container,
            text=(
                "Technologies:\n\n"
                "• Python\n"
                "• Tkinter\n"
                "• hashlib\n"
                "• platform\n"
                "• PyInstaller"
            ),
            justify="left"
        )

        technologies.pack(
            pady=10
        )

    # ========================================================
    # CLOSE APPLICATION
    # ========================================================

    def close_application(self):
        """Close the application."""

        self.root.destroy()


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

def main():
    """Start the application."""

    root = tk.Tk()

    app = UtilityApp(root)

    root.protocol(
        "WM_DELETE_WINDOW",
        app.close_application
    )

    root.mainloop()


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":
    main()
```
