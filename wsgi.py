from app import app, socketio
from app import view 
# Create a WSGI application for deployment
application = socketio.WSGIApp(app)
