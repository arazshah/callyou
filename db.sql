-- کاربران اصلی
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    user_type VARCHAR(20) NOT NULL CHECK (user_type IN ('client', 'consultant', 'admin')),
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    two_factor_enabled BOOLEAN DEFAULT false,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- پروفایل کاربران
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    avatar_url VARCHAR(500),
    bio TEXT,
    birth_date DATE,
    gender VARCHAR(10),
    city VARCHAR(100),
    country VARCHAR(100) DEFAULT 'Iran',
    timezone VARCHAR(50) DEFAULT 'Asia/Tehran',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- گروه‌های مشاوران (شرکت‌ها)
CREATE TABLE consultant_groups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    logo_url VARCHAR(500),
    website VARCHAR(255),
    phone VARCHAR(20),
    email VARCHAR(255),
    address TEXT,
    group_type VARCHAR(20) DEFAULT 'company' CHECK (group_type IN ('company', 'team', 'partnership')),
    is_verified BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- مشاوران
CREATE TABLE consultants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    group_id UUID REFERENCES consultant_groups(id),
    title VARCHAR(200),
    specialization TEXT[],
    experience_years INTEGER,
    education TEXT,
    certifications JSONB,
    languages VARCHAR(100)[] DEFAULT ARRAY['Persian'],
    rating DECIMAL(3,2) DEFAULT 0.00,
    total_consultations INTEGER DEFAULT 0,
    total_revenue INTEGER DEFAULT 0,
    response_time_hours INTEGER DEFAULT 24,
    is_online BOOLEAN DEFAULT false,
    last_seen TIMESTAMP,
    is_featured BOOLEAN DEFAULT false,
    is_sponsored BOOLEAN DEFAULT false,
    subscription_type VARCHAR(20) DEFAULT 'free' CHECK (subscription_type IN ('free', 'professional', 'premium')),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'suspended', 'banned')),
    commission_rate DECIMAL(4,2) DEFAULT 15.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- زمان‌بندی مشاوران
CREATE TABLE consultant_availability (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    consultant_id UUID REFERENCES consultants(id) ON DELETE CASCADE,
    day_of_week INTEGER NOT NULL CHECK (day_of_week >= 0 AND day_of_week <= 6), -- 0=Sunday
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_available BOOLEAN DEFAULT true,
    timezone VARCHAR(50) DEFAULT 'Asia/Tehran',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- استثناهای زمان‌بندی (تعطیلات، مرخصی)
CREATE TABLE consultant_time_exceptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    consultant_id UUID REFERENCES consultants(id) ON DELETE CASCADE,
    exception_date DATE NOT NULL,
    start_time TIME,
    end_time TIME,
    exception_type VARCHAR(20) NOT NULL CHECK (exception_type IN ('unavailable', 'busy', 'holiday')),
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- تعرفه‌های مشاوران
CREATE TABLE consultant_pricing (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    consultant_id UUID REFERENCES consultants(id) ON DELETE CASCADE,
    service_type VARCHAR(50) NOT NULL CHECK (service_type IN ('voice_call', 'video_call', 'text_chat', 'project_based')),
    duration_minutes INTEGER NOT NULL,
    price_amount INTEGER NOT NULL,
    currency VARCHAR(3) DEFAULT 'IRR',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- دسته‌بندی‌های تخصصی
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    icon VARCHAR(50),
    parent_id UUID REFERENCES categories(id),
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- پیام‌های داخلی (صندوق پیام)
CREATE TABLE internal_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sender_id UUID REFERENCES users(id),
    recipient_id UUID REFERENCES users(id),
    subject VARCHAR(200),
    message_body TEXT NOT NULL,
    message_type VARCHAR(20) DEFAULT 'text' CHECK (message_type IN ('text', 'file', 'consultation_request')),
    is_read BOOLEAN DEFAULT false,
    is_archived BOOLEAN DEFAULT false,
    parent_message_id UUID REFERENCES internal_messages(id),
    priority VARCHAR(10) DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    read_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- فایل‌های پیام‌های داخلی
CREATE TABLE message_attachments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID REFERENCES internal_messages(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_size INTEGER NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- چت‌های زنده (قبل از رزرو)
CREATE TABLE live_chats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES users(id),
    consultant_id UUID REFERENCES consultants(id),
    session_id VARCHAR(100) UNIQUE NOT NULL,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'ended', 'transferred')),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- پیام‌های چت زنده
CREATE TABLE live_chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_id UUID REFERENCES live_chats(id) ON DELETE CASCADE,
    sender_id UUID REFERENCES users(id),
    message_text TEXT,
    message_type VARCHAR(20) DEFAULT 'text' CHECK (message_type IN ('text', 'file', 'system')),
    file_url VARCHAR(500),
    is_read BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- درخواست‌های مشاوره
CREATE TABLE consultation_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES users(id),
    consultant_id UUID REFERENCES consultants(id),
    category_id UUID REFERENCES categories(id),
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    consultation_type VARCHAR(20) NOT NULL CHECK (consultation_type IN ('scheduled', 'immediate')),
    service_type VARCHAR(20) NOT NULL CHECK (service_type IN ('voice_call', 'video_call', 'text_chat')),
    duration_minutes INTEGER NOT NULL,
    scheduled_datetime TIMESTAMP,
    actual_start_time TIMESTAMP,
    actual_end_time TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'rejected', 'ongoing', 'completed', 'cancelled', 'no_show')),
    priority VARCHAR(10) DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    cancellation_reason TEXT,
    cancelled_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- جلسات مشاوره
