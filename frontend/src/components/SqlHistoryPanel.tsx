import React from 'react';
import { List, Typography, Empty } from 'antd';
import { CodeOutlined } from '@ant-design/icons';
import type { Message } from '../types';

interface Props {
  messages: Message[];
  selectedIndex: number | null;
  onSelect: (index: number) => void;
}

const SqlHistoryPanel: React.FC<Props> = ({ messages, selectedIndex, onSelect }) => {
  const sqlMessages = messages
    .map((msg, idx) => ({ msg, idx }))
    .filter(({ msg }) => msg.role === 'assistant' && msg.sql_data?.sql);

  if (sqlMessages.length === 0) {
    return (
      <div style={{ padding: '16px', textAlign: 'center' }}>
        <Empty description="暂无SQL记录" image={Empty.PRESENTED_IMAGE_SIMPLE} />
      </div>
    );
  }

  return (
    <div style={{ padding: '4px 8px' }}>
      <Typography.Text strong style={{ display: 'block', padding: '8px 4px', fontSize: '13px' }}>
        SQL 历史记录
      </Typography.Text>
      <List
        size="small"
        dataSource={sqlMessages}
        renderItem={({ msg, idx }, listIdx) => (
          <List.Item
            style={{
              cursor: 'pointer',
              padding: '6px 8px',
              borderRadius: '4px',
              marginBottom: '2px',
              background: selectedIndex === idx ? '#e6f4ff' : 'transparent',
              border: selectedIndex === idx ? '1px solid #91caff' : '1px solid transparent',
            }}
            onClick={() => onSelect(idx)}
          >
            <div style={{ width: '100%', overflow: 'hidden' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '2px' }}>
                <CodeOutlined style={{ color: '#1677ff', fontSize: '12px' }} />
                <Typography.Text type="secondary" style={{ fontSize: '11px' }}>
                  SQL #{listIdx + 1}
                </Typography.Text>
              </div>
              <Typography.Text
                ellipsis
                style={{ fontSize: '12px', fontFamily: 'Consolas, Monaco, monospace', display: 'block' }}
              >
                {msg.sql_data!.sql.length > 80 ? msg.sql_data!.sql.substring(0, 80) + '...' : msg.sql_data!.sql}
              </Typography.Text>
            </div>
          </List.Item>
        )}
      />
    </div>
  );
};

export default SqlHistoryPanel;
