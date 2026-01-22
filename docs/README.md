# Documentation & Reference Files

This folder contains documentation, archived files, and reference materials for the Aadhaar Identity Intelligence Platform.

## 📁 Contents

### Screenshots & Diagrams
- `banner.png` - Project banner
- `diagram_1.png` - System architecture diagram
- `diagram_2.png` - Data flow diagram
- `laptop_*.png` - Desktop UI screenshots
- `mobile_screens.png` - Mobile responsive views

### Archived Code
- `main_old_backup.py` - Previous version of main.py (before refactoring)

### Scripts & Setup
- `setup_new_platform.sh` - Initial platform setup script
- `start_backend.sh` - Backend startup script (Unix/Mac)
- `start_frontend.sh` - Frontend startup script (Unix/Mac)
- `start_platform.bat` - Platform startup script (Windows)
- `start_platform.sh` - Platform startup script (Unix/Mac)
- `run_sync.bat` - Data synchronization script (Windows)

### Tests
- `tests/` - Test files directory
  - `test_fuzzy_matching.py` - Fuzzy matching tests
  - `test_system.py` - System integration tests

### Notes
- `Untitled.md` - Miscellaneous notes

## 🚀 Quick Start (Production)

For production deployment, refer to the main README.md in the project root.

### Starting the Application

**On Windows:**
```bash
# Start backend
cd backend && python main.py

# Start frontend (in new terminal)
cd frontend && npm run dev
```

**On Unix/Mac:**
```bash
# Use the provided scripts
./docs/start_backend.sh
./docs/start_frontend.sh
```

## 📝 Development Notes

All active code is in:
- `/backend/` - FastAPI backend with production architecture
- `/frontend/` - React + Vite frontend
- `/backend/data/` - Aadhaar datasets (CSV files)

This `docs/` folder is for reference and archived materials only.
