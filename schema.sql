-- Concierge Bank Database Schema
-- Run this in Supabase SQL Editor

-- Users table (extends Supabase auth.users)
CREATE TABLE IF NOT EXISTS users (
	id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
	email TEXT UNIQUE NOT NULL,
	full_name TEXT,
	phone TEXT,
	address JSONB,
	photo_url TEXT,
	preferred_brand TEXT DEFAULT 'Cartier',
	notification_preferences JSONB DEFAULT '{"email": true, "sms": false, "push": true}'::jsonb,
	role TEXT DEFAULT 'user' CHECK (role IN ('admin', 'user')),
	account_status TEXT DEFAULT 'active' CHECK (account_status IN ('active', 'blocked', 'suspended')),
	created_at TIMESTAMPTZ DEFAULT NOW(),
	updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Accounts table
CREATE TABLE IF NOT EXISTS accounts (
	id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
	user_id UUID REFERENCES users(id) ON DELETE CASCADE,
	account_number TEXT UNIQUE NOT NULL,
	account_type TEXT NOT NULL, -- Checking, Savings, Investment
	balance DECIMAL(15, 2) DEFAULT 0,
	currency TEXT DEFAULT 'USD',
	status TEXT DEFAULT 'active', -- active, closed, frozen
	routing_number TEXT DEFAULT '121000248', -- Wells Fargo routing number
	created_at TIMESTAMPTZ DEFAULT NOW(),
	updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Cards table
CREATE TABLE IF NOT EXISTS cards (
	id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
	user_id UUID REFERENCES users(id) ON DELETE CASCADE,
	card_number TEXT UNIQUE NOT NULL,
	card_type TEXT NOT NULL, -- Credit, Debit
	card_brand TEXT, -- Cartier, Van Cleef & Arpels, Montblanc, etc.
	cvv TEXT NOT NULL,
	expiry_date TEXT NOT NULL,
	credit_limit DECIMAL(15, 2),
	balance DECIMAL(15, 2) DEFAULT 0,
	status TEXT DEFAULT 'active' CHECK (status IN ('active', 'locked', 'expired', 'reported', 'blocked')),
	created_at TIMESTAMPTZ DEFAULT NOW(),
	updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Transactions table
CREATE TABLE IF NOT EXISTS transactions (
	id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
	account_id UUID REFERENCES accounts(id) ON DELETE CASCADE,
	type TEXT NOT NULL, -- debit, credit
	amount DECIMAL(15, 2) NOT NULL,
	description TEXT,
	merchant TEXT,
	category TEXT,
	created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Transfers table
CREATE TABLE IF NOT EXISTS transfers (
	id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
	user_id UUID REFERENCES users(id) ON DELETE CASCADE,
	from_account_id UUID REFERENCES accounts(id),
	to_account_id UUID REFERENCES accounts(id),
	to_external JSONB, -- For external transfers
	amount DECIMAL(15, 2) NOT NULL,
	transfer_type TEXT, -- internal, external, p2p
	status TEXT DEFAULT 'pending', -- pending, completed, failed
	created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Bills table
CREATE TABLE IF NOT EXISTS bills (
	id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
	user_id UUID REFERENCES users(id) ON DELETE CASCADE,
	payee_name TEXT NOT NULL,
	account_number TEXT,
	bill_type TEXT, -- utility, telecom, credit_card, insurance
	amount DECIMAL(15, 2) NOT NULL,
	due_date DATE NOT NULL,
	auto_pay BOOLEAN DEFAULT FALSE,
	created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Bill Payments table
CREATE TABLE IF NOT EXISTS bill_payments (
	id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
	user_id UUID REFERENCES users(id) ON DELETE CASCADE,
	bill_id UUID REFERENCES bills(id) ON DELETE CASCADE,
	account_id UUID REFERENCES accounts(id),
	amount DECIMAL(15, 2) NOT NULL,
	scheduled_date TIMESTAMPTZ,
	status TEXT DEFAULT 'pending', -- pending, completed, failed
	created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Checks table
CREATE TABLE IF NOT EXISTS checks (
	id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
	user_id UUID REFERENCES users(id) ON DELETE CASCADE,
	account_id UUID REFERENCES accounts(id),
	amount DECIMAL(15, 2) NOT NULL,
	check_number TEXT,
	payee TEXT,
	front_image_url TEXT,
	back_image_url TEXT,
	status TEXT DEFAULT 'pending', -- pending, cleared, void
	created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Check Orders table
CREATE TABLE IF NOT EXISTS check_orders (
	id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
	user_id UUID REFERENCES users(id) ON DELETE CASCADE,
	account_id UUID REFERENCES accounts(id),
	design TEXT, -- Montblanc, Cartier, etc.
	quantity INTEGER NOT NULL,
	status TEXT DEFAULT 'processing', -- processing, shipped, delivered
	created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Statements table
CREATE TABLE IF NOT EXISTS statements (
	id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
	user_id UUID REFERENCES users(id) ON DELETE CASCADE,
	account_id UUID REFERENCES accounts(id),
	period_start DATE NOT NULL,
	period_end DATE NOT NULL,
	pdf_url TEXT,
	created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Notifications table
CREATE TABLE IF NOT EXISTS notifications (
	id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
	user_id UUID REFERENCES users(id) ON DELETE CASCADE,
	type TEXT NOT NULL,
	message TEXT NOT NULL,
	delivery_method TEXT, -- email, sms, push
	read BOOLEAN DEFAULT FALSE,
	created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Card Issue Reports table
CREATE TABLE IF NOT EXISTS card_issue_reports (
	id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
	user_id UUID REFERENCES users(id) ON DELETE CASCADE,
	card_id UUID REFERENCES cards(id) ON DELETE CASCADE,
	issue_type TEXT NOT NULL CHECK (issue_type IN ('lost', 'stolen', 'damaged', 'other')),
	description TEXT,
	status TEXT DEFAULT 'investigating' CHECK (status IN ('investigating', 'resolved', 'card_blocked')),
	admin_notes TEXT,
	created_at TIMESTAMPTZ DEFAULT NOW(),
	resolved_at TIMESTAMPTZ
);

-- Beneficiaries table
CREATE TABLE IF NOT EXISTS beneficiaries (
	id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
	user_id UUID REFERENCES users(id) ON DELETE CASCADE,
	full_name TEXT NOT NULL,
	relationship TEXT NOT NULL,
	email TEXT,
	phone TEXT,
	percentage DECIMAL(5, 2) NOT NULL,
	created_at TIMESTAMPTZ DEFAULT NOW(),
	updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_accounts_user_id ON accounts(user_id);
CREATE INDEX IF NOT EXISTS idx_cards_user_id ON cards(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_account_id ON transactions(account_id);
CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON transactions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_transfers_user_id ON transfers(user_id);
CREATE INDEX IF NOT EXISTS idx_bills_user_id ON bills(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_beneficiaries_user_id ON beneficiaries(user_id);
CREATE INDEX IF NOT EXISTS idx_card_issue_reports_user_id ON card_issue_reports(user_id);
CREATE INDEX IF NOT EXISTS idx_card_issue_reports_card_id ON card_issue_reports(card_id);
CREATE INDEX IF NOT EXISTS idx_card_issue_reports_created_at ON card_issue_reports(created_at DESC);

-- Enable Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE cards ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE transfers ENABLE ROW LEVEL SECURITY;
ALTER TABLE bills ENABLE ROW LEVEL SECURITY;
ALTER TABLE bill_payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE checks ENABLE ROW LEVEL SECURITY;
ALTER TABLE check_orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE statements ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE beneficiaries ENABLE ROW LEVEL SECURITY;
ALTER TABLE card_issue_reports ENABLE ROW LEVEL SECURITY;