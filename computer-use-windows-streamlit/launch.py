"""
Streamlit App Launcher
Run with: @python launch.py
"""
import os
import sys
import streamlit.web.cli as stcli

def main():
    # Set up the path to the Streamlit app
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.environ["PYTHONPATH"] = current_dir
    
    # Path to the Streamlit app file
    app_path = os.path.join(current_dir, "computer_use", "streamlit.py")
    
    # Launch the Streamlit app using the CLI module
    sys.argv = ["streamlit", "run", app_path]
    sys.exit(stcli.main())

if __name__ == "__main__":
    main()
