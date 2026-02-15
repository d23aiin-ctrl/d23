"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  BarChart,
  Users,
  Activity,
  MessageSquare,
  Clock,
  TrendingUp,
  AlertCircle,
  Database,
  Send
} from "lucide-react";

type WhatsAppUser = {
  phone: string;
  last_seen?: string | null;
  message_count?: number;
};

type WhatsAppMessage = {
  direction: "incoming" | "outgoing";
  text?: string | null;
  created_at?: string | null;
  response_type?: string | null;
};

type UsersResponse = {
  count: number;
  users: WhatsAppUser[];
};

type ChatResponse = {
  phone: string;
  count: number;
  messages: WhatsAppMessage[];
};

type CountsResponse = {
  whatsapp_users_total: number;
  whatsapp_users_active_24h: number;
};

type AnalyticsData = {
  intent_distribution: Record<string, number>;
  message_volume: Array<{ date: string; count: number }>;
  peak_hours: Array<{ hour: number; count: number }>;
  total_messages: number;
};

type SystemHealthData = {
  api_status: "healthy" | "degraded" | "down";
  database_status: "connected" | "disconnected";
  error_rate: number;
  uptime: string;
  last_error?: string;
};

const PAGE_SIZE = 15;

function formatTimestamp(value?: string | null) {
  if (!value) return "";
  return value.replace("T", " ").replace("Z", "");
}

