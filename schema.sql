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
	status TEXT DEFAULT 'active', -- active, locked, expired
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

-- RLS Policies (users can only access their own data)
CREATE POLICY "Users can view own data" ON users FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can insert own data" ON users FOR INSERT WITH CHECK (auth.uid() = id);
CREATE POLICY "Users can update own data" ON users FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can view own accounts" ON accounts FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can create own accounts" ON accounts FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own accounts" ON accounts FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can view own cards" ON cards FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can create own cards" ON cards FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own cards" ON cards FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can view own transactions" ON transactions FOR SELECT USING (
	EXISTS (SELECT 1 FROM accounts WHERE accounts.id = transactions.account_id AND accounts.user_id = auth.uid())
);
CREATE POLICY "Users can create own transactions" ON transactions FOR INSERT WITH CHECK (
	EXISTS (SELECT 1 FROM accounts WHERE accounts.id = transactions.account_id AND accounts.user_id = auth.uid())
);

CREATE POLICY "Users can view own transfers" ON transfers FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can create own transfers" ON transfers FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view own bills" ON bills FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own bills" ON bills FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own bill payments" ON bill_payments FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can create own bill payments" ON bill_payments FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view own checks" ON checks FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own checks" ON checks FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own check orders" ON check_orders FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can create own check orders" ON check_orders FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view own statements" ON statements FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can view own notifications" ON notifications FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can update own notifications" ON notifications FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can view own beneficiaries" ON beneficiaries FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own beneficiaries" ON beneficiaries FOR ALL USING (auth.uid() = user_id);
