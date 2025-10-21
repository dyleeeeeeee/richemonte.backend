# Transaction-Only Blocking Feature

## Overview
This feature allows admins to block user transactions while still permitting login access. Users with blocked transactions can view their accounts and data but cannot perform any financial operations.

## Implementation

### 1. Database Schema
**New Column:** `transactions_blocked BOOLEAN DEFAULT FALSE` in `users` table

**Migration File:** `migrations/add_transactions_blocked.sql`
- Run this migration in Supabase SQL Editor to add the column
- Safe to run multiple times (includes IF NOT EXISTS check)

**Schema Update:** `schema.sql` line 16 includes the column definition

### 2. JWT Token Enhancement
**File:** `auth/jwt_handler.py`
- Added `transactions_blocked` parameter to `create_jwt_token()` function
- JWT payload now includes `transactions_blocked: bool` field
- This allows middleware to check transaction status without database queries

### 3. Middleware
**File:** `auth/middleware.py`
- New decorator: `require_transactions_enabled`
- Checks JWT token for `transactions_blocked` flag
- Returns 403 error with user-friendly message if blocked
- Must be used AFTER `@require_auth` decorator

**Usage:**
```python
@transfers_bp.route('', methods=['POST'])
@require_auth
@require_transactions_enabled
async def create_transfer(user):
    # Transaction logic here
    pass
```

### 4. Admin Endpoints
**File:** `routes/admin.py`

#### Block User Transactions
```http
POST /api/admin/users/{user_id}/block-transactions
Authorization: Bearer {admin_token}
```
- Sets `transactions_blocked = TRUE`
- Admin cannot block their own transactions
- Returns updated user object

#### Unblock User Transactions
```http
POST /api/admin/users/{user_id}/unblock-transactions
Authorization: Bearer {admin_token}
```
- Sets `transactions_blocked = FALSE`
- Returns updated user object

#### Update User (includes transactions_blocked)
```http
PUT /api/admin/users/{user_id}
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "transactions_blocked": true
}
```
- Can update `transactions_blocked` along with other fields
- Allowed fields: `full_name`, `phone`, `address`, `preferred_brand`, `role`, `account_status`, `transactions_blocked`

### 5. Protected Endpoints
The following transaction endpoints now require `@require_transactions_enabled`:

**Transfers:** `routes/transfers.py`
- `POST /api/transfers` - Create transfer

**Bills:** `routes/bills.py`
- `POST /api/bills/{bill_id}/pay` - Pay bill

**Checks:** `routes/checks.py`
- `POST /api/checks/deposit` - Deposit check

### 6. Login Updates
**File:** `routes/auth.py`
- Login endpoint now includes `transactions_blocked` in JWT token creation
- Registration defaults `transactions_blocked` to `FALSE`

## Blocking Comparison

| Feature | Account Blocked | Transactions Blocked |
|---------|----------------|---------------------|
| Can Login | ❌ No | ✅ Yes |
| View Accounts | ❌ No | ✅ Yes |
| View Transactions | ❌ No | ✅ Yes |
| View Bills | ❌ No | ✅ Yes |
| Create Transfers | ❌ No | ❌ No |
| Pay Bills | ❌ No | ❌ No |
| Deposit Checks | ❌ No | ❌ No |
| Update Profile | ❌ No | ✅ Yes |
| View Notifications | ❌ No | ✅ Yes |

## Error Messages
- **Account Blocked:** "Account blocked. Contact support." (HTTP 403)
- **Transactions Blocked:** "Your transactions have been temporarily blocked. Please contact Concierge Bank support for assistance." (HTTP 403)

## Testing
1. Create user account
2. Admin blocks transactions: `POST /api/admin/users/{user_id}/block-transactions`
3. User can still login: `POST /api/auth/login` ✅
4. User attempts transfer: `POST /api/transfers` ❌ (403 error)
5. Admin unblocks transactions: `POST /api/admin/users/{user_id}/unblock-transactions`
6. User can now transfer: `POST /api/transfers` ✅

## Files Modified
- ✅ `migrations/add_transactions_blocked.sql` - Database migration
- ✅ `schema.sql` - Schema definition
- ✅ `auth/jwt_handler.py` - JWT token creation
- ✅ `auth/middleware.py` - Transaction blocking middleware
- ✅ `auth/__init__.py` - Export new decorator
- ✅ `routes/auth.py` - Include transactions_blocked in JWT
- ✅ `routes/admin.py` - Admin endpoints for blocking/unblocking
- ✅ `routes/transfers.py` - Apply middleware to transfers
- ✅ `routes/bills.py` - Apply middleware to bill payments
- ✅ `routes/checks.py` - Apply middleware to check deposits

## Status: ✅ IMPLEMENTED
Transaction-only blocking is fully implemented and ready for use.
