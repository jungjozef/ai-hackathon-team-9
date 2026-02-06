import { departments, DepartmentId } from "@/lib/departments";
import { cn } from "@/lib/utils";

interface DepartmentBadgeProps {
  departmentId: DepartmentId;
  showLabel?: boolean;
  size?: "sm" | "md";
  label?: string;
}

export function DepartmentBadge({
  departmentId,
  showLabel = true,
  size = "md",
  label,
}: DepartmentBadgeProps) {
  const dept = departments[departmentId];
  const Icon = dept.icon;

  return (
    <div
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full font-medium",
        dept.bgClass,
        dept.colorClass,
        size === "sm" ? "px-2 py-0.5 text-xs" : "px-3 py-1 text-sm"
      )}
    >
      <Icon className={size === "sm" ? "h-3 w-3" : "h-4 w-4"} />
      {showLabel && <span>{label ?? dept.name}</span>}
    </div>
  );
}
