# Activate the virtual environment
.venv\Scripts\activate

# Set environment variables for Flask
$env:FLASK_APP="app.py"
$env:FLASK_DEBUG=1

# Run the Flask app
flask run