import React from 'react';
import { Button, List, Tooltip } from 'antd';
import { PlusOutlined, DeleteOutlined, MessageOutlined, SettingOutlined, DatabaseOutlined } from '@ant-design/icons';
import type { Session } from '../types';

interface Props {
  sessions: Session[];
  currentSessionId?: string;
  onSelectSession: (id: string) => void;
  onNewChat: () => void;
  onDeleteSession: (id: string) => void;
  onOpenSettings: () => void;
  onOpenSchemaManager: () => void;
}

const Sidebar: React.FC<Props> = ({ sessions, currentSessionId, onSelectSession, onNewChat, onDeleteSession, onOpenSettings, onOpenSchemaManager }) => {
  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ padding: '16px' }}>
        <Button type="primary" icon={<PlusOutlined />} block onClick={onNewChat} style={{ marginBottom: '8px' }}>
          新建对话
        </Button>
      </div>
      <div style={{ flex: 1, overflow: 'auto', padding: '0 8px' }}>
        <List
          dataSource={sessions}
          renderItem={session => (
            <List.Item
              style={{
                cursor: 'pointer', borderRadius: '6px', padding: '8px 10px', marginBottom: '4px',
                background: currentSessionId === session.session_id ? 'rgba(255,255,255,0.15)' : 'transparent',
                color: '#fff'
              }}
              onClick={() => onSelectSession(session.session_id)}
              actions={[
                <Tooltip title="删除" key="del">
                  <DeleteOutlined
                    style={{ color: '#ff4d4f' }}
                    onClick={e => { e.stopPropagation(); onDeleteSession(session.session_id); }}
                  />
                </Tooltip>
              ]}
            >
              <List.Item.Meta
                avatar={<MessageOutlined style={{ color: '#69b1ff' }} />}
                title={<span style={{ color: '#fff', fontSize: '13px' }}>{session.title}</span>}
                description={<span style={{ color: '#aaa', fontSize: '11px' }}>{new Date(session.updated_at).toLocaleDateString('zh-CN')}</span>}
              />
            </List.Item>
          )}
        />
      </div>
      <div style={{ padding: '8px 16px', borderTop: '1px solid rgba(255,255,255,0.1)' }}>
        <Button type="text" icon={<DatabaseOutlined />} block onClick={onOpenSchemaManager}
          style={{ color: '#aaa', textAlign: 'left', marginBottom: '4px' }}>
          表结构管理
        </Button>
        <Button type="text" icon={<SettingOutlined />} block onClick={onOpenSettings}
          style={{ color: '#aaa', textAlign: 'left' }}>
          系统设置
        </Button>
      </div>
    </div>
  );
};

export default Sidebar;
