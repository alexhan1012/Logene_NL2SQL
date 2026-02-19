import axios from 'axios';
import type { ChatResponse, Message, Session, TableSchema } from './types';

const api = axios.create({ baseURL: 'http://localhost:8000' });

export const sendMessage = (question: string, session_id?: string) =>
  api.post<ChatResponse>('/api/chat', { question, session_id }).then(r => r.data);

export const getHistory = () =>
  api.get<Session[]>('/api/history').then(r => r.data);

export const getSession = (session_id: string) =>
  api.get<Message[]>(`/api/history/${session_id}`).then(r => r.data);

export const getTables = () =>
  api.get<Record<string, TableSchema>>('/api/tables').then(r => r.data);

export const deleteSession = (session_id: string) =>
  api.delete(`/api/history/${session_id}`).then(r => r.data);
