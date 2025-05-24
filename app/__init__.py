from flask import Flask

def create_app():
    app = Flask(
        __name__,
        static_folder='static',
        template_folder='templates'
    )

    app.secret_key = 'secret_key'
    app.config['SESSION_PERMANENT'] = False  # Optional: session expires when browser closes

    # Import and register blueprints
    from app.routes.admin_routes import admin_bp
    from app.routes.user_routes import user_bp

    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)

    return app
