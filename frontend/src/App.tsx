import React, { useState, useEffect, useRef } from 'react';
import { Layout, Tabs, Spin, message } from 'antd';
import Sidebar from './components/Sidebar';
import ChatMessage from './components/ChatMessage';
import TableSchemaPanel from './components/TableSchemaPanel';
import TableRelationDiagram from './components/TableRelationDiagram';
import type { Message as MsgType, Session, TableSchema } from './types';
import { sendMessage, getHistory, getSession, getTables, deleteSession } from './api';
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
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadHistory();
    getTables().then(setTables).catch(console.error);
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
    } catch (e: unknown) {
      const errMsg = e instanceof Error ? e.message : '未知错误';
      console.error('SQL生成失败:', e);
      message.error('SQL生成失败: ' + errMsg);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: '抱歉，处理您的请求时出现错误，请检查后端服务是否正常运行。'
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
