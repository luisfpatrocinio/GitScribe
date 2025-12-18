# GitScribe ✍️ 🤖

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Typer](https://img.shields.io/badge/CLI-Typer-white?style=for-the-badge&logo=fastapi)](https://typer.tiangolo.com/)
[![Gemini AI](https://img.shields.io/badge/AI-Google%20Gemini-orange?style=for-the-badge&logo=google)](https://deepmind.google/technologies/gemini/)
[![Code Style](https://img.shields.io/badge/Code%20Style-Black-black?style=for-the-badge)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

> **Stop writing commit messages. Let AI do it for you.**
> A professional CLI tool that analyzes your staged changes and generates semantic Git commit messages using Google Gemini.

---

## 🚀 Features (v0.4.0)

- **🤖 AI-Powered:** Uses Google's Gemini Flash model to understand code logic.
- **🧠 Context-Aware:** Reads a `.gitscribe-context` file from your repo root to understand project-specific rules or languages.
- **✨ Conventional Commits:** Ensures all messages follow the standard `type(scope): subject`.
- **⚡ Direct Workflow:** Just run `git-scribe` and let the magic happen.
- **🔍 Debug Mode:** Check exactly what was sent to the AI with `--last-prompt`.
- **🏎️ Express Mode (`--auto`):** Automatically stages, commits, and pushes without confirmation.
- **🎨 Adaptive Styles:** Choose your output style (`concise`, `default`, `detailed`).
- **🛡️ Large Diff Handling:** Filters huge files automatically to prevent API errors.
- **💎 Cyber Blue UI:** A beautiful, terminal-agnostic interface built with **Rich**.

---

## 🛠️ Installation

### Option 1: Global Usage (Recommended)

Use [pipx](https://pypa.github.io/pipx/) to run GitScribe from any directory on your system.

```bash
# Clone the repository
git clone https://github.com/luisfpatrocinio/GitScribe.git
cd GitScribe

# Install in editable mode
pipx install -e .
```

### Option 2: Development Setup

If you want to contribute to the code:

```bash
# Install dependencies with Poetry
poetry install
```

### 🔑 Configuration

Create a `.env` file in the root directory (GitScribe will find it automatically, even when running globally):

```bash
cp .env.example .env
```

Add your API Key:

```env
GEMINI_API_KEY=your_actual_api_key_here
```

---

## 💻 Usage

If installed via `pipx`, just run the command in any git repository:

```bash
git-scribe
```

### Options

| Flag            | Short | Description                                                                       |
| --------------- | ----- | --------------------------------------------------------------------------------- |
| `--add`         | `-A`  | **Stage All:** Run `git add .` before generating the message.                     |
| `--auto`        | `-a`  | **Express Mode:** Automatically stage all, commit, and push without confirmation. |
| `--style`       | `-s`  | Output style: `concise`, `default`, or `detailed`.                                |
| `--context`     | `-c`  | Provide extra context to the AI (e.g., "Fixing the login bug").                   |
| `--last-prompt` |       | Show the exact prompt sent to Gemini in the last execution (Debug).               |
| `--help`        |       | Show detailed help and commands.                                                  |

---

## 🧠 Advanced Usage: Project Context

GitScribe v0.4.0+ supports project-specific context.
Create a file named `.gitscribe-context` in the root of your repository. GitScribe will read this file and send it to the AI to improve accuracy.

**Example `.gitscribe-context`:**

```text
Project: E-commerce Backend
Language: Python (Django)
Style: Formal, avoiding emojis in commit messages.
Focus: Pay attention to database migration files.
```

---

## 🏗️ Project Structure

This project follows a professional modular architecture:

```text
GitScribe/
├── src/git_scribe/
│   ├── ai_ops.py    # Gemini API logic & Logging
│   ├── git_ops.py   # Git subprocess wrapper
│   ├── config.py    # Environment & Path management
│   ├── main.py      # Typer CLI entry point
│   └── ui.py        # Rich UI components & Theme
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
