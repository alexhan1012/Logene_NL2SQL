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
  id?: number;
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

export interface DatabaseVendor {
  id: number;
  name: string;
  display_name: string;
}

export interface SchemaLibrary {
  id: number;
  name: string;
  description?: string;
}

export interface SchemaTableInfo {
  id: number;
  table_name: string;
  description?: string;
  fields: TableField[];
}
