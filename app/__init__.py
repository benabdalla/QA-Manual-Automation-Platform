from flask import Flask
from app.database import db

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    
    db.init_app(app)

    from app.routes.gherkin import gherkin_bp
    app.register_blueprint(gherkin_bp)
    
    return app