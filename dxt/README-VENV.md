# DXT Virtual Environment Setup

This directory contains a complete virtual environment setup for building DXT packages. The virtual environment ensures that all dependencies are properly isolated and available for building.

## Quick Start

### Option 1: Python Script (Cross-Platform)
```bash
python dxt/setup-venv.py
```

### Option 2: Platform-Specific Scripts

#### Windows
```powershell
.\dxt\activate-venv.ps1 -Create -Install
```

#### Unix/Linux
```bash
./dxt/activate-venv.sh --create --install
```

## What This Sets Up

1. **Virtual Environment**: Creates `dxt/venv/` with Python and pip
2. **Dependencies**: Installs all required packages from `requirements-dxt.txt`
3. **Isolation**: Keeps DXT building dependencies separate from your main Python environment
4. **Reproducibility**: Ensures consistent builds across different systems

## Requirements File

The `requirements-dxt.txt` file contains all necessary dependencies for:

- **Core Dependencies**: FastMCP, FastAPI, Uvicorn, Pydantic, etc.
- **Build Tools**: setuptools, wheel, build, pip, twine
- **Development Tools**: pytest, black, isort, mypy, flake8
- **Additional Libraries**: typing-extensions, anyio, starlette, etc.

## Using the Virtual Environment

### After Setup

Once the virtual environment is created and activated, you can:

1. **Build DXT Package**:
   ```bash
   python dxt/scripts/build.py
   ```

2. **Run Tests**:
   ```bash
   python -m pytest
   ```

3. **Check Available Packages**:
   ```bash
   python -c "import pkg_resources; [print(f'{p.project_name}=={p.version}') for p in pkg_resources.working_set]"
   ```

### Manual Activation

If you need to activate the environment manually:

#### Windows
```powershell
.\dxt\venv\Scripts\Activate.ps1
```

#### Unix/Linux
```bash
source ./dxt/venv/bin/activate
```

## Benefits

- **Clean Environment**: No conflicts with system Python packages
- **Reproducible Builds**: Same dependencies every time
- **Isolated Development**: Safe to install development packages
- **Easy Cleanup**: Just delete the `dxt/venv/` directory

## Troubleshooting

### Virtual Environment Not Found
If you get a "Virtual environment not found" error:
1. Run the setup script: `python dxt/setup-venv.py`
2. Or create manually: `python -m venv dxt/venv`
3. Then install requirements: `dxt/venv/bin/python -m pip install -r dxt/requirements-dxt.txt`

### Permission Issues (Unix/Linux)
```bash
chmod +x dxt/activate-venv.sh
chmod +x dxt/setup-venv.py
```

### Package Installation Issues
If pip install fails:
1. Ensure you have internet connection
2. Try upgrading pip first: `python -m pip install --upgrade pip`
3. Check if the requirements file exists and is readable

## File Structure

```
dxt/
├── venv/                    # Virtual environment (created)
├── requirements-dxt.txt     # Dependencies list
├── setup-venv.py           # Cross-platform setup script
├── activate-venv.ps1       # Windows activation script
├── activate-venv.sh        # Unix/Linux activation script
└── README-VENV.md          # This file
```

## Integration with Build Process

The `dxt/scripts/build.py` script automatically:
- Checks if the virtual environment exists
- Provides setup instructions if missing
- Uses the isolated environment for building
- Ensures all dependencies are available

This makes the DXT building process completely self-contained and reproducible.
