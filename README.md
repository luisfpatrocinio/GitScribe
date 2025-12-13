# GitScribe ✍️🤖

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Typer](https://img.shields.io/badge/CLI-Typer-white?style=for-the-badge&logo=fastapi)](https://typer.tiangolo.com/)
[![Gemini AI](https://img.shields.io/badge/AI-Google%20Gemini-orange?style=for-the-badge&logo=google)](https://deepmind.google/technologies/gemini/)
[![Code Style](https://img.shields.io/badge/Code%20Style-Black-black?style=for-the-badge)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Stop writing commit messages. Let AI do it for you.**
> A professional CLI tool that analyzes your staged changes and generates semantic Git commit messages using Google Gemini.

---

## 🚀 Features

- **🤖 AI-Powered:** Uses Google's Gemini Flash model to understand code logic, not just text changes.
- **✨ Conventional Commits:** Ensures all messages follow the standard `type(scope): subject` format.
- **🛡️ Smart Checks:**
  - Auto-stages files if you forgot `git add .`.
  - Handles huge diffs by filtering generic large files or asking for context.
  - Prevents empty commits.
- **🎨 Beautiful UI:** Built with **Rich** for colorful diff summaries, spinners, and Markdown rendering.
- **⚡ Workflow Automation:** Can automatically push to remote and handle upstream branch creation.

---

## 🛠️ Installation

### Prerequisites

- Python 3.10+
- [Poetry](https://python-poetry.org/) (Recommended for dependency management)
- A Google Gemini API Key (Get it [here](https://aistudio.google.com/app/apikey))

### Setup (Development)

1. **Clone the repository:**

   ```bash
   git clone https://github.com/luisfpatrocinio/GitScribe.git
   cd GitScribe
   ```

2. **Install dependencies:**

   ```bash
   poetry install
   ```

3. **Configure Environment:**
   Create a `.env` file in the root directory:
   ```bash
   cp .env.example .env
   ```
   Add your API Key:
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
   ```

---

## 💻 Usage

To run the tool via Poetry:

```bash
poetry run git-scribe commit
```

### Options

| Flag        | Short | Description                                                                       |
| ----------- | ----- | --------------------------------------------------------------------------------- |
| `--context` | `-c`  | Provide extra context to the AI (e.g., "Fixing the login bug").                   |
| `--push`    | `-p`  | Automatically push to remote after a successful commit.                           |
| `--filter`  | `-f`  | Specific file extension to prioritize if the diff is too large (Default: `.gml`). |
| `--help`    |       | Show all available commands.                                                      |

### Examples

**Standard Commit:**

```bash
poetry run git-scribe commit
```

**With Context (Helps the AI understand intent):**

```bash
poetry run git-scribe commit -c "Refactoring the authentication middleware for better security"
```

**Commit and Push immediately:**

```bash
poetry run git-scribe commit --push
```

---

## 🏗️ Project Structure

This project follows a professional modular architecture:

```text
GitScribe/
├── src/git_scribe/
│   ├── ai_ops.py    # Gemini API integration
│   ├── git_ops.py   # Git subprocess wrapper
│   ├── config.py    # Settings management
│   ├── main.py      # Typer CLI entry point
│   └── ui.py        # Rich UI components
├── tests/           # Unit tests
├── pyproject.toml   # Dependencies & Metadata
└── README.md
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (Use **GitScribe** 😉)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.

---

<p align="center">
  Built with ❤️ by <a href="https://github.com/luisfpatrocinio">Luis Felipe Patrocinio</a>
</p>
