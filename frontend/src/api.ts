import axios from 'axios';
import type { ChatResponse, Message, Session, TableSchema, DatabaseVendor, SchemaLibrary, SchemaTableInfo, TableRelation } from './types';

const envBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim();
const apiBaseUrl = (envBaseUrl && envBaseUrl.length > 0 ? envBaseUrl : 'http://localhost:8000').replace(/\/+$/, '');
const parsedTimeout = Number(import.meta.env.VITE_API_TIMEOUT_MS ?? 120000);
const apiTimeout = Number.isFinite(parsedTimeout) && parsedTimeout > 0 ? parsedTimeout : 120000;

const api = axios.create({ 
  baseURL: apiBaseUrl,
  timeout: apiTimeout,
  headers: {
    'Content-Type': 'application/json',
  }
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    console.log(`🚀 Request: ${config.method?.toUpperCase()} ${config.baseURL}${config.url}`);
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
    if (error.code === 'ECONNABORTED' || error.message?.toLowerCase().includes('timeout')) {
      console.error('❌ Request timeout:', error.message);
      error.message = '请求超时，请稍后重试（后端处理可能较慢）';
    } else if (error.message === 'Network Error') {
      error.message = `无法连接到服务器 (${apiBaseUrl})，请检查后端服务和网络`;
    }

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
      if (error.code !== 'ECONNABORTED') {
        error.message = `无法连接到服务器 (${apiBaseUrl})，请检查后端是否运行`;
      }
    } else {
      console.error('❌ Error:', error.message);
    }
    return Promise.reject(error);
  }
);

export const sendMessage = (question: string, session_id?: string, db_vendor?: string, schema_library_id?: number) =>
  api.post<ChatResponse>('/api/chat', { question, session_id, db_vendor, schema_library_id }).then(r => r.data);

export const getHistory = () =>
  api.get<Session[]>('/api/history').then(r => r.data);

export const getSession = (session_id: string) =>
  api.get<Message[]>(`/api/history/${session_id}`).then(r => r.data);

export const getTables = (library_id?: number) =>
  api.get<Record<string, TableSchema>>('/api/tables', { params: library_id ? { library_id } : {} }).then(r => r.data);

export const deleteSession = (session_id: string) =>
  api.delete(`/api/history/${session_id}`).then(r => r.data);

export const healthCheck = () =>
  api.get('/health').then(r => r.data);

// Settings
export const getSettings = () =>
  api.get<Record<string, string>>('/api/settings').then(r => r.data);

export const updateSettings = (items: { key: string; value: string }[]) =>
  api.put('/api/settings', items).then(r => r.data);

// Database Vendors
export const getVendors = () =>
  api.get<DatabaseVendor[]>('/api/vendors').then(r => r.data);

export const createVendor = (name: string, display_name: string) =>
  api.post<DatabaseVendor>('/api/vendors', { name, display_name }).then(r => r.data);

export const deleteVendor = (id: number) =>
  api.delete(`/api/vendors/${id}`).then(r => r.data);

// Schema Libraries
export const getSchemaLibraries = () =>
  api.get<SchemaLibrary[]>('/api/schema-libraries').then(r => r.data);

export const createSchemaLibrary = (name: string, description?: string) =>
  api.post<SchemaLibrary>('/api/schema-libraries', { name, description }).then(r => r.data);

export const updateSchemaLibrary = (id: number, data: { name?: string; description?: string }) =>
  api.put<SchemaLibrary>(`/api/schema-libraries/${id}`, data).then(r => r.data);

export const deleteSchemaLibrary = (id: number) =>
  api.delete(`/api/schema-libraries/${id}`).then(r => r.data);

// Schema Tables
export const getLibraryTables = (libraryId: number) =>
  api.get<SchemaTableInfo[]>(`/api/schema-libraries/${libraryId}/tables`).then(r => r.data);

export const createSchemaTable = (libraryId: number, table_name: string, description?: string) =>
  api.post<SchemaTableInfo>(`/api/schema-libraries/${libraryId}/tables`, { table_name, description }).then(r => r.data);

export const updateSchemaTable = (tableId: number, data: { table_name?: string; description?: string }) =>
  api.put(`/api/schema-tables/${tableId}`, data).then(r => r.data);

export const deleteSchemaTable = (tableId: number) =>
  api.delete(`/api/schema-tables/${tableId}`).then(r => r.data);

// Schema Fields
export const createSchemaField = (tableId: number, name: string, field_type: string, description?: string) =>
  api.post(`/api/schema-tables/${tableId}/fields`, { name, field_type, description }).then(r => r.data);

export const updateSchemaField = (fieldId: number, data: { name?: string; field_type?: string; description?: string }) =>
  api.put(`/api/schema-fields/${fieldId}`, data).then(r => r.data);

export const deleteSchemaField = (fieldId: number) =>
  api.delete(`/api/schema-fields/${fieldId}`).then(r => r.data);

// Table Relations
export const getLibraryRelations = (libraryId: number) =>
  api.get<TableRelation[]>(`/api/schema-libraries/${libraryId}/relations`).then(r => r.data);

export const createTableRelation = (libraryId: number, data: Omit<TableRelation, 'id' | 'library_id'>) =>
  api.post<TableRelation>(`/api/schema-libraries/${libraryId}/relations`, data).then(r => r.data);

export const updateTableRelation = (relationId: number, data: Partial<Omit<TableRelation, 'id' | 'library_id'>>) =>
  api.put<TableRelation>(`/api/table-relations/${relationId}`, data).then(r => r.data);

export const deleteTableRelation = (relationId: number) =>
  api.delete(`/api/table-relations/${relationId}`).then(r => r.data);
