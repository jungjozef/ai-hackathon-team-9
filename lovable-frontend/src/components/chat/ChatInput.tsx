import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Send } from "lucide-react";
import { DepartmentId, departments } from "@/lib/departments";
import { DepartmentBadge } from "./DepartmentBadge";

interface ChatInputProps {
  onSend: (message: string) => void;
  selectedDepartment: DepartmentId;
  departmentLabel?: string;
  disabled?: boolean;
}

export function ChatInput({
  onSend,
  selectedDepartment,
  departmentLabel,
  disabled,
}: ChatInputProps) {
  const [message, setMessage] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSend(message.trim());
      setMessage("");
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const quickReplies = [
    "What's the process?",
    "Can you help me?",
    "I have a question",
  ];

  return (
    <div className="border-t bg-background p-4">
      <div className="mb-3 flex items-center gap-2">
        <span className="text-sm text-muted-foreground">Asking:</span>
        <DepartmentBadge departmentId={selectedDepartment} size="sm" />
      </div>

      <div className="mb-3 flex flex-wrap gap-2">
        {quickReplies.map((reply) => (
          <Button
            key={reply}
            variant="outline"
            size="sm"
            onClick={() => setMessage(reply)}
            className="text-xs"
          >
            {reply}
          </Button>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="flex gap-2">
        <Textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={`Ask ${departmentLabel ?? departments[selectedDepartment].name} a question...`}
          className="min-h-[64px] max-h-40 resize-none"
          rows={2}
          disabled={disabled}
        />
        <Button
          type="submit"
          size="icon"
          disabled={!message.trim() || disabled}
          className="shrink-0"
        >
          <Send className="h-4 w-4" />
        </Button>
      </form>
    </div>
  );
}