export default function EnhancedAdminDashboard() {
  const apiBase = useMemo(
    () => process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:9002",
    []
  );

  // Users & Chat state
  const [users, setUsers] = useState<WhatsAppUser[]>([]);
  const [counts, setCounts] = useState<CountsResponse | null>(null);
  const [selectedPhone, setSelectedPhone] = useState<string | null>(null);
  const [messages, setMessages] = useState<WhatsAppMessage[]>([]);
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  // Analytics state
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);

  // System Health state
  const [systemHealth, setSystemHealth] = useState<SystemHealthData | null>(null);

  // Broadcast state
  const [broadcastMessage, setBroadcastMessage] = useState("");
  const [broadcastStatus, setBroadcastStatus] = useState<string | null>(null);

  // Loading states
  const [loadingUsers, setLoadingUsers] = useState(false);
  const [loadingChat, setLoadingChat] = useState(false);
  const [loadingAnalytics, setLoadingAnalytics] = useState(false);
  const [loadingHealth, setLoadingHealth] = useState(false);
  const [sendingBroadcast, setSendingBroadcast] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const chatRef = useRef<HTMLDivElement | null>(null);

  // Load users
  const loadUsers = useCallback(async () => {
    setLoadingUsers(true);
    setError(null);
    try {
      const [usersRes, countsRes] = await Promise.all([
        fetch(`${apiBase}/admin/whatsapp-users-list`),
        fetch(`${apiBase}/admin/whatsapp-users`),
      ]);
      if (!usersRes.ok) throw new Error("Failed to load users.");
      if (!countsRes.ok) throw new Error("Failed to load stats.");

      const usersJson = (await usersRes.json()) as UsersResponse;
      const countsJson = (await countsRes.json()) as CountsResponse;
      setUsers(usersJson.users || []);
      setCounts(countsJson);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load data.");
    } finally {
      setLoadingUsers(false);
    }
  }, [apiBase]);

  // Load chat
  const loadChat = useCallback(
    async (phone: string, reset = true) => {
      setLoadingChat(true);
      setError(null);
      try {
        const currentOffset = reset ? 0 : offset;
        const res = await fetch(
          `${apiBase}/admin/whatsapp-chats?phone=${encodeURIComponent(
            phone
          )}&limit=${PAGE_SIZE}&offset=${currentOffset}`
        );
        if (!res.ok) throw new Error("Failed to load chat.");

        const data = (await res.json()) as ChatResponse;
        const nextMessages = data.messages || [];
        setHasMore(nextMessages.length === PAGE_SIZE);
        setOffset(currentOffset + nextMessages.length);
        setMessages((prev) =>
          reset ? nextMessages : [...nextMessages, ...prev]
        );
        if (reset) {
          setSelectedPhone(phone);
        }
        if (reset && chatRef.current) {
          requestAnimationFrame(() => {
            if (chatRef.current) {
              chatRef.current.scrollTop = chatRef.current.scrollHeight;
            }
          });
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load chat.");
      } finally {
        setLoadingChat(false);
      }
    },
    [apiBase, offset]
  );

  // Load analytics
  const loadAnalytics = useCallback(async () => {
    setLoadingAnalytics(true);
    try {
      const res = await fetch(`${apiBase}/admin/analytics`);
      if (!res.ok) throw new Error("Failed to load analytics.");
      const data = (await res.json()) as AnalyticsData;
      setAnalytics(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load analytics.");
    } finally {
      setLoadingAnalytics(false);
    }
  }, [apiBase]);

  // Load system health
  const loadSystemHealth = useCallback(async () => {
    setLoadingHealth(true);
    try {
      const res = await fetch(`${apiBase}/admin/system-health`);
      if (!res.ok) throw new Error("Failed to load system health.");
      const data = (await res.json()) as SystemHealthData;
      setSystemHealth(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load system health.");
    } finally {
      setLoadingHealth(false);
    }
  }, [apiBase]);

  // Send broadcast
  const sendBroadcast = useCallback(async () => {
    if (!broadcastMessage.trim()) {
      setBroadcastStatus("Please enter a message");
      return;
    }

    setSendingBroadcast(true);
    setBroadcastStatus(null);
    try {
      const res = await fetch(`${apiBase}/admin/broadcast`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: broadcastMessage }),
      });
      if (!res.ok) throw new Error("Failed to send broadcast.");

      const data = await res.json();
      setBroadcastStatus(`Broadcast sent to ${data.sent_count} users`);
      setBroadcastMessage("");
    } catch (err) {
      setBroadcastStatus(err instanceof Error ? err.message : "Failed to send broadcast.");
    } finally {
      setSendingBroadcast(false);
    }
  }, [apiBase, broadcastMessage]);

  // Initial load
  useEffect(() => {
    loadUsers();
  }, [loadUsers]);

  // Filter users based on search
  const filteredUsers = useMemo(() => {
    if (!searchQuery.trim()) return users;
    const query = searchQuery.toLowerCase();
    return users.filter(user => user.phone.toLowerCase().includes(query));
  }, [users, searchQuery]);

  return (
    <div className="h-[100dvh] overflow-hidden bg-[var(--background)] text-[var(--foreground)]">
      <div className="mx-auto flex h-full max-w-7xl flex-col gap-6 px-6 py-6">
        {/* Header */}
        <div>
          <div className="text-3xl font-bold tracking-tight">
            Admin Dashboard
          </div>
          <p className="mt-2 text-sm text-[var(--muted-foreground)]">
            Monitor and manage your WhatsApp bot platform
          </p>
        </div>

        {/* Error banner */}
        {error ? (
          <div className="rounded-xl border border-red-400/40 bg-red-500/10 px-4 py-3 text-sm text-red-200">
            {error}
          </div>
        ) : null}

        {/* Tabs */}
        <Tabs defaultValue="analytics" className="flex-1 min-h-0 flex flex-col">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="analytics" onClick={loadAnalytics}>
              <BarChart className="mr-2 h-4 w-4" />
              Analytics
            </TabsTrigger>
            <TabsTrigger value="users">
              <Users className="mr-2 h-4 w-4" />
              Users
            </TabsTrigger>
            <TabsTrigger value="health" onClick={loadSystemHealth}>
              <Activity className="mr-2 h-4 w-4" />
              System Health
            </TabsTrigger>
            <TabsTrigger value="broadcast">
              <Send className="mr-2 h-4 w-4" />
              Broadcast
            </TabsTrigger>
          </TabsList>

          {/* Analytics Tab */}
          <TabsContent value="analytics" className="flex-1 min-h-0 overflow-auto space-y-4">
            {loadingAnalytics ? (
              <div className="text-sm text-[var(--muted-foreground)]">Loading analytics...</div>
            ) : analytics ? (
              <>
                {/* Stats Overview */}
                <div className="grid gap-4 md:grid-cols-3">
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm font-medium flex items-center gap-2">
                        <MessageSquare className="h-4 w-4" />
                        Total Messages
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold">{analytics.total_messages.toLocaleString()}</div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm font-medium flex items-center gap-2">
                        <Users className="h-4 w-4" />
                        Total Users
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold">{counts?.whatsapp_users_total ?? "—"}</div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm font-medium flex items-center gap-2">
                        <TrendingUp className="h-4 w-4" />
                        Active (24h)
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold">{counts?.whatsapp_users_active_24h ?? "—"}</div>
                    </CardContent>
                  </Card>
                </div>

                {/* Intent Distribution */}
                <Card>
                  <CardHeader>
                    <CardTitle>Intent Distribution</CardTitle>
                    <CardDescription>Most requested features</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {Object.entries(analytics.intent_distribution)
                        .sort(([, a], [, b]) => b - a)
                        .slice(0, 10)
                        .map(([intent, count]) => (
                          <div key={intent} className="flex items-center justify-between">
                            <span className="text-sm font-medium capitalize">
                              {intent.replace(/_/g, " ")}
                            </span>
                            <div className="flex items-center gap-3">
                              <div className="w-48 h-2 bg-[var(--secondary)] rounded-full overflow-hidden">
                                <div
                                  className="h-full bg-emerald-500"
                                  style={{
                                    width: `${(count / Math.max(...Object.values(analytics.intent_distribution))) * 100}%`
                                  }}
                                />
                              </div>
                              <span className="text-sm text-[var(--muted-foreground)] w-12 text-right">
                                {count}
                              </span>
                            </div>
                          </div>
                        ))}
                    </div>
                  </CardContent>
                </Card>

                {/* Peak Hours */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Clock className="h-5 w-5" />
                      Peak Activity Hours
                    </CardTitle>
                    <CardDescription>Message distribution by hour of day</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-end justify-between h-32 gap-1">
                      {analytics.peak_hours.map(({ hour, count }) => (
                        <div key={hour} className="flex flex-col items-center flex-1 gap-1">
                          <div className="w-full bg-emerald-500/20 rounded-t relative group">
                            <div
                              className="w-full bg-emerald-500 rounded-t transition-all"
                              style={{
                                height: `${(count / Math.max(...analytics.peak_hours.map(h => h.count))) * 100}px`
                              }}
                            />
                            <div className="absolute -top-8 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity bg-[var(--popover)] border border-[var(--border)] px-2 py-1 rounded text-xs whitespace-nowrap">
                              {count} msgs
                            </div>
                          </div>
                          <span className="text-[10px] text-[var(--muted-foreground)]">
                            {hour}h
                          </span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </>
            ) : (
              <div className="text-sm text-[var(--muted-foreground)]">
                Click the Analytics tab to load data.
              </div>
            )}
          </TabsContent>

          {/* Users Tab */}
          <TabsContent value="users" className="flex-1 min-h-0 flex flex-col gap-4">
            {/* Search bar */}
            <div className="flex items-center gap-3">
              <Input
                placeholder="Search by phone number..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="max-w-sm"
              />
              <Button onClick={loadUsers} variant="outline" size="sm">
                Refresh
              </Button>
            </div>

            {/* Users and Chat Grid */}
            <div className="grid flex-1 min-h-0 gap-6 md:grid-cols-2">
              {/* Users List */}
              <Card className="flex flex-col min-h-0">
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm">
                    Users ({filteredUsers.length})
                  </CardTitle>
                </CardHeader>
                <CardContent className="flex-1 overflow-auto">
                  {loadingUsers ? (
                    <div className="text-sm text-[var(--muted-foreground)]">
                      Loading users...
                    </div>
                  ) : filteredUsers.length === 0 ? (
                    <div className="text-sm text-[var(--muted-foreground)]">
                      No users found.
                    </div>
                  ) : (
                    <div className="space-y-2">
                      {filteredUsers.map((user) => (
                        <button
                          key={user.phone}
                          type="button"
                          onClick={() => loadChat(user.phone, true)}
                          className={`w-full rounded-xl border px-4 py-3 text-left transition ${
                            selectedPhone === user.phone
                              ? "border-emerald-500 bg-emerald-500/10"
                              : "border-transparent hover:border-[var(--border)] hover:bg-[var(--secondary)]"
                          }`}
                        >
                          <div className="flex items-center justify-between gap-3 text-sm font-medium">
                            <span>{user.phone}</span>
                            <span className="text-xs text-[var(--muted-foreground)]">
                              {formatTimestamp(user.last_seen)}
                            </span>
                          </div>
                          <div className="mt-1 text-xs text-[var(--muted-foreground)]">
                            Messages: {user.message_count ?? 0}
                          </div>
                        </button>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Chat Window */}
              <Card className="flex flex-col min-h-0">
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm">Chat</CardTitle>
                </CardHeader>
                <CardContent className="flex-1 overflow-auto" ref={chatRef}>
                  {!selectedPhone ? (
                    <div className="text-sm text-[var(--muted-foreground)]">
                      Select a user to view messages.
                    </div>
                  ) : (
                    <div className="space-y-3">
                      <div className="text-sm font-semibold">{selectedPhone}</div>
                      {hasMore ? (
                        <Button
                          type="button"
                          onClick={() => selectedPhone && loadChat(selectedPhone, false)}
                          variant="outline"
                          size="sm"
                          className="w-full"
                          disabled={loadingChat}
                        >
                          {loadingChat ? "Loading..." : "Load older messages"}
                        </Button>
                      ) : null}
                      {messages.length === 0 ? (
                        <div className="text-sm text-[var(--muted-foreground)]">
                          No messages yet.
                        </div>
                      ) : (
                        messages.map((msg, index) => (
                          <div
                            key={`${msg.created_at}-${index}`}
                            className={`flex ${
                              msg.direction === "incoming"
                                ? "justify-start"
                                : "justify-end"
                            }`}
                          >
                            <div
                              className={`max-w-[72%] rounded-2xl px-4 py-3 text-sm shadow-sm ${
                                msg.direction === "incoming"
                                  ? "bg-[var(--secondary)] text-[var(--foreground)]"
                                  : "bg-emerald-500/15 text-[var(--foreground)]"
                              }`}
                            >
                              <div className="whitespace-pre-wrap">
                                {msg.text || ""}
                              </div>
                              {msg.response_type && (
                                <div className="mt-1 text-[10px] text-[var(--muted-foreground)] italic">
                                  {msg.response_type}
                                </div>
                              )}
                              <div className="mt-2 text-[10px] text-[var(--muted-foreground)]">
                                {formatTimestamp(msg.created_at)}
                              </div>
                            </div>
                          </div>
                        ))
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* System Health Tab */}
          <TabsContent value="health" className="flex-1 min-h-0 overflow-auto space-y-4">
            {loadingHealth ? (
              <div className="text-sm text-[var(--muted-foreground)]">Loading system health...</div>
            ) : systemHealth ? (
              <>
                <div className="grid gap-4 md:grid-cols-3">
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm font-medium flex items-center gap-2">
                        <Activity className="h-4 w-4" />
                        API Status
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className={`text-2xl font-bold ${
                        systemHealth.api_status === "healthy" ? "text-green-500" :
                        systemHealth.api_status === "degraded" ? "text-yellow-500" :
                        "text-red-500"
                      }`}>
                        {systemHealth.api_status.toUpperCase()}
                      </div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm font-medium flex items-center gap-2">
                        <Database className="h-4 w-4" />
                        Database
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className={`text-2xl font-bold ${
                        systemHealth.database_status === "connected" ? "text-green-500" : "text-red-500"
                      }`}>
                        {systemHealth.database_status.toUpperCase()}
                      </div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm font-medium flex items-center gap-2">
                        <AlertCircle className="h-4 w-4" />
                        Error Rate
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold">{systemHealth.error_rate.toFixed(2)}%</div>
                    </CardContent>
                  </Card>
                </div>

                <Card>
                  <CardHeader>
                    <CardTitle>System Information</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-[var(--muted-foreground)]">Uptime</span>
                      <span className="text-sm font-medium">{systemHealth.uptime}</span>
                    </div>
                    {systemHealth.last_error && (
                      <div className="flex flex-col gap-1">
                        <span className="text-sm text-[var(--muted-foreground)]">Last Error</span>
                        <code className="text-xs bg-red-500/10 border border-red-500/20 rounded px-2 py-1">
                          {systemHealth.last_error}
                        </code>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </>
            ) : (
              <div className="text-sm text-[var(--muted-foreground)]">
                Click the System Health tab to load data.
              </div>
            )}
          </TabsContent>

          {/* Broadcast Tab */}
          <TabsContent value="broadcast" className="flex-1 min-h-0 overflow-auto space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Broadcast Message</CardTitle>
                <CardDescription>
                  Send a message to all active WhatsApp users (last 24h)
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Message</label>
                  <Textarea
                    placeholder="Enter your broadcast message..."
                    value={broadcastMessage}
                    onChange={(e) => setBroadcastMessage(e.target.value)}
                    rows={6}
                  />
                  <div className="text-xs text-[var(--muted-foreground)]">
                    Characters: {broadcastMessage.length}
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <Button
                    onClick={sendBroadcast}
                    disabled={sendingBroadcast || !broadcastMessage.trim()}
                  >
                    <Send className="mr-2 h-4 w-4" />
                    {sendingBroadcast ? "Sending..." : `Send to ${counts?.whatsapp_users_active_24h ?? 0} users`}
                  </Button>
                  {broadcastStatus && (
                    <span className="text-sm text-[var(--muted-foreground)]">
                      {broadcastStatus}
                    </span>
                  )}
                </div>

                <div className="rounded-lg border border-yellow-500/20 bg-yellow-500/10 px-4 py-3">
                  <div className="flex items-start gap-2">
                    <AlertCircle className="h-5 w-5 text-yellow-500 mt-0.5" />
                    <div className="text-sm">
                      <strong>Note:</strong> This will send the message to all users active in the last 24 hours.
                      Use this feature carefully as it may result in high message volume.
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
