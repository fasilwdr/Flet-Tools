import flet as ft
import db
from db import execute_query

# Define the main function for Flet
def main(page: ft.Page):
    page.title = "Notes App"
    page.theme_mode = ft.ThemeMode.LIGHT

    # Refresh all notes from the database
    def sync_notes():
        all_notes = execute_query("SELECT id, note FROM notes")
        notes.controls.clear()
        for note_id, note_text in all_notes:
            notes.controls.append(
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(note_text, width=300),
                        ft.IconButton(icon=ft.icons.DELETE, data=note_id, on_click=delete_note),
                    ]
                )
            )
        notes.update()

    # Add a new note to the database and refresh the list
    def add_note(e):
        note_text = new_note.value
        if note_text:  # Only add if there's something to add
            execute_query("INSERT INTO notes (note) VALUES (?)", (note_text,))
            new_note.value = ""
            new_note.update()
            sync_notes()

    # Delete a note from the database and refresh the list
    def delete_note(e):
        execute_query("DELETE FROM notes WHERE id = ?", (e.control.data,))
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
ft.app(target=main, assets_dir='assets')
