import { ChatSidebar } from "@/components/layout/ChatSidebar";
import { ChatPanel } from "@/components/layout/ChatPanel";
import { useChat } from "@/hooks/useChat";
import { useAuth } from "@/hooks/useAuth";

const Index = () => {
  const { user, loading: authLoading, error: authError, isAuthenticated, login, logout } = useAuth();
  const {
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
    documents,
    documentsLoading,
    documentsError,
    refreshDocuments,
    uploadDocument,
    deleteDocument,
  } = useChat(isAuthenticated);

  const departmentInfo = departmentsById[selectedDepartment];

  return (
    <div className="flex h-screen w-full bg-background">
      <ChatSidebar
        selectedDepartment={selectedDepartment}
        onSelectDepartment={selectDepartment}
        departmentsMeta={departmentsMeta}
        isAuthenticated={isAuthenticated}
        conversations={conversations}
        activeConversationId={activeConversationId}
        onSelectConversation={selectConversation}
        onNewChat={startNewChat}
        documents={documents}
        documentsLoading={documentsLoading}
        documentsError={documentsError}
        onRefreshDocuments={refreshDocuments}
        onUploadDocument={uploadDocument}
        onDeleteDocument={deleteDocument}
      />
      <ChatPanel
        messages={currentMessages}
        selectedDepartment={selectedDepartment}
        departmentName={departmentInfo?.name}
        departmentDescription={departmentInfo?.description}
        onSend={sendMessage}
        isTyping={isTyping}
        isAuthenticated={isAuthenticated}
        user={user}
        authLoading={authLoading}
        authError={authError}
        onLogin={login}
        onLogout={logout}
      />
    </div>
  );
};

export default Index;
