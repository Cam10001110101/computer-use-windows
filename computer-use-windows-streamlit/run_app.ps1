# Change to the streamlit app directory
cd computer-use-windows-streamlit

# Set PYTHONPATH to current directory
$env:PYTHONPATH = "."

# Run the Streamlit app
python -m streamlit run computer_use\streamlit.py
