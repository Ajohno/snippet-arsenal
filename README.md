# Code Snippet Arsenal

Code Snippet Arsenal is a **Python desktop application** built using **Tkinter** that allows users to **store, search, and manage code snippets** using a local **SQLite database**.

The project focuses on simplicity, local storage, and usability, avoiding unnecessary complexity such as web frameworks or external services.

---

## Overview

This application creates a **Tkinter desktop window** that enables users to store and retrieve reusable code snippets efficiently.

The program is composed of two primary parts:

1. **SQLite Database**
   - Saves code snippets permanently in a local `.db` file.

2. **Tkinter User Interface**
   - Provides a graphical interface for adding, editing, searching, and deleting snippets.

---

## Technologies Used

### Python

The primary programming language used to build the application.

### SQLite (`sqlite3`)

- Built-in Python database library.
- Creates and manages a local database file.
- Executes SQL queries to store and retrieve snippets.

### Tkinter

- Python’s built-in GUI toolkit.
- Used to create windows, buttons, text fields, and layouts.

### ttk (Themed Tkinter Widgets)

- A collection of styled Tkinter widgets.
- Provides cleaner and more modern UI components such as tables and buttons.

### messagebox

- Displays popup notifications.
- Used for confirmations, warnings, and error messages.

---

## Features

- Add and edit code snippets
- Search snippets by keyword
- Store metadata such as language, tags, and status
- Copy snippet code to the clipboard
- Persist data locally using SQLite

---

## Running the Application

From the project directory, run:

```bash
python main.py
```
