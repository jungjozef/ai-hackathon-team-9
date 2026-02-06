import { useRef, useEffect } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { LogIn, LogOut } from "lucide-react";
import { ChatMessage } from "../chat/ChatMessage";
import { ChatInput } from "../chat/ChatInput";
import { TypingIndicator } from "../chat/TypingIndicator";
import { DepartmentBadge } from "../chat/DepartmentBadge";
import {
  ChatMessage as ChatMessageType,
  DepartmentId,
  departments,
} from "@/lib/departments";
import { ApiUser } from "@/lib/api";

interface ChatPanelProps {
  messages: ChatMessageType[];
  selectedDepartment: DepartmentId;
  departmentName?: string;
  departmentDescription?: string;
  onSend: (message: string) => void;
  isTyping: boolean;
  isAuthenticated: boolean;
  user: ApiUser | null;
  authLoading: boolean;
  authError: string | null;
  onLogin: () => void;
  onLogout: () => void;
}

export function ChatPanel({
  messages,
  selectedDepartment,
  departmentName,
  departmentDescription,
  onSend,
  isTyping,
  isAuthenticated,
  user,
  authLoading,
  authError,
  onLogin,
  onLogout,
}: ChatPanelProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const dept = departments[selectedDepartment];
  const deptName = departmentName ?? dept.name;
  const deptDescription =
    departmentDescription ?? `Ask questions and get answers from the ${deptName} team`;
  const userInitials =
    user?.name
      ?.split(" ")
      .map((part) => part[0])
      .slice(0, 2)
      .join("")
      .toUpperCase() ?? "G";

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  return (
    <div className="flex flex-1 flex-col">
      {/* Header */}
      <header className="flex items-center justify-between gap-3 border-b bg-background px-6 py-4">
        <div className="flex items-center gap-3">
          <DepartmentBadge departmentId={selectedDepartment} label={deptName} />
          <div>
            <h2 className="font-semibold">Chat with {deptName}</h2>
            <p className="text-sm text-muted-foreground">
              {deptDescription}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {authError && (
            <span className="hidden text-xs text-destructive md:inline">{authError}</span>
          )}
          <div className="flex items-center gap-2">
            <Avatar className="h-9 w-9">
              {user?.picture_url && <AvatarImage src={user.picture_url} alt={user.name} />}
              <AvatarFallback className="bg-primary text-primary-foreground">
                {userInitials}
              </AvatarFallback>
            </Avatar>
            {authLoading ? (
              <span className="text-xs text-muted-foreground">Checking...</span>
            ) : isAuthenticated ? (
              <Button variant="outline" size="sm" className="gap-2" onClick={onLogout}>
                <LogOut className="h-4 w-4" />
                Sign out
              </Button>
            ) : (
              <Button size="sm" className="gap-2" onClick={onLogin}>
                <LogIn className="h-4 w-4" />
                Sign in
              </Button>
            )}
          </div>
        </div>
      </header>

      {/* Messages */}
      <ScrollArea className="flex-1 p-6" ref={scrollRef}>
        <div className="mx-auto max-w-3xl space-y-6">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <div
                className={`mb-4 flex h-16 w-16 items-center justify-center rounded-full ${dept.bgClass}`}
              >
                <dept.icon className={`h-8 w-8 ${dept.colorClass}`} />
              </div>
              <h3 className="mb-2 text-lg font-semibold">
                Start a conversation with {deptName}
              </h3>
              <p className="max-w-sm text-sm text-muted-foreground">
                Type your question below and the {deptName} team will respond
                with helpful information.
              </p>
            </div>
          )}

          {messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))}

          {isTyping && <TypingIndicator departmentId={selectedDepartment} />}
        </div>
      </ScrollArea>

      {/* Input */}
      {!isAuthenticated && (
        <div className="px-6 pb-2 text-xs text-muted-foreground">
          Sign in with Google to send messages.
        </div>
      )}
      <ChatInput
        onSend={onSend}
        selectedDepartment={selectedDepartment}
        departmentLabel={deptName}
        disabled={isTyping || !isAuthenticated}
      />
    </div>
  );
}
