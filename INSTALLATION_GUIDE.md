# Ghost Protocol Installation Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (for development)

## Installation Methods

### Method 1: Development Installation (Recommended)

1. **Clone or extract the project**:
   \`\`\`bash
   # If you have the ZIP file, extract it to a directory
   # If using git:
   git clone <repository-url>
   cd ghost-protocol
   \`\`\`

2. **Create a virtual environment**:
   \`\`\`bash
   python -m venv venv
   
   # Activate on Windows:
   venv\Scripts\activate
   
   # Activate on Linux/Mac:
   source venv/bin/activate
   \`\`\`

3. **Install in development mode**:
   \`\`\`bash
   pip install -e .
   \`\`\`

4. **Verify installation**:
   \`\`\`bash
   python scripts/quick_test.py
   \`\`\`

### Method 2: Direct Installation

1. **Install from source**:
   \`\`\`bash
   pip install .
   \`\`\`

2. **Or install with all dependencies**:
   \`\`\`bash
   pip install -r requirements.txt
   pip install .
   \`\`\`

## Running the Application

After successful installation, you can use these commands:

### Start the Team Server
\`\`\`bash
gpserver
# or
python -m ghost_protocol.server.main
\`\`\`

### Start the Client Console
\`\`\`bash
ghost
# or
python -m ghost_protocol.client.main
\`\`\`

### Start a Beacon
\`\`\`bash
gpbeacon
# or
python -m ghost_protocol.beacon.main
\`\`\`

## Troubleshooting

### Common Issues

1. **"No module named 'ghost_protocol'" error**:
   - Make sure you installed the package: `pip install -e .`
   - Check if you're in the correct directory
   - Verify virtual environment is activated

2. **PyQt6 GUI issues**:
   - On Linux: `sudo apt-get install python3-pyqt6`
   - On Mac: `brew install pyqt6`
   - On Windows: Should work with pip installation

3. **Database connection errors**:
   - Check if PostgreSQL is running (if using PostgreSQL)
   - Verify database credentials in configuration
   - Run database migrations: `alembic upgrade head`

4. **Port already in use**:
   - Check if another instance is running
   - Change port in configuration file
   - Kill existing processes: `pkill -f ghost_protocol`

5. **Permission errors**:
   - Run with appropriate permissions
   - Check file ownership and permissions
   - On Linux/Mac: `chmod +x scripts/*.py`

### Verification Steps

1. **Test imports**:
   \`\`\`python
   python -c "import ghost_protocol; print('Success!')"
   \`\`\`

2. **Test console commands**:
   \`\`\`bash
   gpserver --help
   ghost --help
   gpbeacon --help
   \`\`\`

3. **Run comprehensive tests**:
   \`\`\`bash
   python scripts/run_comprehensive_tests.py
   \`\`\`

## Configuration

1. **Copy example configuration**:
   \`\`\`bash
   cp config/config.example.yaml config/config.yaml
   \`\`\`

2. **Edit configuration file**:
   - Set database connection details
   - Configure network settings
   - Set security parameters

3. **Environment variables**:
   \`\`\`bash
   export GHOST_PROTOCOL_CONFIG=config/config.yaml
   export GHOST_PROTOCOL_LOG_LEVEL=INFO
   \`\`\`

## Development Setup

For development work:

1. **Install development dependencies**:
   \`\`\`bash
   pip install -r requirements.txt
   pip install -e .[dev]
   \`\`\`

2. **Set up pre-commit hooks**:
   \`\`\`bash
   pre-commit install
   \`\`\`

3. **Run tests**:
   \`\`\`bash
   pytest tests/
   \`\`\`

## Next Steps

After successful installation:
1. Read the documentation in `docs/`
2. Review the architecture guide
3. Start with the quickstart tutorial
4. Join the community for support

For more help, check the troubleshooting section or open an issue on GitHub.
