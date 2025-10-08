"""
Concierge Bank - Modular Quart Backend Application
Luxury banking platform with Supabase and Resend integration
"""
import logging
from quart import Quart
from quart_cors import cors

from core.config import FRONTEND_URL

# Import all route blueprints
from routes import (
	auth_bp,
	accounts_bp,
	cards_bp,
	transfers_bp,
	bills_bp,
	checks_bp,
	notifications_bp,
	settings_bp,
	health_bp
)

# Configure logging
logging.basicConfig(
	level=logging.INFO,
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app():
	"""Application factory"""
	app = Quart(__name__)
	
	# Configure CORS
	app = cors(app, allow_origin=FRONTEND_URL, allow_credentials=True)
	
	# Register blueprints
	app.register_blueprint(auth_bp)
	app.register_blueprint(accounts_bp)
	app.register_blueprint(cards_bp)
	app.register_blueprint(transfers_bp)
	app.register_blueprint(bills_bp)
	app.register_blueprint(checks_bp)
	app.register_blueprint(notifications_bp)
	app.register_blueprint(settings_bp)
	app.register_blueprint(health_bp)
	
	logger.info("Concierge Bank API initialized successfully")
	return app


# Create app instance
app = create_app()


if __name__ == '__main__':
	app.run(debug=True)
