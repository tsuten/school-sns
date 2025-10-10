# Design Document

## Overview

The startup scripts system will provide a comprehensive set of cross-platform automation tools for the SNS-for-U22 project. The system consists of multiple script files that handle different aspects of project setup, development, and database management. The design focuses on modularity, cross-platform compatibility, and ease of use for developers at all experience levels.

The core architecture separates concerns into distinct script categories: main startup scripts, database management scripts, utility scripts, and configuration management. Each script will provide clear feedback, error handling, and logging to ensure developers can quickly identify and resolve issues.

## Architecture

### Script Organization

```
scripts/
├── start_dev.py               # Main development startup script
├── start_prod.py              # Production startup script  
├── setup.py                   # Initial project setup
├── db/
│   ├── __init__.py
│   ├── reset_db.py            # Database reset script
│   ├── migrate.py             # Migration management script
│   └── seed_data.py           # Test data generation script
├── utils/
│   ├── __init__.py
│   ├── platform_utils.py      # Cross-platform utilities
│   ├── dependency_checker.py  # Dependency checking utility
│   ├── installer.py           # Dependency installation utility
│   ├── process_manager.py     # Process management utilities
│   └── logger.py              # Logging utilities
├── config/
│   ├── __init__.py
│   ├── settings.py            # Configuration management
│   ├── dev.json               # Development configuration
│   ├── prod.json              # Production configuration
│   └── default.json           # Default configuration settings
└── main.py                    # Main CLI entry point
```

### Cross-Platform Strategy

The system will use Python's built-in cross-platform capabilities:
- `os` and `sys` modules for platform detection and path handling
- `subprocess` module for cross-platform command execution
- `pathlib` for modern path handling
- Platform-specific logic encapsulated in utility functions
- JSON configuration files for easy parsing and modification

### Process Management

For concurrent process management (running Django and SvelteKit simultaneously):
- Unix systems: Use background processes with process groups for clean termination
- Windows: Use `start` command with process tracking
- Implement graceful shutdown handlers for both platforms

## Components and Interfaces

### 1. Main Startup Scripts

#### start-dev.sh/.bat
**Purpose**: Primary development environment startup
**Interface**: 
- Input: Optional port configurations via environment variables or command line args
- Output: Running Django server (default port 8000) and SvelteKit dev server (default port 5173)
- Logging: Progress messages, error handling, server status

**Key Functions**:
- Dependency verification
- Virtual environment setup/activation
- Package installation (Python and npm)
- Database migration
- Concurrent server startup
- Process monitoring and cleanup

#### start-prod.sh/.bat
**Purpose**: Production environment startup
**Interface**:
- Input: Production configuration file
- Output: Production-ready Django server with built SvelteKit frontend
- Logging: Production-level logging with timestamps

**Key Functions**:
- Production dependency verification
- Frontend build process
- Static file collection
- Production server startup
- SSL/security configuration handling

#### setup.sh/.bat
**Purpose**: Initial project setup for new developers
**Interface**:
- Input: Optional configuration parameters
- Output: Fully configured development environment
- Logging: Step-by-step setup progress

**Key Functions**:
- System dependency checking
- Virtual environment creation
- Initial package installation
- Database initialization
- Configuration file setup

### 2. Database Management Scripts

#### db/reset-db.sh/.bat
**Purpose**: Complete database reset and fresh migration
**Interface**:
- Input: Confirmation prompt (with --force flag to skip)
- Output: Fresh database with all migrations applied
- Logging: Backup creation, deletion confirmation, migration progress

**Key Functions**:
- Database backup creation
- SQLite file deletion
- Fresh migration execution
- Error recovery for failed migrations

#### db/migrate.sh/.bat
**Purpose**: Handle Django migrations with error recovery
**Interface**:
- Input: Optional app name for specific migrations
- Output: Successfully migrated database
- Logging: Migration status, error details, recovery steps

**Key Functions**:
- Standard migration execution
- Individual app migration fallback
- Migration conflict resolution
- Rollback capabilities

#### db/seed-data.sh/.bat
**Purpose**: Generate test data using existing Django scripts
**Interface**:
- Input: Optional data volume parameters
- Output: Database populated with test data
- Logging: Data generation progress, record counts

**Key Functions**:
- Execute existing random user generation
- Execute existing circle generation
- Custom data scenarios
- Data validation

### 3. Utility Scripts

#### utils/check-deps.sh/.bat
**Purpose**: Verify all required dependencies are installed
**Interface**:
- Input: None
- Output: Dependency status report
- Return codes: 0 for success, non-zero for missing dependencies

