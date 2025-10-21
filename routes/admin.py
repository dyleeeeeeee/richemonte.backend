"""
Admin routes for Concierge Bank - Superuser operations
"""
import logging
from datetime import datetime
from quart import Blueprint, request, jsonify

from core import get_supabase_client
from auth import require_auth
from utils import verify_account_ownership, update_account_balance, insert_record
from services import notify_user
from templates import bill_payment_email

logger = logging.getLogger(__name__)
admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')
supabase = get_supabase_client()


def require_admin(user):
    """Decorator to ensure user is admin"""
    if user.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    return None


@admin_bp.route('/users', methods=['GET'])
@require_auth
async def get_all_users(user):
    """Get all users (admin only)"""
    admin_check = require_admin(user)
    if admin_check:
        return admin_check

    users = supabase.table('users').select('*').execute()
    return jsonify(users.data)


@admin_bp.route('/users/<user_id>', methods=['PUT'])
@require_auth
async def update_user(user, user_id):
    """Update user details (admin only)"""
    admin_check = require_admin(user)
    if admin_check:
        return admin_check

    data = await request.get_json()

    # Only allow updating certain fields
    allowed_fields = ['full_name', 'phone', 'address', 'preferred_brand', 'role', 'account_status', 'transactions_blocked', 'transaction_pin_hash']
    update_data = {k: v for k, v in data.items() if k in allowed_fields}
    
    # Handle PIN update - store plain PIN
    if 'transaction_pin_hash' in update_data:
        pin = update_data['transaction_pin_hash']
        if pin and isinstance(pin, str) and pin.isdigit() and len(pin) == 6:
            update_data['transaction_pin_hash'] = pin
        else:
            return jsonify({'error': 'Transaction PIN must be exactly 6 digits'}), 400

    result = supabase.table('users').update(update_data).eq('id', user_id).execute()
    logger.info(f"User {user_id} updated by admin {user['user_id']}")
    return jsonify(result.data[0])


@admin_bp.route('/accounts', methods=['GET'])
@require_auth
async def get_all_accounts(user):
    """Get all accounts (admin only)"""
    admin_check = require_admin(user)
    if admin_check:
        return admin_check

    accounts = supabase.table('accounts').select('*, users(full_name, email)').execute()
    return jsonify(accounts.data)


@admin_bp.route('/accounts/<account_id>/balance', methods=['PUT'])
@require_auth
async def update_account_balance_admin(user, account_id):
    """Update account balance (admin only)"""
    admin_check = require_admin(user)
    if admin_check:
        return admin_check

    data = await request.get_json()
    new_balance = float(data['balance'])

    result = supabase.table('accounts').update({
        'balance': new_balance,
        'updated_at': datetime.utcnow().isoformat()
    }).eq('id', account_id).execute()

    logger.info(f"Account {account_id} balance updated to {new_balance} by admin {user['user_id']}")
    return jsonify(result.data[0])


@admin_bp.route('/bills/create', methods=['POST'])
@require_auth
async def create_bill_for_user(user):
    """Create bill for specific user (admin only)"""
    admin_check = require_admin(user)
    if admin_check:
        return admin_check

    data = await request.get_json()

    bill_data = {
        'user_id': data['user_id'],
        'payee_name': data['payee_name'],
        'account_number': data.get('account_number', ''),
        'bill_type': data.get('bill_type', 'utility'),
        'amount': float(data['amount']),
        'due_date': data['due_date'],
        'auto_pay': data.get('auto_pay', False),
        'created_at': datetime.utcnow().isoformat()
    }

    result = supabase.table('bills').insert(bill_data).execute()
    logger.info(f"Bill created for user {data['user_id']} by admin {user['user_id']}: {data['payee_name']}")
    return jsonify(result.data[0]), 201