CREATE TABLE consultation_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id UUID REFERENCES consultation_requests(id),
    room_id VARCHAR(100) UNIQUE NOT NULL,
    access_token VARCHAR(255),
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    duration_minutes INTEGER,
    recording_url VARCHAR(500),
    recording_enabled BOOLEAN DEFAULT false,
    session_notes TEXT,
    technical_issues TEXT,
    connection_quality VARCHAR(20),
    status VARCHAR(20) DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'ongoing', 'completed', 'cancelled', 'failed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- پرداخت‌ها
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    consultation_request_id UUID REFERENCES consultation_requests(id),
    amount INTEGER NOT NULL,
    original_amount INTEGER NOT NULL,
    discount_amount INTEGER DEFAULT 0,
    commission_amount INTEGER DEFAULT 0,
    currency VARCHAR(3) DEFAULT 'IRR',
    payment_type VARCHAR(20) NOT NULL CHECK (payment_type IN ('prepayment', 'completion', 'full', 'refund')),
    payment_method VARCHAR(20) CHECK (payment_method IN ('wallet', 'gateway', 'card', 'bank_transfer')),
    transaction_id VARCHAR(100),
    gateway_transaction_id VARCHAR(100),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'refunded', 'cancelled')),
    gateway_response JSONB,
    refund_reason TEXT,
    refunded_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- کیف پول
CREATE TABLE wallets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) UNIQUE,
    balance INTEGER DEFAULT 0,
    frozen_balance INTEGER DEFAULT 0, -- مبلغ در انتظار تسویه
    currency VARCHAR(3) DEFAULT 'IRR',
    is_active BOOLEAN DEFAULT true,
    last_transaction_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- تراکنش‌های کیف پول
CREATE TABLE wallet_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    wallet_id UUID REFERENCES wallets(id),
    amount INTEGER NOT NULL,
    balance_after INTEGER NOT NULL,
    transaction_type VARCHAR(20) NOT NULL CHECK (transaction_type IN ('deposit', 'withdrawal', 'payment', 'refund', 'commission', 'bonus', 'penalty')),
    description TEXT,
    reference_id UUID,
    reference_type VARCHAR(50), -- 'consultation', 'payment', 'refund', etc.
    status VARCHAR(20) DEFAULT 'completed' CHECK (status IN ('pending', 'completed', 'failed', 'cancelled')),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- کوپن‌های تخفیف
CREATE TABLE discount_coupons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100),
    description TEXT,
    discount_type VARCHAR(20) NOT NULL CHECK (discount_type IN ('percentage', 'fixed_amount')),
    discount_value INTEGER NOT NULL,
    minimum_amount INTEGER DEFAULT 0,
    maximum_discount INTEGER,
    max_usage INTEGER DEFAULT 1,
    max_usage_per_user INTEGER DEFAULT 1,
    current_usage INTEGER DEFAULT 0,
    valid_from TIMESTAMP NOT NULL,
    valid_until TIMESTAMP NOT NULL,
    applicable_categories UUID[] DEFAULT '{}',
    applicable_consultants UUID[] DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- استفاده از کوپن‌ها
CREATE TABLE coupon_usages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    coupon_id UUID REFERENCES discount_coupons(id),
    user_id UUID REFERENCES users(id),
    consultation_request_id UUID REFERENCES consultation_requests(id),
    discount_amount INTEGER NOT NULL,
    used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- نظرات و امتیازات
