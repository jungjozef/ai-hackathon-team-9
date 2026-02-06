import { useState, useCallback, useEffect, useMemo } from "react";
import {
  ChatMessage,
  ChatConversation,
  DepartmentId,
  departmentList,
  departmentIdFromName,
  DepartmentMeta,
  departments,
} from "@/lib/departments";
import {
  ApiDocument,
  fetchDepartments,
  fetchDocuments,
  uploadDocument,
  deleteDocument,
  sendChat,
  ChatHistoryItem,
} from "@/lib/api";

const generateId = () => Math.random().toString(36).substring(2, 9);

const defaultDepartmentMeta: DepartmentMeta[] = departmentList.map((dept) => ({
  id: dept.id,
  name: dept.name,
  description: "",
}));

export function useChat(isAuthenticated: boolean) {
  const [conversations, setConversations] = useState<ChatConversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [selectedDepartment, setSelectedDepartment] = useState<DepartmentId>("engineering");
  const [currentMessages, setCurrentMessages] = useState<ChatMessage[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [departmentsMeta, setDepartmentsMeta] = useState<DepartmentMeta[]>(defaultDepartmentMeta);
  const [departmentsLoading, setDepartmentsLoading] = useState(true);
  const [departmentsError, setDepartmentsError] = useState<string | null>(null);
  const [documents, setDocuments] = useState<ApiDocument[]>([]);
  const [documentsLoading, setDocumentsLoading] = useState(true);
  const [documentsError, setDocumentsError] = useState<string | null>(null);

  const departmentsById = useMemo(() => {
    return departmentsMeta.reduce<Record<DepartmentId, DepartmentMeta>>((acc, dept) => {
      acc[dept.id] = dept;
      return acc;
    }, {} as Record<DepartmentId, DepartmentMeta>);
  }, [departmentsMeta]);

  useEffect(() => {
    const load = async () => {
      try {
        const apiDepartments = await fetchDepartments();
        const mapped = apiDepartments
          .map((dept) => {
            const id = departmentIdFromName(dept.name);
            if (!id) {
              return null;
            }
            return {
              id,
              name: dept.name,
              description: dept.description ?? "",
            } satisfies DepartmentMeta;
          })
          .filter((dept): dept is DepartmentMeta => dept !== null);
        if (mapped.length > 0) {
          setDepartmentsMeta(mapped);
          setSelectedDepartment((prev) =>
            mapped.some((dept) => dept.id === prev) ? prev : mapped[0].id
          );
        }
      } catch (error) {
        console.error("Failed to load departments", error);
        setDepartmentsError(
          error instanceof Error ? error.message : "Failed to load departments."
        );
      } finally {
        setDepartmentsLoading(false);
      }
    };

    load();
  }, []);

  useEffect(() => {
    if (!isAuthenticated) {
      setDocuments([]);
      setDocumentsLoading(false);
      setDocumentsError(null);
      return;
    }

    setDocumentsLoading(true);
    const loadDocs = async () => {
      try {
        const docs = await fetchDocuments();
        setDocuments(docs);
      } catch (error) {
        console.error("Failed to load documents", error);
        setDocumentsError(error instanceof Error ? error.message : "Failed to load documents.");
      } finally {
        setDocumentsLoading(false);
      }
    };

    loadDocs();
  }, [isAuthenticated]);

  const sendMessage = useCallback(
    async (content: string) => {
      if (!isAuthenticated) {
        const warningMessage: ChatMessage = {
          id: generateId(),
          content: "Please sign in with Google to ask questions.",
          sender: "department",
          department: selectedDepartment,
          timestamp: new Date(),
        };
        setCurrentMessages((prev) => [...prev, warningMessage]);
        return;
      }

      const userMessage: ChatMessage = {
        id: generateId(),
        content,
        sender: "user",
        timestamp: new Date(),
      };

      const pendingMessages = [...currentMessages, userMessage];
      setCurrentMessages(pendingMessages);
      setIsTyping(true);

      const history: ChatHistoryItem[] = currentMessages.map((message) => ({
        role: message.sender === "user" ? "user" : "assistant",
        content: message.content,
      }));

      try {
        const deptName = departmentsById[selectedDepartment]?.name ?? departments[selectedDepartment].name;
        const reply = await sendChat(deptName, content, history);
        const departmentResponse: ChatMessage = {
          id: generateId(),
          content: reply,
          sender: "department",
          department: selectedDepartment,
          timestamp: new Date(),
        };
        const updatedMessages = [...pendingMessages, departmentResponse];
        setCurrentMessages(updatedMessages);
        setIsTyping(false);

        setConversations((prev) => {
          if (activeConversationId) {
            return prev.map((conv) =>
              conv.id === activeConversationId
                ? {
                    ...conv,
                    lastMessage: reply,
                    timestamp: new Date(),
                    messages: updatedMessages,
                  }
                : conv
            );
          }

          const newConversation: ChatConversation = {
            id: `conv-${generateId()}`,
            title: content.slice(0, 40) + (content.length > 40 ? "..." : ""),
            department: selectedDepartment,
            lastMessage: reply,
            timestamp: new Date(),
            messages: updatedMessages,
          };
          setActiveConversationId(newConversation.id);
          return [newConversation, ...prev];
        });
      } catch (error) {
        const message =
          error instanceof Error ? error.message : "Something went wrong. Please try again.";
        const departmentResponse: ChatMessage = {
          id: generateId(),
          content: message,
          sender: "department",
          department: selectedDepartment,
          timestamp: new Date(),
        };
        const updatedMessages = [...pendingMessages, departmentResponse];
        setCurrentMessages(updatedMessages);
        setIsTyping(false);
      }
    },
    [activeConversationId, currentMessages, departmentsById, selectedDepartment, isAuthenticated]
  );

  const selectConversation = useCallback(
    (id: string) => {
      const conv = conversations.find((c) => c.id === id);
      if (conv) {
        setActiveConversationId(id);
        setCurrentMessages(conv.messages);
        setSelectedDepartment(conv.department);
      }
    },
    [conversations]
  );

  const startNewChat = useCallback(() => {
    setActiveConversationId(null);
    setCurrentMessages([]);
  }, []);

  const selectDepartment = useCallback((dept: DepartmentId) => {
    setSelectedDepartment(dept);
    setActiveConversationId(null);
    setCurrentMessages([]);
  }, []);

  const refreshDocuments = useCallback(async () => {
    if (!isAuthenticated) {
      setDocuments([]);
      setDocumentsLoading(false);
      setDocumentsError(null);
      return;
    }
    setDocumentsLoading(true);
    setDocumentsError(null);
    try {
      const docs = await fetchDocuments();
      setDocuments(docs);
    } catch (error) {
      setDocumentsError(error instanceof Error ? error.message : "Failed to load documents.");
    } finally {
      setDocumentsLoading(false);
    }
  }, [isAuthenticated]);

  const handleUploadDocument = useCallback(async (file: File) => {
    await uploadDocument(file);
    await refreshDocuments();
  }, [refreshDocuments]);

  const handleDeleteDocument = useCallback(async (docId: number) => {
    await deleteDocument(docId);
    setDocuments((prev) => prev.filter((doc) => doc.id !== docId));
  }, []);

  return {
    conversations,
    activeConversationId,
    selectedDepartment,
    currentMessages,
    isTyping,
    sendMessage,
    selectConversation,
    startNewChat,
    selectDepartment,
    departmentsMeta,
    departmentsById,
    departmentsLoading,
    departmentsError,
    documents,
    documentsLoading,
    documentsError,
    refreshDocuments,
    uploadDocument: handleUploadDocument,
    deleteDocument: handleDeleteDocument,
  };
}
