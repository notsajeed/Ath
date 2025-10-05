# Ath - AI Python Code Assistant

Ath is an intelligent Python code analysis tool that helps you understand and work with your Python codebase using AI. It analyzes your Python project structure and provides contextual assistance through an interactive chat interface.

## Features

- 🧠 **AI-Powered Python Analysis** - Understand your Python codebase with AI assistance
- 🔍 **Python Code Inspection** - Browse and analyze individual Python files, functions, and classes
- 💬 **Interactive Chat** - Ask questions about your Python code in natural language
- 🤖 **Multiple AI Providers** - OpenAI, Anthropic Claude, and local Ollama support
- 📁 **Project Context** - AI understands your entire Python project structure
- 🏗️ **AST-Based Parsing** - Deep understanding of Python syntax and structure
- 💾 **Lightweight Storage** - Efficient SQLite storage of code chunks

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/notsajeed/Ath.git
cd Ath
```

### 2. Install Ath

```bash
pip install -e .
```

### 3. Initialize Your Project

```bash
ath init --force
```

## Basic Usage

### Get Help

```bash
ath --help
```

### Inspect Python Files

```bash
# Inspect a specific Python file
ath inspect path/to/your/file.py

# Inspect from project root
ath inspect src/main.py
ath inspect tests/test_utils.py
```

### Start AI Chat

```bash
ath chat
```

## Configuring AI Providers (No Environment Variables Needed)

### Show Current Config

```bash
ath config show
```

Displays the current configuration (API keys hidden).

### Set Default Provider

```bash
ath config set provider openai
ath config set provider ollama
ath config set provider anthropic
```

Sets the default AI provider for chat sessions.

### Set Default Model

```bash
ath config set model codellama:7b
ath config set model codellama:13b
```

Sets the default model for the selected provider.

### Set API Keys

```bash
ath config set openai_key sk-xxxx-your-key
ath config set anthropic_key sk-xxxx-your-key
```

Saves API keys in the local config file.

**Note:** Using environment variables is optional if you prefer, but all necessary settings are now stored locally.

## Example Workflow

```bash
# 1. Initialize your Python project
ath init --force

# 2. Inspect your Python code structure
ath inspect src/main.py

# 3. Configure AI provider and model
ath config set provider ollama
ath config set model codellama:7b

# 4. Set API key (if required)
ath config set ollama_key sk-xxxx-your-key

# 5. Start AI chat session
ath chat

# 6. Ask questions about your Python code
You: What functions are in main.py?
You: How does the User class work?
You: Show me all the imports in this project
```

## Recommended Models

### For Code Analysis

- **Best:** `codellama:13b` (needs ~8GB RAM)
- **Balanced:** `codellama:7b` (needs ~4GB RAM)
- **Fast:** `codellama` (usually 7b, faster responses)
- **Alternative:** `deepseek-coder:6.7b`

### For General Chat

- **Lightweight:** `gemma3:1b`
- **Better:** `llama3:8b`

## Tips

- 💡 **Be Specific:** Ask about specific Python files, functions, or classes
- 🎯 **Use File Names:** "What's in test2.py?" works better than "tell me about the test file"
- 🔄 **Context Matters:** Ath understands your entire Python project, so reference your actual code
- 📝 **File Paths:** Use paths relative to your project root
- 🐍 **Python-Specific:** Ask about imports, decorators, classes, inheritance, etc.

## What Ath Analyzes

- ✅ Python files (`.py`)
- ✅ Functions with docstrings and parameters
- ✅ Classes with methods and inheritance
- ✅ Module-level code and imports
- ✅ Project structure and relationships

## Possibilities

- 🔄 JavaScript/TypeScript support
- 🔄 Java support
- 🔄 Go support
- 🔄 Rust support
- 🔄 Multi-language projects
- 🔄 Git integration for change analysis
- 🔄 Documentation generation
- 🔄 Code quality suggestions

## Troubleshooting

### Ollama Issues

- **"Ollama is not running":** Start the Ollama desktop app
- **"404 error":** The model isn't installed - run `ollama pull model-name`
- **Slow responses:** Try a smaller model or ensure Ollama has enough RAM

### API Issues

- **"Please set API key":** Use `ath config set <provider>_key sk-xxxx-your-key`
- **"API error":** Check your API key and internet connection

### Accuracy Issues

- **Generic responses:** Try a larger/better model (codellama vs gemma)
- **Wrong file info:** Be more specific in your questions
- **Context confusion:** Mention the exact file path in your question

## Contributing

Feel free to contribute improvements, bug fixes, or new features!

## License

MIT License