CREATE TABLE reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    consultation_request_id UUID REFERENCES consultation_requests(id),
    client_id UUID REFERENCES users(id),
    consultant_id UUID REFERENCES consultants(id),
    overall_rating INTEGER CHECK (overall_rating >= 1 AND overall_rating <= 5),
    communication_rating INTEGER CHECK (communication_rating >= 1 AND communication_rating <= 5),
    expertise_rating INTEGER CHECK (expertise_rating >= 1 AND expertise_rating <= 5),
    punctuality_rating INTEGER CHECK (punctuality_rating >= 1 AND punctuality_rating <= 5),
    comment TEXT,
    pros TEXT,
    cons TEXT,
    is_anonymous BOOLEAN DEFAULT false,
    is_approved BOOLEAN DEFAULT true,
    helpful_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- فایل‌های جلسات
CREATE TABLE session_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES consultation_sessions(id),
    uploader_id UUID REFERENCES users(id),
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_size INTEGER NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(20) CHECK (file_type IN ('document', 'image', 'video', 'audio', 'other')),
    is_secure BOOLEAN DEFAULT true,
    download_count INTEGER DEFAULT 0,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- یادآوری‌ها
CREATE TABLE reminders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    consultation_request_id UUID REFERENCES consultation_requests(id),
    user_id UUID REFERENCES users(id),
    reminder_type VARCHAR(20) NOT NULL CHECK (reminder_type IN ('sms', 'email', 'push', 'internal')),
    scheduled_time TIMESTAMP NOT NULL,
    message TEXT,
    is_sent BOOLEAN DEFAULT false,
    sent_at TIMESTAMP,
    delivery_status VARCHAR(20) DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- پشتیبانی
CREATE TABLE support_tickets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    subject VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    category VARCHAR(50),
    priority VARCHAR(10) DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    status VARCHAR(20) DEFAULT 'open' CHECK (status IN ('open', 'in_progress', 'waiting_customer', 'resolved', 'closed')),
    assigned_to UUID REFERENCES users(id),
    resolution_notes TEXT,
    satisfaction_rating INTEGER CHECK (satisfaction_rating >= 1 AND satisfaction_rating <= 5),
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- پیام‌های تیکت پشتیبانی
CREATE TABLE support_ticket_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticket_id UUID REFERENCES support_tickets(id) ON DELETE CASCADE,
    sender_id UUID REFERENCES users(id),
    message TEXT NOT NULL,
    is_internal BOOLEAN DEFAULT false,
    attachments JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- نوتیفیکیشن‌ها
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(50) NOT NULL,
    priority VARCHAR(10) DEFAULT 'normal',
    is_read BOOLEAN DEFAULT false,
    is_sent BOOLEAN DEFAULT false,
    delivery_method VARCHAR(20)[] DEFAULT ARRAY['internal'],
    data JSONB,
    action_url VARCHAR(500),
    expires_at TIMESTAMP,
    read_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- تنظیمات سیستم
CREATE TABLE system_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT NOT NULL,
    setting_type VARCHAR(20) DEFAULT 'string' CHECK (setting_type IN ('string', 'integer', 'boolean', 'json')),
    description TEXT,
    is_public BOOLEAN DEFAULT false,
    updated_by UUID REFERENCES users(id),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- لاگ فعالیت‌ها (برای امنیت)
CREATE TABLE activity_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    ip_address INET,
    user_agent TEXT,
    details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- بکاپ‌ها
CREATE TABLE backup_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    backup_type VARCHAR(20) NOT NULL CHECK (backup_type IN ('full', 'incremental', 'differential')),
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT,
    status VARCHAR(20) DEFAULT 'in_progress' CHECK (status IN ('in_progress', 'completed', 'failed')),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT
);

-- ایندکس‌های مهم برای بهینه‌سازی
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_phone ON users(phone);
CREATE INDEX idx_users_type ON users(user_type);
CREATE INDEX idx_consultants_status ON consultants(status);
CREATE INDEX idx_consultants_online ON consultants(is_online);
CREATE INDEX idx_consultation_requests_status ON consultation_requests(status);
CREATE INDEX idx_consultation_requests_client ON consultation_requests(client_id);
CREATE INDEX idx_consultation_requests_consultant ON consultation_requests(consultant_id);
CREATE INDEX idx_consultation_requests_datetime ON consultation_requests(scheduled_datetime);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_payments_user ON payments(user_id);
CREATE INDEX idx_wallet_transactions_wallet ON wallet_transactions(wallet_id);
CREATE INDEX idx_notifications_user_unread ON notifications(user_id, is_read);
CREATE INDEX idx_internal_messages_recipient_unread ON internal_messages(recipient_id, is_read);
CREATE INDEX idx_live_chats_participants ON live_chats(client_id, consultant_id);