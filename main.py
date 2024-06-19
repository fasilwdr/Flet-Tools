import flet as ft
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

# Define SQLAlchemy Base and Notes model
Base = declarative_base()

class Notes(Base):
    __tablename__ = 'notes'
    id = Column(Integer, primary_key=True)
    note = Column(String, nullable=False)

# Initialize the SQLite engine and create a session
engine = create_engine('sqlite:///data.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

# Create the table if it does not exist
Base.metadata.create_all(engine)

# Define the main function for Flet
def main(page: ft.Page):
    page.title = "Notes App"
    page.theme_mode = ft.ThemeMode.LIGHT

    # Refresh all notes from the database
    def sync_notes():
        all_notes = session.query(Notes).all()
        notes.controls.clear()
        for note in all_notes:
            notes.controls.append(
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(note.note, width=300),
                        ft.IconButton(icon=ft.icons.DELETE, on_click=lambda e, note_id=note.id: delete_note(note_id)),
                    ]
                )
            )
        notes.update()

    # Add a new note to the database and refresh the list
    def add_note(e):
        note_text = new_note.value
        if note_text:  # Only add if there's something to add
            session.add(Notes(note=note_text))
            session.commit()
            new_note.value = ""
            new_note.update()
            sync_notes()

    # Delete a note from the database and refresh the list
    def delete_note(note_id):
        note_to_delete = session.query(Notes).get(note_id)
        if note_to_delete:
            session.delete(note_to_delete)
            session.commit()
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
