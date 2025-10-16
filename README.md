# AI Office Tool — File Organizer (Enhanced Demo)

This enhanced demo includes:
- CLI with organize / undo / history commands
- Logging to .aioffice_logs/organizer.log
- History files (JSON) stored per organize action for undo

## Usage
Organize files:
    python file_organizer_enhanced.py organize ./test_files

Dry run:
    python file_organizer_enhanced.py organize ./test_files --dry-run

Undo last organize:
    python file_organizer_enhanced.py undo ./test_files

List history:
    python file_organizer_enhanced.py history ./test_files
