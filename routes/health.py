"""
Health check route for Concierge Bank
"""
from datetime import datetime
from quart import Blueprint, jsonify

health_bp = Blueprint('health', __name__)


@health_bp.route('/health', methods=['GET'])
async def health_check():
	"""Health check endpoint"""
	return jsonify({
		'status': 'healthy',
		'timestamp': datetime.utcnow().isoformat()
	})
