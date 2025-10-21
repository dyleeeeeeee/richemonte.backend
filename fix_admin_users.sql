-- Fix existing users to ensure they have role field
-- Run this in Supabase SQL Editor to update existing users

-- First, ensure all users have a role (default to 'user' if NULL)
UPDATE users 
SET role = 'user' 
WHERE role IS NULL;

-- To make a specific user an admin, run this (replace with actual email):
-- UPDATE users SET role = 'admin' WHERE email = 'admin@example.com';

-- Example: Make first user in system an admin (ONLY for testing)
-- UPDATE users SET role = 'admin' WHERE id = (SELECT id FROM users ORDER BY created_at LIMIT 1);

-- Check all users and their roles:
SELECT id, email, full_name, role, account_status, created_at 
FROM users 
ORDER BY created_at;
