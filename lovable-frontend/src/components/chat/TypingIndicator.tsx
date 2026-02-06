import { DepartmentId, departments } from "@/lib/departments";
import { cn } from "@/lib/utils";

interface TypingIndicatorProps {
  departmentId: DepartmentId;
}

export function TypingIndicator({ departmentId }: TypingIndicatorProps) {
  const dept = departments[departmentId];
  const Icon = dept.icon;

  return (
    <div className="flex items-start gap-3 animate-message-in">
      <div
        className={cn(
          "flex h-8 w-8 items-center justify-center rounded-full",
          dept.bgClass,
          dept.colorClass
        )}
      >
        <Icon className="h-4 w-4" />
      </div>

      <div
        className={cn(
          "rounded-2xl border-l-4 px-4 py-3",
          dept.borderClass,
          dept.bgClass
        )}
      >
        <div className="flex items-center gap-1">
          <span
            className={cn(
              "h-2 w-2 animate-bounce rounded-full",
              dept.colorClass.replace("text-", "bg-")
            )}
            style={{ animationDelay: "0ms" }}
          />
          <span
            className={cn(
              "h-2 w-2 animate-bounce rounded-full",
              dept.colorClass.replace("text-", "bg-")
            )}
            style={{ animationDelay: "150ms" }}
          />
          <span
            className={cn(
              "h-2 w-2 animate-bounce rounded-full",
              dept.colorClass.replace("text-", "bg-")
            )}
            style={{ animationDelay: "300ms" }}
          />
        </div>
      </div>
    </div>
  );
}
