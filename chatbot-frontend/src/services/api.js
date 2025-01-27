import axios from 'axios';
const API_URL = 'http://127.0.0.1:8000';

export const chatApi = {
  sendMessage: async (message, sessionId) => {
    const response = await axios.post(`${API_URL}/chat/chat`, {
      message,
      session_id: sessionId
    });
    return response.data;
  },
  getHistory: async (sessionId) => {
    const response = await axios.get(`${API_URL}/chat/history/${sessionId}`);
    return response.data;
  },
  getAllSessions: async () => {
    const response = await axios.get(`${API_URL}/chat/sessions`);
    return response.data;
  },
  deleteSession: async (sessionId) => {
    const response = await axios.delete(`${API_URL}/chat/sessions/${sessionId}`);
    return response.data;
  },
  queryPatientInfo: async ({ question, session_id }) => {
    const response = await axios.post(`${API_URL}/patient/patients/query`, {
      question: question,
      session_id: session_id
    });
    return response.data;
  },
  createSession: async () => {
    const response = await axios.post(`${API_URL}/memory/session/create`);
    return response.data;
  },
  saveMessage: async (sessionId, role, content) => {
    const response = await axios.post(`${API_URL}/memory/session/${sessionId}/add_message`, {
      message: content,
      role: role
    });
    return response.data;
  }
};