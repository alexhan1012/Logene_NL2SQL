import axios from 'axios';
import type { ChatResponse, Message, Session, TableSchema } from './types';

const api = axios.create({ 
  baseURL: 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    console.log(`🚀 Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ Request error:', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    console.log(`✅ Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    if (error.response) {
      console.error(`❌ Response error: ${error.response.status} - ${error.response.statusText}`);
      console.error('Error data:', error.response.data);
      
      // 更详细的错误信息
      if (error.response.status === 401) {
        error.message = `认证失败: ${error.response.data?.detail || '无效的 API 密钥'}`;
      } else if (error.response.status === 503) {
        error.message = `服务不可用: ${error.response.data?.detail || '服务未初始化'}`;
      } else if (error.response.data?.detail) {
        error.message = error.response.data.detail;
      }
    } else if (error.request) {
      console.error('❌ No response received:', error.request);
      error.message = '无法连接到服务器，请检查后端是否运行';
    } else {
      console.error('❌ Error:', error.message);
    }
    return Promise.reject(error);
  }
);

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

export const healthCheck = () =>
  api.get('/health').then(r => r.data);
