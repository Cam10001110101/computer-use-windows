# Anthropic Computer Use LangChain Agent

A powerful Windows desktop agent that combines Anthropic's Claude with LangChain for advanced system interaction and tool usage. This agent provides an interactive desktop experience with capabilities including system operations, web search, and more.

## Features

- Interactive desktop control with mouse and keyboard automation
- System command execution with Windows compatibility
- Multi-tool integration:
  - DuckDuckGo Search
  - Brave Search
  - Tavily Search
  - Wikipedia Search
  - FireCrawl web scraping
- User-friendly PyQt5 interface
- Flexible tool framework for easy expansion
- Comprehensive error handling and security validation

## Prerequisites

- Windows operating system
- Python 3.8+
- Required API keys:
  - ANTHROPIC_API_KEY
  - FIRECRAWL_API_KEY
  - BRAVE_API_KEY
  - TAVILY_API_KEY

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd anthropic-computer-use-langchain-agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
   - Rename `.env.example` to `.env`
   - Add your API keys to the `.env` file

## Usage

Run the application:
```bash
python Agent/chatbot_gui.py
```

The PyQt5 GUI will launch, providing an interface to interact with the agent.

## Project Structure

```
├── Agent/
│   ├── Tools/                 # Tool implementations
│   │   ├── base.py           # Base tool classes
│   │   ├── bash.py           # Command execution
│   │   ├── computer.py       # System interaction
│   │   └── ...               # Other tool implementations
│   ├── chatbot_gui.py        # PyQt5 GUI implementation
│   ├── config.yaml           # Configuration settings
│   └── langchain_chatbot_anthropic.py  # Core application
├── Docs/                     # Documentation
└── README.md                 # This file
```

## Tools

### System Tools
- **Computer Control**: Mouse, keyboard, and screen interactions
- **Command Execution**: Windows-compatible system command execution with Unix command translation

### Search Tools
- DuckDuckGo Search
- Brave Search
- Tavily Search
- Wikipedia Search

### Web Tools
- FireCrawl web scraping
- HTML to Markdown conversion

## Configuration

The application uses two main configuration files:
- `config.yaml`: Application settings and tool configurations
- `.env`: Environment variables and API keys

## Development

### Architecture
- **User Interface**: PyQt5-based GUI (chatbot_gui.py)
- **Backend Logic**: Core agent logic and tool integration (langchain_chatbot_anthropic.py)
- **Tools**: Modular tool implementations
- **Configuration**: Environment variables and YAML configuration

### Adding New Tools
Tools can be added by:
1. Creating a new tool class in the Tools directory
2. Implementing required methods (_run and _arun)
3. Registering the tool in the main application

## Security

- Command validation system for safe execution
- API key protection through environment variables
- Forbidden operation protection
- Safe execution environment

## License

[License information]

## Contributing

[Contribution guidelines]
