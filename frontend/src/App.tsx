import React, { useState, useEffect, useRef } from 'react';
import { Layout, Tabs, Spin, message, Alert } from 'antd';
import Sidebar from './components/Sidebar';
import ChatMessage from './components/ChatMessage';
import TableSchemaPanel from './components/TableSchemaPanel';
import TableRelationDiagram from './components/TableRelationDiagram';
import type { Message as MsgType, Session, TableSchema } from './types';
import { sendMessage, getHistory, getSession, getTables, deleteSession, healthCheck } from './api';
import { Input, Button } from 'antd';
import { SendOutlined } from '@ant-design/icons';
import './App.css';

const { Sider, Content } = Layout;

const App: React.FC = () => {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string | undefined>();
  const [messages, setMessages] = useState<MsgType[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [tables, setTables] = useState<Record<string, TableSchema>>({});
  const [lastSqlData, setLastSqlData] = useState<any>(null);
  const [backendError, setBackendError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // 检查后端连接
    healthCheck()
      .then(() => {
        console.log('✅ Backend is connected');
        setBackendError(null);
      })
      .catch((err) => {
        console.error('❌ Backend connection failed:', err);
        setBackendError('后端服务未响应，请确保后端服务已启动（端口 8000）');
      });

    loadHistory();
    getTables().then(setTables).catch((err) => {
      console.error('Failed to load tables:', err);
      setBackendError('无法加载表结构，请检查后端服务');
    });
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadHistory = async () => {
    try {
      const data = await getHistory();
      setSessions(data);
    } catch (e) {
      console.error(e);
    }
  };

  const handleSelectSession = async (sessionId: string) => {
    setCurrentSessionId(sessionId);
    try {
      const msgs = await getSession(sessionId);
      setMessages(msgs);
      const lastAssistant = msgs.filter(m => m.role === 'assistant').pop();
      if (lastAssistant?.sql_data) setLastSqlData(lastAssistant.sql_data);
    } catch (e) {
      console.error(e);
    }
  };

  const handleNewChat = () => {
    setCurrentSessionId(undefined);
    setMessages([]);
    setLastSqlData(null);
  };

  const handleDeleteSession = async (sessionId: string) => {
    await deleteSession(sessionId);
    if (currentSessionId === sessionId) handleNewChat();
    loadHistory();
  };

  const handleSend = async () => {
    if (!inputValue.trim() || loading) return;
    const question = inputValue.trim();
    setInputValue('');

    const userMsg: MsgType = { role: 'user', content: question };
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);

    try {
      const response = await sendMessage(question, currentSessionId);
      setCurrentSessionId(response.session_id);

      const assistantMsg: MsgType = {
        role: 'assistant',
        content: `\`\`\`sql\n${response.sql}\n\`\`\`\n\n${response.explanation}`,
        sql_data: response
      };
      setMessages(prev => [...prev, assistantMsg]);
      setLastSqlData(response);
      loadHistory();
      setBackendError(null);
    } catch (e: unknown) {
      let errMsg = '未知错误';
      
      if (e instanceof Error) {
        errMsg = e.message;
      } else if (typeof e === 'object' && e !== null && 'response' in e) {
        const response = (e as any).response;
        if (response?.data?.detail) {
          errMsg = response.data.detail;
        }
      }
      
      console.error('SQL生成失败:', e);
      
      // 显示错误信息
      if (errMsg.includes('401') || errMsg.includes('认证')) {
        setBackendError(`❌ API 认证失败: ${errMsg}\n\n请查看 API_KEY_SETUP.md 配置文档`);
      } else if (errMsg.includes('503') || errMsg.includes('未初始化')) {
        setBackendError(`❌ 后端服务错误: ${errMsg}`);
      } else {
        setBackendError(`❌ 错误: ${errMsg}`);
      }
      
      message.error('请求失败: ' + errMsg);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `❌ 错误: ${errMsg}\n\n请检查:\n1. 后端服务是否运行\n2. API 密钥配置是否正确`
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout style={{ height: '100vh', overflow: 'hidden' }}>
      <Sider width={250} style={{ background: '#001529', overflow: 'auto', height: '100vh' }}>
        <Sidebar
          sessions={sessions}
          currentSessionId={currentSessionId}
          onSelectSession={handleSelectSession}
          onNewChat={handleNewChat}
          onDeleteSession={handleDeleteSession}
        />
      </Sider>
      <Content style={{ display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden' }}>
        {backendError && (
          <Alert
            message="连接错误"
            description={backendError}
            type="error"
            showIcon
            closable
            onClose={() => setBackendError(null)}
            style={{ margin: '8px' }}
          />
        )}
        <div style={{ flex: 1, overflow: 'auto', padding: '16px', background: '#f5f5f5' }}>
          {messages.length === 0 ? (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', color: '#999' }}>
              <div style={{ textAlign: 'center' }}>
                <h2 style={{ color: '#333', marginBottom: '8px' }}>PathQC NL2SQL</h2>
                <p>请输入自然语言问题，我将为您生成SQL查询</p>
              </div>
            </div>
          ) : (
            messages.map((msg, idx) => <ChatMessage key={idx} message={msg} />)
          )}
          {loading && (
            <div style={{ textAlign: 'center', padding: '16px' }}>
              <Spin tip="正在生成SQL..." />
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        <div style={{ padding: '12px 16px', background: '#fff', borderTop: '1px solid #e8e8e8', display: 'flex', gap: '8px', flexShrink: 0 }}>
          <Input.TextArea
            value={inputValue}
            onChange={e => setInputValue(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); } }}
            placeholder="输入问题，例如：查询今天所有已发布的病理报告..."
            autoSize={{ minRows: 1, maxRows: 4 }}
            style={{ flex: 1 }}
            disabled={loading}
          />
          <Button type="primary" icon={<SendOutlined />} onClick={handleSend} loading={loading} style={{ alignSelf: 'flex-end' }}>
            发送
          </Button>
        </div>
      </Content>
      <Sider width={380} style={{ background: '#fff', borderLeft: '1px solid #e8e8e8', overflow: 'auto', height: '100vh' }}>
        <Tabs defaultActiveKey="schema" style={{ height: '100%' }} items={[
          {
            key: 'relation',
            label: '表关系',
            children: <TableRelationDiagram sqlData={lastSqlData} />,
          },
          {
            key: 'schema',
            label: '表结构',
            children: <TableSchemaPanel tables={tables} />,
          },
        ]} />
      </Sider>
    </Layout>
  );
};

export default App;
