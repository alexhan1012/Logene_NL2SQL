import React, { useState } from 'react';
import { Collapse, Tag, Typography, Empty } from 'antd';
import { ApiOutlined, TableOutlined } from '@ant-design/icons';
import type { CallLogEntry, Message } from '../types';

interface Props {
  messages: Message[];
}

const STEP_LABELS: Record<string, string> = {
  table_selection: '第一步：选表',
  sql_generation: '第二步：生成SQL',
};

const ROLE_LABELS: Record<string, string> = {
  system: '系统提示',
  user: '用户消息',
};

const ROLE_COLORS: Record<string, string> = {
  system: '#722ed1',
  user: '#1677ff',
};

const LogEntry: React.FC<{ log: CallLogEntry; index: number }> = ({ log, index }) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <div
      style={{
        border: '1px solid #e8e8e8',
        borderRadius: 6,
        marginBottom: 8,
        overflow: 'hidden',
        background: '#fafafa',
      }}
    >
      {/* Header */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 8,
          padding: '8px 12px',
          background: '#f0f5ff',
          cursor: 'pointer',
          borderBottom: expanded ? '1px solid #e8e8e8' : 'none',
        }}
        onClick={() => setExpanded(!expanded)}
      >
        <ApiOutlined style={{ color: '#1677ff' }} />
        <Typography.Text strong style={{ fontSize: 13 }}>
          调用 #{index + 1} — {STEP_LABELS[log.step] ?? log.step}
        </Typography.Text>
        {log.selected_tables && log.selected_tables.length > 0 && (
          <span style={{ marginLeft: 4 }}>
            {log.selected_tables.map(t => (
              <Tag key={t} icon={<TableOutlined />} color="blue" style={{ fontSize: 11 }}>
                {t}
              </Tag>
            ))}
          </span>
        )}
        <span style={{ marginLeft: 'auto', color: '#999', fontSize: 12 }}>
          {expanded ? '▲ 收起' : '▼ 展开'}
        </span>
      </div>

      {expanded && (
        <div style={{ padding: '10px 12px' }}>
          {/* Request messages */}
          <Typography.Text
            type="secondary"
            style={{ fontSize: 12, display: 'block', marginBottom: 6 }}
          >
            📤 请求消息
          </Typography.Text>
          {log.request.map((msg, i) => (
            <div key={i} style={{ marginBottom: 8 }}>
              <Tag color={ROLE_COLORS[msg.role] ?? 'default'} style={{ fontSize: 11, marginBottom: 4 }}>
                {ROLE_LABELS[msg.role] ?? msg.role}
              </Tag>
              <pre
                style={{
                  background: '#1e1e1e',
                  color: '#d4d4d4',
                  padding: '8px 10px',
                  borderRadius: 4,
                  fontSize: 12,
                  margin: 0,
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                  fontFamily: 'Consolas, Monaco, monospace',
                  maxHeight: 300,
                  overflow: 'auto',
                }}
              >
                {msg.content}
              </pre>
            </div>
          ))}

          {/* Response */}
          <Typography.Text
            type="secondary"
            style={{ fontSize: 12, display: 'block', marginTop: 10, marginBottom: 6 }}
          >
            📥 模型响应
          </Typography.Text>
          <pre
            style={{
              background: '#f6ffed',
              color: '#135200',
              border: '1px solid #b7eb8f',
              padding: '8px 10px',
              borderRadius: 4,
              fontSize: 12,
              margin: 0,
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word',
              fontFamily: 'Consolas, Monaco, monospace',
              maxHeight: 200,
              overflow: 'auto',
            }}
          >
            {log.response}
          </pre>
        </div>
      )}
    </div>
  );
};

const CallLogPanel: React.FC<Props> = ({ messages }) => {
  const logsByQuestion: { question: string; logs: CallLogEntry[] }[] = messages
    .reduce<{ question: string; logs: CallLogEntry[] }[]>((logsByQuestion, msg, idx) => {
      if (msg.role === 'assistant' && msg.sql_data?.call_logs?.length) {
        // Find the preceding user message
        const prevUser = [...messages].slice(0, idx).reverse().find(m => m.role === 'user');
        logsByQuestion.push({ question: prevUser?.content ?? '未知问题', logs: msg.sql_data.call_logs });
      }
      return logsByQuestion;
    }, []);

  if (logsByQuestion.length === 0) {
    return (
      <div style={{ padding: '24px 16px', textAlign: 'center' }}>
        <Empty description="暂无调用日志" image={Empty.PRESENTED_IMAGE_SIMPLE} />
        <Typography.Text type="secondary" style={{ fontSize: 12 }}>
          发送问题后，这里会显示每次 LLM 调用的请求和响应详情
        </Typography.Text>
      </div>
    );
  }

  return (
    <div style={{ padding: '8px' }}>
      <Collapse
        accordion
        defaultActiveKey={[String(logsByQuestion.length - 1)]}
        items={logsByQuestion.map((item, i) => ({
          key: String(i),
          label: (
            <Typography.Text ellipsis style={{ fontSize: 13, maxWidth: 260 }}>
              问题 #{i + 1}: {item.question}
            </Typography.Text>
          ),
          children: (
            <div>
              {item.logs.map((log, j) => (
                <LogEntry key={j} log={log} index={j} />
              ))}
            </div>
          ),
        }))}
      />
    </div>
  );
};

export default CallLogPanel;
