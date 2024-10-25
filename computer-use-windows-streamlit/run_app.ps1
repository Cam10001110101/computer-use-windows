# Initialize conda for PowerShell
$condaPath = "$env:USERPROFILE\anaconda3"
if (Test-Path "$env:ProgramData\anaconda3") {
    $condaPath = "$env:ProgramData\anaconda3"
}
(& "$condaPath\Scripts\conda.exe" "shell.powershell" "hook") | Out-String | Invoke-Expression

# Activate conda environment
conda activate computer_use

# Set PYTHONPATH to current directory
$env:PYTHONPATH = "."

# Run the Streamlit app
python -m streamlit run computer_use_demo/streamlit.py
