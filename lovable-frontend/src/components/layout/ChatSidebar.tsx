import { useRef, useState } from "react";
import { Plus, MessageSquare, Trash2, Upload } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Input } from "@/components/ui/input";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import {
  DepartmentId,
  departments,
  ChatConversation,
  DepartmentMeta,
} from "@/lib/departments";
import { DepartmentBadge } from "../chat/DepartmentBadge";
import { cn } from "@/lib/utils";
import { format } from "date-fns";
import { ApiDocument } from "@/lib/api";
import { toast } from "sonner";

interface ChatSidebarProps {
  selectedDepartment: DepartmentId;
  onSelectDepartment: (dept: DepartmentId) => void;
  departmentsMeta: DepartmentMeta[];
  isAuthenticated: boolean;
  conversations: ChatConversation[];
  activeConversationId: string | null;
  onSelectConversation: (id: string) => void;
  onNewChat: () => void;
  documents: ApiDocument[];
  documentsLoading: boolean;
  documentsError?: string | null;
  onRefreshDocuments: () => Promise<void>;
  onUploadDocument: (file: File) => Promise<void>;
  onDeleteDocument: (docId: number) => Promise<void>;
}

export function ChatSidebar({
  selectedDepartment,
  onSelectDepartment,
  departmentsMeta,
  isAuthenticated,
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewChat,
  documents,
  documentsLoading,
  documentsError,
  onRefreshDocuments,
  onUploadDocument,
  onDeleteDocument,
}: ChatSidebarProps) {
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [uploading, setUploading] = useState(false);
  const [deletingId, setDeletingId] = useState<number | null>(null);

  const handleUpload = async () => {
    const file = fileInputRef.current?.files?.[0];
    if (!file) {
      toast.error("Select a file to upload.");
      return;
    }
    setUploading(true);
    try {
      await onUploadDocument(file);
      toast.success(`Uploaded ${file.name}`);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : "Upload failed.";
      toast.error(message);
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (docId: number) => {
    setDeletingId(docId);
    try {
      await onDeleteDocument(docId);
      toast.success("Document deleted.");
    } catch (error) {
      const message = error instanceof Error ? error.message : "Delete failed.";
      toast.error(message);
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="flex h-full w-72 flex-col border-r bg-sidebar">
      {/* Logo & Title */}
      <div className="flex items-center gap-2 border-b p-4">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary">
          <MessageSquare className="h-5 w-5 text-primary-foreground" />
        </div>
        <div>
          <h1 className="font-semibold">Company Q&A</h1>
          <p className="text-xs text-muted-foreground">Ask any department</p>
        </div>
      </div>

      {/* Department Selector */}
      <div className="p-4">
        <p className="mb-2 text-xs font-medium text-muted-foreground uppercase tracking-wide">
          Select Department
        </p>
        <div className="grid grid-cols-2 gap-2">
          {departmentsMeta.map((deptMeta) => {
            const dept = departments[deptMeta.id];
            const Icon = dept.icon;
            const isSelected = selectedDepartment === deptMeta.id;
            return (
              <button
                key={deptMeta.id}
                onClick={() => onSelectDepartment(deptMeta.id)}
                className={cn(
                  "flex items-center gap-2 rounded-lg border p-2 text-left text-sm transition-all hover:border-border",
                  isSelected
                    ? cn("border-2", dept.borderClass.replace("border-l-", "border-"), dept.bgClass)
                    : "border-transparent bg-sidebar-accent"
                )}
              >
                <Icon className={cn("h-4 w-4", isSelected ? dept.colorClass : "text-muted-foreground")} />
                <span className={cn("truncate text-xs", isSelected && "font-medium")}>
                  {deptMeta.name}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      <Separator />

      {/* New Chat Button */}
      <div className="p-4">
        <Button onClick={onNewChat} className="w-full gap-2" variant="outline">
          <Plus className="h-4 w-4" />
          New Chat
        </Button>
      </div>

      <Separator />

      {/* Knowledge Base */}
      <div className="p-4">
        <p className="mb-2 text-xs font-medium text-muted-foreground uppercase tracking-wide">
          Knowledge Base
        </p>
        <div className="space-y-2">
          <Input
            ref={fileInputRef}
            type="file"
            accept=".txt,.md,.pdf"
            className="cursor-pointer text-xs"
            disabled={!isAuthenticated}
          />
          <Button
            onClick={handleUpload}
            className="w-full gap-2"
            variant="outline"
            disabled={uploading || !isAuthenticated}
          >
            <Upload className="h-4 w-4" />
            {uploading ? "Uploading..." : "Upload Document"}
          </Button>
        </div>
      </div>

      <div className="px-4 pb-2">
        {!isAuthenticated ? (
          <p className="text-xs text-muted-foreground">Sign in to view documents.</p>
        ) : documentsLoading ? (
          <div className="text-xs text-muted-foreground">Loading documents...</div>
        ) : documentsError ? (
          <div className="space-y-2 text-xs text-muted-foreground">
            <p>{documentsError}</p>
            <Button
              variant="outline"
              size="sm"
              className="h-7 px-2 text-xs"
              onClick={() => void onRefreshDocuments()}
            >
              Retry
            </Button>
          </div>
        ) : documents.length === 0 ? (
          <p className="text-xs text-muted-foreground">No documents uploaded yet.</p>
        ) : (
          <ScrollArea className="max-h-40 pr-2">
            <Accordion type="multiple" className="space-y-1">
              {documents.map((doc) => (
                <AccordionItem key={doc.id} value={`doc-${doc.id}`} className="border-none">
                  <AccordionTrigger className="rounded-lg bg-sidebar-accent px-3 py-2 text-left text-xs font-medium">
                    <span className="truncate">{doc.title}</span>
                  </AccordionTrigger>
                  <AccordionContent className="px-3 pb-2 pt-1 text-xs text-muted-foreground">
                    <p className="max-h-24 overflow-hidden text-ellipsis">{doc.content}</p>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="mt-2 h-7 px-2 text-xs"
                      onClick={() => handleDelete(doc.id)}
                      disabled={deletingId === doc.id}
                    >
                      <Trash2 className="mr-1 h-3 w-3" />
                      {deletingId === doc.id ? "Deleting..." : "Delete"}
                    </Button>
                  </AccordionContent>
                </AccordionItem>
              ))}
            </Accordion>
          </ScrollArea>
        )}
      </div>

      <Separator />

      {/* Chat History */}
      <div className="flex-1 overflow-hidden">
        <p className="px-4 pb-2 text-xs font-medium text-muted-foreground uppercase tracking-wide">
          Recent Chats
        </p>
        <ScrollArea className="h-full px-2">
          <div className="space-y-1 pb-4">
            {conversations.map((conv) => (
              <button
                key={conv.id}
                onClick={() => onSelectConversation(conv.id)}
                className={cn(
                  "flex w-full flex-col gap-1 rounded-lg p-3 text-left transition-colors hover:bg-sidebar-accent",
                  activeConversationId === conv.id && "bg-sidebar-accent"
                )}
              >
                <div className="flex items-center justify-between">
                  <DepartmentBadge departmentId={conv.department} size="sm" showLabel={false} />
                  <span className="text-xs text-muted-foreground">
                    {format(conv.timestamp, "MMM d")}
                  </span>
                </div>
                <p className="truncate text-sm font-medium">{conv.title}</p>
                <p className="truncate text-xs text-muted-foreground">
                  {conv.lastMessage}
                </p>
              </button>
            ))}
          </div>
        </ScrollArea>
      </div>
    </div>
  );
}
