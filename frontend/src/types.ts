export interface Message {
  id?: number;
  role: 'user' | 'assistant';
  content: string;
  sql_data?: {
    sql: string;
    tables_used: string[];
    joins: string[];
    explanation: string;
  };
  created_at?: string;
}

export interface Session {
  session_id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface TableField {
  name: string;
  type: string;
  description: string;
}

export interface TableSchema {
  description: string;
  fields: TableField[];
}

export interface ChatResponse {
  sql: string;
  tables_used: string[];
  joins: string[];
  explanation: string;
  session_id: string;
}
