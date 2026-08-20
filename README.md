# KanMind Backend

KanMind Backend is a REST API for a Kanban board application built with Django and Django REST Framework.

The API provides user authentication as well as functionality for managing boards, tasks, board members, assignees, reviewers, and comments.

## Technologies

- Python
- Django
- Django REST Framework
- Token Authentication
- django-cors-headers
- SQLite

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/biancaliebholz/kanmind_backend.git
cd kanmind_backend
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

macOS / Linux:

```bash
source venv/bin/activate
```

Windows:

```bash
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Apply database migrations

```bash
python manage.py migrate
```

### 6. Create an admin user

```bash
python manage.py createsuperuser
```

Follow the instructions in the terminal to create the superuser.

### 7. Start the development server

```bash
python manage.py runserver
```

The API is then available at:

```text
http://127.0.0.1:8000/api/
```

The Django admin interface is available at:

```text
http://127.0.0.1:8000/admin/
```

## Authentication

The API uses Django REST Framework Token Authentication.

Authenticated requests must include the token in the HTTP header:

```text
Authorization: Token <your-token>
```

A token is returned after successful registration or login.

## API Structure

The API provides endpoints for:

- User registration and login
- Email lookup
- Boards and board members
- Tasks
- Assigned and reviewing tasks
- Task comments

Access to protected resources requires authentication. Additional permissions depend on board membership, ownership, task relationships, and comment authorship.

## Project Structure

```text
kanmind_backend/
├── auth_app/
│   └── api/
├── boards_app/
│   └── api/
├── task_app/
│   └── api/
├── core/
├── manage.py
├── requirements.txt
└── README.md
```

Each application contains its API-specific serializers, views, URLs, and permissions inside its `api/` directory.

## Project Features and Special Considerations

- A custom user model is used with email-based authentication instead of username-based authentication.
- The API uses Django REST Framework Token Authentication.
- CORS is configured to allow communication with the separately hosted frontend during development.
- Board access is restricted to the board owner and its members.
- Task access and modification depend on board membership and the respective permissions.
- Only authorized users can access protected API endpoints.
- Comments are associated with tasks and their authors.
- Only the author of a comment can delete that comment.
- The frontend is maintained separately and is not included in this repository.
- The local SQLite database is excluded from version control.

## Development

Check the Django configuration with:

```bash
python manage.py check
```

Run the development server with:

```bash
python manage.py runserver
```

## Notes

The SQLite database file is not included in the repository. After cloning the project, run the migrations to create a local database.

This project is intended for development and educational purposes.