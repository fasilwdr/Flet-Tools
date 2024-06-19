import flet as ft
import sqlite3

# Define the main function for Flet
def main(page: ft.Page):
    page.title = "Notes App"
    page.theme_mode = ft.ThemeMode.LIGHT

    # Refresh all notes from the database
    def sync_notes():
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, note FROM notes")
        all_notes = cursor.fetchall()
        notes.controls.clear()
        for note_id, note_text in all_notes:
            notes.controls.append(
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(note_text, width=300),
                        ft.IconButton(icon=ft.icons.DELETE, on_click=lambda e, note_id=note_id: delete_note(note_id)),
                    ]
                )
            )
        notes.update()
        conn.close()

    # Add a new note to the database and refresh the list
    def add_note(e):
        note_text = new_note.value
        if note_text:  # Only add if there's something to add
            conn = sqlite3.connect('data.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO notes (note) VALUES (?)", (note_text,))
            conn.commit()
            conn.close()
            new_note.value = ""
            new_note.update()
            sync_notes()

    # Delete a note from the database and refresh the list
    def delete_note(note_id):
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        conn.commit()
        conn.close()
        sync_notes()

    # Define Flet UI components
    new_note = ft.TextField(hint_text="Enter new note", width=300)
    notes = ft.Column()

    # Add components to the page
    page.add(
        ft.Row(
            controls=[
                new_note,
                ft.IconButton(icon=ft.icons.ADD, on_click=add_note)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        notes
    )

    # Initial sync of notes
    sync_notes()

# Run the Flet app
ft.app(target=main)
