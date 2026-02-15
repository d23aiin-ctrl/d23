"use client";

import { useState } from "react";
import { Mail, Send, X, Loader2, Check, Clock, Calendar } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";

interface EmailComposeData {
  to: string;
  subject: string;
  body: string;
  cc?: string;
  bcc?: string;
}

interface EmailScheduleData extends EmailComposeData {
  scheduled_at: string;
  timezone: string;
}

interface EmailComposeCardProps {
  initialData: EmailComposeData;
  onSend: (data: EmailComposeData) => Promise<void>;
  onSchedule?: (data: EmailScheduleData) => Promise<void>;
  onCancel?: () => void;
}

// Quick schedule presets
const SCHEDULE_PRESETS = [
  { label: "10 min", minutes: 10 },
  { label: "30 min", minutes: 30 },
  { label: "1 hour", minutes: 60 },
  { label: "2 hours", minutes: 120 },
  { label: "Tomorrow 9 AM", minutes: -1 }, // Special case
];

export function EmailComposeCard({ initialData, onSend, onSchedule, onCancel }: EmailComposeCardProps) {
  const [emailData, setEmailData] = useState<EmailComposeData>(initialData);
  const [isSending, setIsSending] = useState(false);
  const [sent, setSent] = useState(false);
  const [scheduled, setScheduled] = useState(false);
  const [scheduledTime, setScheduledTime] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [showCcBcc, setShowCcBcc] = useState(false);
  const [scheduleMode, setScheduleMode] = useState(false);
  const [scheduleDate, setScheduleDate] = useState("");
  const [scheduleTime, setScheduleTime] = useState("");
  const [selectedPreset, setSelectedPreset] = useState<number | null>(null);
  const [useCustomTime, setUseCustomTime] = useState(false);

  // Get minimum date (today)
  const today = new Date().toISOString().split("T")[0];

  // Calculate scheduled time from preset
  const getScheduledTimeFromPreset = (minutes: number): Date => {
    if (minutes === -1) {
      // Tomorrow 9 AM
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      tomorrow.setHours(9, 0, 0, 0);
      return tomorrow;
    }
    return new Date(Date.now() + minutes * 60 * 1000);
  };

  // Handle preset selection
  const handlePresetSelect = (index: number, minutes: number) => {
    setSelectedPreset(index);
    setUseCustomTime(false);
    const scheduledAt = getScheduledTimeFromPreset(minutes);
    // Update the date/time fields for display
    setScheduleDate(scheduledAt.toISOString().split("T")[0]);
    setScheduleTime(scheduledAt.toTimeString().slice(0, 5));
  };

  const isValidEmail = (email: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim());

  const handleSend = async () => {
    if (!emailData.to || !emailData.subject) {
      setError("Please fill in recipient and subject");
      return;
    }
    if (!isValidEmail(emailData.to)) {
      setError("Please enter a valid email address");
      return;
    }

    setIsSending(true);
    setError(null);

    try {
      await onSend(emailData);
      setSent(true);
    } catch (err) {
      setError((err as Error).message || "Failed to send email");
    } finally {
      setIsSending(false);
    }
  };

  const handleSchedule = async () => {
    if (!emailData.to || !emailData.subject) {
      setError("Please fill in recipient and subject");
      return;
    }
    if (!isValidEmail(emailData.to)) {
      setError("Please enter a valid email address");
      return;
    }

    if (!scheduleDate || !scheduleTime) {
      setError("Please select date and time for scheduling");
      return;
    }

    if (!onSchedule) {
      setError("Scheduling not available");
      return;
    }

    // Combine date and time into ISO string
    const scheduledAt = new Date(`${scheduleDate}T${scheduleTime}`);

    if (scheduledAt <= new Date()) {
      setError("Scheduled time must be in the future");
      return;
    }

    setIsSending(true);
    setError(null);

    try {
      await onSchedule({
        ...emailData,
        scheduled_at: scheduledAt.toISOString(),
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      });
      setScheduled(true);
      setScheduledTime(scheduledAt.toLocaleString());
    } catch (err) {
      setError((err as Error).message || "Failed to schedule email");
    } finally {
      setIsSending(false);
    }
  };

  if (sent) {
    return (
      <div className="rounded-xl border border-emerald-500/30 bg-emerald-50 p-4 max-w-md">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-full bg-emerald-100">
            <Check className="h-5 w-5 text-emerald-600" />
          </div>
          <div>
            <p className="font-medium text-emerald-700">Email Sent!</p>
            <p className="text-sm text-neutral-500">Your email has been sent to {emailData.to}</p>
          </div>
        </div>
      </div>
    );
  }

  if (scheduled) {
    return (
      <div className="rounded-xl border border-blue-500/30 bg-blue-50 p-4 max-w-md">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-full bg-blue-100">
            <Clock className="h-5 w-5 text-blue-600" />
          </div>
          <div>
            <p className="font-medium text-blue-700">Email Scheduled!</p>
            <p className="text-sm text-neutral-500">
              Your email to {emailData.to} will be sent on {scheduledTime}
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-neutral-200 bg-white backdrop-blur-sm p-4 max-w-lg w-full shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-violet-100">
            <Mail className="h-4 w-4 text-violet-600" />
          </div>
          <span className="font-medium text-neutral-900">Compose Email</span>
        </div>
        {onCancel && (
          <Button
            variant="ghost"
            size="icon"
            onClick={onCancel}
            className="h-8 w-8 text-neutral-500 hover:text-neutral-900"
          >
            <X className="h-4 w-4" />
          </Button>
        )}
      </div>

      {/* Form */}
      <div className="space-y-3">
        {/* To */}
        <div className="space-y-1">
          <Label className="text-xs text-neutral-500">To</Label>
          <Input
            type="email"
            value={emailData.to}
            onChange={(e) => setEmailData({ ...emailData, to: e.target.value })}
            placeholder="recipient@example.com"
            className="bg-neutral-50 border-neutral-200 text-neutral-900 placeholder:text-neutral-400 focus:border-violet-500"
          />
        </div>

        {/* CC/BCC Toggle */}
        {!showCcBcc && (
          <button
            onClick={() => setShowCcBcc(true)}
            className="text-xs text-violet-600 hover:text-violet-500"
          >
            + Add CC/BCC
          </button>
        )}

        {/* CC */}
        {showCcBcc && (
          <>
            <div className="space-y-1">
              <Label className="text-xs text-neutral-500">CC</Label>
              <Input
                type="email"
                value={emailData.cc || ""}
                onChange={(e) => setEmailData({ ...emailData, cc: e.target.value })}
                placeholder="cc@example.com"
                className="bg-neutral-50 border-neutral-200 text-neutral-900 placeholder:text-neutral-400 focus:border-violet-500"
              />
            </div>
            <div className="space-y-1">
              <Label className="text-xs text-neutral-500">BCC</Label>
              <Input
                type="email"
                value={emailData.bcc || ""}
                onChange={(e) => setEmailData({ ...emailData, bcc: e.target.value })}
                placeholder="bcc@example.com"
                className="bg-neutral-50 border-neutral-200 text-neutral-900 placeholder:text-neutral-400 focus:border-violet-500"
              />
            </div>
          </>
        )}

        {/* Subject */}
        <div className="space-y-1">
          <Label className="text-xs text-neutral-500">Subject</Label>
          <Input
            value={emailData.subject}
            onChange={(e) => setEmailData({ ...emailData, subject: e.target.value })}
            placeholder="Email subject"
            className="bg-neutral-50 border-neutral-200 text-neutral-900 placeholder:text-neutral-400 focus:border-violet-500"
          />
        </div>

        {/* Body */}
        <div className="space-y-1">
          <Label className="text-xs text-neutral-500">Message</Label>
          <Textarea
            value={emailData.body}
            onChange={(e) => setEmailData({ ...emailData, body: e.target.value })}
            placeholder="Type your message here..."
            rows={6}
            className="bg-neutral-50 border-neutral-200 text-neutral-900 placeholder:text-neutral-400 focus:border-violet-500 resize-none"
          />
        </div>

        {/* Schedule Toggle */}
        {onSchedule && (
          <div className="flex items-center justify-between py-2 border-t border-neutral-200">
            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4 text-neutral-500" />
              <span className="text-sm text-neutral-600">Schedule for later</span>
            </div>
            <Switch
              checked={scheduleMode}
              onCheckedChange={setScheduleMode}
              className="data-[state=checked]:bg-violet-600"
            />
          </div>
        )}

        {/* Schedule Date/Time Picker */}
        {scheduleMode && (
          <div className="space-y-3 p-3 rounded-lg bg-neutral-50 border border-neutral-200">
            {/* Quick Presets */}
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-sm text-neutral-500">
                <Clock className="h-4 w-4" />
                <span>Quick schedule</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {SCHEDULE_PRESETS.map((preset, index) => (
                  <button
                    key={index}
                    onClick={() => handlePresetSelect(index, preset.minutes)}
                    className={`px-3 py-1.5 text-xs rounded-lg border transition-all ${
                      selectedPreset === index && !useCustomTime
                        ? "bg-violet-600 border-violet-500 text-white"
                        : "bg-white border-neutral-200 text-neutral-600 hover:border-neutral-300 hover:bg-neutral-100"
                    }`}
                  >
                    {preset.label}
                  </button>
                ))}
                <button
                  onClick={() => {
                    setUseCustomTime(true);
                    setSelectedPreset(null);
                  }}
                  className={`px-3 py-1.5 text-xs rounded-lg border transition-all ${
                    useCustomTime
                      ? "bg-violet-600 border-violet-500 text-white"
                      : "bg-white border-neutral-200 text-neutral-600 hover:border-neutral-300 hover:bg-neutral-100"
                  }`}
                >
                  Custom
                </button>
              </div>
            </div>

            {/* Custom Date/Time (shown when custom is selected or preset chosen) */}
            {(useCustomTime || selectedPreset !== null) && (
              <div className="space-y-2 pt-2 border-t border-neutral-200">
                <div className="flex items-center gap-2 text-sm text-neutral-500">
                  <Calendar className="h-4 w-4" />
                  <span>{useCustomTime ? "Select date and time" : "Scheduled for"}</span>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div className="space-y-1">
                    <Label className="text-xs text-neutral-500">Date</Label>
                    <Input
                      type="date"
                      value={scheduleDate}
                      onChange={(e) => {
                        setScheduleDate(e.target.value);
                        setUseCustomTime(true);
                        setSelectedPreset(null);
                      }}
                      min={today}
                      className="bg-white border-neutral-200 text-neutral-900 focus:border-violet-500"
                    />
                  </div>
                  <div className="space-y-1">
                    <Label className="text-xs text-neutral-500">Time</Label>
                    <Input
                      type="time"
                      value={scheduleTime}
                      onChange={(e) => {
                        setScheduleTime(e.target.value);
                        setUseCustomTime(true);
                        setSelectedPreset(null);
                      }}
                      className="bg-white border-neutral-200 text-neutral-900 focus:border-violet-500"
                    />
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Error */}
        {error && (
          <p className="text-sm text-red-500">{error}</p>
        )}

        {/* Actions */}
        <div className="flex justify-end gap-2 pt-2">
          {onCancel && (
            <Button
              variant="outline"
              onClick={onCancel}
              disabled={isSending}
              className="border-neutral-200 bg-neutral-50 text-neutral-600 hover:bg-neutral-100"
            >
              Cancel
            </Button>
          )}
          {scheduleMode ? (
            <Button
              onClick={handleSchedule}
              disabled={isSending || !emailData.to || !emailData.subject || !scheduleDate || !scheduleTime}
              className="bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white"
            >
              {isSending ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Scheduling...
                </>
              ) : (
                <>
                  <Clock className="h-4 w-4 mr-2" />
                  Schedule Email
                </>
              )}
            </Button>
          ) : (
            <Button
              onClick={handleSend}
              disabled={isSending || !emailData.to || !emailData.subject}
              className="bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white"
            >
              {isSending ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Sending...
                </>
              ) : (
                <>
                  <Send className="h-4 w-4 mr-2" />
                  Send Email
                </>
              )}
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
