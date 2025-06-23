@echo off
echo Installing required packages...
pip install -r requirements.txt

echo Starting Streamlit application...
streamlit run streamlit_app.py

pause
