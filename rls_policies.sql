-- Row Level Security Policies for Concierge Bank
-- Run this in Supabase SQL Editor AFTER schema.sql
-- These policies ensure users can only access their own data

-- ============================================================================
-- ACCOUNTS POLICIES
-- ============================================================================

-- Users can only view their own accounts
CREATE POLICY "Users can view own accounts"
ON accounts FOR SELECT
USING (auth.uid() = user_id);

-- Users can only insert accounts for themselves
CREATE POLICY "Users can create own accounts"
ON accounts FOR INSERT
WITH CHECK (auth.uid() = user_id);

-- Users can only update their own accounts
CREATE POLICY "Users can update own accounts"
ON accounts FOR UPDATE
USING (auth.uid() = user_id);

-- ============================================================================
-- TRANSACTIONS POLICIES
-- ============================================================================

-- Users can only view transactions for their own accounts
CREATE POLICY "Users can view own transactions"
ON transactions FOR SELECT
USING (
	EXISTS (
		SELECT 1 FROM accounts
		WHERE accounts.id = transactions.account_id
		AND accounts.user_id = auth.uid()
	)
);

-- Users can insert transactions for their own accounts
CREATE POLICY "Users can create own transactions"
ON transactions FOR INSERT
WITH CHECK (
	EXISTS (
		SELECT 1 FROM accounts
		WHERE accounts.id = transactions.account_id
		AND accounts.user_id = auth.uid()
	)
);

-- ============================================================================
-- CARDS POLICIES
-- ============================================================================

CREATE POLICY "Users can view own cards"
ON cards FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users can create own cards"
ON cards FOR INSERT
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own cards"
ON cards FOR UPDATE
USING (auth.uid() = user_id);

-- ============================================================================
-- TRANSFERS POLICIES
-- ============================================================================

CREATE POLICY "Users can view own transfers"
ON transfers FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users can create own transfers"
ON transfers FOR INSERT
WITH CHECK (auth.uid() = user_id);

-- ============================================================================
-- BILLS POLICIES
-- ============================================================================

CREATE POLICY "Users can view own bills"
ON bills FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own bills"
ON bills FOR ALL
USING (auth.uid() = user_id);

-- ============================================================================
-- BILL_PAYMENTS POLICIES
-- ============================================================================

CREATE POLICY "Users can view own bill payments"
ON bill_payments FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users can create own bill payments"
ON bill_payments FOR INSERT
WITH CHECK (auth.uid() = user_id);

-- ============================================================================
-- CHECKS POLICIES
-- ============================================================================

CREATE POLICY "Users can view own checks"
ON checks FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users can create own checks"
ON checks FOR INSERT
WITH CHECK (auth.uid() = user_id);

-- ============================================================================
-- CHECK_ORDERS POLICIES
-- ============================================================================

CREATE POLICY "Users can view own check orders"
ON check_orders FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users can create own check orders"
ON check_orders FOR INSERT
WITH CHECK (auth.uid() = user_id);

-- ============================================================================
-- STATEMENTS POLICIES
-- ============================================================================

CREATE POLICY "Users can view own statements"
ON statements FOR SELECT
USING (auth.uid() = user_id);

-- ============================================================================
-- NOTIFICATIONS POLICIES
-- ============================================================================

CREATE POLICY "Users can view own notifications"
ON notifications FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users can update own notifications"
ON notifications FOR UPDATE
USING (auth.uid() = user_id);

-- ============================================================================
-- BENEFICIARIES POLICIES
-- ============================================================================

CREATE POLICY "Users can manage own beneficiaries"
ON beneficiaries FOR ALL
USING (auth.uid() = user_id);

-- ============================================================================
-- CARD_ISSUE_REPORTS POLICIES
-- ============================================================================

CREATE POLICY "Users can view own card reports"
ON card_issue_reports FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users can create own card reports"
ON card_issue_reports FOR INSERT
WITH CHECK (auth.uid() = user_id);

-- Admins can view all reports
CREATE POLICY "Admins can view all card reports"
ON card_issue_reports FOR SELECT
USING (
	EXISTS (
		SELECT 1 FROM users
		WHERE users.id = auth.uid()
		AND users.role = 'admin'
	)
);

-- Admins can update all reports
CREATE POLICY "Admins can update all card reports"
ON card_issue_reports FOR UPDATE
USING (
	EXISTS (
		SELECT 1 FROM users
		WHERE users.id = auth.uid()
		AND users.role = 'admin'
	)
);

-- ============================================================================
-- USERS POLICIES
-- ============================================================================

-- Users can view their own profile
CREATE POLICY "Users can view own profile"
ON users FOR SELECT
USING (auth.uid() = id);

-- Users can update their own profile
CREATE POLICY "Users can update own profile"
ON users FOR UPDATE
USING (auth.uid() = id);

-- Admins can view all users
CREATE POLICY "Admins can view all users"
ON users FOR SELECT
USING (
	EXISTS (
		SELECT 1 FROM users u
		WHERE u.id = auth.uid()
		AND u.role = 'admin'
	)
);
