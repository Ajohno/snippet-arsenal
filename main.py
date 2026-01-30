# ==============================
# Imports
# ==============================

# sqlite3 = built-in lightweight database
import sqlite3

# tkinter = built-in Python GUI toolkit
import tkinter as tk

# ttk = themed widgets (nicer-looking buttons, tables, etc.)
from tkinter import ttk, messagebox


# ==============================
# Configuration
# ==============================

# Name of the SQLite database file
DB_NAME = "snippets.db"


# ==============================
# Database functions
# ==============================

def init_db():
    """
    Create the database and snippets table if it doesn't already exist.
    This runs once when the app starts.
    """
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS snippets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                language TEXT NOT NULL,
                tags TEXT NOT NULL,
                status TEXT NOT NULL,
                code TEXT NOT NULL,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()


def db_search(query: str):
    """
    Search snippets by keyword across multiple fields.
    Returns lightweight rows for the results list.
    """
    q = f"%{query.strip()}%"

    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, title, language, tags, status
            FROM snippets
            WHERE title LIKE ?
               OR language LIKE ?
               OR tags LIKE ?
               OR code LIKE ?
               OR IFNULL(notes, '') LIKE ?
            ORDER BY updated_at DESC
            LIMIT 200
        """, (q, q, q, q, q))

        return cur.fetchall()


def db_get(snippet_id: int):
    """
    Fetch a full snippet by ID.
    Used when clicking a result.
    """
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, title, language, tags, status, code, IFNULL(notes, '')
            FROM snippets
            WHERE id = ?
        """, (snippet_id,))

        return cur.fetchone()


def db_insert(title, language, tags, status, code, notes):
    """
    Insert a brand-new snippet.
    """
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO snippets (title, language, tags, status, code, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (title, language, tags, status, code, notes))

        conn.commit()
        return cur.lastrowid


def db_update(snippet_id, title, language, tags, status, code, notes):
    """
    Update an existing snippet.
    """
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE snippets
            SET title = ?,
                language = ?,
                tags = ?,
                status = ?,
                code = ?,
                notes = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (title, language, tags, status, code, notes, snippet_id))

        conn.commit()


def db_delete(snippet_id):
    """
    Permanently delete a snippet.
    """
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM snippets WHERE id = ?", (snippet_id,))
        conn.commit()


# ==============================
# Main Application Class
# ==============================

