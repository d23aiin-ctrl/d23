-- Migration: Add enhanced tracking fields to whatsapp_chat_messages
-- Date: 2026-01-21
-- Description: Adds session tracking, error tracking, and performance metrics

-- Add new columns for better analytics
ALTER TABLE whatsapp_chat_messages
ADD COLUMN IF NOT EXISTS session_id VARCHAR(128),
ADD COLUMN IF NOT EXISTS user_name VARCHAR(255),
ADD COLUMN IF NOT EXISTS user_language VARCHAR(10) DEFAULT 'en',
ADD COLUMN IF NOT EXISTS processing_time_ms INTEGER,
ADD COLUMN IF NOT EXISTS error_type VARCHAR(50),
ADD COLUMN IF NOT EXISTS error_message TEXT,
ADD COLUMN IF NOT EXISTS is_error BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS sentiment VARCHAR(20),
ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}';

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_whatsapp_messages_session_id ON whatsapp_chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_whatsapp_messages_is_error ON whatsapp_chat_messages(is_error);
CREATE INDEX IF NOT EXISTS idx_whatsapp_messages_error_type ON whatsapp_chat_messages(error_type) WHERE error_type IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_whatsapp_messages_response_type ON whatsapp_chat_messages(response_type);
CREATE INDEX IF NOT EXISTS idx_whatsapp_messages_direction ON whatsapp_chat_messages(direction);
CREATE INDEX IF NOT EXISTS idx_whatsapp_messages_phone_created ON whatsapp_chat_messages(phone_number, created_at DESC);

-- Create composite index for date-based user queries
CREATE INDEX IF NOT EXISTS idx_whatsapp_messages_created_phone ON whatsapp_chat_messages(created_at DESC, phone_number);

-- Add comment
COMMENT ON COLUMN whatsapp_chat_messages.session_id IS 'Session identifier for grouping related messages';
COMMENT ON COLUMN whatsapp_chat_messages.processing_time_ms IS 'Time taken to process the message in milliseconds';
COMMENT ON COLUMN whatsapp_chat_messages.sentiment IS 'Message sentiment: positive, negative, neutral';
COMMENT ON COLUMN whatsapp_chat_messages.metadata IS 'Additional flexible metadata for tracking';
