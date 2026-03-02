import React, { useState, useEffect } from 'react';
import { Modal, Tabs, List, Button, Input, Space, Popconfirm, message, Empty, Tag, Typography, Table as AntTable } from 'antd';
import { PlusOutlined, DeleteOutlined } from '@ant-design/icons';
import type { SchemaLibrary, SchemaTableInfo, TableField } from '../types';
import {
  getSchemaLibraries, createSchemaLibrary, deleteSchemaLibrary,
  getLibraryTables, createSchemaTable, deleteSchemaTable,
  createSchemaField, deleteSchemaField,
} from '../api';

interface Props {
  open: boolean;
  onClose: () => void;
}

const SchemaManager: React.FC<Props> = ({ open, onClose }) => {
  const [libraries, setLibraries] = useState<SchemaLibrary[]>([]);
  const [selectedLib, setSelectedLib] = useState<number | null>(null);
  const [tables, setTables] = useState<SchemaTableInfo[]>([]);
  const [newLibName, setNewLibName] = useState('');
  const [newLibDesc, setNewLibDesc] = useState('');
  const [newTableName, setNewTableName] = useState('');
  const [newTableDesc, setNewTableDesc] = useState('');
  const [expandedTable, setExpandedTable] = useState<number | null>(null);
  const [newFieldName, setNewFieldName] = useState('');
  const [newFieldType, setNewFieldType] = useState('VARCHAR');
  const [newFieldDesc, setNewFieldDesc] = useState('');

  const loadLibraries = async () => {
    try {
      const libs = await getSchemaLibraries();
      setLibraries(libs);
      if (libs.length > 0 && !selectedLib) setSelectedLib(libs[0].id);
    } catch {
      // ignore
    }
  };

  const loadTables = async (libId: number) => {
    try {
      const t = await getLibraryTables(libId);
      setTables(t);
    } catch {
      // ignore
    }
  };

  useEffect(() => {
    if (open) loadLibraries();
  }, [open]);

  useEffect(() => {
    if (selectedLib) loadTables(selectedLib);
  }, [selectedLib]);

  const handleAddLibrary = async () => {
    if (!newLibName.trim()) { message.warning('请输入库名称'); return; }
    try {
      const lib = await createSchemaLibrary(newLibName.trim(), newLibDesc.trim() || undefined);
      setNewLibName('');
      setNewLibDesc('');
      loadLibraries();
      setSelectedLib(lib.id);
      message.success('创建成功');
    } catch {
      message.error('创建失败');
    }
  };

  const handleDeleteLibrary = async (id: number) => {
    try {
      await deleteSchemaLibrary(id);
      if (selectedLib === id) setSelectedLib(null);
      loadLibraries();
      message.success('删除成功');
    } catch {
      message.error('删除失败');
    }
  };

  const handleAddTable = async () => {
    if (!selectedLib || !newTableName.trim()) { message.warning('请输入表名'); return; }
    try {
      await createSchemaTable(selectedLib, newTableName.trim(), newTableDesc.trim() || undefined);
      setNewTableName('');
      setNewTableDesc('');
      loadTables(selectedLib);
      message.success('添加成功');
    } catch {
      message.error('添加失败');
    }
  };

  const handleDeleteTable = async (tableId: number) => {
    try {
      await deleteSchemaTable(tableId);
      if (selectedLib) loadTables(selectedLib);
      message.success('删除成功');
    } catch {
      message.error('删除失败');
    }
  };

  const handleAddField = async (tableId: number) => {
    if (!newFieldName.trim()) { message.warning('请输入字段名'); return; }
    try {
      await createSchemaField(tableId, newFieldName.trim(), newFieldType, newFieldDesc.trim() || undefined);
      setNewFieldName('');
      setNewFieldType('VARCHAR');
      setNewFieldDesc('');
      if (selectedLib) loadTables(selectedLib);
      message.success('添加成功');
    } catch {
      message.error('添加失败');
    }
  };

  const handleDeleteField = async (fieldId: number) => {
    try {
      await deleteSchemaField(fieldId);
      if (selectedLib) loadTables(selectedLib);
      message.success('删除成功');
    } catch {
      message.error('删除失败');
    }
  };

  const libTabs = libraries.map(lib => ({
    key: String(lib.id),
    label: (
      <span>
        {lib.name}
        <Popconfirm title="确认删除此库？所有表和字段都将被删除" onConfirm={(e) => { e?.stopPropagation(); handleDeleteLibrary(lib.id); }}>
          <DeleteOutlined style={{ marginLeft: 8, color: '#ff4d4f', fontSize: '11px' }} onClick={e => e.stopPropagation()} />
        </Popconfirm>
      </span>
    ),
  }));

  return (
    <Modal
      title="数据库表结构管理"
      open={open}
      onCancel={onClose}
      footer={null}
      width={900}
      destroyOnClose
      styles={{ body: { maxHeight: '70vh', overflow: 'auto' } }}
    >
      {/* Add library */}
      <Space style={{ marginBottom: '12px' }}>
        <Input placeholder="库名称" value={newLibName} onChange={e => setNewLibName(e.target.value)} style={{ width: 150 }} />
        <Input placeholder="描述(可选)" value={newLibDesc} onChange={e => setNewLibDesc(e.target.value)} style={{ width: 200 }} />
        <Button type="primary" icon={<PlusOutlined />} onClick={handleAddLibrary}>新建库</Button>
      </Space>

      {libraries.length === 0 ? (
        <Empty description="暂无数据库，请先创建" />
      ) : (
        <Tabs
          activeKey={selectedLib ? String(selectedLib) : undefined}
          onChange={k => setSelectedLib(Number(k))}
          items={libTabs}
        />
      )}

      {selectedLib && (
        <div>
          {/* Add table */}
          <Space style={{ marginBottom: '12px' }}>
            <Input placeholder="表名 (如 T_JCXX)" value={newTableName} onChange={e => setNewTableName(e.target.value)} style={{ width: 180 }} />
            <Input placeholder="表描述" value={newTableDesc} onChange={e => setNewTableDesc(e.target.value)} style={{ width: 250 }} />
            <Button icon={<PlusOutlined />} onClick={handleAddTable}>添加表</Button>
          </Space>

          <List
            dataSource={tables}
            renderItem={table => (
              <List.Item style={{ display: 'block', padding: '8px 0' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                  <Space>
                    <Tag color="blue" style={{ cursor: 'pointer' }} onClick={() => setExpandedTable(expandedTable === table.id ? null : table.id)}>
                      {table.table_name}
                    </Tag>
                    <Typography.Text type="secondary" style={{ fontSize: '12px' }}>{table.description}</Typography.Text>
                    <Typography.Text type="secondary" style={{ fontSize: '11px' }}>({table.fields.length} 字段)</Typography.Text>
                  </Space>
                  <Popconfirm title="确认删除此表？" onConfirm={() => handleDeleteTable(table.id)}>
                    <Button type="text" danger icon={<DeleteOutlined />} size="small" />
                  </Popconfirm>
                </div>

                {expandedTable === table.id && (
                  <div style={{ marginLeft: '16px', marginTop: '8px' }}>
                    <AntTable
                      size="small"
                      dataSource={table.fields}
                      rowKey="id"
                      pagination={false}
                      columns={[
                        { title: '字段名', dataIndex: 'name', key: 'name', width: 150 },
                        { title: '类型', dataIndex: 'type', key: 'type', width: 100 },
                        { title: '描述', dataIndex: 'description', key: 'description' },
                        {
                          title: '操作', key: 'action', width: 60,
                          render: (_: unknown, record: TableField) => (
                            <Popconfirm title="删除字段？" onConfirm={() => handleDeleteField(record.id!)}>
                              <Button type="text" danger icon={<DeleteOutlined />} size="small" />
                            </Popconfirm>
                          )
                        }
                      ]}
                    />
                    <Space style={{ marginTop: '8px' }}>
                      <Input placeholder="字段名" value={newFieldName} onChange={e => setNewFieldName(e.target.value)} style={{ width: 120 }} size="small" />
                      <Input placeholder="类型" value={newFieldType} onChange={e => setNewFieldType(e.target.value)} style={{ width: 100 }} size="small" />
                      <Input placeholder="描述" value={newFieldDesc} onChange={e => setNewFieldDesc(e.target.value)} style={{ width: 150 }} size="small" />
                      <Button icon={<PlusOutlined />} size="small" onClick={() => handleAddField(table.id)}>添加字段</Button>
                    </Space>
                  </div>
                )}
              </List.Item>
            )}
            locale={{ emptyText: '暂无表，请添加' }}
          />
        </div>
      )}
    </Modal>
  );
};

export default SchemaManager;
