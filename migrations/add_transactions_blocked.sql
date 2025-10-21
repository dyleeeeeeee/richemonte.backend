-- Migration: Add transactions_blocked column to users table
-- This allows admins to block only transactions while allowing account login

-- Add transactions_blocked column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'transactions_blocked'
    ) THEN
        ALTER TABLE public.users 
        ADD COLUMN transactions_blocked BOOLEAN DEFAULT FALSE;
        
        RAISE NOTICE 'Added transactions_blocked column to users table';
    ELSE
        RAISE NOTICE 'transactions_blocked column already exists';
    END IF;
END $$;

-- Add comment explaining the column
COMMENT ON COLUMN public.users.transactions_blocked IS 
'When TRUE, user can login but cannot perform any financial transactions (transfers, bill payments, check deposits, etc.)';
