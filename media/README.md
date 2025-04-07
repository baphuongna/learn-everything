# Media Files Directory

This directory is used to store media files uploaded by users or provided by the system.

## Directory Structure

- `profile_pics/`: User profile pictures
- `subject_images/`: Images for subjects
- `lesson_images/`: Images used in lessons
- `flashcard_images/`: Images used in flashcards
- `memory_attachments/`: Files attached to memory items

## Usage

When uploading files through the application, they will be stored in the appropriate subdirectory based on their type.

## Development

In development mode, Django serves these files directly. In production, you should configure your web server (e.g., Nginx, Apache) to serve these files for better performance.

## Note

This directory should be excluded from version control (via .gitignore), but the directory structure should be maintained. The `.gitkeep` files are used to ensure the directories are tracked by Git even when empty.
