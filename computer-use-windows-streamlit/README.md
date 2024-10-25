# Computer Use Windows Streamlit Version

This is the Streamlit version of a Windows automation platform that combines Python's extensive system control capabilities with Anthropic's Claude AI. This project adapts [Anthropic's computer-use-demo](https://github.com/anthropics/anthropic-quickstarts/tree/main/computer-use-demo) specifically for Windows environments.

## Important Implementation Notes

### Differences from Original Demo
The original Anthropic demo was designed with strict isolation between the Streamlit interface and the context accessible to the Anthropic API. This isolation prevented the API from seeing or interacting with its own interface, avoiding potential confusion or recursive interactions.

This version currently does not implement such isolation. As a result:
- When running locally, the Anthropic API can see its own interface in screenshots
- This can potentially cause confusion as the API may try to interact with itself
- Future versions may implement proper isolation mechanisms

### Usage Considerations
This version has been tested primarily in the following configuration:
- Deployed on a VMware virtual machine
- Accessed remotely through a web browser
- Running on an isolated network
- Controlling the Windows environment through the remote interface

### Remote Operation Requirements
When operating remotely, it's important to:
- Use a console/terminal window for operations
- Be aware that display dimensions affect functionality
- Keep the console window at a consistent size
- Position the console appropriately for screenshot capture
- Consider using a fixed console size for reliable automation

Other versions of this project are planned that:
- Won't use Streamlit
- May implement different isolation strategies
- Could use alternative interface approaches

## Power of Integration

This project leverages two key technologies to enable sophisticated computer automation:

1. **Python's Windows Integration**
   - Direct access to Windows API through Python libraries via pywin32
   - System-level automation capabilities
   - File system and process management
   - GUI automation and screen capture
   - Comprehensive Windows event handling

2. **Anthropic's Claude AI**
   - Advanced natural language understanding
   - Context-aware decision making
   - Real-time system state analysis
   - Adaptive command interpretation
   - Visual processing capabilities

## ⚠️ Important Security Notice

This is a very early release intended for developers only. There are many security aspects that have not been tested or intended for general use. Please note:

1. The application has not undergone comprehensive security testing
2. It is not intended for production environments
3. Use in controlled development environments only
4. Exercise caution when granting system access
5. Consider running in an isolated environment

## Features

- Natural language computer control through Claude AI
- Support for multiple API providers:
  - Anthropic
  - AWS Bedrock
  - Google Vertex AI
- Windows-specific automation capabilities:
  - Process management
  - File system operations
  - GUI automation
  - System monitoring
- Real-time screenshot capture and display
- CLI command execution
- Custom system prompt configuration
- Configurable image history management
- Streamlit web interface for remote or local access

## Deployment Recommendations

### Local Development
Not recommended for regular use due to:
- Lack of isolation between API and interface
- Potential for recursive interactions
- Security considerations

### Recommended Setup
1. Deploy on a virtual machine (tested with VMware)
2. Access remotely through web browser
3. Use on an isolated network
4. Use a console window with consistent dimensions
5. Implement additional security measures as needed

### Display Configuration
For optimal functionality when operating remotely:
1. Open a console window on the target system
2. Position it appropriately for automation tasks
3. Maintain consistent window dimensions
4. Avoid resizing during operation
5. Consider using fixed console dimensions for reliability

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/computer_use_windows_streamlit.git
cd computer_use_windows_streamlit
```

2. Install the required dependencies:
```bash
pip install -r computer_use/requirements.txt
```

## Configuration

1. Set up your API credentials:
   - For Anthropic: Enter your API key in the application interface
   - For AWS Bedrock: Configure AWS credentials
   - For Google Vertex AI: Set up Google Cloud credentials and set `CLOUD_ML_REGION` environment variable

2. Optional: Configure custom system prompts through the interface

## Usage

1. Run the application using the provided batch script:
```bash
run_app.bat
```
Or using PowerShell:
```powershell
.\run_app.ps1
```

2. Access the interface through your browser:
   - Local access: `http://localhost:8501` (not recommended for regular use)
   - Remote access: Use the VM's IP address or hostname

3. For remote operation:
   - Open a console window on the target system
   - Position it appropriately for automation tasks
   - Maintain consistent window dimensions
   - Avoid resizing during operation

4. Select your preferred API provider and configure the necessary credentials

5. Start interacting with Claude to control your computer

## Technical Architecture

The project combines several key components:

1. **Core Automation Layer**
   - Python-based Windows API integration
   - System event handling and monitoring
   - Process and file system management
   - Screen capture and image processing

2. **AI Integration Layer**
   - Claude API communication
   - Context management
   - Command interpretation
   - System state analysis

## Project Structure

```
computer_use_windows_streamlit/
├── computer_use/           # Core application code
│   ├── tools/             # Windows automation tools
│   │   ├── base.py       # Base tool interfaces
│   │   ├── computer.py   # System operations
│   │   └── edit.py      # File operations
│   ├── loop.py           # AI interaction loop
│   ├── streamlit.py      # Web interface
│   └── requirements.txt  # Dependencies
├── run_app.bat           # Windows batch launcher
└── run_app.ps1           # PowerShell launcher
```

## Development Status

This is an early development release with the following considerations:

- Currently in beta/experimental stage
- Limited security testing
- Intended for developer exploration
- May contain undocumented features/limitations
- API integration subject to changes
- Testing framework needs to be implemented specifically for Windows environment
- Lacks isolation between API and interface
- Display dimensions affect functionality

## Future Development

Areas for future development include:
- Implementation of Windows-specific test suite
- Enhanced security measures
- Additional Windows-specific automation features
- Performance optimizations for Windows environment
- Proper isolation between API and interface
- Alternative versions without Streamlit dependency
- Improved handling of display dimensions

## Acknowledgments

This project is based on the following Anthropic repositories:
- [computer-use-demo](https://github.com/anthropics/anthropic-quickstarts/tree/main/computer-use-demo) - Original computer use demo implementation

The original work and computer use API are developed by Anthropic.

## License

See [LICENSE](LICENSE) file for details.
