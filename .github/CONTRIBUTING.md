# Contributing to HandBrake MCP Server

Thank you for your interest in contributing to the HandBrake MCP Server! 🎉

This document provides guidelines and information for contributors. Whether you're fixing bugs, adding features, improving documentation, or helping with testing, your contributions are welcome and appreciated.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Community](#community)

## Code of Conduct

This project follows a [Code of Conduct](CODE_OF_CONDUCT.md) to ensure a welcoming environment for all contributors. By participating, you agree to abide by its terms.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- HandBrake CLI installed on your system
- Git

### Quick Setup

1. **Fork and Clone** the repository:
   ```bash
   git clone https://github.com/your-username/handbrake-mcp.git
   cd handbrake-mcp
   ```

2. **Set up development environment**:
   ```bash
   # Install dependencies
   pip install -e ".[dev]"

   # Install HandBrake CLI (see Installation docs)
   ```

3. **Run tests** to ensure everything works:
   ```bash
   python scripts/run_tests.py unit
   ```

## Development Setup

### Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Install in development mode
pip install -e ".[dev]"
```

### Pre-commit Hooks

We use pre-commit hooks to maintain code quality:

```bash
pip install pre-commit
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

## Making Changes

### Branch Naming

Use descriptive branch names following this pattern:
- `feature/description-of-feature`
- `bugfix/issue-description`
- `docs/update-documentation`
- `refactor/component-name`

Example:
```bash
git checkout -b feature/add-batch-processing
```

### Commit Messages

Follow conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Testing related changes
- `chore`: Maintenance tasks

Examples:
```
feat: add batch video processing support

fix: resolve memory leak in transcoding job

docs: update installation instructions for Windows
```

### Code Style

This project uses:
- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

All code must pass these checks before being merged.

## Testing

### Test Structure

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test real HandBrake CLI integration
- **End-to-End Tests**: Test complete workflows

### Running Tests

```bash
# Run all unit tests
python scripts/run_tests.py unit

# Run integration tests (requires HandBrake CLI)
python scripts/run_tests.py integration

# Run all tests
python scripts/run_tests.py all

# Run specific test file
pytest tests/test_handbrake.py -v
```

### Writing Tests

- Use `pytest` framework
- Place test files in `tests/` directory
- Name test files as `test_*.py`
- Use descriptive test function names
- Include docstrings for complex tests

Example:
```python
def test_transcode_success(unit_test_setup):
    """Test successful video transcoding."""
    setup = unit_test_setup

    job_id = await setup['service'].transcode(
        input_path=str(setup['input_file']),
        output_path=str(setup['output_file']),
        preset="Fast 1080p30",
    )

    assert job_id is not None
    # ... more assertions
```

## Submitting Changes

### Pull Request Process

1. **Create a Branch** from `main`
2. **Make Your Changes** following the guidelines above
3. **Test Thoroughly** - ensure all tests pass
4. **Update Documentation** if needed
5. **Create Pull Request** with a clear description

### Pull Request Template

Use the provided PR template which includes:
- Description of changes
- Type of change
- Testing information
- Checklist for common requirements

### Review Process

1. **Automated Checks**: CI/CD will run tests and quality checks
2. **Code Review**: Maintainers will review your code
3. **Feedback**: Address any review comments
4. **Approval**: PR will be merged once approved

### What to Expect

- **Response Time**: PRs are typically reviewed within 1-2 business days
- **Feedback**: Constructive feedback to improve code quality
- **Iteration**: Multiple review cycles are normal
- **Help**: Feel free to ask questions during review

## Community

### Getting Help

- **Issues**: For bugs and feature requests
- **Discussions**: For questions and general discussion
- **Documentation**: Check the [docs](https://sandraschi.github.io/handbrake-mcp/) first

### Communication

- Be respectful and constructive
- Use clear, descriptive language
- Include context and examples when possible
- Help others when you can

### Recognition

Contributors are recognized in:
- Git commit history
- Changelog for significant contributions
- Project documentation

## Development Workflow

### For Small Changes

1. Create issue (optional for small fixes)
2. Create branch and make changes
3. Test locally
4. Submit PR
5. Address feedback
6. Merge

### For Large Features

1. Create issue with detailed description
2. Discuss approach in issue comments
3. Create branch and implement incrementally
4. Submit PR for initial review early
5. Iterate based on feedback
6. Complete implementation
7. Final review and merge

## Additional Resources

- [Installation Guide](https://sandraschi.github.io/handbrake-mcp/installation/)
- [API Documentation](https://sandraschi.github.io/handbrake-mcp/api/tools/)
- [Development Guide](https://sandraschi.github.io/handbrake-mcp/development/contributing/)
- [Project Roadmap](https://sandraschi.github.io/handbrake-mcp/about/roadmap/)

Thank you for contributing to the HandBrake MCP Server! 🚀

