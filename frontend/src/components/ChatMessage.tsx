import React from 'react';
import { Avatar } from 'antd';
import { UserOutlined, RobotOutlined } from '@ant-design/icons';
import type { Message } from '../types';

interface Props {
  message: Message;
}

const ChatMessage: React.FC<Props> = ({ message }) => {
  const isUser = message.role === 'user';

  const renderContent = (content: string) => {
    const sqlMatch = content.match(/```sql\n([\s\S]*?)\n```/);
    if (sqlMatch) {
      const sql = sqlMatch[1];
      const rest = content.replace(/```sql\n[\s\S]*?\n```/, '').trim();
      return (
        <>
          <pre style={{
            background: '#1e1e1e', color: '#d4d4d4', padding: '12px', borderRadius: '6px',
            overflow: 'auto', fontSize: '13px', margin: '8px 0', fontFamily: 'Consolas, Monaco, monospace'
          }}>
            <code>{sql}</code>
          </pre>
          {rest && <p style={{ margin: '8px 0 0', whiteSpace: 'pre-wrap' }}>{rest}</p>}
        </>
      );
    }
    return <p style={{ margin: 0, whiteSpace: 'pre-wrap' }}>{content}</p>;
  };

  return (
    <div style={{ display: 'flex', marginBottom: '16px', flexDirection: isUser ? 'row-reverse' : 'row', gap: '8px' }}>
      <Avatar
        icon={isUser ? <UserOutlined /> : <RobotOutlined />}
        style={{ background: isUser ? '#1677ff' : '#52c41a', flexShrink: 0 }}
      />
      <div style={{
        maxWidth: '80%', padding: '10px 14px',
        borderRadius: isUser ? '12px 2px 12px 12px' : '2px 12px 12px 12px',
        background: isUser ? '#1677ff' : '#fff', color: isUser ? '#fff' : '#000',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
      }}>
        {renderContent(message.content)}
      </div>
    </div>
  );
};

export default ChatMessage;
