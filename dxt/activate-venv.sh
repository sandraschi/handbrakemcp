#!/bin/bash

# Bash script to activate DXT virtual environment

set -e

show_help() {
    echo "DXT Virtual Environment Management Script"
    echo ""
    echo "Usage: ./activate-venv.sh [options]"
    echo ""
    echo "Options:"
    echo "  --create   Create the virtual environment (if it doesn't exist)"
    echo "  --install  Install dependencies from requirements-dxt.txt"
    echo "  --help     Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./activate-venv.sh --create --install  # Create venv and install deps"
    echo "  ./activate-venv.sh                     # Activate existing venv"
    exit 0
}

CREATE_VENV=false
INSTALL_DEPS=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --create)
            CREATE_VENV=true
            shift
            ;;
        --install)
            INSTALL_DEPS=true
            shift
            ;;
        --help)
            show_help
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            ;;
    esac
done

VENV_PATH="./venv"
REQUIREMENTS_PATH="./requirements-dxt.txt"

if [ "$CREATE_VENV" = true ]; then
    echo "Creating virtual environment..."
    if [ -d "$VENV_PATH" ]; then
        echo "Virtual environment already exists. Removing..."
        rm -rf "$VENV_PATH"
    fi

    python3 -m venv "$VENV_PATH"
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment"
        exit 1
    fi
    echo "Virtual environment created successfully"
fi

if [ "$INSTALL_DEPS" = true ]; then
    if [ ! -d "$VENV_PATH" ]; then
        echo "Virtual environment does not exist. Creating..."
        python3 -m venv "$VENV_PATH"
    fi

    echo "Installing dependencies..."
    "$VENV_PATH/bin/python" -m pip install --upgrade pip
    "$VENV_PATH/bin/python" -m pip install -r "$REQUIREMENTS_PATH"
    if [ $? -ne 0 ]; then
        echo "Failed to install dependencies"
        exit 1
    fi
    echo "Dependencies installed successfully"
fi

# Activate the virtual environment
if [ -d "$VENV_PATH" ]; then
    echo "Activating virtual environment..."
    source "$VENV_PATH/bin/activate"
    if [ $? -ne 0 ]; then
        echo "Failed to activate virtual environment"
        exit 1
    fi
    echo "Virtual environment activated"
    echo "You can now run: python dxt/scripts/build.py"
else
    echo "Virtual environment does not exist. Run with --create flag first."
    exit 1
fi
