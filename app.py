from flask import Flask
from utils.database import Base, engine
from utils.extensions import bcrypt, limiter

def create_app():
    app = Flask(__name__)

    bcrypt.init_app(app)
    limiter.init_app(app)

    from models.expense_model import Expense
    from models.users_model import User
    from models.refresh_token_model import RefreshToken

    Base.metadata.create_all(engine)

    from routes.expense_routes import expenses_bp
    from routes.auth_routes import auth_bp

    app.register_blueprint(expenses_bp)
    app.register_blueprint(auth_bp)

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)