class SnippetArsenalApp(tk.Tk):
    """
    Main Tkinter window.
    Inherits from tk.Tk.
    """

    def __init__(self):
        super().__init__()

        # Window configuration
        self.title("Snippet Arsenal")
        self.geometry("1100x650")
        self.minsize(900, 550)

        # Track which snippet is currently selected
        self.selected_id = None

        # ==============================
        # Top bar (Search + New)
        # ==============================

        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")

        ttk.Label(top, text="Search:").pack(side="left")

        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(top, textvariable=self.search_var, width=50)
        self.search_entry.pack(side="left", padx=8)
        self.search_entry.bind("<Return>", lambda e: self.refresh_results())

        ttk.Button(top, text="Search", command=self.refresh_results).pack(side="left")
        ttk.Button(top, text="New", command=self.new_snippet).pack(side="left", padx=8)

        # ==============================
        # Main layout (split view)
        # ==============================

        main = ttk.PanedWindow(self, orient="horizontal")
        main.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # ==============================
        # Left panel (Results list)
        # ==============================

        left = ttk.Frame(main, padding=10)
        main.add(left, weight=1)

        ttk.Label(left, text="Results").pack(anchor="w")

        self.results = ttk.Treeview(
            left,
            columns=("id", "title", "lang", "tags", "status"),
            show="headings"
        )

        # Define table headers
        self.results.heading("id", text="ID")
        self.results.heading("title", text="Title")
        self.results.heading("lang", text="Lang")
        self.results.heading("tags", text="Tags")
        self.results.heading("status", text="Status")

        # Column sizing
        self.results.column("id", width=50, anchor="center")
        self.results.column("title", width=260)
        self.results.column("lang", width=80, anchor="center")
        self.results.column("tags", width=220)
        self.results.column("status", width=80, anchor="center")

        self.results.pack(fill="both", expand=True)
        self.results.bind("<<TreeviewSelect>>", self.on_select)

        # ==============================
        # Right panel (Editor)
        # ==============================

        right = ttk.Frame(main, padding=10)
        main.add(right, weight=2)

        # ----- Metadata form -----
        form = ttk.Frame(right)
        form.pack(fill="x")

        ttk.Label(form, text="Title").grid(row=0, column=0, sticky="w")
        self.title_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.title_var).grid(row=0, column=1, sticky="ew", padx=8)

        ttk.Label(form, text="Language").grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.lang_var = tk.StringVar(value="py")
        ttk.Entry(form, textvariable=self.lang_var, width=12).grid(row=1, column=1, sticky="w", padx=8)

        ttk.Label(form, text="Status").grid(row=1, column=1, sticky="e", pady=(8, 0))
        self.status_var = tk.StringVar(value="draft")
        ttk.Combobox(
            form,
            textvariable=self.status_var,
            values=["draft", "tested", "prod"],
            state="readonly",
            width=10
        ).grid(row=1, column=2, sticky="w", padx=8)

        ttk.Label(form, text="Tags (comma-separated)").grid(row=2, column=0, sticky="w", pady=(8, 0))
        self.tags_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.tags_var).grid(row=2, column=1, columnspan=2, sticky="ew", padx=8)

        form.columnconfigure(1, weight=1)

        # ----- Code editor -----
        ttk.Label(right, text="Code").pack(anchor="w", pady=(12, 0))
        self.code_text = tk.Text(right, height=14, wrap="none", undo=True)
        self.code_text.pack(fill="both", expand=True)

        # ----- Notes editor -----
        ttk.Label(right, text="Notes").pack(anchor="w", pady=(12, 0))
        self.notes_text = tk.Text(right, height=6, wrap="word", undo=True)
        self.notes_text.pack(fill="x")

        # ----- Buttons -----
        btns = ttk.Frame(right)
        btns.pack(fill="x", pady=(12, 0))

        ttk.Button(btns, text="Save", command=self.save_snippet).pack(side="left")
        ttk.Button(btns, text="Copy Code", command=self.copy_code).pack(side="left", padx=8)
        ttk.Button(btns, text="Delete", command=self.delete_snippet).pack(side="left")

        # Initial load
        self.refresh_results()

    # ==============================
    # UI Logic Methods
    # ==============================

    def refresh_results(self):
        """Refresh the search results list."""
        for item in self.results.get_children():
            self.results.delete(item)

        rows = db_search(self.search_var.get())
        for r in rows:
            self.results.insert("", "end", values=r)

    def on_select(self, event=None):
        """Load selected snippet into the editor."""
        sel = self.results.selection()
        if not sel:
            return

        snippet_id = int(self.results.item(sel[0], "values")[0])
        row = db_get(snippet_id)

        self.selected_id = row[0]
        self.title_var.set(row[1])
        self.lang_var.set(row[2])
        self.tags_var.set(row[3])
        self.status_var.set(row[4])

        self.code_text.delete("1.0", "end")
        self.code_text.insert("1.0", row[5])

        self.notes_text.delete("1.0", "end")
        self.notes_text.insert("1.0", row[6])

    def new_snippet(self):
        """Clear the editor to create a new snippet."""
        self.selected_id = None
        self.title_var.set("")
        self.lang_var.set("py")
        self.tags_var.set("")
        self.status_var.set("draft")
        self.code_text.delete("1.0", "end")
        self.notes_text.delete("1.0", "end")

    def save_snippet(self):
        """Insert or update a snippet."""
        title = self.title_var.get().strip()
        language = self.lang_var.get().strip()
        tags = self.tags_var.get().strip()
        status = self.status_var.get().strip()
        code = self.code_text.get("1.0", "end").strip()
        notes = self.notes_text.get("1.0", "end").strip()

        if not title or not language or not tags or not code:
            messagebox.showerror("Error", "Title, language, tags, and code are required.")
            return

        tags = ",".join(t.strip() for t in tags.split(",") if t.strip())

        if self.selected_id is None:
            self.selected_id = db_insert(title, language, tags, status, code, notes)
        else:
            db_update(self.selected_id, title, language, tags, status, code, notes)

        self.refresh_results()
        messagebox.showinfo("Saved", "Snippet saved.")

    def copy_code(self):
        """Copy code to clipboard."""
        code = self.code_text.get("1.0", "end").strip()
        if not code:
            return
        self.clipboard_clear()
        self.clipboard_append(code)

    def delete_snippet(self):
        """Delete the selected snippet."""
        if self.selected_id is None:
            return

        if not messagebox.askyesno("Confirm", "Delete this snippet?"):
            return

        db_delete(self.selected_id)
        self.new_snippet()
        self.refresh_results()


# ==============================
# App entry point
# ==============================

if __name__ == "__main__":
    init_db()
    app = SnippetArsenalApp()
    app.mainloop()
