from app import app, socketio
from app import view  # Import view.py containing your Flask app code
import json

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True, port=5001)
