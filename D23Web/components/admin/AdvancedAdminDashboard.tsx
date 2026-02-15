"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import {
  BarChart,
  Users,
  Activity,
  MessageSquare,
  Clock,
  TrendingUp,
  AlertCircle,
  Database,
  Send,
  Download,
  RefreshCw,
  Filter,
  Calendar,
  PieChart as PieChartIcon,
  LineChart as LineChartIcon
} from "lucide-react";
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart as RechartsBarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from "recharts";

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
  avg_response_time?: number;
  user_engagement?: {
    new_users_7d: number;
    returning_users_7d: number;
    avg_messages_per_user: number;
  };
};

type SystemHealthData = {
  api_status: "healthy" | "degraded" | "down";
  database_status: "connected" | "disconnected";
  error_rate: number;
  uptime: string;
  last_error?: string;
};

const PAGE_SIZE = 15;

const COLORS = ["#10b981", "#3b82f6", "#8b5cf6", "#f59e0b", "#ef4444", "#06b6d4", "#ec4899", "#84cc16"];

function formatTimestamp(value?: string | null) {
  if (!value) return "";
  return value.replace("T", " ").replace("Z", "");
}

function exportToCSV(data: any[], filename: string) {
  if (data.length === 0) return;

  const headers = Object.keys(data[0]);
  const csvContent = [
    headers.join(","),
    ...data.map(row => headers.map(header => JSON.stringify(row[header] ?? "")).join(","))
  ].join("\n");

  const blob = new Blob([csvContent], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

export default function AdvancedAdminDashboard() {
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

  // Filter states
  const [dateRange, setDateRange] = useState("7"); // days
  const [intentFilter, setIntentFilter] = useState<string>("all");
  const [directionFilter, setDirectionFilter] = useState<string>("all");
  const [autoRefresh, setAutoRefresh] = useState(false);

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
      const res = await fetch(`${apiBase}/admin/analytics?days=${dateRange}`);
      if (!res.ok) throw new Error("Failed to load analytics.");
      const data = (await res.json()) as AnalyticsData;
      setAnalytics(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load analytics.");
    } finally {
      setLoadingAnalytics(false);
    }
  }, [apiBase, dateRange]);

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

  // Auto-refresh effect
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      loadUsers();
      loadAnalytics();
      loadSystemHealth();
    }, 30000); // Refresh every 30 seconds

    return () => clearInterval(interval);
  }, [autoRefresh, loadUsers, loadAnalytics, loadSystemHealth]);

  // Initial load
  useEffect(() => {
    loadUsers();
  }, [loadUsers]);

  // Reload analytics when date range changes
  useEffect(() => {
    if (analytics) {
      loadAnalytics();
    }
  }, [dateRange]);

  // Filter users based on search
  const filteredUsers = useMemo(() => {
    if (!searchQuery.trim()) return users;
    const query = searchQuery.toLowerCase();
    return users.filter(user => user.phone.toLowerCase().includes(query));
  }, [users, searchQuery]);

  // Filter messages
  const filteredMessages = useMemo(() => {
    let filtered = messages;

    if (directionFilter !== "all") {
      filtered = filtered.filter(msg => msg.direction === directionFilter);
    }

    if (intentFilter !== "all") {
      filtered = filtered.filter(msg => msg.response_type === intentFilter);
    }

    return filtered;
  }, [messages, directionFilter, intentFilter]);

  // Get unique intents for filter
  const availableIntents = useMemo(() => {
    const intents = new Set<string>();
    messages.forEach(msg => {
      if (msg.response_type) intents.add(msg.response_type);
    });
    return Array.from(intents).sort();
  }, [messages]);

  // Prepare pie chart data
  const pieChartData = useMemo(() => {
    if (!analytics) return [];
    return Object.entries(analytics.intent_distribution)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 8)
      .map(([name, value]) => ({
        name: name.replace(/_/g, " "),
        value
      }));
  }, [analytics]);

  return (
    <div className="h-[100dvh] overflow-hidden bg-[var(--background)] text-[var(--foreground)]">
      <div className="mx-auto flex h-full max-w-[1600px] flex-col gap-4 px-6 py-4">
        {/* Header with controls */}
        <div className="flex items-center justify-between">
          <div>
            <div className="text-3xl font-bold tracking-tight">
              Admin Dashboard
            </div>
            <p className="mt-1 text-sm text-[var(--muted-foreground)]">
              Advanced analytics and monitoring
            </p>
          </div>

          <div className="flex items-center gap-3">
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                loadUsers();
                loadAnalytics();
                loadSystemHealth();
              }}
            >
              <RefreshCw className="mr-2 h-4 w-4" />
              Refresh
            </Button>

            <Button
              variant={autoRefresh ? "default" : "outline"}
              size="sm"
              onClick={() => setAutoRefresh(!autoRefresh)}
            >
              <Activity className="mr-2 h-4 w-4" />
              {autoRefresh ? "Auto-refresh ON" : "Auto-refresh OFF"}
            </Button>
          </div>
        </div>

        {/* Error banner */}
        {error ? (
          <div className="rounded-xl border border-red-400/40 bg-red-500/10 px-4 py-2 text-sm text-red-200">
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
            {/* Filters */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm flex items-center gap-2">
                  <Filter className="h-4 w-4" />
                  Filters
                </CardTitle>
              </CardHeader>
              <CardContent className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <Label htmlFor="dateRange" className="text-sm whitespace-nowrap">
                    <Calendar className="inline h-4 w-4 mr-1" />
                    Date Range:
                  </Label>
                  <Select value={dateRange} onValueChange={setDateRange}>
                    <SelectTrigger id="dateRange" className="w-32">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="1">Last 24h</SelectItem>
                      <SelectItem value="7">Last 7 days</SelectItem>
                      <SelectItem value="14">Last 14 days</SelectItem>
                      <SelectItem value="30">Last 30 days</SelectItem>
                      <SelectItem value="90">Last 90 days</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    if (analytics) {
                      exportToCSV(
                        Object.entries(analytics.intent_distribution).map(([intent, count]) => ({
                          intent,
                          count
                        })),
                        `analytics-${new Date().toISOString().split('T')[0]}.csv`
                      );
                    }
                  }}
                >
                  <Download className="mr-2 h-4 w-4" />
                  Export Data
                </Button>
              </CardContent>
            </Card>

            {loadingAnalytics ? (
              <div className="text-sm text-[var(--muted-foreground)]">Loading analytics...</div>
            ) : analytics ? (
              <>
                {/* Stats Overview */}
                <div className="grid gap-4 md:grid-cols-4">
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm font-medium flex items-center gap-2">
                        <MessageSquare className="h-4 w-4" />
                        Total Messages
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold">{analytics.total_messages.toLocaleString()}</div>
                      <p className="text-xs text-[var(--muted-foreground)] mt-1">
                        Last {dateRange} days
                      </p>
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
                      <p className="text-xs text-[var(--muted-foreground)] mt-1">
                        All time
                      </p>
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
                      <p className="text-xs text-[var(--muted-foreground)] mt-1">
                        Currently active
                      </p>
                    </CardContent>
                  </Card>
                  {analytics.user_engagement && (
                    <Card>
                      <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium flex items-center gap-2">
                          <Activity className="h-4 w-4" />
                          Avg Msgs/User
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">
                          {analytics.user_engagement.avg_messages_per_user.toFixed(1)}
                        </div>
                        <p className="text-xs text-[var(--muted-foreground)] mt-1">
                          Engagement rate
                        </p>
                      </CardContent>
                    </Card>
                  )}
                </div>

                {/* Charts Row 1 */}
                <div className="grid gap-4 md:grid-cols-2">
                  {/* Message Volume Line Chart */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <LineChartIcon className="h-5 w-5" />
                        Message Volume Trend
                      </CardTitle>
                      <CardDescription>Daily message count over time</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <ResponsiveContainer width="100%" height={250}>
                        <AreaChart data={analytics.message_volume}>
                          <defs>
                            <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="5%" stopColor="#10b981" stopOpacity={0.8}/>
                              <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                            </linearGradient>
                          </defs>
                          <CartesianGrid strokeDasharray="3 3" opacity={0.1} />
                          <XAxis
                            dataKey="date"
                            tick={{ fontSize: 11 }}
                            tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                          />
                          <YAxis tick={{ fontSize: 11 }} />
                          <Tooltip
                            contentStyle={{
                              backgroundColor: 'var(--card)',
                              border: '1px solid var(--border)',
                              borderRadius: '8px'
                            }}
                          />
                          <Area
                            type="monotone"
                            dataKey="count"
                            stroke="#10b981"
                            fillOpacity={1}
                            fill="url(#colorCount)"
                          />
                        </AreaChart>
                      </ResponsiveContainer>
                    </CardContent>
                  </Card>

                  {/* Intent Distribution Pie Chart */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <PieChartIcon className="h-5 w-5" />
                        Intent Distribution
                      </CardTitle>
                      <CardDescription>Top features requested by users</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <ResponsiveContainer width="100%" height={250}>
                        <PieChart>
                          <Pie
                            data={pieChartData}
                            cx="50%"
                            cy="50%"
                            labelLine={false}
                            label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                            outerRadius={80}
                            fill="#8884d8"
                            dataKey="value"
                          >
                            {pieChartData.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                          </Pie>
                          <Tooltip
                            contentStyle={{
                              backgroundColor: 'var(--card)',
                              border: '1px solid var(--border)',
                              borderRadius: '8px'
                            }}
                          />
                        </PieChart>
                      </ResponsiveContainer>
                    </CardContent>
                  </Card>
                </div>

                {/* Charts Row 2 */}
                <div className="grid gap-4 md:grid-cols-2">
                  {/* Peak Hours Bar Chart */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Clock className="h-5 w-5" />
                        Peak Activity Hours
                      </CardTitle>
                      <CardDescription>Message distribution by hour of day</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <ResponsiveContainer width="100%" height={250}>
                        <RechartsBarChart data={analytics.peak_hours}>
                          <CartesianGrid strokeDasharray="3 3" opacity={0.1} />
                          <XAxis
                            dataKey="hour"
                            tick={{ fontSize: 11 }}
                            tickFormatter={(value) => `${value}h`}
                          />
                          <YAxis tick={{ fontSize: 11 }} />
                          <Tooltip
                            contentStyle={{
                              backgroundColor: 'var(--card)',
                              border: '1px solid var(--border)',
                              borderRadius: '8px'
                            }}
                            labelFormatter={(value) => `${value}:00`}
                          />
                          <Bar dataKey="count" fill="#3b82f6" radius={[8, 8, 0, 0]} />
                        </RechartsBarChart>
                      </ResponsiveContainer>
                    </CardContent>
                  </Card>

                  {/* Intent Distribution Bar Chart */}
                  <Card>
                    <CardHeader>
                      <CardTitle>Top Intents (Detailed)</CardTitle>
                      <CardDescription>Most popular bot features</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <ResponsiveContainer width="100%" height={250}>
                        <RechartsBarChart
                          data={Object.entries(analytics.intent_distribution)
                            .sort(([, a], [, b]) => b - a)
                            .slice(0, 10)
                            .map(([name, count]) => ({ name: name.replace(/_/g, " "), count }))}
                          layout="vertical"
                        >
                          <CartesianGrid strokeDasharray="3 3" opacity={0.1} />
                          <XAxis type="number" tick={{ fontSize: 11 }} />
                          <YAxis
                            type="category"
                            dataKey="name"
                            tick={{ fontSize: 10 }}
                            width={100}
                          />
                          <Tooltip
                            contentStyle={{
                              backgroundColor: 'var(--card)',
                              border: '1px solid var(--border)',
                              borderRadius: '8px'
                            }}
                          />
                          <Bar dataKey="count" fill="#8b5cf6" radius={[0, 8, 8, 0]} />
                        </RechartsBarChart>
                      </ResponsiveContainer>
                    </CardContent>
                  </Card>
                </div>

                {/* User Engagement */}
                {analytics.user_engagement && (
                  <Card>
                    <CardHeader>
                      <CardTitle>User Engagement (Last 7 Days)</CardTitle>
                      <CardDescription>New vs returning users</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="grid gap-4 md:grid-cols-3">
                        <div className="flex flex-col gap-2">
                          <span className="text-sm text-[var(--muted-foreground)]">New Users</span>
                          <span className="text-2xl font-bold text-green-500">
                            {analytics.user_engagement.new_users_7d}
                          </span>
                        </div>
                        <div className="flex flex-col gap-2">
                          <span className="text-sm text-[var(--muted-foreground)]">Returning Users</span>
                          <span className="text-2xl font-bold text-blue-500">
                            {analytics.user_engagement.returning_users_7d}
                          </span>
                        </div>
                        <div className="flex flex-col gap-2">
                          <span className="text-sm text-[var(--muted-foreground)]">Retention Rate</span>
                          <span className="text-2xl font-bold text-purple-500">
                            {((analytics.user_engagement.returning_users_7d /
                              (analytics.user_engagement.new_users_7d + analytics.user_engagement.returning_users_7d)) * 100).toFixed(1)}%
                          </span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </>
            ) : (
              <div className="text-sm text-[var(--muted-foreground)]">
                Click the Analytics tab to load data.
              </div>
            )}
          </TabsContent>

          {/* Users Tab */}
          <TabsContent value="users" className="flex-1 min-h-0 flex flex-col gap-4">
            {/* Filters */}
            <div className="flex items-center gap-3 flex-wrap">
              <Input
                placeholder="Search by phone number..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="max-w-xs"
              />

              <Select value={directionFilter} onValueChange={setDirectionFilter}>
                <SelectTrigger className="w-40">
                  <SelectValue placeholder="Direction" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Messages</SelectItem>
                  <SelectItem value="incoming">Incoming</SelectItem>
                  <SelectItem value="outgoing">Outgoing</SelectItem>
                </SelectContent>
              </Select>

              {availableIntents.length > 0 && (
                <Select value={intentFilter} onValueChange={setIntentFilter}>
                  <SelectTrigger className="w-48">
                    <SelectValue placeholder="Intent Type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Intents</SelectItem>
                    {availableIntents.map(intent => (
                      <SelectItem key={intent} value={intent}>
                        {intent.replace(/_/g, " ")}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              )}

              <Button onClick={loadUsers} variant="outline" size="sm">
                <RefreshCw className="mr-2 h-4 w-4" />
                Refresh
              </Button>

              <Button
                variant="outline"
                size="sm"
                onClick={() => exportToCSV(users, `users-${new Date().toISOString().split('T')[0]}.csv`)}
              >
                <Download className="mr-2 h-4 w-4" />
                Export Users
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
                  <CardTitle className="text-sm flex items-center justify-between">
                    <span>Chat {selectedPhone ? `- ${selectedPhone}` : ""}</span>
                    {selectedPhone && (
                      <span className="text-xs text-[var(--muted-foreground)] font-normal">
                        {filteredMessages.length} messages
                      </span>
                    )}
                  </CardTitle>
                </CardHeader>
                <CardContent className="flex-1 overflow-auto" ref={chatRef}>
                  {!selectedPhone ? (
                    <div className="text-sm text-[var(--muted-foreground)]">
                      Select a user to view messages.
                    </div>
                  ) : (
                    <div className="space-y-3">
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
                      {filteredMessages.length === 0 ? (
                        <div className="text-sm text-[var(--muted-foreground)]">
                          No messages match the current filters.
                        </div>
                      ) : (
                        filteredMessages.map((msg, index) => (
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
                                <div className="mt-1 text-[10px] bg-blue-500/20 text-blue-300 px-2 py-0.5 rounded inline-block">
                                  {msg.response_type.replace(/_/g, " ")}
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
                  <Label htmlFor="broadcast-message">Message</Label>
                  <Textarea
                    id="broadcast-message"
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
