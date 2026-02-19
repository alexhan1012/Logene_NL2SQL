import React from 'react';
import { Collapse, Tag, Typography } from 'antd';
import type { TableSchema } from '../types';

interface Props {
  tables: Record<string, TableSchema>;
}

const TableSchemaPanel: React.FC<Props> = ({ tables }) => {
  const items = Object.entries(tables).map(([tableName, schema]) => ({
    key: tableName,
    label: (
      <span>
        <Tag color="blue">{tableName}</Tag>
        <Typography.Text type="secondary" style={{ fontSize: '12px' }}>{schema.description}</Typography.Text>
      </span>
    ),
    children: (
      <div>
        {schema.fields?.map(field => (
          <div
            key={field.name}
            style={{
              display: 'flex', gap: '8px', padding: '3px 0',
              borderBottom: '1px solid #f0f0f0', fontSize: '12px'
            }}
          >
            <Tag color="green" style={{ minWidth: '120px', fontSize: '11px' }}>{field.name}</Tag>
            <Tag color="orange" style={{ fontSize: '11px' }}>{field.type}</Tag>
            <span style={{ color: '#666' }}>{field.description}</span>
          </div>
        ))}
      </div>
    )
  }));

  return (
    <div style={{ padding: '8px' }}>
      <Collapse size="small" items={items} />
    </div>
  );
};

export default TableSchemaPanel;