**Key Functions**:
- Python version checking (3.8+)
- Node.js version checking (16+)
- pip availability
- npm availability
- Virtual environment tools

#### utils/install-deps.sh/.bat
**Purpose**: Automated dependency installation
**Interface**:
- Input: Optional package manager preferences
- Output: Installed dependencies
- Logging: Installation progress, error handling

**Key Functions**:
- Python package installation from requirements.txt
- npm package installation in frontend directory
- Virtual environment creation
- Package manager updates

#### utils/cleanup.sh/.bat
**Purpose**: Clean up development artifacts and processes
**Interface**:
- Input: Optional cleanup scope (cache, processes, files)
- Output: Cleaned development environment
- Logging: Cleanup actions performed

**Key Functions**:
- Stop running development servers
- Clean Python cache files
- Clean npm cache and node_modules
- Remove temporary files

## Data Models

### Configuration Schema

```json
{
  "ports": {
    "django": 8000,
    "sveltekit": 5173
  },
  "paths": {
    "venv": ".venv",
    "frontend": "web-frontend/app",
    "backend": "sns"
  },
  "database": {
    "backup_before_reset": true,
    "auto_migrate": true
  },
  "logging": {
    "level": "INFO",
    "file": "scripts/logs/startup.log"
  }
}
```

### Environment Variables

```bash
# Development
DJANGO_PORT=8000
SVELTEKIT_PORT=5173
VENV_PATH=.venv
DEBUG=true

# Production
DJANGO_SETTINGS_MODULE=sns.settings_prod
STATIC_ROOT=/var/www/static
MEDIA_ROOT=/var/www/media
```

### Process Tracking

```json
{
  "processes": [
    {
      "name": "django",
      "pid": 12345,
      "port": 8000,
      "status": "running"
    },
    {
      "name": "sveltekit",
      "pid": 12346,
      "port": 5173,
      "status": "running"
    }
  ]
}
```

## Error Handling

### Error Categories

1. **Dependency Errors**: Missing Python, Node.js, pip, npm
   - Detection: Version checking commands
   - Recovery: Clear installation instructions with platform-specific links

2. **Permission Errors**: Virtual environment creation, file access
   - Detection: Command exit codes and error messages
   - Recovery: Permission fixing instructions, alternative paths

3. **Network Errors**: Package installation failures
   - Detection: pip/npm error codes
   - Recovery: Retry mechanisms, alternative package sources

4. **Database Errors**: Migration failures, corruption
   - Detection: Django management command exit codes
   - Recovery: Individual app migrations, database reset options

5. **Port Conflicts**: Server startup failures
   - Detection: Port binding errors
   - Recovery: Alternative port suggestions, process killing

### Error Recovery Strategies

- **Graceful Degradation**: Continue with available functionality when non-critical components fail
- **Automatic Retry**: Retry network operations with exponential backoff
- **User Guidance**: Provide specific, actionable error messages with next steps
- **Rollback Capability**: Ability to undo changes when setup fails partway through

## Testing Strategy

### Unit Testing

- **Script Function Testing**: Test individual functions within scripts using shell testing frameworks
- **Configuration Parsing**: Verify configuration file parsing and validation
- **Error Handling**: Test error conditions and recovery mechanisms

### Integration Testing

- **End-to-End Workflows**: Test complete startup sequences from clean state
- **Cross-Platform Testing**: Verify scripts work on Windows, macOS, and Linux
- **Database Operations**: Test migration and reset operations with various database states

### Manual Testing Scenarios

1. **Fresh Installation**: Test setup on clean system without any dependencies
2. **Partial Installation**: Test with some dependencies already installed
3. **Corrupted State**: Test recovery from various failure states
4. **Port Conflicts**: Test behavior when default ports are occupied
5. **Permission Issues**: Test behavior with restricted file system permissions

### Automated Testing Pipeline

- **CI/CD Integration**: Run tests on multiple platforms in continuous integration
- **Docker Testing**: Use containers to simulate clean installation environments
- **Regression Testing**: Ensure new changes don't break existing functionality

### Performance Testing

- **Startup Time**: Measure and optimize script execution time
- **Resource Usage**: Monitor CPU and memory usage during operations
- **Concurrent Operations**: Test stability when running multiple scripts simultaneously

### Validation Testing

- **Configuration Validation**: Test with various configuration file formats and values
- **Input Validation**: Test script behavior with invalid command line arguments
- **Environment Validation**: Test in various system configurations and states