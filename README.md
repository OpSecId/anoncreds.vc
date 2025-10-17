# anoncreds.vc

A Flask-based application for anonymous credentials verification.

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) - Fast Python package installer and resolver

## Installation

1. Install uv if you haven't already:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Clone the repository:
   ```bash
   git clone <repository-url>
   cd anoncreds.vc
   ```

3. Install dependencies:
   ```bash
   uv sync
   ```
   
   Note: The project is configured as an application (not a package), so uv will install dependencies without trying to build the project itself.

## Usage

### Development

Run the application in development mode:
```bash
uv run python main.py
```

Note: Make sure to configure the required environment variables before running the application.

### Production

The application can be run with Gunicorn:
```bash
uv run gunicorn --bind 0.0.0.0:5000 --workers 4 main:app
```

### Docker

Build and run with Docker:
```bash
docker build -t anoncreds-vc .
docker run -p 5000:5000 anoncreds-vc
```

## Development

### Adding Dependencies

To add a new dependency:
```bash
uv add <package-name>
```

To add a development dependency:
```bash
uv add --dev <package-name>
```

### Updating Dependencies

To update all dependencies:
```bash
uv sync --upgrade
```

### Running Commands

All Python commands should be run through uv:
```bash
uv run <command>
```

## Project Structure

- `app/` - Flask application code
- `config.py` - Configuration settings
- `main.py` - Application entry point
- `pyproject.toml` - Project configuration and dependencies
- `uv.lock` - Locked dependency versions