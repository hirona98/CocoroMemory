# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Virtual Environment Setup (PowerShell)
```powershell
# Activate virtual environment
.venv\Scripts\activate

# Deactivate when done
deactivate
```

### Building the Application
```powershell
# Build standalone Windows executable
./build.ps1
```
This creates a portable Windows executable in `dist/CocoroMemory/` with embedded PostgreSQL.

### Running Development Server
```powershell
# Activate virtual environment first
.venv\Scripts\activate

# Run the FastAPI server
python src/main.py
```
The API documentation will be available at `http://localhost:8000/docs`

### Code Quality Tools
```powershell
# Run linter (Ruff)
ruff check .

# Run type checker
mypy .

# Format code with Ruff
ruff format .
```

## Architecture Overview

### Core Components

1. **FastAPI Application** (`src/main.py`)
   - Entry point for the application
   - Integrates ChatMemory library for conversation persistence
   - Manages PostgreSQL lifecycle through PostgresManager
   - Requires `OPENAI_API_KEY` in `.env` file

2. **PostgreSQL Manager** (`src/postgres_manager.py`)
   - Handles embedded PostgreSQL server initialization and lifecycle
   - Automatically finds PostgreSQL binaries in various locations
   - Creates and manages database with vector extension support
   - Default connection: `postgres://postgres:postgres@127.0.0.1:5433/postgres`

3. **Build System**
   - PyInstaller packages everything into a single Windows executable
   - PostgreSQL binaries are embedded in `_internal/pgsql/`
   - The `CocoroMemory.spec` file is auto-generated and modified by `build.ps1`

### Key Dependencies

- **chatmemory>=1.0.0**: Core conversation memory functionality with vector storage
- **fastapi/uvicorn**: Web API framework and server
- **psycopg2-binary**: PostgreSQL adapter
- **pyinstaller**: Creates standalone Windows executables

### Database Configuration

The embedded PostgreSQL instance:
- Runs on port 5433 (to avoid conflicts with standard PostgreSQL)
- Includes pgvector extension for AI embeddings
- Data stored in `Data/` directory
- Logs written to `Logs/postgresql.log`

### Distribution Structure

When built, the application creates:
```
dist/CocoroMemory/
├── CocoroMemory.exe      # Main executable
├── Data/                  # PostgreSQL data directory
├── Logs/                  # Application and database logs
├── Scripts/               # Database management scripts
│   ├── initdb.bat
│   ├── start_postgres.bat
│   └── stop_postgres.bat
└── _internal/             # Bundled runtime and PostgreSQL
    └── pgsql/
        └── bin/           # PostgreSQL executables
```

## Development Notes

- The application expects PostgreSQL binaries to be available either in the development environment (`pgsql/bin/`) or bundled in the distribution (`_internal/pgsql/bin/`)
- Database initialization is automatic on first run
- The `.env` file must contain `OPENAI_API_KEY` for the ChatMemory functionality
- Use Ruff for all formatting and linting (configured in `pyproject.toml`)

## ユーザーとのコミュニケーション

ユーザーとは日本語でコミュニケーションを取ること
コメントの言語は日本語にすること
