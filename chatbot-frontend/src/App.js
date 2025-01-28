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
    let sessionId = currentSession;
    if (!sessionId) {
      const response = await chatApi.createSession();
      sessionId = response.session_id;
      setCurrentSession(sessionId);
      setSessions((prev) => [...prev, sessionId]); // Ajouter la nouvelle session immédiatement
    }
    setIsLoading(true);
    try {
      const response = await chatApi.sendMessage(content, sessionId);
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

  const handleNewSession = async () => {
    console.log('Creating new session...');
    try {
      const response = await chatApi.createSession();
      const newSession = response.session_id;
      setCurrentSession(newSession);
      setMessages([]); // Réinitialiser les messages pour la nouvelle session
      setSessions((prev) => [...prev, newSession]); // Ajouter la nouvelle session immédiatement
  
      // Sauvegarder la session vide dans MongoDB
      await chatApi.saveMessage(newSession, 'system', 'Session créée');
      console.log('New session created:', newSession);
    } catch (error) {
      console.error('Error creating new session:', error);
    }
  };
  
  const handleQueryPatientInfo = async (question) => {
    setIsLoading(true);
    let sessionId = currentSession;
    if (!sessionId) {
      const response = await chatApi.createSession();
      sessionId = response.session_id;
      setCurrentSession(sessionId);
      setSessions((prev) => [...prev, sessionId]); // Ajouter la nouvelle session immédiatement
    }
    try {
      const response = await chatApi.queryPatientInfo({ question, session_id: sessionId });
      console.log('Query response:', response);
  
      // Mettre à jour les messages dans l'état
      setMessages((prev) => [
        ...prev,
        { role: 'user', content: question },
        { role: 'assistant', content: response.response }
      ]);
  
      // Sauvegarder les messages dans MongoDB
      await chatApi.saveMessage(sessionId, 'user', question);
      await chatApi.saveMessage(sessionId, 'assistant', response.response);
    } catch (error) {
      console.error('Error querying patient info:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container h-screen overflow-hidden">
      <div className="flex h-full bg-gray-900 rounded-lg shadow-lg">
        <ConversationsList
          sessions={sessions}
          currentSession={currentSession}
          onSessionChange={setCurrentSession}
          onDeleteSession={handleDeleteSession}
          onNewSession={handleNewSession}
        />
        <div className="flex-1 flex flex-col bg-gray-800">
          <header className="bg-blue-250 text-white p-3">
            <h1 className="text-xl font-bold">Application Médical</h1>
          </header>
          <ChatWindow messages={messages} />
          <MessageInput onQueryPatientInfo={handleQueryPatientInfo} isLoading={isLoading} />          
          {/* Ajouter un formulaire pour interroger les informations des patients */}
        </div>
      </div>
    </div>
  );
}

export default App;