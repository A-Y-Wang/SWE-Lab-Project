from flask import Flask
import os
 
app = Flask(__name__, static_folder='./build', static_url_path='/')

def create_app():
    from backend.usercontrol import users_bp
    app.register_blueprint(users_bp, url_prefix='/users')
    return app

app = create_app()

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.errorhandler(404)
def not_found(e):
    return app.send_static_file('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False, port=os.environ.get('PORT', 80))