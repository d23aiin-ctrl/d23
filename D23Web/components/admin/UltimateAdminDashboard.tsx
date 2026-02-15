"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthFetch } from "@/hooks/useAuthFetch";
import { logout } from "@/lib/admin-auth";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import {
  BarChart,
  Users,
  Activity,
  MessageSquare,
  Clock,
  TrendingUp,
  TrendingDown,
  AlertCircle,
  Database,
  Send,
  Download,
  RefreshCw,
  Filter,
  Calendar,
  PieChart as PieChartIcon,
  LineChart as LineChartIcon,
  ArrowUp,
  ArrowDown,
  Minus,
  Star,
  Zap,
  LogOut,
  Wrench,
  Settings
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
  first_seen?: string | null;
  last_active?: string | null;
};

type WhatsAppMessage = {
  direction: "incoming" | "outgoing";
  text?: string | null;
  created_at?: string | null;
  response_type?: string | null;
};

type Activity = {
  phone: string;
  direction: string;
  text?: string | null;
  response_type?: string | null;
  created_at?: string | null;
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
  user_engagement?: {
    new_users_7d: number;
    returning_users_7d: number;
    avg_messages_per_user: number;
  };
};

type GrowthMetrics = {
  current_period: {
    messages: number;
    users: number;
  };
  previous_period: {
    messages: number;
    users: number;
  };
  change: {
    messages_percent: number;
    users_percent: number;
  };
};

type ConversationMetrics = {
  total_conversations: number;
  avg_messages_per_conversation: number;
  incoming_messages: number;
  outgoing_messages: number;
  response_rate: number;
};

type SystemHealthData = {
  api_status: "healthy" | "degraded" | "down";
  database_status: "connected" | "disconnected";
  error_rate: number;
  uptime: string;
  last_error?: string;
};

type ToolUsage = {
  tool: string;
  usage_count: number;
  unique_users: number;
};

type ToolsUsageData = {
  tools_usage: ToolUsage[];
  usage_trend: Record<string, Array<{ date: string; count: number }>>;
  hourly_usage: Record<string, Record<number, number>>;
  top_users_per_tool: Record<string, Array<{ phone: string; usage_count: number }>>;
  recent_usage: Array<{ phone: string; tool: string; timestamp: string }>;
  summary: {
    total_tools: number;
    total_tool_uses: number;
    date_range_days: number;
    most_popular_tool: string | null;
  };
};

const PAGE_SIZE = 15;
const COLORS = ["#10b981", "#3b82f6", "#8b5cf6", "#f59e0b", "#ef4444", "#06b6d4", "#ec4899", "#84cc16"];

