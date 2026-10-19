
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
import requests

# ---------------- DATABASE ----------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "contacts.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT NOT NULL
)
""")
conn.commit()

# ---------------- COLORS ----------------

BG = "#F3F6FB"
BLUE = "#2457C5"
DARK = "#172B4D"
WHITE = "#FFFFFF"
GREEN = "#16865B"
RED = "#D64545"
GOLD = "#E5A000"
GRAY = "#65758B"

# ---------------- MAIN WINDOW ----------------

root = tk.Tk()
root.title("Contact Book | Contact Manager")
root.geometry("900x650")
root.minsize(750, 580)
root.configure(bg=BG)

style = ttk.Style()
style.theme_use("clam")

style.configure(
    "Treeview",
    background=WHITE,
    foreground=DARK,
    rowheight=30,
    fieldbackground=WHITE,
    font=("Arial", 10)
)

style.configure(
    "Treeview.Heading",
    background=BLUE,
    foreground=WHITE,
    font=("Arial", 10, "bold"),
    padding=8
)

style.map(
    "Treeview",
    background=[("selected", "#D9E7FF")],
    foreground=[("selected", DARK)]
)

# ---------------- HEADER ----------------

header = tk.Frame(root, bg=BLUE, height=85)
header.pack(fill="x")
header.pack_propagate(False)

tk.Label(
    header,
    text="CONTACT BOOK",
    font=("Arial", 23, "bold"),
    bg=BLUE,
    fg=WHITE
).pack(pady=(13, 0))

tk.Label(
    header,
    text="Manage your contacts in one place",
    font=("Arial", 10),
    bg=BLUE,
    fg=WHITE
).pack(pady=3)

# ---------------- CONTACT FORM ----------------

form = tk.Frame(root, bg=WHITE, padx=18, pady=12)
form.pack(fill="x", padx=20, pady=(15, 8))

tk.Label(
    form,
    text="Contact Details",
    font=("Arial", 14, "bold"),
    bg=WHITE,
    fg=DARK
).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 10))

tk.Label(form, text="Name *", bg=WHITE, fg=GRAY).grid(
    row=1, column=0, sticky="w", padx=(0, 8)
)
tk.Label(form, text="Email", bg=WHITE, fg=GRAY).grid(
    row=1, column=1, sticky="w", padx=8
)
tk.Label(form, text="Phone Number *", bg=WHITE, fg=GRAY).grid(
    row=1, column=2, sticky="w", padx=8
)

name_entry = tk.Entry(form, font=("Arial", 11), relief="solid", bd=1)
email_entry = tk.Entry(form, font=("Arial", 11), relief="solid", bd=1)
phone_entry = tk.Entry(form, font=("Arial", 11), relief="solid", bd=1)

name_entry.grid(row=2, column=0, sticky="ew", padx=(0, 8), ipady=6)
email_entry.grid(row=2, column=1, sticky="ew", padx=8, ipady=6)
phone_entry.grid(row=2, column=2, sticky="ew", padx=8, ipady=6)

form.grid_columnconfigure(0, weight=1)
form.grid_columnconfigure(1, weight=1)
form.grid_columnconfigure(2, weight=1)

# ---------------- BUTTON HELPER ----------------

def make_button(parent, text, command, color):
    return tk.Button(
        parent,
        text=text,
        command=command,
        bg=color,
        fg=WHITE,
        activebackground=color,
        activeforeground=WHITE,
        font=("Arial", 10, "bold"),
        relief="flat",
        cursor="hand2",
        padx=12,
        pady=8
    )

# ---------------- CONTACT TABLE ----------------

table_frame = tk.Frame(root, bg=WHITE, padx=12, pady=12)
table_frame.pack(fill="both", expand=True, padx=20, pady=8)

tk.Label(
    table_frame,
    text="Saved Contacts",
    font=("Arial", 14, "bold"),
    bg=WHITE,
    fg=DARK
).pack(anchor="w", pady=(0, 10))

columns = ("name", "email", "phone")

contact_table = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings",
    selectmode="browse"
)

contact_table.heading("name", text="Name")
contact_table.heading("email", text="Email Address")
contact_table.heading("phone", text="Phone Number")

contact_table.column("name", width=180, anchor="w")
contact_table.column("email", width=280, anchor="w")
contact_table.column("phone", width=170, anchor="w")

scrollbar = ttk.Scrollbar(
    table_frame,
    orient="vertical",
    command=contact_table.yview
)
contact_table.configure(yscrollcommand=scrollbar.set)

scrollbar.pack(side="right", fill="y")
contact_table.pack(fill="both", expand=True)

# ---------------- STATUS ----------------

status_label = tk.Label(
    root,
    text="Ready",
    bg=BG,
    fg=GRAY,
    font=("Arial", 9)
)
status_label.pack(anchor="w", padx=22, pady=(0, 5))

# ---------------- FUNCTIONS ----------------

def clear_form():
    name_entry.delete(0, tk.END)
    email_entry.delete(0, tk.END)
    phone_entry.delete(0, tk.END)


def refresh_contacts(search_text=""):
    for item in contact_table.get_children():
        contact_table.delete(item)

    cursor.execute("""
        SELECT id, name, email, phone
        FROM contacts
        WHERE name LIKE ?
        ORDER BY name COLLATE NOCASE
    """, ("%" + search_text + "%",))

    contacts = cursor.fetchall()

    for contact in contacts:
        contact_id, name, email, phone = contact

        # Database ID is kept as the hidden Treeview item ID.
        contact_table.insert(
            "",
            tk.END,
            iid=str(contact_id),
            values=(name, email or "", phone)
        )

    status_label.config(
        text=f"Total contacts shown: {len(contacts)}"
    )


def fetch_api_contacts():
    url = "https://jsonplaceholder.typicode.com/users"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        users = response.json()

        # Clear the table before showing API contacts
        for item in contact_table.get_children():
            contact_table.delete(item)

        for user in users:
            contact_table.insert(
                "",
                tk.END,
                iid=f"api_{user['id']}",
                values=(
                    user.get("name", ""),
                    user.get("email", ""),
                    user.get("phone", "")
                )
            )

        status_label.config(
            text=f"API contacts loaded: {len(users)}"
        )

    except (requests.RequestException, ValueError) as error:
        messagebox.showerror(
            "API Error",
            f"Could not fetch contacts.\n{error}"
        )


def add_contact():
    name = name_entry.get().strip()
    email = email_entry.get().strip()
    phone = phone_entry.get().strip()

    if not name or not phone:
        messagebox.showwarning(
            "Missing Details",
            "Please enter Name and Phone Number."
        )
        return

    try:
        cursor.execute("""
            INSERT INTO contacts (name, email, phone)
            VALUES (?, ?, ?)
        """, (name, email, phone))

        conn.commit()
        refresh_contacts()
        clear_form()

        messagebox.showinfo(
            "Success",
            "Contact saved successfully!"
        )

    except sqlite3.Error as error:
        messagebox.showerror("Database Error", str(error))


def search_contact():
    search_text = search_entry.get().strip()
    refresh_contacts(search_text)


def show_all_contacts():
    search_entry.delete(0, tk.END)
    refresh_contacts()


def select_contact():
    selected = contact_table.selection()

    if not selected:
        messagebox.showwarning(
            "Select Contact",
            "Please select a contact from the table."
        )
        return None

    if selected[0].startswith("api_"):
        messagebox.showinfo(
            "API Contact",
            "API contacts are read-only. "
            "Load saved contacts to edit or delete them."
        )
        return None

    contact_id = int(selected[0])

    cursor.execute("""
        SELECT id, name, email, phone
        FROM contacts
        WHERE id = ?
    """, (contact_id,))

    return cursor.fetchone()


def edit_contact():
    contact = select_contact()

    if contact is None:
        return

    contact_id, name, email, phone = contact

    edit_window = tk.Toplevel(root)
    edit_window.title("Edit Contact")
    edit_window.geometry("380x300")
    edit_window.configure(bg=WHITE)
    edit_window.transient(root)
    edit_window.grab_set()

    tk.Label(
        edit_window,
        text="Update Contact",
        font=("Arial", 16, "bold"),
        bg=WHITE,
        fg=BLUE
    ).pack(pady=12)

    fields = []

    for label_text, value in [
        ("Name *", name),
        ("Email", email or ""),
        ("Phone Number *", phone)
    ]:
        tk.Label(
            edit_window,
            text=label_text,
            bg=WHITE,
            fg=DARK
        ).pack(anchor="w", padx=25)

        entry = tk.Entry(
            edit_window,
            font=("Arial", 11),
            relief="solid",
            bd=1
        )
        entry.pack(fill="x", padx=25, pady=(3, 8), ipady=4)
        entry.insert(0, value)
        fields.append(entry)

    def save_changes():
        new_name = fields[0].get().strip()
        new_email = fields[1].get().strip()
        new_phone = fields[2].get().strip()

        if not new_name or not new_phone:
            messagebox.showwarning(
                "Missing Details",
                "Name and Phone Number are required.",
                parent=edit_window
            )
            return

        try:
            cursor.execute("""
                UPDATE contacts
                SET name = ?, email = ?, phone = ?
                WHERE id = ?
            """, (new_name, new_email, new_phone, contact_id))

            conn.commit()
            refresh_contacts(search_entry.get().strip())
            edit_window.destroy()

            messagebox.showinfo(
                "Success",
                "Contact updated successfully!"
            )

        except sqlite3.Error as error:
            messagebox.showerror(
                "Database Error",
                str(error),
                parent=edit_window
            )

    make_button(
        edit_window,
        "Save Changes",
        save_changes,
        GREEN
    ).pack(pady=10)


def delete_contact():
    contact = select_contact()

    if contact is None:
        return

    contact_id, name, email, phone = contact

    confirm = messagebox.askyesno(
        "Confirm Delete",
        f"Do you want to delete {name}?"
    )

    if not confirm:
        return

    try:
        cursor.execute(
            "DELETE FROM contacts WHERE id = ?",
            (contact_id,)
        )
        conn.commit()

        refresh_contacts(search_entry.get().strip())

        messagebox.showinfo(
            "Success",
            "Contact deleted successfully!"
        )

    except sqlite3.Error as error:
        messagebox.showerror("Database Error", str(error))


def on_close():
    conn.close()
    root.destroy()


# ---------------- ACTION BUTTONS ----------------

actions = tk.Frame(root, bg=BG)
actions.pack(fill="x", padx=20, pady=5)

make_button(
    actions, "Save Contact", add_contact, BLUE
).pack(side="left", padx=(0, 8))

make_button(
    actions, "Edit Selected", edit_contact, GOLD
).pack(side="left", padx=8)

make_button(
    actions, "Delete Selected", delete_contact, RED
).pack(side="left", padx=8)


make_button(
    actions,
    "Load API Contacts",
    fetch_api_contacts,
    GREEN
).pack(side="left", padx=8)


# ---------------- SEARCH BAR ----------------

search_frame = tk.Frame(root, bg=BG)
search_frame.pack(fill="x", padx=20, pady=(5, 15))

tk.Label(
    search_frame,
    text="Search by name:",
    bg=BG,
    fg=DARK,
    font=("Arial", 10, "bold")
).pack(side="left", padx=(0, 8))

search_entry = tk.Entry(
    search_frame,
    font=("Arial", 11),
    relief="solid",
    bd=1
)
search_entry.pack(side="left", fill="x", expand=True, ipady=5)

make_button(
    search_frame, "Search", search_contact, GREEN
).pack(side="left", padx=6)

make_button(
    search_frame, "Show All", show_all_contacts, GRAY
).pack(side="left", padx=3)

search_entry.bind("<Return>", lambda event: search_contact())

# ---------------- START APPLICATION ----------------

refresh_contacts()
root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()
