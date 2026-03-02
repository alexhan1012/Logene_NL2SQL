import React, { useState, useEffect } from 'react';
import { Modal, Tabs, Form, Input, Select, Button, List, Space, Popconfirm, message, Typography, Card } from 'antd';
import { DeleteOutlined, PlusOutlined } from '@ant-design/icons';
import type { DatabaseVendor, SchemaLibrary, SchemaTableInfo } from '../types';
import {
  getSettings, updateSettings,
  getVendors, createVendor, deleteVendor,
  getSchemaLibraries, getLibraryTables,
} from '../api';

interface Props {
  open: boolean;
  onClose: () => void;
}

const SettingsModal: React.FC<Props> = ({ open, onClose }) => {
  const [settings, setSettings] = useState<Record<string, string>>({});
  const [vendors, setVendors] = useState<DatabaseVendor[]>([]);
  const [newVendorName, setNewVendorName] = useState('');
  const [newVendorDisplay, setNewVendorDisplay] = useState('');
  const [saving, setSaving] = useState(false);

  // Fixed context tables state
  const [libraries, setLibraries] = useState<SchemaLibrary[]>([]);
  const [fixedTablesLibraryId, setFixedTablesLibraryId] = useState<number | undefined>();
  const [availableTables, setAvailableTables] = useState<SchemaTableInfo[]>([]);
  const [fixedTableNames, setFixedTableNames] = useState<string[]>([]);
  const [savingFixed, setSavingFixed] = useState(false);

  const loadData = async () => {
    try {
      const [s, v, libs] = await Promise.all([getSettings(), getVendors(), getSchemaLibraries()]);
      setSettings(s);
      setVendors(v);
      setLibraries(libs);
      if (libs.length > 0) {
        const firstId = libs[0].id;
        setFixedTablesLibraryId(firstId);
        const key = `fixed_context_tables_${firstId}`;
        try {
          setFixedTableNames(s[key] ? JSON.parse(s[key]) : []);
        } catch (e) {
          console.warn('Failed to parse fixed_context_tables setting:', e);
          setFixedTableNames([]);
        }
        const tables = await getLibraryTables(firstId);
        setAvailableTables(tables);
      }
    } catch {
      // ignore
    }
  };

  useEffect(() => {
    if (open) loadData();
  }, [open]);

  const handleFixedLibraryChange = async (libId: number) => {
    setFixedTablesLibraryId(libId);
    try {
      const tables = await getLibraryTables(libId);
      setAvailableTables(tables);
      const key = `fixed_context_tables_${libId}`;
      try {
        setFixedTableNames(settings[key] ? JSON.parse(settings[key]) : []);
      } catch (e) {
        console.warn('Failed to parse fixed_context_tables setting:', e);
        setFixedTableNames([]);
      }
    } catch {
      setAvailableTables([]);
      setFixedTableNames([]);
    }
  };

  const handleSaveFixedTables = async () => {
    if (!fixedTablesLibraryId) return;
    setSavingFixed(true);
    try {
      const key = `fixed_context_tables_${fixedTablesLibraryId}`;
      await updateSettings([{ key, value: JSON.stringify(fixedTableNames) }]);
      setSettings(prev => ({ ...prev, [key]: JSON.stringify(fixedTableNames) }));
      message.success('固定上下文表已保存');
    } catch {
      message.error('保存失败');
    } finally {
      setSavingFixed(false);
    }
  };

  const handleSaveSettings = async () => {
    setSaving(true);
    try {
      const items = Object.entries(settings).map(([key, value]) => ({ key, value }));
      await updateSettings(items);
      message.success('设置已保存');
    } catch {
      message.error('保存失败');
    } finally {
      setSaving(false);
    }
  };

  const handleAddVendor = async () => {
    if (!newVendorName.trim() || !newVendorDisplay.trim()) {
      message.warning('请填写完整信息');
      return;
    }
    try {
      await createVendor(newVendorName.trim(), newVendorDisplay.trim());
      setNewVendorName('');
      setNewVendorDisplay('');
      loadData();
      message.success('添加成功');
    } catch {
      message.error('添加失败');
    }
  };

  const handleDeleteVendor = async (id: number) => {
    try {
      await deleteVendor(id);
      loadData();
      message.success('删除成功');
    } catch {
      message.error('删除失败');
    }
  };

  const providerOptions = [
    { value: 'bailian', label: '阿里云百炼' },
    { value: 'ark', label: '火山引擎(Ark)' },
    { value: 'siliconflow', label: '硅基流动(SiliconFlow)' },
  ];

  return (
    <Modal
      title="系统设置"
      open={open}
      onCancel={onClose}
      footer={null}
      width={700}
      destroyOnClose
    >
      <Tabs items={[
        {
          key: 'llm',
          label: 'LLM 配置',
          children: (
            <div>
              <Form layout="vertical">
                <Form.Item label="模型服务提供商">
                  <Select
                    value={settings.llm_provider || 'bailian'}
                    onChange={(v) => setSettings({ ...settings, llm_provider: v })}
                    options={providerOptions}
                  />
                </Form.Item>
                <Form.Item label="API Key">
                  <Input.Password
                    value={settings.api_key || ''}
                    onChange={(e) => setSettings({ ...settings, api_key: e.target.value })}
                    placeholder="输入API密钥"
                  />
                </Form.Item>
                <Form.Item label="Base URL (可选)">
                  <Input
                    value={settings.base_url || ''}
                    onChange={(e) => setSettings({ ...settings, base_url: e.target.value })}
                    placeholder="留空使用默认地址"
                  />
                </Form.Item>
                <Form.Item label="模型名称 (可选)">
                  <Input
                    value={settings.model_name || ''}
                    onChange={(e) => setSettings({ ...settings, model_name: e.target.value })}
                    placeholder="留空使用默认模型"
                  />
                </Form.Item>
                <Button type="primary" onClick={handleSaveSettings} loading={saving}>
                  保存设置
                </Button>
              </Form>
              <Typography.Text type="secondary" style={{ display: 'block', marginTop: '12px', fontSize: '12px' }}>
                注意：LLM 配置变更需要重启后端服务才能生效。当前配置将保存到数据库中供未来使用。
              </Typography.Text>
            </div>
          ),
        },
        {
          key: 'fixed_tables',
          label: '固定上下文表',
          children: (
            <div>
              <Typography.Paragraph type="secondary" style={{ fontSize: '13px' }}>
                配置在每次生成SQL时，始终添加到第二步上下文中的表（例如：患者基础信息表）。
              </Typography.Paragraph>
              <Form layout="vertical">
                <Form.Item label="选择Schema库">
                  <Select
                    value={fixedTablesLibraryId}
                    onChange={handleFixedLibraryChange}
                    options={libraries.map(l => ({ value: l.id, label: l.name }))}
                    placeholder="请选择库"
                    style={{ width: '100%' }}
                  />
                </Form.Item>
                <Form.Item label="固定包含的表（可多选）">
                  <Select
                    mode="multiple"
                    value={fixedTableNames}
                    onChange={setFixedTableNames}
                    options={availableTables.map(t => ({
                      value: t.table_name,
                      label: `${t.table_name}${t.description ? ` — ${t.description}` : ''}`,
                    }))}
                    placeholder="选择始终添加到上下文的表"
                    style={{ width: '100%' }}
                    allowClear
                    showSearch
                    filterOption={(input, option) =>
                      (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
                    }
                  />
                </Form.Item>
                <Button type="primary" onClick={handleSaveFixedTables} loading={savingFixed}>
                  保存固定表配置
                </Button>
              </Form>
            </div>
          ),
        },
        {
          key: 'vendors',
          label: '数据库厂商',
          children: (
            <div>
              <Card size="small" title="已配置的数据库厂商" style={{ marginBottom: '16px' }}>
                <List
                  size="small"
                  dataSource={vendors}
                  renderItem={(v) => (
                    <List.Item
                      actions={[
                        <Popconfirm title="确认删除？" onConfirm={() => handleDeleteVendor(v.id)} key="del">
                          <Button type="text" danger icon={<DeleteOutlined />} size="small" />
                        </Popconfirm>
                      ]}
                    >
                      <List.Item.Meta
                        title={v.display_name}
                        description={v.name}
                      />
                    </List.Item>
                  )}
                  locale={{ emptyText: '暂无配置' }}
                />
              </Card>
              <Card size="small" title="添加新数据库厂商">
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Input
                    placeholder="标识名 (如: sqlserver)"
                    value={newVendorName}
                    onChange={e => setNewVendorName(e.target.value)}
                  />
                  <Input
                    placeholder="显示名 (如: SQL Server)"
                    value={newVendorDisplay}
                    onChange={e => setNewVendorDisplay(e.target.value)}
                  />
                  <Button type="primary" icon={<PlusOutlined />} onClick={handleAddVendor}>
                    添加
                  </Button>
                </Space>
              </Card>
            </div>
          ),
        },
      ]} />
    </Modal>
  );
};

export default SettingsModal;
