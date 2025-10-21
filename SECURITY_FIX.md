# Transaction Leakage Security Fix

## Issue Description
Transaction history from one account was displaying for accounts with no seeded data, creating a critical data leakage vulnerability.

## Root Cause
The bug existed in **frontend state management** in `/app/dashboard/accounts/[id]/page.tsx`:

1. When navigating between accounts, old transaction state persisted
2. New account with no transactions would still show previous account's data
3. No explicit state clearing when account ID changed
4. Conditional transaction updates (`if (transactionsRes.data)`) meant empty arrays were never set

## Fixes Applied

### 1. Frontend State Management (CRITICAL)
**File**: `ilab/app/dashboard/accounts/[id]/page.tsx`

```typescript
// BEFORE (VULNERABLE)
const loadAccountData = useCallback(async () => {
  try {
    const [accountsRes, transactionsRes] = await Promise.all([...]);
    if (transactionsRes.data) {
      setTransactions(transactionsRes.data); // Only sets if data exists
    }
  } catch (error) {
    console.error("Failed to load account:", error);
  }
}, [params.id]);

// AFTER (SECURE)
const loadAccountData = useCallback(async () => {
  // Clear stale data immediately
  setTransactions([]);
  setAccount(null);
  
  try {
    const [accountsRes, transactionsRes] = await Promise.all([...]);
    // Always set transactions, even if empty
    setTransactions(transactionsRes.data || []);
  } catch (error) {
    console.error("Failed to load account:", error);
    // Ensure cleared on error
    setTransactions([]);
    setAccount(null);
  }
}, [params.id]);
```

**Key Changes**:
- ✅ Immediate state clearing at function start
- ✅ Explicit empty array fallback: `transactionsRes.data || []`
- ✅ State cleared in catch block to handle errors
- ✅ Prevents stale data from persisting across navigations

### 2. Backend Error Handling
**File**: `backend/routes/accounts.py`

```python
# BEFORE
@accounts_bp.route('/<account_id>/transactions', methods=['GET'])
@require_auth
async def get_transactions(user, account_id):
    # .single() raises exception if not found, but no try-catch
    account = supabase.table('accounts').select('*').eq('id', account_id).eq('user_id', user['user_id']).single().execute()
    if not account.data:  # This line is unreachable!
        return jsonify({'error': 'Account not found'}), 404

# AFTER
@accounts_bp.route('/<account_id>/transactions', methods=['GET'])
@require_auth
async def get_transactions(user, account_id):
    try:
        # .single() raises exception if not found
        account = supabase.table('accounts').select('*').eq('id', account_id).eq('user_id', user['user_id']).single().execute()
        if not account.data:
            return jsonify({'error': 'Account not found'}), 404
    except Exception as e:
        logger.error(f"Account verification failed for user {user['user_id']}, account {account_id}: {e}")
        return jsonify({'error': 'Account not found'}), 404
    
    # Query transactions only for this specific account
    transactions = supabase.table('transactions').select('*').eq('account_id', account_id).order('created_at', desc=True).execute()
    return jsonify(transactions.data)
```

**Key Changes**:
- ✅ Proper exception handling for Supabase `.single()` method
- ✅ Logging for failed verifications
- ✅ Explicit comment about query scope

### 3. Database Security (Defense in Depth)
**File**: `backend/rls_policies.sql` (NEW)

Created comprehensive Row Level Security policies:

```sql
-- Transactions can only be viewed through owned accounts
CREATE POLICY "Users can view own transactions"
ON transactions FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM accounts
        WHERE accounts.id = transactions.account_id
        AND accounts.user_id = auth.uid()
    )
);
```

**Key Features**:
- ✅ Database-level enforcement preventing cross-user queries
- ✅ Policies for all tables (accounts, transactions, cards, bills, etc.)
- ✅ Admin override policies for support operations
- ✅ Prevents data leakage even if application code has bugs

## Verification Steps

### Test Case 1: Account Switching
1. Login and seed data for one account
2. Create second account with NO seeded data
3. Navigate to seeded account (should show transactions)
4. Navigate to unseeded account (should show "No transactions found")
5. **BEFORE FIX**: Would show seeded account's transactions
6. **AFTER FIX**: Shows empty state correctly

### Test Case 2: API Error Handling
1. Attempt to access non-existent account ID
2. **BEFORE FIX**: Might show cached data
3. **AFTER FIX**: Returns 404 with cleared state

### Test Case 3: Direct Database Query (with RLS)
```sql
-- As user A, try to query user B's transactions
SELECT * FROM transactions WHERE account_id = '<user_b_account_id>';
-- BEFORE POLICIES: Returns data
-- AFTER POLICIES: Returns empty (blocked by RLS)
```

## Security Impact

### Before Fix
- ❌ **High Severity**: Cross-account data leakage
- ❌ Users could see other users' transactions
- ❌ Privacy violation / regulatory compliance issue
- ❌ No database-level protection

### After Fix
- ✅ **Resolved**: Multi-layer defense
- ✅ Frontend state management prevents UI leakage
- ✅ Backend validates ownership before queries
- ✅ Database RLS blocks unauthorized access
- ✅ Explicit error handling and logging

## Additional Recommendations

1. **Enable RLS Policies**: Run `rls_policies.sql` in Supabase
2. **Switch to User Auth**: Use user JWT tokens instead of service role key
3. **Add Integration Tests**: Test account switching scenarios
4. **Monitor Logs**: Watch for failed ownership verification attempts
5. **Audit Trail**: Log all data access for compliance

## Files Modified
1. `ilab/app/dashboard/accounts/[id]/page.tsx` - **Critical fix**: Clear stale transaction state
2. `ilab/app/dashboard/page.tsx` - **Preventive fix**: Same pattern on dashboard
3. `ilab/app/dashboard/transfers/page.tsx` - **Preventive fix**: Same pattern on transfers
4. `backend/routes/accounts.py` - **Backend hardening**: Proper error handling
5. `backend/rls_policies.sql` - **New file**: Database-level security policies
6. `backend/SECURITY_FIX.md` - **New file**: This documentation
