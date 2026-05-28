-- MoneyLendingManager - Initial Schema Migration
-- Database: moneylender
-- Version: 001

CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY,
    cognito_sub VARCHAR(128) UNIQUE NOT NULL,
    email VARCHAR(255),
    phone_number VARCHAR(20),
    full_name VARCHAR(100) NOT NULL,
    language_preference ENUM('en', 'ta') DEFAULT 'en',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_roles (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    role ENUM('FUND_MANAGER', 'MEMBER', 'BOT') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY uq_user_role (user_id, role)
);

CREATE TABLE IF NOT EXISTS chit_groups (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    manager_id VARCHAR(36) NOT NULL,
    member_slots INT NOT NULL CHECK (member_slots BETWEEN 8 AND 15),
    amount_per_person DECIMAL(12, 2) NOT NULL,
    targeting_amount DECIMAL(14, 2) GENERATED ALWAYS AS (member_slots * amount_per_person) STORED,
    monthly_auction_amount DECIMAL(14, 2) GENERATED ALWAYS AS ((member_slots * amount_per_person) / member_slots) STORED,
    manager_fee_percent DECIMAL(5, 2) DEFAULT 0.00,
    currency VARCHAR(3) DEFAULT 'INR',
    status ENUM('DRAFT', 'ACTIVE', 'COMPLETED', 'ARCHIVED') DEFAULT 'DRAFT',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (manager_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS group_members (
    id VARCHAR(36) PRIMARY KEY,
    group_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    role ENUM('MANAGER', 'MEMBER', 'BOT') NOT NULL,
    has_won BOOLEAN DEFAULT FALSE,
    won_month INT,
    status ENUM('ACTIVE', 'REMOVED') DEFAULT 'ACTIVE',
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES chit_groups(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE KEY uq_group_member (group_id, user_id)
);

CREATE TABLE IF NOT EXISTS auctions (
    id VARCHAR(36) PRIMARY KEY,
    group_id VARCHAR(36) NOT NULL,
    month_number INT NOT NULL,
    scheduled_at DATETIME,
    opened_at DATETIME,
    closed_at DATETIME,
    status ENUM('SCHEDULED', 'OPEN', 'CLOSED', 'CANCELLED') DEFAULT 'SCHEDULED',
    winner_id VARCHAR(36),
    winning_bid_amount DECIMAL(12, 2),
    disbursement_amount DECIMAL(12, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES chit_groups(id),
    FOREIGN KEY (winner_id) REFERENCES users(id),
    UNIQUE KEY uq_group_month (group_id, month_number)
);

CREATE TABLE IF NOT EXISTS bids (
    id VARCHAR(36) PRIMARY KEY,
    auction_id VARCHAR(36) NOT NULL,
    member_id VARCHAR(36) NOT NULL,
    bid_amount DECIMAL(12, 2) NOT NULL,
    placed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (auction_id) REFERENCES auctions(id),
    FOREIGN KEY (member_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS contributions (
    id VARCHAR(36) PRIMARY KEY,
    group_id VARCHAR(36) NOT NULL,
    auction_id VARCHAR(36) NOT NULL,
    member_id VARCHAR(36) NOT NULL,
    month_number INT NOT NULL,
    amount_due DECIMAL(12, 2) NOT NULL,
    deadline_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES chit_groups(id),
    FOREIGN KEY (auction_id) REFERENCES auctions(id),
    FOREIGN KEY (member_id) REFERENCES users(id),
    UNIQUE KEY uq_contribution (group_id, member_id, month_number)
);

CREATE TABLE IF NOT EXISTS payment_records (
    id VARCHAR(36) PRIMARY KEY,
    contribution_id VARCHAR(36) NOT NULL,
    member_id VARCHAR(36) NOT NULL,
    confirmed_by VARCHAR(36),
    status ENUM('PENDING', 'CONFIRMED', 'REJECTED') DEFAULT 'PENDING',
    confirmed_at DATETIME,
    rejection_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (contribution_id) REFERENCES contributions(id),
    FOREIGN KEY (member_id) REFERENCES users(id),
    FOREIGN KEY (confirmed_by) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS attachments (
    id VARCHAR(36) PRIMARY KEY,
    payment_record_id VARCHAR(36) NOT NULL,
    s3_key VARCHAR(512) NOT NULL,
    file_name VARCHAR(255),
    content_type VARCHAR(100),
    description TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (payment_record_id) REFERENCES payment_records(id) ON DELETE CASCADE
);

-- Indexes for common queries
CREATE INDEX idx_groups_manager ON chit_groups(manager_id);
CREATE INDEX idx_groups_status ON chit_groups(status);
CREATE INDEX idx_members_group ON group_members(group_id);
CREATE INDEX idx_members_user ON group_members(user_id);
CREATE INDEX idx_auctions_group ON auctions(group_id);
CREATE INDEX idx_bids_auction ON bids(auction_id);
CREATE INDEX idx_contributions_group_month ON contributions(group_id, month_number);
CREATE INDEX idx_payments_status ON payment_records(status);
CREATE INDEX idx_payments_member ON payment_records(member_id);
