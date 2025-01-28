const ConversationsList = ({ sessions, currentSession, onSessionChange, onDeleteSession, onNewSession }) => {
  console.log('ConversationsList sessions:', sessions);
  return (
    <div className="w-80 border-r p-4 bg-gray-800 text-gray-100 relative conversations-background">
      <h2 className="text-xl font-bold mb-4">Conversations</h2>
      <button
        onClick={onNewSession}
        className="w-full text-left px-3 py-2 rounded-lg bg-blue-500 text-white hover:bg-blue-600 mb-4"
      >
        Nouvelle discussion
      </button>
      <div className="space-y-2">
        {sessions
          .filter(session => session) // Filtrer les sessions nulles ou indéfinies
          .map((session) => (
            <div key={session} className="flex justify-between items-center">
              <button
                onClick={() => onSessionChange(session)}
                className={`flex-grow mr-2 w-3/4 ${
                  currentSession === session ? 'active' : ''
                }`}
              >
                Session {session.slice(-2)}
              </button>
              <button
                onClick={() => onDeleteSession(session)}
                className="text-red-500 hover:text-red-700 flex-shrink-0 w-1/4"
              >
                ✕
              </button>
              <div className="absolute bottom-4 right-4">
        <img src="/logo.png" alt="Logo" className="w-13 h-12" />
      </div>
            </div>
          ))}
      </div>
    </div>
  );
};

export default ConversationsList;