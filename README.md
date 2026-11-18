# PoGO Pings

A Discord bot that monitors Pokémon GO promo codes and sends Discord alerts when new codes are discovered.

## Features

- Automatically checks for new Pokémon GO promo codes
- Sends Discord alerts when a new code is found
- Configuration through environment variables

## Project Structure

```
pogo-pings/
├── .github/workflows/   # CI / automation workflows
├── src/pogo_pings/      # Application source code
├── tests/               # Test suite
├── .env.example         # Example environment configuration
├── Dockerfile           # Container image definition
├── compose.yaml         # Docker Compose setup
└── pyproject.toml       # Project metadata and dependencies
```

## Getting Started

### Prerequisites

- Python 3.x (see `pyproject.toml` for the exact supported version)
- A Discord bot token or webhook URL
- Docker and Docker Compose (optional, for containerized deployment)

### 1. Clone the repository

```bash
git clone https://github.com/emiHuy/pogo-pings.git
cd pogo-pings
```

### 2. Configure environment variables

Copy the example file and fill in your values:

```bash
cp .env.example .env
```

Open `.env` and set each variable listed there.

### 3. Run it

**With Docker (recommended)**

```bash
docker compose up -d --build
```

View logs:

```bash
docker compose logs -f
```

**Locally with Python**

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e .
python -m pogo_pings
```

## Testing

```bash
pip install -e ".[dev]"
pytest
```

## How It Works

1. PoGO Pings periodically polls Leek Duck for Pokémon GO promo codes.
2. New codes are compared against codes it has already seen.
3. When a new code is found, an alert is posted to your Discord channel.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full breakdown.

### Poll Results

Each poll reports a summary of what happened:

| Key | Meaning |
| --- | --- |
| `processed` | New codes successfully sent to Discord |
| `skipped` | Codes already seen, so no alert was sent |
| `failed` | New codes whose alert failed |

## Sources

Promo codes are gathered from:

- [Leek Duck](https://leekduck.com) - a Pokémon GO news and info site

## Disclaimer

This project is not affiliated with or endorsed by Niantic, Nintendo, The Pokémon Company, Leek Duck, or Discord. Pokémon and Pokémon GO are trademarks of their respective owners.


## License

This project is licensed under the [MIT License](LICENSE).
