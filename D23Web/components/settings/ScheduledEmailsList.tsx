"use client";

import { useState, useEffect } from "react";
import { Mail, Clock, Trash2, Edit2, Loader2, Calendar, X, Check, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import authFetch from "@/lib/auth_fetch";
import { useToast } from "@/components/ui/use-toast";

interface ScheduledEmail {
  id: string;
  to: string;
  subject: string;
  body?: string;
  scheduled_at: string;
  status: string;
  created_at: string;
  last_run_at?: string;
  run_count?: number;
}

interface ScheduledEmailsListProps {
  accessToken: string | null;
}

export function ScheduledEmailsList({ accessToken }: ScheduledEmailsListProps) {
  const { toast } = useToast();
  const [emails, setEmails] = useState<ScheduledEmail[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>("all");

  // Edit dialog state
  const [editingEmail, setEditingEmail] = useState<ScheduledEmail | null>(null);
  const [editForm, setEditForm] = useState({ to: "", subject: "", body: "", scheduled_at: "", scheduled_date: "", scheduled_time: "" });
  const [isSaving, setIsSaving] = useState(false);
  const [editError, setEditError] = useState<string | null>(null);

  const apiBase = process.env.NEXT_PUBLIC_API_URL || "/api"; // Use Next.js proxy to avoid CORS

  const fetchScheduledEmails = async () => {
    if (!accessToken) return;

    setLoading(true);
    try {
      const url = statusFilter === "all"
        ? `${apiBase}/chat/email/scheduled`
        : `${apiBase}/chat/email/scheduled?status=${statusFilter}`;
      const response = await authFetch(url, {}, accessToken);
      if (response.ok) {
        const data = await response.json();
        setEmails(data);
      } else {
        setError("Failed to load scheduled emails");
      }
    } catch (err) {
      setError("Failed to load scheduled emails");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchScheduledEmails();
  }, [accessToken, statusFilter]);

  const handleCancel = async (emailId: string) => {
    if (!accessToken) return;

    try {
      const response = await authFetch(
        `${apiBase}/chat/email/scheduled/${emailId}`,
        { method: "DELETE" },
        accessToken
      );

      if (response.ok) {
        // Update local state - change status to cancelled
        setEmails(emails.map((e) =>
          e.id === emailId ? { ...e, status: "cancelled" } : e
        ));
      } else {
        toast({ title: "Error", description: "Failed to cancel scheduled email", variant: "destructive" });
      }
    } catch (err) {
      toast({ title: "Error", description: "Failed to cancel scheduled email", variant: "destructive" });
    }
  };

  const openEditDialog = (email: ScheduledEmail) => {
    const scheduledDate = email.scheduled_at ? new Date(email.scheduled_at) : new Date();
    setEditingEmail(email);
    setEditForm({
      to: email.to || "",
      subject: email.subject || "",
      body: email.body || "",
      scheduled_at: email.scheduled_at || "",
      scheduled_date: scheduledDate.toISOString().split("T")[0],
      scheduled_time: scheduledDate.toTimeString().slice(0, 5),
    });
    setEditError(null);
  };

  const handleSaveEdit = async () => {
    if (!accessToken || !editingEmail) return;

    if (!editForm.to || !editForm.subject) {
      setEditError("Please fill in recipient and subject");
      return;
    }

    // Combine date and time
    const scheduledAt = new Date(`${editForm.scheduled_date}T${editForm.scheduled_time}`);
    if (scheduledAt <= new Date()) {
      setEditError("Scheduled time must be in the future");
      return;
    }

    setIsSaving(true);
    setEditError(null);

    try {
      const response = await authFetch(
        `${apiBase}/chat/email/scheduled/${editingEmail.id}`,
        {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            to: editForm.to,
            subject: editForm.subject,
            body: editForm.body,
            scheduled_at: scheduledAt.toISOString(),
          }),
        },
        accessToken
      );

      if (response.ok) {
        const updated = await response.json();
        // Update local state
        setEmails(emails.map((e) =>
          e.id === editingEmail.id
            ? { ...e, to: updated.to, subject: updated.subject, body: updated.body, scheduled_at: updated.scheduled_at }
            : e
        ));
        setEditingEmail(null);
      } else {
        const err = await response.json();
        setEditError(err.detail || "Failed to update scheduled email");
      }
    } catch (err) {
      setEditError("Failed to update scheduled email");
    } finally {
      setIsSaving(false);
    }
  };

  const formatDateTime = (isoString: string) => {
    const date = new Date(isoString);
    return date.toLocaleString(undefined, {
      dateStyle: "medium",
      timeStyle: "short",
    });
  };

  const getTimeRemaining = (scheduledAt: string) => {
    const now = new Date();
    const scheduled = new Date(scheduledAt);
    const diff = scheduled.getTime() - now.getTime();

    if (diff <= 0) return "Sending soon...";

    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 0) return `${days}d ${hours % 24}h remaining`;
    if (hours > 0) return `${hours}h ${minutes % 60}m remaining`;
    return `${minutes}m remaining`;
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "active":
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs bg-blue-500/20 text-blue-400 border border-blue-500/30">
            <Clock className="h-3 w-3" />
            Scheduled
          </span>
        );
      case "completed":
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
            <Check className="h-3 w-3" />
            Sent
          </span>
        );
      case "cancelled":
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs bg-red-500/20 text-red-400 border border-red-500/30">
            <X className="h-3 w-3" />
            Cancelled
          </span>
        );
      case "failed":
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs bg-amber-500/20 text-amber-400 border border-amber-500/30">
            <AlertCircle className="h-3 w-3" />
            Failed
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs bg-neutral-500/20 text-neutral-400 border border-neutral-500/30">
            {status}
          </span>
        );
    }
  };

  // Get minimum date (today)
  const today = new Date().toISOString().split("T")[0];

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="h-6 w-6 animate-spin text-violet-400" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Status Filter */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-neutral-500">
          {emails.length} email{emails.length !== 1 ? "s" : ""}
        </p>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-[140px] bg-neutral-50 border-neutral-200 text-neutral-900">
            <SelectValue placeholder="Filter status" />
          </SelectTrigger>
          <SelectContent className="bg-white border-neutral-200">
            <SelectItem value="all" className="text-neutral-900 hover:bg-neutral-100">All Status</SelectItem>
            <SelectItem value="active" className="text-neutral-900 hover:bg-neutral-100">Scheduled</SelectItem>
            <SelectItem value="completed" className="text-neutral-900 hover:bg-neutral-100">Sent</SelectItem>
            <SelectItem value="cancelled" className="text-neutral-900 hover:bg-neutral-100">Cancelled</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {emails.length === 0 ? (
        <div className="text-center py-8">
          <Mail className="h-12 w-12 text-neutral-300 mx-auto mb-3" />
          <p className="text-neutral-500">No scheduled emails</p>
          <p className="text-sm text-neutral-400 mt-1">
            Schedule an email from the chat to see it here
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {emails.map((email) => (
            <div
              key={email.id}
              className="rounded-lg border border-neutral-200 bg-white p-4 hover:border-neutral-300 transition-colors"
            >
              <div className="flex items-start justify-between gap-4">
                {/* Email Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1 flex-wrap">
                    <Mail className="h-4 w-4 text-violet-600 flex-shrink-0" />
                    <span className="font-medium text-neutral-900 truncate">{email.to}</span>
                    {getStatusBadge(email.status)}
                  </div>
                  <p className="text-sm text-neutral-600 truncate mb-2">{email.subject}</p>
                  <div className="flex items-center gap-4 text-xs text-neutral-400 flex-wrap">
                    <div className="flex items-center gap-1">
                      <Calendar className="h-3 w-3" />
                      <span>{formatDateTime(email.scheduled_at)}</span>
                    </div>
                    {email.status === "active" && (
                      <div className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        <span className="text-blue-400">{getTimeRemaining(email.scheduled_at)}</span>
                      </div>
                    )}
                    {email.status === "completed" && email.last_run_at && (
                      <div className="flex items-center gap-1">
                        <Check className="h-3 w-3 text-emerald-400" />
                        <span className="text-emerald-400">Sent {formatDateTime(email.last_run_at)}</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Actions - only show for active emails */}
                {email.status === "active" && (
                  <div className="flex items-center gap-2">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => openEditDialog(email)}
                      className="h-8 w-8 text-neutral-500 hover:text-neutral-900 hover:bg-neutral-100"
                    >
                      <Edit2 className="h-4 w-4" />
                    </Button>
                    <AlertDialog>
                      <AlertDialogTrigger asChild>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8 text-red-400 hover:text-red-300 hover:bg-red-500/10"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </AlertDialogTrigger>
                      <AlertDialogContent className="bg-white border-neutral-200">
                        <AlertDialogHeader>
                          <AlertDialogTitle className="text-neutral-900">Cancel Scheduled Email?</AlertDialogTitle>
                          <AlertDialogDescription className="text-neutral-500">
                            This will cancel the scheduled email to {email.to}. This action cannot be undone.
                          </AlertDialogDescription>
                        </AlertDialogHeader>
                        <AlertDialogFooter>
                          <AlertDialogCancel className="bg-neutral-100 border-neutral-300 text-neutral-900 hover:bg-neutral-200">
                            Keep Email
                          </AlertDialogCancel>
                          <AlertDialogAction
                            onClick={() => handleCancel(email.id)}
                            className="bg-red-600 hover:bg-red-700 text-white"
                          >
                            Cancel Email
                          </AlertDialogAction>
                        </AlertDialogFooter>
                      </AlertDialogContent>
                    </AlertDialog>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {error && (
        <p className="text-sm text-red-400 text-center">{error}</p>
      )}

      {/* Edit Dialog */}
      <Dialog open={!!editingEmail} onOpenChange={() => setEditingEmail(null)}>
        <DialogContent className="sm:max-w-md bg-white border-neutral-200 text-neutral-900">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-neutral-900">
              <Edit2 className="h-5 w-5 text-violet-600" />
              Edit Scheduled Email
            </DialogTitle>
          </DialogHeader>

          <div className="space-y-4 py-4">
            {/* To */}
            <div className="space-y-2">
              <Label className="text-neutral-600">To</Label>
              <Input
                type="email"
                value={editForm.to}
                onChange={(e) => setEditForm({ ...editForm, to: e.target.value })}
                placeholder="recipient@example.com"
                className="bg-neutral-50 border-neutral-200 text-neutral-900 placeholder:text-neutral-400"
              />
            </div>

            {/* Subject */}
            <div className="space-y-2">
              <Label className="text-neutral-600">Subject</Label>
              <Input
                value={editForm.subject}
                onChange={(e) => setEditForm({ ...editForm, subject: e.target.value })}
                placeholder="Email subject"
                className="bg-neutral-50 border-neutral-200 text-neutral-900 placeholder:text-neutral-400"
              />
            </div>

            {/* Body */}
            <div className="space-y-2">
              <Label className="text-neutral-600">Message</Label>
              <Textarea
                value={editForm.body}
                onChange={(e) => setEditForm({ ...editForm, body: e.target.value })}
                placeholder="Type your message..."
                rows={4}
                className="bg-neutral-50 border-neutral-200 text-neutral-900 placeholder:text-neutral-400 resize-none"
              />
            </div>

            {/* Date/Time */}
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-2">
                <Label className="text-neutral-600">Date</Label>
                <Input
                  type="date"
                  value={editForm.scheduled_date}
                  onChange={(e) => setEditForm({ ...editForm, scheduled_date: e.target.value })}
                  min={today}
                  className="bg-neutral-50 border-neutral-200 text-neutral-900"
                />
              </div>
              <div className="space-y-2">
                <Label className="text-neutral-600">Time</Label>
                <Input
                  type="time"
                  value={editForm.scheduled_time}
                  onChange={(e) => setEditForm({ ...editForm, scheduled_time: e.target.value })}
                  className="bg-neutral-50 border-neutral-200 text-neutral-900"
                />
              </div>
            </div>

            {editError && (
              <p className="text-sm text-red-400">{editError}</p>
            )}
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setEditingEmail(null)}
              disabled={isSaving}
              className="border-neutral-300 bg-neutral-100 text-neutral-600 hover:bg-neutral-200"
            >
              Cancel
            </Button>
            <Button
              onClick={handleSaveEdit}
              disabled={isSaving || !editForm.to || !editForm.subject}
              className="bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white"
            >
              {isSaving ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Saving...
                </>
              ) : (
                "Save Changes"
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
