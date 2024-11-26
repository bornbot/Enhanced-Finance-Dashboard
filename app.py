from flask import Flask, render_template
from dashboard import dash_app

# Create Flask app
flask_app = Flask(__name__)

# Initialize Dash app
dash_app.init_app(flask_app)

# Define Flask routes
@flask_app.route('/')
def home():
    return render_template('home.html')

if __name__ == "__main__":
    flask_app.run(debug=True)
