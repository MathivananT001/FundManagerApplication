-- MoneyLendingManager - Dev Seed Data
-- WARNING: For development/testing only. Do NOT run in production.

INSERT INTO users (id, cognito_sub, email, phone_number, full_name, language_preference) VALUES
('usr-001', 'cognito-sub-001', 'manager@example.com', '+919876543210', 'Rajesh Kumar', 'ta'),
('usr-002', 'cognito-sub-002', 'member1@example.com', '+919876543211', 'Priya Sharma', 'en'),
('usr-003', 'cognito-sub-003', 'member2@example.com', '+919876543212', 'Arun Patel', 'ta'),
('usr-bot', 'cognito-sub-bot', NULL, NULL, 'MLM Bot Agent', 'en');

INSERT INTO user_roles (id, user_id, role) VALUES
('role-001', 'usr-001', 'FUND_MANAGER'),
('role-002', 'usr-002', 'MEMBER'),
('role-003', 'usr-003', 'MEMBER'),
('role-bot', 'usr-bot', 'BOT');

INSERT INTO chit_groups (id, name, description, manager_id, member_slots, amount_per_person, manager_fee_percent, status) VALUES
('grp-001', 'Test Chit Fund', 'Development test group', 'usr-001', 10, 5000.00, 2.00, 'ACTIVE');

INSERT INTO group_members (id, group_id, user_id, role) VALUES
('gm-001', 'grp-001', 'usr-001', 'MANAGER'),
('gm-002', 'grp-001', 'usr-002', 'MEMBER'),
('gm-003', 'grp-001', 'usr-003', 'MEMBER'),
('gm-bot', 'grp-001', 'usr-bot', 'BOT');
