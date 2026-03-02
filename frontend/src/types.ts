export interface CallLogEntry {
  step: 'table_selection' | 'sql_generation';
  request: { role: string; content: string }[];
  response: string;
  selected_tables?: string[];
}

export interface Message {
  id?: number;
  role: 'user' | 'assistant';
  content: string;
  sql_data?: {
    sql: string;
    tables_used: string[];
    joins: string[];
    explanation: string;
    call_logs?: CallLogEntry[];
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
  call_logs?: CallLogEntry[];
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

export interface TableRelation {
  id: number;
  library_id: number;
  from_table: string;
  from_column: string;
  to_table: string;
  to_column: string;
  description?: string;
}
