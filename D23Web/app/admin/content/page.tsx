"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Save,
  RotateCcw,
  ArrowLeft,
  Type,
  BarChart3,
  Globe,
  Users,
  Plus,
  Trash2,
  GripVertical,
  Eye
} from "lucide-react";

interface Stat {
  value: string;
  label: string;
  icon: string;
}

interface Language {
  name: string;
  code: string;
  english: string;
}

interface Founder {
  name: string;
  role: string;
  twitter: string;
  linkedin: string;
}

interface LandingContent {
  hero: {
    title: string;
    subtitle: string;
    rotatingWords: string[];
    description: string;
    ctaPrimary: string;
    ctaSecondary: string;
    whatsappLink: string;
  };
  stats: Stat[];
  languages: Language[];
  founders: Founder[];
  meta: {
    title: string;
    description: string;
  };
}

export default function AdminContentPage() {
  const router = useRouter();
  const [content, setContent] = useState<LandingContent | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "https://api.d23.ai";

  const getAuthHeaders = () => {
    const token = localStorage.getItem("admin_token");
    return {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`,
    };
  };

  useEffect(() => {
    // Check auth
    const token = localStorage.getItem("admin_token");
    if (!token) {
      router.push("/admin/login");
      return;
    }
    fetchContent();
  }, []);

  const fetchContent = async () => {
    try {
      const response = await fetch(`${apiBase}/admin/landing-content`);
      if (!response.ok) throw new Error("Failed to fetch content");
      const data = await response.json();
      setContent(data);
    } catch (err) {
      setError("Failed to load content");
    } finally {
      setLoading(false);
    }
  };

  const saveContent = async () => {
    if (!content) return;
    setSaving(true);
    setError("");
    setSuccess("");

    try {
      const response = await fetch(`${apiBase}/admin/landing-content`, {
        method: "PUT",
        headers: getAuthHeaders(),
        body: JSON.stringify(content),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Failed to save");
      }

      setSuccess("Content saved successfully!");
      setTimeout(() => setSuccess(""), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save content");
    } finally {
      setSaving(false);
    }
  };

  const resetContent = async () => {
    if (!confirm("Are you sure you want to reset to default content?")) return;

    setSaving(true);
    setError("");

    try {
      const response = await fetch(`${apiBase}/admin/landing-content/reset`, {
        method: "POST",
        headers: getAuthHeaders(),
      });

      if (!response.ok) throw new Error("Failed to reset");

      const data = await response.json();
      setContent(data.content);
      setSuccess("Content reset to defaults!");
      setTimeout(() => setSuccess(""), 3000);
    } catch (err) {
      setError("Failed to reset content");
    } finally {
      setSaving(false);
    }
  };

  const updateHero = (field: string, value: string | string[]) => {
    if (!content) return;
    setContent({
      ...content,
      hero: { ...content.hero, [field]: value },
    });
  };

  const updateStat = (index: number, field: keyof Stat, value: string) => {
    if (!content) return;
    const newStats = [...content.stats];
    newStats[index] = { ...newStats[index], [field]: value };
    setContent({ ...content, stats: newStats });
  };

  const addStat = () => {
    if (!content) return;
    setContent({
      ...content,
      stats: [...content.stats, { value: "0", label: "New Stat", icon: "📊" }],
    });
  };

  const removeStat = (index: number) => {
    if (!content) return;
    setContent({
      ...content,
      stats: content.stats.filter((_, i) => i !== index),
    });
  };

  const updateFounder = (index: number, field: keyof Founder, value: string) => {
    if (!content) return;
    const newFounders = [...content.founders];
    newFounders[index] = { ...newFounders[index], [field]: value };
    setContent({ ...content, founders: newFounders });
  };

  const addFounder = () => {
    if (!content) return;
    setContent({
      ...content,
      founders: [...content.founders, { name: "", role: "", twitter: "#", linkedin: "#" }],
    });
  };

  const removeFounder = (index: number) => {
    if (!content) return;
    setContent({
      ...content,
      founders: content.founders.filter((_, i) => i !== index),
    });
  };

  const updateMeta = (field: string, value: string) => {
    if (!content) return;
    setContent({
      ...content,
      meta: { ...content.meta, [field]: value },
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[var(--background)]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-emerald-500"></div>
      </div>
    );
  }

  if (!content) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[var(--background)]">
        <Alert variant="destructive">
          <AlertDescription>Failed to load content</AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[var(--background)] p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={() => router.push("/admin/whatsapp")}>
              <ArrowLeft className="h-5 w-5" />
            </Button>
            <div>
              <h1 className="text-2xl font-bold text-[var(--foreground)]">Landing Page Content</h1>
              <p className="text-[var(--muted-foreground)]">Manage your website content</p>
            </div>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => window.open("https://d23.ai", "_blank")}>
              <Eye className="h-4 w-4 mr-2" />
              Preview
            </Button>
            <Button variant="outline" onClick={resetContent} disabled={saving}>
              <RotateCcw className="h-4 w-4 mr-2" />
              Reset
            </Button>
            <Button onClick={saveContent} disabled={saving} className="bg-emerald-600 hover:bg-emerald-700">
              <Save className="h-4 w-4 mr-2" />
              {saving ? "Saving..." : "Save Changes"}
            </Button>
          </div>
        </div>

        {/* Alerts */}
        {error && (
          <Alert variant="destructive" className="mb-4">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}
        {success && (
          <Alert className="mb-4 border-emerald-500 bg-emerald-500/10">
            <AlertDescription className="text-emerald-500">{success}</AlertDescription>
          </Alert>
        )}

        {/* Tabs */}
        <Tabs defaultValue="hero" className="space-y-4">
          <TabsList className="grid grid-cols-4 w-full max-w-xl">
            <TabsTrigger value="hero" className="flex items-center gap-2">
              <Type className="h-4 w-4" />
              Hero
            </TabsTrigger>
            <TabsTrigger value="stats" className="flex items-center gap-2">
              <BarChart3 className="h-4 w-4" />
              Stats
            </TabsTrigger>
            <TabsTrigger value="team" className="flex items-center gap-2">
              <Users className="h-4 w-4" />
              Team
            </TabsTrigger>
            <TabsTrigger value="meta" className="flex items-center gap-2">
              <Globe className="h-4 w-4" />
              SEO
            </TabsTrigger>
          </TabsList>

          {/* Hero Section */}
          <TabsContent value="hero">
            <Card>
              <CardHeader>
                <CardTitle>Hero Section</CardTitle>
                <CardDescription>Main heading and call-to-action content</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label>Main Title</Label>
                    <Input
                      value={content.hero.title}
                      onChange={(e) => updateHero("title", e.target.value)}
                      placeholder="Need an answer?"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Subtitle Prefix</Label>
                    <Input
                      value={content.hero.subtitle}
                      onChange={(e) => updateHero("subtitle", e.target.value)}
                      placeholder="just"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label>Rotating Words (comma separated)</Label>
                  <Input
                    value={content.hero.rotatingWords.join(", ")}
                    onChange={(e) => updateHero("rotatingWords", e.target.value.split(",").map(w => w.trim()))}
                    placeholder="पूछो, કહો, ಕೇಳಿ, అడుగు, D23"
                  />
                  <p className="text-xs text-[var(--muted-foreground)]">
                    These words rotate in the hero section. Use regional language words.
                  </p>
                </div>

                <div className="space-y-2">
                  <Label>Description</Label>
                  <Textarea
                    value={content.hero.description}
                    onChange={(e) => updateHero("description", e.target.value)}
                    placeholder="Your AI assistant that speaks your language..."
                    rows={3}
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label>Primary CTA Text</Label>
                    <Input
                      value={content.hero.ctaPrimary}
                      onChange={(e) => updateHero("ctaPrimary", e.target.value)}
                      placeholder="Start on WhatsApp"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Secondary CTA Text</Label>
                    <Input
                      value={content.hero.ctaSecondary}
                      onChange={(e) => updateHero("ctaSecondary", e.target.value)}
                      placeholder="Try Web Chat"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label>WhatsApp Link</Label>
                  <Input
                    value={content.hero.whatsappLink}
                    onChange={(e) => updateHero("whatsappLink", e.target.value)}
                    placeholder="https://wa.me/919934438606"
                  />
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Stats Section */}
          <TabsContent value="stats">
            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <div>
                    <CardTitle>Statistics</CardTitle>
                    <CardDescription>Numbers displayed on the landing page</CardDescription>
                  </div>
                  <Button onClick={addStat} size="sm">
                    <Plus className="h-4 w-4 mr-2" />
                    Add Stat
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {content.stats.map((stat, index) => (
                  <div key={index} className="flex items-center gap-4 p-4 border rounded-lg bg-[var(--secondary)]/30">
                    <GripVertical className="h-5 w-5 text-[var(--muted-foreground)] cursor-move" />
                    <div className="flex-1 grid grid-cols-3 gap-4">
                      <div className="space-y-1">
                        <Label className="text-xs">Value</Label>
                        <Input
                          value={stat.value}
                          onChange={(e) => updateStat(index, "value", e.target.value)}
                          placeholder="5000+"
                        />
                      </div>
                      <div className="space-y-1">
                        <Label className="text-xs">Label</Label>
                        <Input
                          value={stat.label}
                          onChange={(e) => updateStat(index, "label", e.target.value)}
                          placeholder="Active Users"
                        />
                      </div>
                      <div className="space-y-1">
                        <Label className="text-xs">Icon (emoji)</Label>
                        <Input
                          value={stat.icon}
                          onChange={(e) => updateStat(index, "icon", e.target.value)}
                          placeholder="👥"
                        />
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => removeStat(index)}
                      className="text-red-500 hover:text-red-600 hover:bg-red-500/10"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Team Section */}
          <TabsContent value="team">
            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <div>
                    <CardTitle>Team / Founders</CardTitle>
                    <CardDescription>Team members displayed on the website</CardDescription>
                  </div>
                  <Button onClick={addFounder} size="sm">
                    <Plus className="h-4 w-4 mr-2" />
                    Add Member
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {content.founders.map((founder, index) => (
                  <div key={index} className="p-4 border rounded-lg bg-[var(--secondary)]/30 space-y-4">
                    <div className="flex justify-between items-center">
                      <span className="font-medium">Member {index + 1}</span>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => removeFounder(index)}
                        className="text-red-500 hover:text-red-600 hover:bg-red-500/10"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-1">
                        <Label className="text-xs">Name</Label>
                        <Input
                          value={founder.name}
                          onChange={(e) => updateFounder(index, "name", e.target.value)}
                          placeholder="John Doe"
                        />
                      </div>
                      <div className="space-y-1">
                        <Label className="text-xs">Role</Label>
                        <Input
                          value={founder.role}
                          onChange={(e) => updateFounder(index, "role", e.target.value)}
                          placeholder="Co-Founder & CEO"
                        />
                      </div>
                      <div className="space-y-1">
                        <Label className="text-xs">Twitter URL</Label>
                        <Input
                          value={founder.twitter}
                          onChange={(e) => updateFounder(index, "twitter", e.target.value)}
                          placeholder="https://twitter.com/username"
                        />
                      </div>
                      <div className="space-y-1">
                        <Label className="text-xs">LinkedIn URL</Label>
                        <Input
                          value={founder.linkedin}
                          onChange={(e) => updateFounder(index, "linkedin", e.target.value)}
                          placeholder="https://linkedin.com/in/username"
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </TabsContent>

          {/* SEO/Meta Section */}
          <TabsContent value="meta">
            <Card>
              <CardHeader>
                <CardTitle>SEO & Meta</CardTitle>
                <CardDescription>Search engine optimization settings</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-2">
                  <Label>Page Title</Label>
                  <Input
                    value={content.meta.title}
                    onChange={(e) => updateMeta("title", e.target.value)}
                    placeholder="D23 AI | Bharat's WhatsApp AI Assistant"
                  />
                  <p className="text-xs text-[var(--muted-foreground)]">
                    This appears in browser tabs and search results
                  </p>
                </div>
                <div className="space-y-2">
                  <Label>Meta Description</Label>
                  <Textarea
                    value={content.meta.description}
                    onChange={(e) => updateMeta("description", e.target.value)}
                    placeholder="Get instant answers in Hindi, Tamil, Telugu & 11+ Indian languages"
                    rows={3}
                  />
                  <p className="text-xs text-[var(--muted-foreground)]">
                    This appears in search engine results (keep under 160 characters)
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
