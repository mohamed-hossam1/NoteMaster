# NoteMaster - Modern Note Taking Application

NoteMaster is a complete desktop note-taking solution with a modern UI, user authentication, and diverse note-taking capabilities including rich text, sketching, image attachments, and audio recordings. It utilizes an SQLite database for persistent storage.

## Features

- **User Authentication**: Secure login and registration with password hashing (bcrypt).
- **Note Management**:
  - Create, view, and delete notes.
  - Regular notes.
  - Password-protected (secure) notes.
- **Rich Content Editing**:
  - Text editing for detailed notes.
  - Drawing/sketching canvas with adjustable brush size and color.
  - Image attachments with thumbnail previews and deletion.
  - Audio recording and playback within notes.
- **Modern UI**:
  - Custom-styled widgets with a gradient theme.
  - Frameless, draggable windows.
  - Responsive layouts internally.
- **Data Storage**:
  - SQLite database for users and note metadata.
  - User-specific folders for image and audio file storage.

## Technology Stack

- **Programming Language**: Python 3
- **UI Framework**: PyQt5
- **Database**: SQLite
- **Password Hashing**: bcrypt
- **Audio Handling**: PyAudio, wave

## Project Structure

```plaintext
NoteMaster-main/
├── data/                         # Database files and user media
│   ├── notes_app.db              # SQLite database file (auto-generated)
│   └── users/                    # User-specific media folders (auto-generated)
│       └── [username]/
│           ├── audio/
│           └── images/
├── src/
│   ├── core/                     # Core interfaces and security utilities
│   │   ├── __init__.py
│   │   ├── interfaces.py
│   │   └── security_utils.py
│   ├── data/                     # Database interaction logic
│   │   ├── __init__.py
│   │   ├── database_manager.py
│   │   ├── note_repository.py
│   │   └── user_repository.py
│   ├── services/                 # Business logic
│   │   ├── __init__.py
│   │   ├── note_service.py
│   │   ├── user_folder_manager.py
│   │   └── user_service.py
│   └── ui/                       # User interface components
│       ├── __init__.py
│       ├── add_note_window.py
│       ├── assets/              # UI image assets (icons, etc.)
│       │   ├── KEY.png
│       │   ├── addnote.png
│       │   ├── back.png
│       │   ├── exit.png
│       │   └── note.png
│       ├── base_window.py
│       ├── home_window.py
│       ├── login_window.py
│       ├── note_window.py
│       ├── shared_ui_components.py
│       ├── signup_window.py
│       └── styles/              # Stylesheets for UI windows
│           ├── __init__.py
│           ├── login_window_styles.py
│           └── signup_window_styles.py
├── .gitignore
├── main.py                      # Main application entry point
├── README.md                    # This file
└── requirements.txt             # Python dependencies
```

## Getting Started

### Prerequisites

- Python 3.7+
- `pip`
- Optional system packages for PyAudio:
  - Debian/Ubuntu: `sudo apt-get install portaudio19-dev python3-dev`
  - Fedora: `sudo dnf install portaudio-devel python3-devel`
  - macOS: `brew install portaudio`

### Installation

```bash
git clone https://github.com/mohamed-hossam1/NoteMaster.git
cd NoteMaster-main
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
pip install -r requirements.txt
```

### Running the Application

```bash
python main.py
```
