
#!/usr/bin/env python3
"""
NoteMaster - Modern Note Taking Application
A complete desktop note-taking solution with modern UI and database storage

Features:
- User authentication with secure password hashing
- Regular and password-protected notes
- Text editing with rich content
- Drawing/sketching capabilities
- Image attachments with thumbnail preview
- Audio recording and playback
- Modern gradient UI design
- SQLite database storage
- Responsive layout
"""

import sys
from PyQt5.QtWidgets import QApplication
from src.data.database_manager import SQLiteDatabaseManager
from src.data.user_repository import SQLiteUserRepository
from src.services.user_service import UserService
from src.ui.login_window import LoginWindow


def main():
    # Create QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("NoteMaster")
    app.setApplicationVersion("2.0")
    
    # Set application style
    app.setStyle("Fusion")
    
    # Initialize database and services
    db_manager = SQLiteDatabaseManager() # Singleton instance
    user_repository = SQLiteUserRepository()
    user_service = UserService(user_repository)
    
    # Create and show login window, injecting dependencies
    login_window = LoginWindow(user_service)
    login_window.show()
    
    # Run application
    exit_code = 0
    try:
        exit_code = app.exec_()
    finally:
        # Close database connection on exit
        db_manager.close()
        print("Application closed. Database connection terminated.")
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()


