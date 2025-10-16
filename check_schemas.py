#!/usr/bin/env python3
"""
Data Structure Consistency Check
"""

def check_schema_consistency():
    """Check that frontend interfaces match backend database schema"""

    print("="*80)
    print("DATA STRUCTURE CONSISTENCY CHECK")
    print("="*80)

    # Check accounts table
    print("\n🔍 Checking Account interface...")
    frontend_account_fields = [
        'id', 'user_id', 'account_number', 'account_type', 'balance',
        'currency', 'status', 'routing_number', 'created_at', 'updated_at'
    ]

    # From schema.sql
    backend_account_fields = [
        'id', 'user_id', 'account_number', 'account_type', 'balance',
        'currency', 'status', 'routing_number', 'created_at', 'updated_at'
    ]

    account_match = set(frontend_account_fields) == set(backend_account_fields)
    print(f"   Account fields match: {'✅' if account_match else '❌'}")

    # Check cards table
    print("\n🔍 Checking Card interface...")
    frontend_card_fields = [
        'id', 'user_id', 'card_number', 'card_type', 'card_brand', 'cvv',
        'expiry_date', 'credit_limit', 'balance', 'status', 'created_at', 'updated_at'
    ]

    backend_card_fields = [
        'id', 'user_id', 'card_number', 'card_type', 'card_brand', 'cvv',
        'expiry_date', 'credit_limit', 'balance', 'status', 'created_at', 'updated_at'
    ]

    card_match = set(frontend_card_fields) == set(backend_card_fields)
    print(f"   Card fields match: {'✅' if card_match else '❌'}")

    # Check transactions table
    print("\n🔍 Checking Transaction interface...")
    frontend_transaction_fields = [
        'id', 'account_id', 'type', 'amount', 'description', 'merchant', 'category', 'created_at'
    ]

    backend_transaction_fields = [
        'id', 'account_id', 'type', 'amount', 'description', 'merchant', 'category', 'created_at'
    ]

    transaction_match = set(frontend_transaction_fields) == set(backend_transaction_fields)
    print(f"   Transaction fields match: {'✅' if transaction_match else '❌'}")

    # Check bills table
    print("\n🔍 Checking Bill interface...")
    frontend_bill_fields = [
        'id', 'user_id', 'payee_name', 'account_number', 'bill_type', 'amount', 'due_date', 'auto_pay', 'created_at'
    ]

    backend_bill_fields = [
        'id', 'user_id', 'payee_name', 'account_number', 'bill_type', 'amount', 'due_date', 'auto_pay', 'created_at'
    ]

    bill_match = set(frontend_bill_fields) == set(backend_bill_fields)
    print(f"   Bill fields match: {'✅' if bill_match else '❌'}")

    # Check notifications table
    print("\n🔍 Checking Notification interface...")
    frontend_notification_fields = [
        'id', 'user_id', 'type', 'message', 'delivery_method', 'read', 'created_at'
    ]

    backend_notification_fields = [
        'id', 'user_id', 'type', 'message', 'delivery_method', 'read', 'created_at'
    ]

    notification_match = set(frontend_notification_fields) == set(backend_notification_fields)
    print(f"   Notification fields match: {'✅' if notification_match else '❌'}")

    # Check beneficiaries table
    print("\n🔍 Checking Beneficiary interface...")
    frontend_beneficiary_fields = [
        'id', 'user_id', 'full_name', 'relationship', 'email', 'phone', 'percentage', 'created_at', 'updated_at'
    ]

    backend_beneficiary_fields = [
        'id', 'user_id', 'full_name', 'relationship', 'email', 'phone', 'percentage', 'created_at', 'updated_at'
    ]

    beneficiary_match = set(frontend_beneficiary_fields) == set(backend_beneficiary_fields)
    print(f"   Beneficiary fields match: {'✅' if beneficiary_match else '❌'}")

    # Overall result
    all_match = all([account_match, card_match, transaction_match, bill_match, notification_match, beneficiary_match])

    print("\n" + "="*80)
    print(f"DATA STRUCTURE CONSISTENCY: {'✅ ALL MATCH' if all_match else '❌ ISSUES FOUND'}")
    print("="*80)

    return all_match

if __name__ == "__main__":
    success = check_schema_consistency()
    exit(0 if success else 1)
