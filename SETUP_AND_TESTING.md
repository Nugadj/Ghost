# Ghost Protocol - Setup and Testing Guide

## Prerequisites

- Python 3.8 or higher
- Git (for cloning/downloading)
- Virtual environment (recommended)

## Installation Steps

### 1. Create Virtual Environment
\`\`\`bash
# Create virtual environment
python -m venv ghost_protocol_env

# Activate virtual environment
# On Windows:
ghost_protocol_env\Scripts\activate
# On macOS/Linux:
source ghost_protocol_env/bin/activate
\`\`\`

### 2. Install Dependencies
\`\`\`bash
# Install all dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
\`\`\`

### 3. Verify Installation
\`\`\`bash
# Check if console commands are available
gpserver --help
ghost --help
gpbeacon --help
\`\`\`

## Running the Project

### Option 1: Using Console Commands (Recommended)

#### Start the Team Server
\`\`\`bash
# Basic server startup
gpserver

# With custom host and port
gpserver 127.0.0.1 mypassword --port 50050

# With configuration file
gpserver --config config/server.yaml
\`\`\`

#### Start the Client GUI
\`\`\`bash
# Basic client startup
ghost

# Connect to specific server
ghost --server 127.0.0.1 --port 50050

# With configuration file
ghost --config config/client.yaml
\`\`\`

#### Start a Beacon
\`\`\`bash
# Basic beacon startup
gpbeacon

# With specific configuration
gpbeacon --config config/beacon.yaml
\`\`\`

### Option 2: Direct Python Execution

#### Start Team Server
\`\`\`bash
python -m ghost_protocol.server.main
\`\`\`

#### Start Client
\`\`\`bash
python -m ghost_protocol.client.main
\`\`\`

#### Start Beacon
\`\`\`bash
python -m ghost_protocol.beacon.main
\`\`\`

## Testing the Project

### 1. Run Unit Tests
\`\`\`bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=ghost_protocol --cov-report=html

# Run specific test files
python -m pytest tests/test_core_base.py -v
python -m pytest tests/test_database_models.py -v
\`\`\`

### 2. Run Integration Tests
\`\`\`bash
# Run integration tests
python -m pytest tests/test_integration.py -v

# Run security tests
python -m pytest tests/test_security.py -v
\`\`\`

### 3. Run Comprehensive Analysis
\`\`\`bash
# Run comprehensive test suite
python scripts/run_comprehensive_tests.py

# Run codebase analysis
python scripts/analyze_codebase.py
\`\`\`

## Troubleshooting Common Issues

### 1. Import Errors
If you encounter import errors, ensure:
- Virtual environment is activated
- Package is installed with `pip install -e .`
- All dependencies are installed

### 2. PyQt6 Issues
If GUI doesn't start:
\`\`\`bash
# Install PyQt6 separately
pip install PyQt6

# On Linux, you might need additional packages
sudo apt-get install python3-pyqt6
\`\`\`

### 3. Database Connection Issues
If database tests fail:
- Ensure PostgreSQL is running (if using asyncpg)
- Check database configuration in config files
- Verify database credentials

### 4. Network/Port Issues
If server won't start:
- Check if port is already in use: `netstat -an | grep 50050`
- Try different port: `gpserver --port 50051`
- Check firewall settings

## Configuration

### Server Configuration
Create `config/server.yaml`:
\`\`\`yaml
server:
  host: "0.0.0.0"
  port: 50050
  password: "your_secure_password"
  
database:
  url: "sqlite:///ghost_protocol.db"
  
logging:
  level: "INFO"
  file: "logs/server.log"
\`\`\`

### Client Configuration
Create `config/client.yaml`:
\`\`\`yaml
client:
  server_host: "127.0.0.1"
  server_port: 50050
  
logging:
  level: "INFO"
  file: "logs/client.log"
\`\`\`

## Development Workflow

### 1. Code Quality Checks
\`\`\`bash
# Format code
black ghost_protocol/

# Check linting
flake8 ghost_protocol/

# Type checking
mypy ghost_protocol/
\`\`\`

### 2. Pre-commit Hooks
\`\`\`bash
# Install pre-commit hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
\`\`\`

## Testing Checklist

- [ ] Virtual environment created and activated
- [ ] All dependencies installed successfully
- [ ] Package installed in development mode
- [ ] Console commands work (`gpserver --help`, `ghost --help`, `gpbeacon --help`)
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Server starts without errors
- [ ] Client GUI opens successfully
- [ ] Database connection works
- [ ] Network communication between components works

## Getting Help

If you encounter issues:
1. Check the logs in the `logs/` directory
2. Run the diagnostic script: `python scripts/analyze_codebase.py`
3. Ensure all dependencies are correctly installed
4. Check the GitHub issues for known problems
