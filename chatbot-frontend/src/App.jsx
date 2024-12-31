import { useState, useEffect } from 'react';
import ChatWindow from './components/ChatWindow';
import MessageInput from './components/MessageInput';
import ConversationsList from './components/ConversationsList';
import { chatApi } from './services/api';

function App() {
  const [messages, setMessages] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [currentSession, setCurrentSession] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // Créer une nouvelle session au chargement initial
    const newSession = `session-${Date.now()}`;
    setCurrentSession(newSession);
    loadSessions();
  }, []);

  useEffect(() => {
    if (currentSession) {
      loadHistory();
    }
  }, [currentSession]);

  const loadSessions = async () => {
    try {
      const response = await chatApi.getAllSessions();
      console.log('Sessions loaded:', response);
      setSessions(response);
    } catch (error) {
      console.error('Error loading sessions:', error);
    }
  };

  const loadHistory = async () => {
    try {
      const history = await chatApi.getHistory(currentSession);
      console.log('History loaded:', history);
      setMessages(history);
    } catch (error) {
      console.error('Error loading history:', error);
    }
  };

  const handleSendMessage = async (content) => {
    if (!currentSession) return;
    setIsLoading(true);
    try {
      const response = await chatApi.sendMessage(content, currentSession);
      console.log('Message sent:', response);
      setMessages((prev) => [
        ...prev,
        { role: 'user', content },
        { role: 'assistant', content: response.response }
      ]);
    } catch (error) {
      console.error('Error sending message:', error);
      // Afficher une notification d'erreur
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteSession = async (sessionId) => {
    try {
      await chatApi.deleteSession(sessionId);
      setSessions(sessions.filter(session => session !== sessionId));
      if (currentSession === sessionId) {
        setCurrentSession(null);
        setMessages([]);
      }
    } catch (error) {
      console.error('Error deleting session:', error);
    }
  };

  return (
    <div className="flex h-screen bg-gray-900">
      <ConversationsList
        sessions={sessions}
        currentSession={currentSession}
        onSessionChange={setCurrentSession}
        onDeleteSession={handleDeleteSession}
      />
      <div className="flex-1 flex flex-col">
        <ChatWindow messages={messages} />
        <MessageInput onSendMessage={handleSendMessage} isLoading={isLoading} />
      </div>
    </div>
  );
}

export default App;