@admin_bp.route('/notifications/send', methods=['POST'])
@require_auth
async def send_notification_to_user(user):
    """Send notification to specific user (admin only)"""
    admin_check = require_admin(user)
    if admin_check:
        return admin_check

    data = await request.get_json()
    
    # Validate required fields
    if not data.get('user_id'):
        return jsonify({'error': 'User ID is required'}), 400
    if not data.get('message'):
        return jsonify({'error': 'Message is required'}), 400

    notification_type = data.get('type', 'admin_message')
    message = data['message']
    target_user_id = data['user_id']
    
    # Create notification title based on type
    title_map = {
        'admin_message': 'Admin Message',
        'account_alert': 'Account Alert',
        'security': 'Security Notice',
        'transaction': 'Transaction Update'
    }
    title = title_map.get(notification_type, 'Notification')

    # Create in-app notification
    notification_data = {
        'user_id': target_user_id,
        'type': notification_type,
        'title': title,
        'message': message,
        'delivery_method': 'push',
        'read': False,
        'created_at': datetime.utcnow().isoformat()
    }

    result = supabase.table('notifications').insert(notification_data).execute()
    
    if not result.data:
        logger.error(f"Failed to create notification for user {target_user_id}")
        return jsonify({'error': 'Failed to create notification'}), 500

    # Send email notification if requested
    if data.get('send_email', False):
        try:
            # Generate HTML email content
            email_html = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #d4af37 0%, #c5a028 100%); padding: 30px; text-align: center;">
                    <h1 style="color: white; margin: 0;">{title}</h1>
                </div>
                <div style="background: white; padding: 30px; border: 1px solid #e0e0e0;">
                    <p style="color: #333; font-size: 16px; line-height: 1.6;">{message}</p>
                    <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 20px 0;">
                    <p style="color: #666; font-size: 14px;">This is an administrative notification from Concierge Bank.</p>
                </div>
            </div>
            """
            
            await notify_user(
                supabase,
                target_user_id,
                notification_type,
                message,
                title,
                email_html
            )
            logger.info(f"Email notification sent to user {target_user_id} by admin {user['user_id']}")
        except Exception as e:
            logger.error(f"Failed to send email notification to user {target_user_id}: {e}")
            # Don't fail the request if email fails, notification was still created

    logger.info(f"Notification sent to user {target_user_id} by admin {user['user_id']}: {message[:50]}")
    return jsonify(result.data[0]), 201


@admin_bp.route('/stats', methods=['GET'])
@require_auth
async def get_admin_stats(user):
    """Get admin dashboard statistics"""
    admin_check = require_admin(user)
    if admin_check:
        return admin_check

    # Get various stats
    users_count = supabase.table('users').select('id', count='exact').execute()
    accounts_count = supabase.table('accounts').select('id', count='exact').execute()
    total_balance = supabase.table('accounts').select('balance').execute()
    bills_count = supabase.table('bills').select('id', count='exact').execute()

    # Calculate total balance
    total_balance_value = sum(account['balance'] for account in total_balance.data) if total_balance.data else 0

    stats = {
        'total_users': len(users_count.data) if users_count.data else 0,
        'total_accounts': len(accounts_count.data) if accounts_count.data else 0,
        'total_balance': total_balance_value,
        'total_bills': len(bills_count.data) if bills_count.data else 0,
    }

    return jsonify(stats)


@admin_bp.route('/users/<user_id>/block', methods=['POST'])
@require_auth
async def block_user(user, user_id):
    """Block a user from logging in (admin only)"""
    admin_check = require_admin(user)
    if admin_check:
        return admin_check

    # Prevent admin from blocking themselves
    if user_id == user['user_id']:
        return jsonify({'error': 'Cannot block yourself'}), 400

    result = supabase.table('users').update({
        'account_status': 'blocked',
        'updated_at': datetime.utcnow().isoformat()
    }).eq('id', user_id).execute()

    logger.info(f"User {user_id} blocked by admin {user['user_id']}")
    return jsonify(result.data[0])


@admin_bp.route('/users/<user_id>/unblock', methods=['POST'])
@require_auth
async def unblock_user(user, user_id):
    """Unblock a user (admin only)"""
    admin_check = require_admin(user)
    if admin_check:
        return admin_check

    result = supabase.table('users').update({
        'account_status': 'active',
        'updated_at': datetime.utcnow().isoformat()
    }).eq('id', user_id).execute()

    logger.info(f"User {user_id} unblocked by admin {user['user_id']}")
    return jsonify(result.data[0])


@admin_bp.route('/users/<user_id>/block-transactions', methods=['POST'])
@require_auth
async def block_user_transactions(user, user_id):
    """Block user transactions while allowing login (admin only)"""
    admin_check = require_admin(user)
    if admin_check:
        return admin_check

    # Prevent admin from blocking their own transactions
    if user_id == user['user_id']:
        return jsonify({'error': 'Cannot block your own transactions'}), 400

    result = supabase.table('users').update({
        'transactions_blocked': True,
        'updated_at': datetime.utcnow().isoformat()
    }).eq('id', user_id).execute()

    logger.info(f"User {user_id} transactions blocked by admin {user['user_id']}")
    return jsonify(result.data[0])


@admin_bp.route('/users/<user_id>/unblock-transactions', methods=['POST'])
@require_auth
async def unblock_user_transactions(user, user_id):
    """Unblock user transactions (admin only)"""
    admin_check = require_admin(user)
    if admin_check:
        return admin_check

    result = supabase.table('users').update({
        'transactions_blocked': False,
        'updated_at': datetime.utcnow().isoformat()
    }).eq('id', user_id).execute()

    logger.info(f"User {user_id} transactions unblocked by admin {user['user_id']}")
    return jsonify(result.data[0])
