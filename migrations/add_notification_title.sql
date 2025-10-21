-- Migration: Add title column to notifications table
-- Date: 2025-10-21
-- Description: Add title field to support better notification display

-- Add title column to notifications table if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'notifications' 
        AND column_name = 'title'
    ) THEN
        ALTER TABLE notifications ADD COLUMN title TEXT;
        RAISE NOTICE 'Added title column to notifications table';
    ELSE
        RAISE NOTICE 'Title column already exists in notifications table';
    END IF;
END $$;