function formatTimestamp(value?: string | null) {
  if (!value) return "";
  const date = new Date(value);
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

function formatTimeAgo(value?: string | null) {
  if (!value) return "";
  const date = new Date(value);
  const now = new Date();
  const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (seconds < 60) return `${seconds}s ago`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  return `${Math.floor(seconds / 86400)}d ago`;
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

export default function UltimateAdminDashboard() {
  const router = useRouter();
  const apiBase = useMemo(
    () => process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:9002",
    []
  );

  // Use authenticated fetch
  const authFetch = useAuthFetch(apiBase);

  // State
  const [users, setUsers] = useState<WhatsAppUser[]>([]);
  const [counts, setCounts] = useState<CountsResponse | null>(null);
  const [selectedPhone, setSelectedPhone] = useState<string | null>(null);
  const [messages, setMessages] = useState<WhatsAppMessage[]>([]);
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  // New state for additional features
  const [topUsers, setTopUsers] = useState<WhatsAppUser[]>([]);
  const [recentActivity, setRecentActivity] = useState<Activity[]>([]);
  const [growthMetrics, setGrowthMetrics] = useState<GrowthMetrics | null>(null);
  const [conversationMetrics, setConversationMetrics] = useState<ConversationMetrics | null>(null);

  // Filter states
  const [dateRange, setDateRange] = useState("7");
  const [toolsDateRange, setToolsDateRange] = useState("30");
  const [intentFilter, setIntentFilter] = useState<string>("all");
  const [directionFilter, setDirectionFilter] = useState<string>("all");
  const [toolSearchQuery, setToolSearchQuery] = useState("");
  const [minToolUsage, setMinToolUsage] = useState(0);
  const [autoRefresh, setAutoRefresh] = useState(false);

  // User filters
  const [userActivityFilter, setUserActivityFilter] = useState<string>("all");
  const [minMessages, setMinMessages] = useState(0);
  const [maxMessages, setMaxMessages] = useState(0);
  const [userSortBy, setUserSortBy] = useState<string>("last_seen");

  // Analytics state
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [systemHealth, setSystemHealth] = useState<SystemHealthData | null>(null);
  const [toolsUsage, setToolsUsage] = useState<ToolsUsageData | null>(null);

  // Broadcast state
  const [broadcastMessage, setBroadcastMessage] = useState("");
  const [broadcastStatus, setBroadcastStatus] = useState<string | null>(null);

  // Loading states
  const [loadingUsers, setLoadingUsers] = useState(false);
  const [loadingChat, setLoadingChat] = useState(false);
  const [loadingAnalytics, setLoadingAnalytics] = useState(false);
  const [loadingHealth, setLoadingHealth] = useState(false);
  const [loadingToolsUsage, setLoadingToolsUsage] = useState(false);
  const [sendingBroadcast, setSendingBroadcast] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const chatRef = useRef<HTMLDivElement | null>(null);

  // Load all data
  const loadUsers = useCallback(async () => {
    setLoadingUsers(true);
    setError(null);
    try {
      const [usersRes, countsRes] = await Promise.all([
        authFetch(`${apiBase}/admin/whatsapp-users-list`),
        authFetch(`${apiBase}/admin/whatsapp-users`),
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
  }, [apiBase, authFetch]);

  const loadChat = useCallback(
    async (phone: string, reset = true) => {
      setLoadingChat(true);
      setError(null);
      try {
        const currentOffset = reset ? 0 : offset;
        const res = await authFetch(
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
    [apiBase, offset, authFetch]
  );

  const loadAnalytics = useCallback(async () => {
    setLoadingAnalytics(true);
    try {
      const res = await authFetch(`${apiBase}/admin/analytics?days=${dateRange}`);
      if (!res.ok) throw new Error("Failed to load analytics.");
      const data = (await res.json()) as AnalyticsData;
      setAnalytics(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load analytics.");
    } finally {
      setLoadingAnalytics(false);
    }
  }, [apiBase, dateRange, authFetch]);

  const loadTopUsers = useCallback(async () => {
    try {
      const res = await authFetch(`${apiBase}/admin/top-users?limit=10`);
      if (res.ok) {
        const data = await res.json();
        setTopUsers(data.users || []);
      }
    } catch (err) {
      console.error("Failed to load top users:", err);
    }
  }, [apiBase, authFetch]);

  const loadRecentActivity = useCallback(async () => {
    try {
      const res = await authFetch(`${apiBase}/admin/recent-activity?limit=15`);
      if (res.ok) {
        const data = await res.json();
        setRecentActivity(data.activities || []);
      }
    } catch (err) {
      console.error("Failed to load recent activity:", err);
    }
  }, [apiBase, authFetch]);

  const loadGrowthMetrics = useCallback(async () => {
    try {
      const res = await authFetch(`${apiBase}/admin/growth-metrics`);
      if (res.ok) {
        const data = await res.json();
        setGrowthMetrics(data);
      }
    } catch (err) {
      console.error("Failed to load growth metrics:", err);
    }
  }, [apiBase, authFetch]);

  const loadConversationMetrics = useCallback(async () => {
    try {
      const res = await authFetch(`${apiBase}/admin/conversation-metrics`);
      if (res.ok) {
        const data = await res.json();
        setConversationMetrics(data);
      }
    } catch (err) {
      console.error("Failed to load conversation metrics:", err);
    }
  }, [apiBase, authFetch]);

  const loadSystemHealth = useCallback(async () => {
    setLoadingHealth(true);
    try {
      const res = await authFetch(`${apiBase}/admin/system-health`);
      if (!res.ok) throw new Error("Failed to load system health.");
      const data = (await res.json()) as SystemHealthData;
      setSystemHealth(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load system health.");
    } finally {
      setLoadingHealth(false);
    }
  }, [apiBase, authFetch]);

  const sendBroadcast = useCallback(async () => {
    if (!broadcastMessage.trim()) {
      setBroadcastStatus("Please enter a message");
      return;
    }

    setSendingBroadcast(true);
    setBroadcastStatus(null);
    try {
      const res = await authFetch(`${apiBase}/admin/broadcast`, {
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
  }, [apiBase, broadcastMessage, authFetch]);

  const exportUserChat = useCallback(async (phone: string) => {
    try {
      const res = await authFetch(`${apiBase}/admin/export-chat/${encodeURIComponent(phone)}`);
      if (!res.ok) throw new Error("Failed to export chat.");

      const data = await res.json();
      exportToCSV(data.messages, `chat-${phone}-${new Date().toISOString().split('T')[0]}.csv`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to export chat.");
    }
  }, [apiBase, authFetch]);

  const loadToolsUsage = useCallback(async () => {
    setLoadingToolsUsage(true);
    try {
      const res = await authFetch(`${apiBase}/admin/tools-usage?days=${toolsDateRange}`);
      if (!res.ok) throw new Error("Failed to load tools usage.");
      const data = (await res.json()) as ToolsUsageData;
      setToolsUsage(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load tools usage.");
    } finally {
      setLoadingToolsUsage(false);
    }
  }, [apiBase, toolsDateRange, authFetch]);

  // Auto-refresh effect
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      loadUsers();
      loadAnalytics();
      loadSystemHealth();
      loadTopUsers();
      loadRecentActivity();
      loadGrowthMetrics();
      loadConversationMetrics();
      loadToolsUsage();
    }, 30000);

    return () => clearInterval(interval);
  }, [autoRefresh, loadUsers, loadAnalytics, loadSystemHealth, loadTopUsers, loadRecentActivity, loadGrowthMetrics, loadConversationMetrics, loadToolsUsage]);

  // Initial load
  useEffect(() => {
    loadUsers();
    loadTopUsers();
    loadRecentActivity();
    loadGrowthMetrics();
    loadConversationMetrics();
    loadAnalytics();
  }, [loadUsers, loadTopUsers, loadRecentActivity, loadGrowthMetrics, loadConversationMetrics, loadAnalytics]);

  // Reload analytics when date range changes
  useEffect(() => {
    if (analytics) {
      loadAnalytics();
    }
  }, [dateRange]);

  // Reload tools usage when tools date range changes
  useEffect(() => {
    if (toolsUsage) {
      loadToolsUsage();
    }
  }, [toolsDateRange]);

  // Filter users
  const filteredUsers = useMemo(() => {
    let filtered = users;

    // Search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(user => user.phone.toLowerCase().includes(query));
    }

    // Activity filter
    if (userActivityFilter !== "all") {
      const now = new Date();
      filtered = filtered.filter(user => {
        if (!user.last_seen) return false;
        const lastSeen = new Date(user.last_seen);
        const hoursDiff = (now.getTime() - lastSeen.getTime()) / (1000 * 60 * 60);

        if (userActivityFilter === "24h") return hoursDiff <= 24;
        if (userActivityFilter === "7d") return hoursDiff <= 168; // 7 days
        if (userActivityFilter === "30d") return hoursDiff <= 720; // 30 days
        if (userActivityFilter === "inactive") return hoursDiff > 720; // >30 days
        return true;
      });
    }

    // Message count filter
    if (minMessages > 0) {
      filtered = filtered.filter(user => (user.message_count || 0) >= minMessages);
    }
    if (maxMessages > 0) {
      filtered = filtered.filter(user => (user.message_count || 0) <= maxMessages);
    }

    // Sort
    const sorted = [...filtered];
    if (userSortBy === "last_seen") {
      sorted.sort((a, b) => {
        if (!a.last_seen) return 1;
        if (!b.last_seen) return -1;
        return new Date(b.last_seen).getTime() - new Date(a.last_seen).getTime();
      });
    } else if (userSortBy === "message_count") {
      sorted.sort((a, b) => (b.message_count || 0) - (a.message_count || 0));
    } else if (userSortBy === "first_seen") {
      sorted.sort((a, b) => {
        if (!a.first_seen) return 1;
        if (!b.first_seen) return -1;
        return new Date(b.first_seen).getTime() - new Date(a.first_seen).getTime();
      });
    } else if (userSortBy === "phone") {
      sorted.sort((a, b) => a.phone.localeCompare(b.phone));
    }

    return sorted;
  }, [users, searchQuery, userActivityFilter, minMessages, maxMessages, userSortBy]);

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

  // Filter tools
  const filteredTools = useMemo(() => {
    if (!toolsUsage) return [];

    let filtered = toolsUsage.tools_usage;

    // Apply search filter
    if (toolSearchQuery.trim()) {
      const query = toolSearchQuery.toLowerCase();
      filtered = filtered.filter(tool =>
        tool.tool.toLowerCase().includes(query)
      );
    }

    // Apply minimum usage filter
    if (minToolUsage > 0) {
      filtered = filtered.filter(tool => tool.usage_count >= minToolUsage);
    }

    return filtered;
  }, [toolsUsage, toolSearchQuery, minToolUsage]);

  // Calculate filtered total uses
  const filteredTotalUses = useMemo(() => {
    return filteredTools.reduce((sum, tool) => sum + tool.usage_count, 0);
  }, [filteredTools]);

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
      <div className="mx-auto flex h-full max-w-[1600px] flex-col gap-3 px-6 py-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <div className="text-3xl font-bold tracking-tight flex items-center gap-3">
              Ultimate Admin Dashboard
              <Badge variant="outline" className="text-xs">
                <Zap className="h-3 w-3 mr-1" />
                Live Data
              </Badge>
            </div>
            <p className="mt-1 text-sm text-[var(--muted-foreground)]">
              Advanced analytics, insights & monitoring
            </p>
          </div>

          <div className="flex items-center gap-3">
            <Button
              variant="outline"
              size="sm"
              onClick={() => router.push("/admin/content")}
            >
              <Settings className="mr-2 h-4 w-4" />
              Content
            </Button>

            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                loadUsers();
                loadAnalytics();
                loadSystemHealth();
                loadTopUsers();
                loadRecentActivity();
                loadGrowthMetrics();
                loadConversationMetrics();
                loadToolsUsage();
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
              {autoRefresh ? "Auto ON" : "Auto OFF"}
            </Button>

            <Button
              variant="outline"
              size="sm"
              onClick={() => logout(apiBase)}
            >
              <LogOut className="mr-2 h-4 w-4" />
              Logout
            </Button>
          </div>
        </div>

        {/* Error banner */}
        {error ? (
          <div className="rounded-xl border border-red-400/40 bg-red-500/10 px-4 py-2 text-sm text-red-200 flex items-center gap-2">
            <AlertCircle className="h-4 w-4" />
            {error}
          </div>
        ) : null}

        {/* Quick Stats with Growth */}
        {growthMetrics && (
          <div className="grid gap-3 md:grid-cols-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium flex items-center justify-between">
                  <span className="flex items-center gap-2">
                    <MessageSquare className="h-4 w-4" />
                    Messages (7d)
                  </span>
                  {growthMetrics.change.messages_percent > 0 ? (
                    <ArrowUp className="h-4 w-4 text-green-500" />
                  ) : growthMetrics.change.messages_percent < 0 ? (
                    <ArrowDown className="h-4 w-4 text-red-500" />
                  ) : (
                    <Minus className="h-4 w-4 text-gray-500" />
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{growthMetrics.current_period.messages.toLocaleString()}</div>
                <p className={`text-xs mt-1 ${
                  growthMetrics.change.messages_percent > 0 ? "text-green-500" :
                  growthMetrics.change.messages_percent < 0 ? "text-red-500" : "text-gray-500"
                }`}>
                  {growthMetrics.change.messages_percent > 0 ? "+" : ""}
                  {growthMetrics.change.messages_percent.toFixed(1)}% vs previous week
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium flex items-center justify-between">
                  <span className="flex items-center gap-2">
                    <Users className="h-4 w-4" />
                    Active Users (7d)
                  </span>
                  {growthMetrics.change.users_percent > 0 ? (
                    <ArrowUp className="h-4 w-4 text-green-500" />
                  ) : growthMetrics.change.users_percent < 0 ? (
                    <ArrowDown className="h-4 w-4 text-red-500" />
                  ) : (
                    <Minus className="h-4 w-4 text-gray-500" />
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{growthMetrics.current_period.users}</div>
                <p className={`text-xs mt-1 ${
                  growthMetrics.change.users_percent > 0 ? "text-green-500" :
                  growthMetrics.change.users_percent < 0 ? "text-red-500" : "text-gray-500"
                }`}>
                  {growthMetrics.change.users_percent > 0 ? "+" : ""}
                  {growthMetrics.change.users_percent.toFixed(1)}% vs previous week
                </p>
              </CardContent>
            </Card>

            {conversationMetrics && (
              <>
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium flex items-center gap-2">
                      <TrendingUp className="h-4 w-4" />
                      Response Rate
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{conversationMetrics.response_rate.toFixed(1)}%</div>
                    <p className="text-xs text-[var(--muted-foreground)] mt-1">
                      Bot responsiveness
                    </p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium flex items-center gap-2">
                      <MessageSquare className="h-4 w-4" />
                      Avg Msgs/User
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{conversationMetrics.avg_messages_per_conversation.toFixed(1)}</div>
                    <p className="text-xs text-[var(--muted-foreground)] mt-1">
                      Engagement level
                    </p>
                  </CardContent>
                </Card>
              </>
            )}
          </div>
        )}

        {/* Tabs */}
        <Tabs defaultValue="analytics" className="flex-1 min-h-0 flex flex-col">
          <TabsList className="grid w-full grid-cols-6">
            <TabsTrigger value="analytics" onClick={loadAnalytics}>
              <BarChart className="mr-2 h-4 w-4" />
              Analytics
            </TabsTrigger>
            <TabsTrigger value="tools" onClick={loadToolsUsage}>
              <Wrench className="mr-2 h-4 w-4" />
              Tools
            </TabsTrigger>
            <TabsTrigger value="overview">
              <Star className="mr-2 h-4 w-4" />
              Overview
            </TabsTrigger>
            <TabsTrigger value="users">
              <Users className="mr-2 h-4 w-4" />
              Users
            </TabsTrigger>
            <TabsTrigger value="health" onClick={loadSystemHealth}>
              <Activity className="mr-2 h-4 w-4" />
              Health
            </TabsTrigger>
            <TabsTrigger value="broadcast">
              <Send className="mr-2 h-4 w-4" />
              Broadcast
            </TabsTrigger>
          </TabsList>

          {/* Tools Usage Tab */}
          <TabsContent value="tools" className="flex-1 min-h-0 overflow-auto space-y-4">
            {/* Filters */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm flex items-center gap-2">
                  <Filter className="h-4 w-4" />
                  Filters
                </CardTitle>
              </CardHeader>
              <CardContent className="flex flex-wrap items-center gap-4">
                <div className="flex items-center gap-2">
                  <Label htmlFor="toolsDateRange" className="text-sm whitespace-nowrap">
                    <Calendar className="inline h-4 w-4 mr-1" />
                    Date Range:
                  </Label>
                  <Select value={toolsDateRange} onValueChange={setToolsDateRange}>
                    <SelectTrigger id="toolsDateRange" className="w-32">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="1">Last 24h</SelectItem>
                      <SelectItem value="7">Last 7 days</SelectItem>
                      <SelectItem value="14">Last 14 days</SelectItem>
                      <SelectItem value="30">Last 30 days</SelectItem>
                      <SelectItem value="90">Last 90 days</SelectItem>
                      <SelectItem value="180">Last 6 months</SelectItem>
                      <SelectItem value="365">Last year</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="flex items-center gap-2">
                  <Label htmlFor="toolSearch" className="text-sm whitespace-nowrap">
                    Search Tool:
                  </Label>
                  <Input
                    id="toolSearch"
                    placeholder="Search tools..."
                    value={toolSearchQuery}
                    onChange={(e) => setToolSearchQuery(e.target.value)}
                    className="w-48"
                  />
                </div>

                <div className="flex items-center gap-2">
                  <Label htmlFor="minUsage" className="text-sm whitespace-nowrap">
                    Min Usage:
                  </Label>
                  <Input
                    id="minUsage"
                    type="number"
                    min="0"
                    placeholder="0"
                    value={minToolUsage || ""}
                    onChange={(e) => setMinToolUsage(parseInt(e.target.value) || 0)}
                    className="w-24"
                  />
                </div>

                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setToolSearchQuery("");
                    setMinToolUsage(0);
                  }}
                >
                  Clear Filters
                </Button>

                <Button
                  variant="outline"
                  size="sm"
                  onClick={loadToolsUsage}
                >
                  <RefreshCw className="mr-2 h-4 w-4" />
                  Refresh
                </Button>

                {toolsUsage && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      exportToCSV(
                        filteredTools.map(t => ({
                          tool: t.tool,
                          usage_count: t.usage_count,
                          unique_users: t.unique_users
                        })),
                        `tools-usage-${new Date().toISOString().split('T')[0]}.csv`
                      );
                    }}
                  >
                    <Download className="mr-2 h-4 w-4" />
                    Export Data
                  </Button>
                )}
              </CardContent>
            </Card>

            {loadingToolsUsage ? (
              <div className="text-sm text-[var(--muted-foreground)]">Loading tools usage...</div>
            ) : toolsUsage ? (
              <>
                {/* Summary Cards */}
                <div className="grid gap-4 md:grid-cols-4">
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm font-medium flex items-center gap-2">
                        <Wrench className="h-4 w-4" />
                        {filteredTools.length < toolsUsage.summary.total_tools ? "Filtered Tools" : "Total Tools"}
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold">
                        {filteredTools.length}
                        {filteredTools.length < toolsUsage.summary.total_tools && (
                          <span className="text-sm text-[var(--muted-foreground)] ml-2">
                            / {toolsUsage.summary.total_tools}
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-[var(--muted-foreground)] mt-1">
                        {filteredTools.length < toolsUsage.summary.total_tools
                          ? "Matching filters"
                          : "Available features"}
                      </p>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm font-medium flex items-center gap-2">
                        <TrendingUp className="h-4 w-4" />
                        Total Uses
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold">
                        {filteredTotalUses.toLocaleString()}
                        {filteredTotalUses < toolsUsage.summary.total_tool_uses && (
                          <span className="text-sm text-[var(--muted-foreground)] ml-2">
                            / {toolsUsage.summary.total_tool_uses.toLocaleString()}
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-[var(--muted-foreground)] mt-1">
                        Last {toolsUsage.summary.date_range_days} days
                      </p>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm font-medium flex items-center gap-2">
                        <Star className="h-4 w-4 text-yellow-500" />
                        Most Popular
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-lg font-bold truncate">
                        {filteredTools.length > 0
                          ? filteredTools[0].tool.replace(/_/g, " ")
                          : "N/A"}
                      </div>
                      <p className="text-xs text-[var(--muted-foreground)] mt-1">
                        {filteredTools.length > 0
                          ? `${filteredTools[0].usage_count} uses`
                          : "No tools found"}
                      </p>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm font-medium flex items-center gap-2">
                        <Activity className="h-4 w-4" />
                        Avg Usage
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold">
                        {filteredTools.length > 0
                          ? (filteredTotalUses / filteredTools.length).toFixed(0)
                          : 0}
                      </div>
                      <p className="text-xs text-[var(--muted-foreground)] mt-1">
                        {filteredTools.length > 0 ? "Uses per tool" : "No data"}
                      </p>
                    </CardContent>
                  </Card>
                </div>

                {/* Tools Usage Table */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-sm flex items-center gap-2">
                      <Wrench className="h-5 w-5" />
                      Tools Usage Ranking
                    </CardTitle>
                    <CardDescription>
                      {filteredTools.length === toolsUsage.tools_usage.length
                        ? `All ${filteredTools.length} tools sorted by usage count`
                        : `Showing ${filteredTools.length} of ${toolsUsage.tools_usage.length} tools`}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    {filteredTools.length === 0 ? (
                      <div className="text-sm text-[var(--muted-foreground)] text-center py-8">
                        No tools match the current filters.
                      </div>
                    ) : (
                      <div className="max-h-[400px] overflow-auto">
                        <div className="space-y-2">
                          {filteredTools.map((tool, idx) => (
                          <div
                            key={tool.tool}
                            className="flex items-center justify-between px-4 py-3 rounded-lg border border-[var(--border)] hover:bg-[var(--secondary)] transition"
                          >
                            <div className="flex items-center gap-3 flex-1 min-w-0">
                              <Badge variant="outline" className="w-10 h-8 flex items-center justify-center shrink-0">
                                #{idx + 1}
                              </Badge>
                              <div className="flex-1 min-w-0">
                                <div className="text-sm font-medium truncate">
                                  {tool.tool.replace(/_/g, " ")}
                                </div>
                                <div className="text-xs text-[var(--muted-foreground)]">
                                  {tool.unique_users} unique users
                                </div>
                              </div>
                            </div>
                            <div className="flex items-center gap-3 shrink-0">
                              <Badge variant="secondary" className="text-sm">
                                {tool.usage_count.toLocaleString()} uses
                              </Badge>
                              <div className="w-32 h-2 bg-[var(--secondary)] rounded-full overflow-hidden">
                                <div
                                  className="h-full bg-gradient-to-r from-green-500 to-emerald-500"
                                  style={{
                                    width: `${filteredTools.length > 0 ? (tool.usage_count / filteredTools[0].usage_count) * 100 : 0}%`
                                  }}
                                />
                              </div>
                            </div>
                          </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Charts */}
                <div className="grid gap-4 md:grid-cols-2">
                  {/* Top 10 Tools Bar Chart */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-sm">
                        {filteredTools.length > 10 ? "Top 10" : "All"} Tools
                      </CardTitle>
                      <CardDescription>
                        {filteredTools.length > 0 ? "Usage comparison" : "No data to display"}
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      {filteredTools.length === 0 ? (
                        <div className="h-[300px] flex items-center justify-center text-sm text-[var(--muted-foreground)]">
                          No tools match the current filters
                        </div>
                      ) : (
                        <ResponsiveContainer width="100%" height={300}>
                          <RechartsBarChart
                            data={filteredTools.slice(0, 10).map(t => ({
                              name: t.tool.replace(/_/g, " "),
                              count: t.usage_count
                            }))}
                            layout="vertical"
                          >
                          <CartesianGrid strokeDasharray="3 3" opacity={0.1} />
                          <XAxis type="number" tick={{ fontSize: 11 }} />
                          <YAxis
                            type="category"
                            dataKey="name"
                            tick={{ fontSize: 10 }}
                            width={120}
                          />
                          <Tooltip
                            contentStyle={{
                              backgroundColor: 'var(--card)',
                              border: '1px solid var(--border)',
                              borderRadius: '8px'
                            }}
                          />
                          <Bar dataKey="count" fill="#10b981" radius={[0, 8, 8, 0]} />
                        </RechartsBarChart>
                      </ResponsiveContainer>
                      )}
                    </CardContent>
                  </Card>

                  {/* Recent Tool Usage */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-sm flex items-center gap-2">
                        <Clock className="h-4 w-4" />
                        Recent Tool Usage
                      </CardTitle>
                      <CardDescription>Last 20 tool uses</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2 max-h-[300px] overflow-auto">
                        {toolsUsage.recent_usage.map((usage, idx) => (
                          <div
                            key={idx}
                            className="flex items-start gap-3 px-3 py-2 rounded-lg border border-[var(--border)] hover:bg-[var(--secondary)] transition"
                          >
                            <div className="w-2 h-2 rounded-full bg-green-500 mt-1.5" />
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center justify-between gap-2 mb-1">
                                <span className="text-xs font-medium truncate">{usage.phone}</span>
                                <span className="text-xs text-[var(--muted-foreground)] whitespace-nowrap">
                                  {formatTimeAgo(usage.timestamp)}
                                </span>
                              </div>
                              <Badge variant="outline" className="text-xs">
                                {usage.tool.replace(/_/g, " ")}
                              </Badge>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* Top Users Per Tool */}
                {Object.keys(toolsUsage.top_users_per_tool).length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle>Top Users Per Tool</CardTitle>
                      <CardDescription>Most active users for each tool</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                        {Object.entries(toolsUsage.top_users_per_tool).slice(0, 6).map(([tool, users]) => (
                          <div key={tool} className="border border-[var(--border)] rounded-lg p-4">
                            <h4 className="text-sm font-semibold mb-3 flex items-center gap-2">
                              <Wrench className="h-4 w-4" />
                              {tool.replace(/_/g, " ")}
                            </h4>
                            <div className="space-y-2">
                              {users.map((user, idx) => (
                                <div key={user.phone} className="flex items-center justify-between text-xs">
                                  <span className="truncate flex-1">
                                    <Badge variant="outline" className="mr-2 text-xs">#{idx + 1}</Badge>
                                    {user.phone}
                                  </span>
                                  <Badge variant="secondary" className="ml-2 text-xs">
                                    {user.usage_count}
                                  </Badge>
                                </div>
                              ))}
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </>
            ) : (
              <div className="text-sm text-[var(--muted-foreground)]">
                Click the Tools tab to load data.
              </div>
            )}
          </TabsContent>

          {/* Overview Tab - NEW! */}
          <TabsContent value="overview" className="flex-1 min-h-0 overflow-auto space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              {/* Top Active Users */}
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm flex items-center gap-2">
                    <Star className="h-4 w-4 text-yellow-500" />
                    Most Active Users
                  </CardTitle>
                  <CardDescription>Top 10 users by message count</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 max-h-[400px] overflow-auto">
                    {topUsers.map((user, idx) => (
                      <div
                        key={user.phone}
                        className="flex items-center justify-between px-3 py-2 rounded-lg border border-[var(--border)] hover:bg-[var(--secondary)] transition cursor-pointer"
                        onClick={() => loadChat(user.phone, true)}
                      >
                        <div className="flex items-center gap-3">
                          <Badge variant="outline" className="w-8 h-8 flex items-center justify-center">
                            #{idx + 1}
                          </Badge>
                          <div>
                            <div className="text-sm font-medium">{user.phone}</div>
                            <div className="text-xs text-[var(--muted-foreground)]">
                              Last active: {formatTimeAgo(user.last_active)}
                            </div>
                          </div>
                        </div>
                        <Badge variant="secondary">
                          {user.message_count} msgs
                        </Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Recent Activity Feed */}
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm flex items-center gap-2">
                    <Activity className="h-4 w-4 text-blue-500" />
                    Recent Activity
                  </CardTitle>
                  <CardDescription>Live activity feed</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 max-h-[400px] overflow-auto">
                    {recentActivity.map((activity, idx) => (
                      <div
                        key={idx}
                        className="flex items-start gap-3 px-3 py-2 rounded-lg border border-[var(--border)] hover:bg-[var(--secondary)] transition"
                      >
                        <div className={`w-2 h-2 rounded-full mt-1.5 ${
                          activity.direction === "incoming" ? "bg-blue-500" : "bg-green-500"
                        }`} />
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between gap-2 mb-1">
                            <span className="text-xs font-medium truncate">{activity.phone}</span>
                            <span className="text-xs text-[var(--muted-foreground)] whitespace-nowrap">
                              {formatTimeAgo(activity.created_at)}
                            </span>
                          </div>
                          <p className="text-xs text-[var(--muted-foreground)] truncate">
                            {activity.text || "[No text]"}
                          </p>
                          {activity.response_type && (
                            <Badge variant="outline" className="text-xs mt-1">
                              {activity.response_type.replace(/_/g, " ")}
                            </Badge>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Conversation Quality Metrics */}
            {conversationMetrics && (
              <Card>
                <CardHeader>
                  <CardTitle>Conversation Quality</CardTitle>
                  <CardDescription>Overall bot performance metrics</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid gap-4 md:grid-cols-4">
                    <div className="flex flex-col gap-1">
                      <span className="text-xs text-[var(--muted-foreground)]">Total Conversations</span>
                      <span className="text-2xl font-bold">{conversationMetrics.total_conversations}</span>
                    </div>
                    <div className="flex flex-col gap-1">
                      <span className="text-xs text-[var(--muted-foreground)]">Incoming Messages</span>
                      <span className="text-2xl font-bold text-blue-500">{conversationMetrics.incoming_messages}</span>
                    </div>
                    <div className="flex flex-col gap-1">
                      <span className="text-xs text-[var(--muted-foreground)]">Outgoing Messages</span>
                      <span className="text-2xl font-bold text-green-500">{conversationMetrics.outgoing_messages}</span>
                    </div>
                    <div className="flex flex-col gap-1">
                      <span className="text-xs text-[var(--muted-foreground)]">Avg Msgs/Conversation</span>
                      <span className="text-2xl font-bold text-purple-500">{conversationMetrics.avg_messages_per_conversation.toFixed(1)}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Analytics Tab - Keep existing with improvements */}
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

                {/* Charts */}
                <div className="grid gap-4 md:grid-cols-2">
                  {/* Message Volume Chart */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2 text-sm">
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
                      <CardTitle className="flex items-center gap-2 text-sm">
                        <PieChartIcon className="h-5 w-5" />
                        Intent Distribution
                      </CardTitle>
                      <CardDescription>Top features requested</CardDescription>
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

                  {/* Peak Hours Bar Chart */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2 text-sm">
                        <Clock className="h-5 w-5" />
                        Peak Activity Hours
                      </CardTitle>
                      <CardDescription>Message distribution by hour</CardDescription>
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

                  {/* Top Intents Bar Chart */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-sm">Top Intents</CardTitle>
                      <CardDescription>Most popular features</CardDescription>
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
            {/* User Filters Card */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm flex items-center gap-2">
                  <Filter className="h-4 w-4" />
                  User Filters
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Row 1: Search and Activity */}
                <div className="flex flex-wrap items-center gap-3">
                  <div className="flex items-center gap-2">
                    <Label htmlFor="userSearch" className="text-sm whitespace-nowrap">
                      Search:
                    </Label>
                    <Input
                      id="userSearch"
                      placeholder="Phone number..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="w-48"
                    />
                  </div>

                  <div className="flex items-center gap-2">
                    <Label htmlFor="userActivity" className="text-sm whitespace-nowrap">
                      Activity:
                    </Label>
                    <Select value={userActivityFilter} onValueChange={setUserActivityFilter}>
                      <SelectTrigger id="userActivity" className="w-40">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Users</SelectItem>
                        <SelectItem value="24h">Active (24h)</SelectItem>
                        <SelectItem value="7d">Active (7d)</SelectItem>
                        <SelectItem value="30d">Active (30d)</SelectItem>
                        <SelectItem value="inactive">Inactive (30d+)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="flex items-center gap-2">
                    <Label htmlFor="sortUsers" className="text-sm whitespace-nowrap">
                      Sort By:
                    </Label>
                    <Select value={userSortBy} onValueChange={setUserSortBy}>
                      <SelectTrigger id="sortUsers" className="w-44">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="last_seen">Last Seen (Recent)</SelectItem>
                        <SelectItem value="message_count">Message Count (High)</SelectItem>
                        <SelectItem value="first_seen">First Seen (New)</SelectItem>
                        <SelectItem value="phone">Phone Number (A-Z)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                {/* Row 2: Message Count Range */}
                <div className="flex flex-wrap items-center gap-3">
                  <div className="flex items-center gap-2">
                    <Label htmlFor="minMessages" className="text-sm whitespace-nowrap">
                      Min Messages:
                    </Label>
                    <Input
                      id="minMessages"
                      type="number"
                      min="0"
                      placeholder="0"
                      value={minMessages || ""}
                      onChange={(e) => setMinMessages(parseInt(e.target.value) || 0)}
                      className="w-24"
                    />
                  </div>

                  <div className="flex items-center gap-2">
                    <Label htmlFor="maxMessages" className="text-sm whitespace-nowrap">
                      Max Messages:
                    </Label>
                    <Input
                      id="maxMessages"
                      type="number"
                      min="0"
                      placeholder="None"
                      value={maxMessages || ""}
                      onChange={(e) => setMaxMessages(parseInt(e.target.value) || 0)}
                      className="w-24"
                    />
                  </div>

                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setSearchQuery("");
                      setUserActivityFilter("all");
                      setMinMessages(0);
                      setMaxMessages(0);
                      setUserSortBy("last_seen");
                    }}
                  >
                    Clear Filters
                  </Button>

                  <Button onClick={loadUsers} variant="outline" size="sm">
                    <RefreshCw className="mr-2 h-4 w-4" />
                    Refresh
                  </Button>

                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => exportToCSV(
                      filteredUsers.map(u => ({
                        phone: u.phone,
                        message_count: u.message_count || 0,
                        last_seen: u.last_seen || "",
                        first_seen: u.first_seen || ""
                      })),
                      `users-${new Date().toISOString().split('T')[0]}.csv`
                    )}
                  >
                    <Download className="mr-2 h-4 w-4" />
                    Export Users
                  </Button>

                  {selectedPhone && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => exportUserChat(selectedPhone)}
                    >
                      <Download className="mr-2 h-4 w-4" />
                      Export Chat
                    </Button>
                  )}
                </div>

                {/* Row 3: Message Filters (for chat view) */}
                <div className="flex flex-wrap items-center gap-3 pt-2 border-t">
                  <span className="text-xs text-[var(--muted-foreground)]">Chat Message Filters:</span>

                  <Select value={directionFilter} onValueChange={setDirectionFilter}>
                    <SelectTrigger className="w-36">
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
                </div>

                {/* Results Summary */}
                {filteredUsers.length < users.length && (
                  <div className="text-xs text-[var(--muted-foreground)] pt-2 border-t">
                    Showing {filteredUsers.length} of {users.length} users
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Users and Chat Grid */}
            <div className="grid flex-1 min-h-0 gap-6 md:grid-cols-2">
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
                          No messages match filters.
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
                                <Badge variant="outline" className="text-xs mt-1">
                                  {msg.response_type.replace(/_/g, " ")}
                                </Badge>
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
