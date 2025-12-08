# -*- coding: utf-8 -*-
from flask import Flask, render_template  

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Register Blueprints
    from .routes.faculty import faculty_bp
    from .routes.budget import budget_bp
    app.register_blueprint(faculty_bp, url_prefix='/faculty')
    app.register_blueprint(budget_bp, url_prefix='/budget')

    # Home route
    @app.route('/')
    def index():
        return render_template('index.html') 

    return app
