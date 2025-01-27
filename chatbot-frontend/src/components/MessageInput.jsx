import { useState } from 'react';
const MessageInput = ({ onSendMessage, isLoading, onQueryPatientInfo }) => {
  const [message, setMessage] = useState('');
  const [question, setQuestion] = useState('');
  
  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim()) {
      onSendMessage(message);
      setMessage('');
    }
  };

  const handleSubmitQuestion = (e) => {
    e.preventDefault();
    if (question.trim()) {
      onQueryPatientInfo(question);
      setQuestion('');
    }
  };

  return (
    <form onSubmit={handleSubmitQuestion} className="flex gap-2 p-4 border-t">
      <input
        type="text"
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Type your message..."
        className="flex-1 rounded-lg border-gray-300 focus:ring-blue-500 focus:border-blue-500 text-black"
        disabled={isLoading}
      />
      <button
        type="submit"
        disabled={isLoading}
        className={`px-4 py-2 rounded-lg bg-blue-500 text-white ${isLoading ? 'opacity-50' : 'hover:bg-blue-600'}`}
      >
        {isLoading ? 'Sending...' : 'Send'}
      </button>
    </form>
  );
};
export default MessageInput;