# Makepro

![CI](https://github.com/noirAnayCO/makepro/actions/workflows/ci.yml/badge.svg)

Makepro is a lightweight terminal IDE focused on clean architecture, predictable behavior, and full control over the terminal.

The project aims to build a modular foundation for a powerful terminal-based development environment.

⚠️ Status: Early development.

---

## Features

Current foundations:

- Clean CLI lifecycle
- Structured project architecture
- Safe filesystem utilities
- Atomic file writing
- Terminal raw mode groundwork
- CI validation

Editor functionality is still under development.

---

## Quick Start

Clone the repository:

git clone https://github.com/YOURNAME/makepro  
cd makepro

Run Makepro:

PYTHONPATH=src python -m makepro

Open a file:

PYTHONPATH=src python -m makepro example.py

---

## CLI

makepro [file]

Options:

--version        Show version and exit  
--readonly       Open file in read-only mode  
--debug          Enable debug logging  
--config PATH    Path to config file  

---

## Project Structure

src/  
 └── makepro/  
     ├── __init__.py  
     ├── __main__.py  
     ├── app.py  
     ├── file_manager.py  
     │  
     ├── config/  
     ├── core/  
     ├── events/  
     ├── render/  
     ├── terminal/  
     └── ui/  

Architecture overview:

app → CLI lifecycle  
file_manager → filesystem abstraction  
terminal → terminal control  
render → rendering pipeline  
events → event system  
ui → UI components  
core → editor engine  

---

## Development

Syntax check:

python -m compileall src

Lint:

ruff check src

CI automatically validates:

- syntax
- imports
- lint rules
- license headers

---

## Roadmap

Planned systems:

- editing engine
- rendering engine
- syntax highlighting
- plugin system
- LSP integration
- high-performance renderer

---

## Long-Term Direction

Makepro is designed to eventually evolve into a serious terminal IDE.

A native C implementation is planned once the architecture stabilizes.

Python version → architecture experimentation  
C version → high-performance implementation  

---

## License

MIT License
