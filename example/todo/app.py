from datetime import datetime

import streamlit as st
from models import Base, Tag, Todo
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Initialize database
engine = create_engine("sqlite:///todos.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# Initialize session
session = Session()

# Streamlit UI
st.title("Todo-Manager")

# Sidebar for filtering
st.sidebar.header("Filter")
category_filter = st.sidebar.text_input("Kategorie filtern")
priority_filter = st.sidebar.slider("Priorität", 1, 5, (1, 5))
status_filter = st.sidebar.selectbox("Status", ["Alle", "Offen", "Abgeschlossen"])

# Main content
st.header("ToDos")

# Add new todo
with st.form("new_todo"):
    st.subheader("Neues Todo")
    title = st.text_input("Titel", "")
    description = st.text_area("Beschreibung", "")
    priority = st.slider("Priorität", 1, 5, 3)
    category = st.text_input("Kategorie", "")
    due_date = st.date_input("Fällig am", datetime.now())
    tags = st.text_input("Tags (durch Komma getrennt)", "")

    if st.form_submit_button("Todo hinzufügen"):
        if title:
            todo = Todo(
                title=title,
                description=description,
                priority=priority,
                category=category,
                due_date=due_date,
            )

            # Add tags
            tag_names = [tag.strip() for tag in tags.split(",") if tag.strip()]
            for tag_name in tag_names:
                tag = session.query(Tag).filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    session.add(tag)
                todo.tags.append(tag)

            session.add(todo)
            session.commit()
            st.success("Todo wurde erfolgreich hinzugefügt!")

# Display todos
st.subheader("Todo-Liste")

# Filter todos
todos = session.query(Todo).filter(
    Todo.category.like(f"%{category_filter}%" if category_filter else "%"),
    Todo.priority.between(priority_filter[0], priority_filter[1]),
)

if status_filter == "Offen":
    todos = todos.filter(~Todo.is_completed)
elif status_filter == "Abgeschlossen":
    todos = todos.filter(Todo.is_completed)

# Sort todos
sort_by = st.radio(
    "Sortieren nach", ["Priorität", "Fällig am", "Erstellt am"], horizontal=True
)
if sort_by == "Priorität":
    todos = todos.order_by(Todo.priority)
elif sort_by == "Fällig am":
    todos = todos.order_by(Todo.due_date)
else:
    todos = todos.order_by(Todo.created_at.desc())

# Display todos
for todo in todos.all():
    with st.expander(f"{todo.title} (Priorität: {todo.priority})"):
        st.write(f"**Beschreibung:** {todo.description}")
        st.write(f"**Kategorie:** {todo.category}")
        st.write(f"**Fällig am:** {todo.due_date.strftime('%d.%m.%Y')}")
        st.write(f"**Tags:** {', '.join(tag.name for tag in todo.tags)}")

        # Todo actions
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Als erledigt markieren", key=f"complete_{todo.id}"):
                todo.is_completed = True
                todo.completion_date = datetime.now()
                session.commit()
                st.success("Todo wurde als erledigt markiert!")
        with col2:
            if st.button("Löschen", key=f"delete_{todo.id}", type="primary"):
                session.delete(todo)
                session.commit()
                st.success("Todo wurde gelöscht!")

# Close session
session.close()
