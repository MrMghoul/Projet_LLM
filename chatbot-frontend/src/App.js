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
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
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

  const handleQueryPatientInfo = async (question) => {
    setIsLoading(true);
    try {
      const response = await chatApi.queryPatientInfo(question);
      console.log('Query response:', response);
      setMessages((prev) => [
        ...prev,
        { role: 'user', content: question },
        { role: 'assistant', content: response.response }
      ]);
    } catch (error) {
      console.error('Error querying patient info:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewSession = () => {
    const newSession = `session-${Date.now()}`;
    setCurrentSession(newSession);
    setMessages([]);
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
    <div className="container h-screen overflow-hidden medical-theme">
      <div className="flex h-full bg-white dark:bg-gray-900 rounded-lg shadow-lg">
        <ConversationsList
          sessions={sessions}
          currentSession={currentSession}
          onSessionChange={setCurrentSession}
          onDeleteSession={handleDeleteSession}
          onNewSession={handleNewSession}
        />
        <div className="flex-1 flex flex-col bg-white dark:bg-gray-800">
        <div className="header flex justify-between items-center">
            <h1>Application Médicale</h1>
          </div>
          <ChatWindow messages={messages} />
          <MessageInput onSendMessage={handleQueryPatientInfo} isLoading={isLoading} />
        </div>
      </div>
    </div>
  );
}

export default App;