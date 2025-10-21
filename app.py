"""
Concierge Bank - Modular Quart Backend Application
Luxury banking platform with Supabase and Resend integration
"""
import logging
from quart import Quart
from quart_cors import cors

from core.config import FRONTEND_URL, LOG_LEVEL

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
	beneficiaries_bp,
	health_bp,
	admin_bp,
	concierge_bp,
	search_bp
)

# Configure logging with verbose output
logging.basicConfig(
	level=getattr(logging, LOG_LEVEL, logging.DEBUG),
	format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger(__name__)
logger.info(f"Logging level set to: {LOG_LEVEL}")


def print_routes(app: Quart):
	"""Print all registered routes in the application"""
	logger.info("="*80)
	logger.info("REGISTERED ROUTES - Concierge Bank API")
	logger.info("="*80)
	
	routes = []
	for rule in app.url_map.iter_rules():
		methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
		routes.append({
			'endpoint': rule.endpoint,
			'methods': methods,
			'path': rule.rule
		})
	
	# Sort by path for readability
	routes.sort(key=lambda x: x['path'])
	
	for route in routes:
		logger.info(f"{route['methods']:<20} {route['path']:<50} -> {route['endpoint']}")
	
	logger.info("="*80)
	logger.info(f"Total routes registered: {len(routes)}")
	logger.info("="*80)


def create_app():
	"""Application factory"""
	logger.debug("Starting Concierge Bank API initialization...")
	app = Quart(__name__)
	
	# Configure CORS
	logger.debug(f"Configuring CORS with origin: {FRONTEND_URL}")
	app = cors(app, allow_origin=FRONTEND_URL, allow_credentials=True)
	
	# Add verbose request/response logging
	@app.before_request
	async def log_request():
		from quart import request
		logger.debug(f">>> REQUEST: {request.method} {request.path}")
		logger.debug(f"    Headers: {dict(request.headers)}")
		# Note: We don't log the request body here because reading it would
		# consume the stream, making it unavailable for the route handler.
		# Body logging should be done within route handlers if needed.
	
	@app.after_request
	async def log_response(response):
		from quart import request
		logger.debug(f"<<< RESPONSE: {request.method} {request.path} -> {response.status_code}")
		return response
	
	# Register blueprints
	logger.debug("Registering blueprints...")
	app.register_blueprint(auth_bp)
	logger.debug("  ✓ auth_bp registered")
	app.register_blueprint(accounts_bp)
	logger.debug("  ✓ accounts_bp registered")
	app.register_blueprint(cards_bp)
	logger.debug("  ✓ cards_bp registered")
	app.register_blueprint(transfers_bp)
	logger.debug("  ✓ transfers_bp registered")
	app.register_blueprint(bills_bp)
	logger.debug("  ✓ bills_bp registered")
	app.register_blueprint(checks_bp)
	logger.debug("  ✓ checks_bp registered")
	app.register_blueprint(notifications_bp)
	logger.debug("  ✓ notifications_bp registered")
	app.register_blueprint(settings_bp)
	logger.debug("  ✓ settings_bp registered")
	app.register_blueprint(beneficiaries_bp)
	logger.debug("  ✓ beneficiaries_bp registered")
	app.register_blueprint(health_bp)
	logger.debug("  ✓ health_bp registered")
	app.register_blueprint(admin_bp)
	logger.debug("  ✓ admin_bp registered")
	app.register_blueprint(concierge_bp)
	logger.debug("  ✓ concierge_bp registered")
	app.register_blueprint(search_bp)
	logger.debug("  ✓ search_bp registered")
	
	logger.info("Concierge Bank API initialized successfully")
	
	# Print all registered routes
	print_routes(app)
	
	return app


# Create app instance
app = create_app()


if __name__ == '__main__':
	app.run(debug=True)
