from app import app, socketio

# Create a WSGI application for deployment
application = socketio.WSGIApp(app)
