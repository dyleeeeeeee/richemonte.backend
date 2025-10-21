-- Migration: Add transaction_pin column to users table
-- This PIN is required for finalizing financial transactions

-- Add transaction_pin column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'transaction_pin_hash'
    ) THEN
        ALTER TABLE public.users
        ADD COLUMN transaction_pin_hash TEXT;

        RAISE NOTICE 'Added transaction_pin_hash column to users table';
    ELSE
        RAISE NOTICE 'transaction_pin_hash column already exists';
    END IF;
END $$;

-- Add comment explaining the column
COMMENT ON COLUMN public.users.transaction_pin_hash IS
'Plain text 6-digit PIN required for finalizing financial transactions. Users can only change this PIN by contacting bank support.';
