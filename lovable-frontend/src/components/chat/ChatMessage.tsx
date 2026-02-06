import { ChatMessage as ChatMessageType, departments } from "@/lib/departments";
import { DepartmentBadge } from "./DepartmentBadge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { cn } from "@/lib/utils";
import { format } from "date-fns";

interface ChatMessageProps {
  message: ChatMessageType;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.sender === "user";
  const dept = message.department ? departments[message.department] : null;

  return (
    <div
      className={cn(
        "flex gap-3 animate-message-in",
        isUser ? "flex-row-reverse" : "flex-row"
      )}
    >
      {!isUser && dept && (
        <Avatar className="h-8 w-8 shrink-0">
          <AvatarFallback className={cn(dept.bgClass, dept.colorClass)}>
            <dept.icon className="h-4 w-4" />
          </AvatarFallback>
        </Avatar>
      )}

      <div
        className={cn(
          "flex max-w-[75%] flex-col gap-1",
          isUser ? "items-end" : "items-start"
        )}
      >
        {!isUser && dept && (
          <DepartmentBadge departmentId={message.department!} size="sm" />
        )}

        <div
          className={cn(
            "rounded-2xl px-4 py-2.5",
            isUser
              ? "bg-primary text-primary-foreground"
              : dept
              ? cn("border-l-4", dept.borderClass, dept.bgClass)
              : "bg-muted"
          )}
        >
          <p className="text-sm leading-relaxed">{message.content}</p>
        </div>

        <span className="text-xs text-muted-foreground">
          {format(message.timestamp, "h:mm a")}
        </span>
      </div>

      {isUser && (
        <Avatar className="h-8 w-8 shrink-0">
          <AvatarFallback className="bg-primary text-primary-foreground">
            U
          </AvatarFallback>
        </Avatar>
      )}
    </div>
  );
}
