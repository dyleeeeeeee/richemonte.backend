-- Migration: Add role and account_status columns to users table
-- Run this in Supabase SQL Editor

-- Add role column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'role'
    ) THEN
        ALTER TABLE public.users 
        ADD COLUMN role TEXT DEFAULT 'user' 
        CHECK (role IN ('admin', 'user'));
        
        RAISE NOTICE 'Added role column to users table';
    ELSE
        RAISE NOTICE 'Role column already exists';
    END IF;
END $$;

-- Add account_status column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'account_status'
    ) THEN
        ALTER TABLE public.users 
        ADD COLUMN account_status TEXT DEFAULT 'active' 
        CHECK (account_status IN ('active', 'blocked', 'suspended'));
        
        RAISE NOTICE 'Added account_status column to users table';
    ELSE
        RAISE NOTICE 'Account_status column already exists';
    END IF;
END $$;

-- Optional: Set a specific user as admin (uncomment and replace email)
-- UPDATE public.users SET role = 'admin' WHERE email = 'doubra.ak@gmail.com';
