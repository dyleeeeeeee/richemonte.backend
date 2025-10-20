# Seed Script Usage Guide

## Overview
The `seed.py` script generates realistic historical banking data for existing users. It's designed with failsafes to prevent duplicate data and runs seamlessly.

## Prerequisites

1. **User must exist** - Register via frontend first (`/register`)
2. **Database schema** - Run migrations in Supabase
3. **Environment** - `.env` file with Supabase credentials

## Basic Usage

### 1. List All Users
```bash
python seed.py --list-users
```
Shows all registered users in the database with their roles.

### 2. Seed Data for a User
```bash
python seed.py --email user@example.com --months 6
```

**Parameters:**
- `--email` (required) - Email of existing user
- `--months` (optional) - Months of history to generate (2-12, default: 6)

## What Gets Seeded

The script creates realistic data **only if it doesn't already exist**:

### ✅ Accounts (3 types)
- **Checking** - Recent account (5 days old)
- **Savings** - Mid-age account (185 days old)
- **Investment** - Oldest account (365 days old)
- Each with realistic balances

### ✅ Cards (3 cards)
- **Cartier Credit Card** - $50k limit (2 years old)
- **Van Cleef & Arpels Credit** - $35k limit (1 year old)
- **Montblanc Debit Card** - No limit (3 months old)

### ✅ Transactions
- **40-150 per account** (more for checking)
- Realistic merchants (luxury brands, utilities, groceries)
- More recent activity (triangular distribution)
- Proper categories and amounts

### ✅ Bills (6 payees)
- Utilities (Con Edison, NYC Water)
- Telecom (Verizon, AT&T)
- Credit Cards
- Insurance

### ✅ Checks (8-20 records)
- Realistic check numbers
- Mix of cleared/pending status
- Staggered dates

### ✅ Notifications (15-40)
- Transaction alerts
- Bill payment confirmations
- Security notifications
- Mix of read/unread

## Failsafe Design

### ✅ Idempotent
Run the script multiple times safely - it won't create duplicates:
```bash
# First run - creates all data
python seed.py --email user@example.com --months 6

# Second run - skips existing data
python seed.py --email user@example.com --months 6
# Output: "Found 3 existing accounts", "Found 3 existing cards", etc.
```

### ✅ Defensive
- Checks for existing data before creating
- Handles missing schema columns gracefully
- Provides clear error messages
- Validates input parameters

## Example Workflow

### Step 1: Register User
```bash
# Via frontend at http://localhost:3000/register
# Or use Supabase dashboard
```

### Step 2: List Users (Optional)
```bash
python seed.py --list-users
```
Output:
```
============================================================
USERS IN DATABASE
============================================================

  user@example.com
    Name: John Doe
    Role: user
    Created: 2025-10-20T14:00:00+00:00

Total: 1 users
```

### Step 3: Seed Data
```bash
python seed.py --email user@example.com --months 6
```
Output:
```
============================================================
CONCIERGE BANK - DATA SEEDER
============================================================
Connecting to Supabase...
Looking up user: user@example.com
User: user@example.com
ID: 123e4567-e89b-12d3-a456-426614174000
Name: John Doe
Role: user
History: 6 months

No accounts found. Creating new ones...
  Created Checking account (opened 5 days ago): 1234567890
  Created Savings account (opened 185 days ago): 1234567891
  Created Investment account (opened 365 days ago): 1234567892
No cards found. Creating new ones...
  Created Cartier Credit (issued 720 days ago): ****4532
  Created Van Cleef & Arpels Credit (issued 365 days ago): ****8901
  Created Montblanc Debit (issued 90 days ago): ****2345
Generating 6 months of transaction history...
  Created 287 realistic transactions
No bills found. Creating payees...
  Created 6 bill payees
No checks found. Creating history...
  Created 15 check records
No notifications found. Creating history...
  Created 28 notifications

============================================================
✅ SEEDING COMPLETE
============================================================
```

## Error Handling

### User Not Found
```bash
python seed.py --email nonexistent@example.com --months 6
```
Output:
```
❌ ERROR: User 'nonexistent@example.com' not found in database

Possible issues:
  1. User hasn't registered yet
  2. Email spelling is different in database
  3. Supabase connection issue

Troubleshooting:
  1. Check Supabase dashboard to see if user exists
  2. Register via: http://localhost:3000/register
```

### Invalid Parameters
```bash
python seed.py --email user@example.com --months 15
```
Output:
```
ERROR: Months must be between 2 and 12
```

### Missing Email
```bash
python seed.py --months 6
```
Output:
```
ERROR: --email is required (or use --list-users)
```

## Tips

1. **Start with 6 months** - Good balance of data volume
2. **Run once per user** - Failsafes prevent duplicates but it's cleaner
3. **Check users first** - Use `--list-users` to verify email spelling
4. **Re-run safely** - Script detects existing data and skips creation

## Advanced

### Seed Multiple Users
```bash
# Create a simple loop
for email in user1@example.com user2@example.com user3@example.com; do
    python seed.py --email $email --months 6
done
```

### Different History Lengths
```bash
# Light user - 2 months
python seed.py --email newuser@example.com --months 2

# Heavy user - 12 months
python seed.py --email poweruser@example.com --months 12
```

## Troubleshooting

### Import Errors
```bash
# Ensure you're in the backend directory
cd backend
python seed.py --email user@example.com --months 6
```

### Supabase Connection Issues
```bash
# Check .env file exists and has correct credentials
cat .env | grep SUPABASE
```

### Schema Mismatch
```bash
# Run migrations first
# In Supabase SQL Editor, run:
# - schema.sql
# - migrations/add_role_and_account_status.sql
```

## Summary

✅ **Seamless** - Failsafes prevent errors and duplicates  
✅ **Realistic** - Data looks like real banking activity  
✅ **Fast** - Generates months of data in seconds  
✅ **Safe** - Can be run multiple times without issues  
✅ **Clear** - Verbose output shows exactly what's happening
