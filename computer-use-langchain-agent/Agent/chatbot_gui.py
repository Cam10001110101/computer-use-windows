import sys
import yaml
from PyQt5.QtWidgets import (QApplication, QVBoxLayout, QHBoxLayout, QTextEdit, 
                           QPushButton, QLabel)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from gui_styles import ModernWidget, button_style, text_edit_style
import io
from contextlib import redirect_stdout
from dotenv import load_dotenv
import os

# Import chatbot functions
from langchain_chatbot_anthropic import setup_graph, handle_input

class EnterAwareTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return and not event.modifiers() & Qt.ShiftModifier:
            self.parent.send_message()
        else:
            super().keyPressEvent(event)

class ChatbotThread(QThread):
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, graph, message, config):
        super().__init__()
        self.graph = graph
        self.message = message
        self.config = config

    def run(self):
        try:
            output = io.StringIO()
            with redirect_stdout(output):
                handle_input(self.graph, self.message, self.config)
            response = output.getvalue().strip()
            self.response_ready.emit(response)
        except Exception as e:
            self.error_occurred.emit(f"Error: {str(e)}")

class ChatbotGUI(ModernWidget):
    def __init__(self):
        super().__init__()
        self.config = self.load_config()
        self.env_vars = self.load_environment()
        self.chatbot = None
        self.initUI()
        self.initialize_chatbot()

    def load_config(self):
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.yaml')
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)

    def load_environment(self):
        load_dotenv()
        return {
            'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY'),
            'LANGSMITH_API_KEY': os.getenv('LANGSMITH_API_KEY'),
            'TAVILY_API_KEY': os.getenv('TAVILY_API_KEY'),
            'BRAVE_API_KEY': os.getenv('BRAVE_API_KEY')
        }

    def initUI(self):
        self.setWindowTitle('Anthropic Chatbot with Computer Use')
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        # Chat display area
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet(text_edit_style)
        layout.addWidget(self.chat_display)

        # Input area
        input_layout = QHBoxLayout()
        self.input_field = EnterAwareTextEdit(self)
        self.input_field.setStyleSheet(text_edit_style)
        self.input_field.setFixedHeight(60)
        self.input_field.setAcceptRichText(False)
        self.send_button = QPushButton('Send')
        self.send_button.setStyleSheet(button_style)
        self.send_button.setFixedHeight(60)
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)
        layout.addLayout(input_layout)

        self.setLayout(layout)

    def initialize_chatbot(self):
        try:
            self.chat_display.append("Initializing Anthropic chatbot with computer use capabilities...")
            self.chatbot = setup_graph()
            self.chat_display.append("Chatbot initialized successfully.")
            self.show_available_tools()
        except Exception as e:
            self.chat_display.append(f"Error initializing chatbot: {str(e)}")

    def show_available_tools(self):
        self.chat_display.append("\nAvailable tools:")
        
        # Computer Use Tools
        self.chat_display.append("\n1. Computer Use Tools:")
        self.chat_display.append("   - computer_tool (mouse, keyboard, screenshots)")
        self.chat_display.append("   - bash_tool (command execution)")
        self.chat_display.append("   - edit_tool (file editing and creation)")
        
        # Search Tools
        self.chat_display.append("\n2. Search Tools:")
        self.chat_display.append("   - TavilySearchResults (web search)")
        self.chat_display.append("   - BraveSearch (web search)")
        self.chat_display.append("   - DuckDuckGoSearch (web search)")
        self.chat_display.append("   - WikipediaSearch (knowledge base)")
        self.chat_display.append("   - FirecrawlTool (documentation search)")
        
        self.chat_display.append("\nReady for your messages!")

    def send_message(self):
        message = self.input_field.toPlainText()
        if message:
            self.chat_display.append(f"\nYou: {message}")
            self.input_field.clear()
            self.get_chatbot_response(message)

    def get_chatbot_response(self, message):
        try:
            config = {
                "configurable": {
                    "thread_id": "1",
                    "temperature": self.config['models']['anthropic']['temperature']
                }
            }

            # Create and start the chatbot thread
            self.chat_thread = ChatbotThread(self.chatbot, message, config)
            self.chat_thread.response_ready.connect(self.handle_response)
            self.chat_thread.error_occurred.connect(self.handle_error)
            self.chat_thread.start()

            # Disable input while processing
            self.input_field.setEnabled(False)
            self.send_button.setEnabled(False)
            self.chat_display.append("\nProcessing...")

        except Exception as e:
            self.chat_display.append(f"\nError: {str(e)}")
            self.input_field.setEnabled(True)
            self.send_button.setEnabled(True)

    def handle_response(self, response):
        self.chat_display.append(f"\nAssistant:\n{response}")
        self.input_field.setEnabled(True)
        self.send_button.setEnabled(True)

    def handle_error(self, error_message):
        self.chat_display.append(f"\n{error_message}")
        self.input_field.setEnabled(True)
        self.send_button.setEnabled(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = ChatbotGUI()
    gui.show()
    sys.exit(app.exec_())
