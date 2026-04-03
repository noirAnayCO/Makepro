# Makepro

<div align="center" style="text-align: justify;">

```
  __  __       _                         
 |  \/  | __ _| | _____ _ __  _ __ ___  
 | |\/| |/ _` | |/ / _ \ '_ \| '__/ _ \ 
 | |  | | (_| |   <  __/ |_) | | | (_) |
 |_|  |_|\__,_|_|\_\___| .__/|_|  \___/ 
                        |_|              
```
A lightweight, hackable terminal IDE — built from scratch, raw terminal first.

[![CI](https://github.com/noirAnayCO/makepro/actions/workflows/ci.yml/badge.svg)](https://github.com/noirAnayCO/makepro/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Status: Early Development](https://img.shields.io/badge/status-early%20development-orange)](#)

</div>

-----

Makepro is a terminal text editor written in Python, built entirely on raw terminal I/O — no TUI framework dependencies. It is designed around clean architecture, full control over the terminal, and an explicit path toward a high-performance native C implementation.

> **⚠️ Early development.** Core editing functionality is under active construction.

-----

## Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Architecture](#architecture)
- [Development](#development)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

-----

## Features

- **Raw terminal renderer** — built directly on `termios`, no Textual or curses dependency
- **Atomic file writes** — data never lost on save; temp-file + `os.replace` strategy
- **Modular architecture** — every subsystem (`terminal`, `render`, `events`, `ui`, `core`) is independently developed and replaceable
- **Clean CLI lifecycle** — argument parsing, logging, TTY validation, and error handling all separated from editor logic
- **Structured logging** — configurable verbosity, debug tracebacks on demand
- **Strict CI** — syntax checks, import validation, lint (ruff), and license header enforcement on every push

-----

## Installation

**From source (recommended during early development):**

```sh
git clone https://github.com/noirAnayCO/makepro --depth=1 && cd makepro
pip install -e .
```

**Run without installing:**

```sh
git clone https://github.com/noirAnayCO/makepro --depth=1 && cd makepro
PYTHONPATH=src python -m makepro
```

**Note: Requires Python 3.10 or later.**

-----

## Usage

```sh
makepro                    # Open with no file
makepro path/to/file.py    # Open a file
makepro --readonly file.py # Open in read-only mode
makepro --debug file.py    # Enable debug logging + full tracebacks
makepro --version          # Print version
makepro --config path.toml # Use a custom config file
```

**Exit codes:**

|Code|Meaning                            |
|----|-----------------------------------|
|0   |Success                            |
|1   |User error (bad args, missing file)|
|2   |Unexpected fatal error             |
|130 |Interrupted (Ctrl-C / SIGINT)      |
|160 |stdin/stdout is not a TTY          |

-----

## Architecture

Makepro is structured as a set of isolated packages, each with a single defined responsibility:

```
src/makepro/
├── app.py           — CLI entry point, lifecycle management
├── file_manager.py  — filesystem abstraction (read, write, validate)
│
├── terminal/        — raw terminal control (termios, raw mode, I/O)
├── render/          — rendering pipeline (diff, draw, cursor)
├── events/          — event loop and input dispatch
├── ui/              — UI components and layout
├── core/            — editor engine (buffer, cursor, commands)
└── config/          — configuration loading and defaults
```

**Data flow:**

```
CLI args → app.py → terminal/raw_mode → events → core (buffer) → render → terminal output
```

The Python implementation is the architecture experimentation layer. Once the design stabilises, a native C port is planned for performance-critical paths.

-----

## Development

**Syntax check:**

```sh
python -m compileall src
```

**Lint:**

```sh
ruff check src
```

**Run from source:**

```sh
PYTHONPATH=src python -m makepro
```

**CI checks (run automatically on push):**

- Python syntax validation (`compileall`)
- Import smoke test
- Lint (`ruff`)
- MIT license header enforcement (`addlicense`)

-----

## Roadmap

|Status|System                   |
|------|-------------------------|
|🔨     |Raw terminal renderer    |
|🔨     |Event loop               |
|⬜     |Buffer and editing engine|
|⬜     |Syntax highlighting      |
|⬜     |Configuration system     |
|⬜     |Plugin interface         |
|⬜     |LSP integration          |
|⬜     |Native C port            |

-----

## Contributing

Makepro is early-stage and the architecture is still being defined. Contributions, issues, and design feedback are welcome.

1. Fork the repository
1. Create a feature branch: `git checkout -b feat/your-feature`
1. Ensure CI passes locally (syntax, lint, license headers)
1. Open a pull request with a clear description

All source files must carry the MIT license header:

```python
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Anay
```

-----

## License

[MIT](./LICENSE) © 2026 noirAnayCO
