import flet as ft


# Define the main function for Flet
def main(page: ft.Page):
    page.title = "Notes App"
    page.theme_mode = ft.ThemeMode.LIGHT
    notes = []

    # Refresh all notes from the database
    def sync_notes():
        notes_controls.controls.clear()
        for note in notes:
            notes_controls.controls.append(
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(note, width=300),
                        ft.IconButton(icon=ft.icons.DELETE, data=note, on_click=delete_note),
                    ]
                )
            )
        notes_controls.update()

    # Add a new note to the database and refresh the list
    def add_note(e):
        note_text = new_note.value
        notes.append(note_text)
        if note_text:  # Only add if there's something to add
            new_note.value = ""
            new_note.update()
            sync_notes()

    # Delete a note from the database and refresh the list
    def delete_note(e):
        notes.remove(e.control.data)
        sync_notes()

    # Define Flet UI components
    new_note = ft.TextField(hint_text="Enter new note", width=300)
    notes_controls = ft.Column()

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
        notes_controls
    )

    # Initial sync of notes
    sync_notes()

# Run the Flet app
ft.app(target=main)
