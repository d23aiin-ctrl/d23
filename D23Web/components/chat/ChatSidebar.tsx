"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
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
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Conversation } from "@/lib/types";
import {
  Plus,
  MessageSquare,
  Edit,
  Trash2,
  Wrench,
  X,
  Check,
  Link2,
  ChevronDown,
  ChevronUp,
  Calendar,
  BookOpen,
  Bot,
  User,
} from "lucide-react";
import { ConnectionsPanel } from "./ConnectionsPanel";

type ChatSidebarProps = {
  sidebarOpen: boolean;
  conversations: Conversation[];
  currentConversationId: string | null;
  isLoadingConversations: boolean;
  editingConversationId: string | null;
  editingTitle: string;
  isLoggedIn?: boolean;
  onStartNewChat: () => void;
  onSelectConversation: (id: string) => void;
  onBeginEdit: (id: string, title: string) => void;
  onTitleChange: (value: string) => void;
  onRename: (id: string) => void;
  onCancelEdit: () => void;
  onDelete: (id: string) => void;
  onLoginClick?: () => void;
};

export function ChatSidebar({
  sidebarOpen,
  conversations,
  currentConversationId,
  isLoadingConversations,
  editingConversationId,
  editingTitle,
  isLoggedIn = false,
  onStartNewChat,
  onSelectConversation,
  onBeginEdit,
  onTitleChange,
  onRename,
  onCancelEdit,
  onDelete,
  onLoginClick,
}: ChatSidebarProps) {
  const router = useRouter();
  const [showConnections, setShowConnections] = useState(false);
  const [showLoginRequired, setShowLoginRequired] = useState(false);

  const handleProtectedNavigation = (path: string) => {
    if (!isLoggedIn) {
      setShowLoginRequired(true);
    } else {
      router.push(path);
    }
  };

  return (
    <aside
      className={`${
        sidebarOpen ? "w-72" : "w-0"
      } transition-all duration-300 ease-in-out flex flex-col bg-neutral-50 border-r border-neutral-200 overflow-hidden`}
    >
      <div className="flex-shrink-0 p-4">
        <Button
          onClick={onStartNewChat}
          className="w-full justify-start gap-3 bg-primary hover:bg-primary/90 text-primary-foreground"
        >
          <Plus className="h-4 w-4" />
          New Chat
        </Button>
      </div>

      <ScrollArea className="flex-1 px-2 h-full overflow-hidden">
        <div className="space-y-1 pb-4">
          {isLoadingConversations ? (
            <div className="flex justify-center py-8">
              <div className="h-5 w-5 animate-spin rounded-full border-2 border-neutral-400 border-t-primary" />
            </div>
          ) : conversations.length === 0 ? (
            <p className="text-center text-sm text-neutral-500 py-8">
              No conversations yet
            </p>
          ) : (
            conversations.map((conv) => (
              <div
                key={conv.id}
                className={`group flex items-center gap-2 px-3 py-2.5 rounded-lg cursor-pointer transition-colors ${
                  currentConversationId === conv.id
                    ? "bg-white border border-neutral-200 shadow-sm text-neutral-900"
                    : "hover:bg-neutral-100 text-neutral-500 hover:text-neutral-900"
                }`}
              >
                <MessageSquare className="h-4 w-4 flex-shrink-0 opacity-60" />
                {editingConversationId === conv.id ? (
                  <div className="flex-1 flex items-center gap-1">
                    <input
                      value={editingTitle}
                      onChange={(e) => onTitleChange(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter") onRename(conv.id);
                        if (e.key === "Escape") onCancelEdit();
                      }}
                      autoFocus
                      className="flex-1 bg-neutral-100 border border-primary rounded px-2 py-1 focus:outline-none text-sm text-neutral-900"
                    />
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-6 w-6"
                      onClick={() => onRename(conv.id)}
                    >
                      <Check className="h-3 w-3" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-6 w-6"
                      onClick={onCancelEdit}
                    >
                      <X className="h-3 w-3" />
                    </Button>
                  </div>
                ) : (
                  <>
                    <span
                      className="flex-1 truncate text-sm"
                      onClick={() => onSelectConversation(conv.id)}
                    >
                      {conv.title}
                    </span>
                    <div className="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-7 w-7 hover:bg-neutral-200"
                        onClick={(e) => {
                          e.stopPropagation();
                          onBeginEdit(conv.id, conv.title);
                        }}
                      >
                        <Edit className="h-3.5 w-3.5" />
                      </Button>
                      <AlertDialog>
                        <AlertDialogTrigger asChild>
                          <Button variant="ghost" size="icon" className="h-7 w-7 hover:bg-neutral-200">
                            <Trash2 className="h-3.5 w-3.5" />
                          </Button>
                        </AlertDialogTrigger>
                        <AlertDialogContent className="bg-white border-neutral-200">
                          <AlertDialogHeader>
                            <AlertDialogTitle>Delete conversation?</AlertDialogTitle>
                            <AlertDialogDescription className="text-neutral-500">
                              This will permanently delete this conversation and all its messages.
                            </AlertDialogDescription>
                          </AlertDialogHeader>
                          <AlertDialogFooter>
                            <AlertDialogCancel className="bg-neutral-100 border-neutral-200 hover:bg-neutral-200">Cancel</AlertDialogCancel>
                            <AlertDialogAction
                              onClick={() => onDelete(conv.id)}
                              className="bg-destructive hover:bg-destructive/90"
                            >
                              Delete
                            </AlertDialogAction>
                          </AlertDialogFooter>
                        </AlertDialogContent>
                      </AlertDialog>
                    </div>
                  </>
                )}
              </div>
            ))
          )}
        </div>
      </ScrollArea>

      {/* Connections Panel or Toggle Button */}
      <div className="flex-shrink-0 border-t border-neutral-200">
        {showConnections ? (
          <div className="flex flex-col" style={{ maxHeight: "320px" }}>
            <div className="flex items-center justify-between px-3 py-2 border-b border-neutral-200 bg-neutral-100/30">
              <span className="text-xs font-medium text-neutral-500 uppercase tracking-wider flex items-center gap-2">
                <Link2 className="h-3.5 w-3.5" />
                Tools & Connections
              </span>
              <Button
                variant="ghost"
                size="icon"
                className="h-6 w-6 hover:bg-neutral-200"
                onClick={() => setShowConnections(false)}
              >
                <ChevronDown className="h-4 w-4" />
              </Button>
            </div>
            <div className="flex-1 overflow-hidden">
              <ConnectionsPanel
                isLoggedIn={isLoggedIn}
                onLoginClick={onLoginClick}
                onManageClick={() => router.push("/settings")}
              />
            </div>
          </div>
        ) : (
          <div className="p-3 space-y-1">
            <Button
              variant="ghost"
              className="w-full justify-between gap-3 text-sm text-neutral-500 hover:text-neutral-900 hover:bg-neutral-100"
              onClick={() => setShowConnections(true)}
            >
              <span className="flex items-center gap-3">
                <Link2 className="h-4 w-4" />
                Tools & Connections
              </span>
              <ChevronUp className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              className="w-full justify-start gap-3 text-sm text-neutral-500 hover:text-neutral-900 hover:bg-neutral-100"
              onClick={() => router.push("/persona")}
            >
              <Bot className="h-4 w-4" />
              AI Personas
            </Button>
            <Button
              variant="ghost"
              className="w-full justify-start gap-3 text-sm text-neutral-500 hover:text-neutral-900 hover:bg-neutral-100"
              onClick={() => handleProtectedNavigation("/profile")}
            >
              <User className="h-4 w-4" />
              Profile
            </Button>
            <Button
              variant="ghost"
              className="w-full justify-start gap-3 text-sm text-neutral-500 hover:text-neutral-900 hover:bg-neutral-100"
              onClick={() => handleProtectedNavigation("/knowledge-base")}
            >
              <BookOpen className="h-4 w-4" />
              Knowledge Base
            </Button>
            <Button
              variant="ghost"
              className="w-full justify-start gap-3 text-sm text-neutral-500 hover:text-neutral-900 hover:bg-neutral-100"
              onClick={() => handleProtectedNavigation("/tasks")}
            >
              <Calendar className="h-4 w-4" />
              Scheduled Tasks
            </Button>
            <Button
              variant="ghost"
              className="w-full justify-start gap-3 text-sm text-neutral-500 hover:text-neutral-900 hover:bg-neutral-100"
              onClick={() => handleProtectedNavigation("/settings")}
            >
              <Wrench className="h-4 w-4" />
              Manage Integrations
            </Button>
          </div>
        )}
      </div>

      {/* Login Required Dialog */}
      <AlertDialog open={showLoginRequired} onOpenChange={setShowLoginRequired}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Login Required</AlertDialogTitle>
            <AlertDialogDescription>
              Please login to access this feature. Sign in with your Google account to manage integrations, view scheduled tasks, and more.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => {
                setShowLoginRequired(false);
                onLoginClick?.();
              }}
            >
              Login
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </aside>
  );
}
