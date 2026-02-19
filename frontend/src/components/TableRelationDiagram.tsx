import React, { useEffect } from 'react';
import ReactFlow, {
  type Node, type Edge, useNodesState, useEdgesState, Background, Controls,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { Empty } from 'antd';

interface Props {
  sqlData?: {
    tables_used: string[];
    joins: string[];
    sql: string;
  } | null;
}

const TableRelationDiagram: React.FC<Props> = ({ sqlData }) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  useEffect(() => {
    if (!sqlData?.tables_used?.length) {
      setNodes([]);
      setEdges([]);
      return;
    }

    const tables = sqlData.tables_used;
    const newNodes: Node[] = tables.map((table, i) => ({
      id: table,
      position: { x: (i % 3) * 180, y: Math.floor(i / 3) * 120 },
      data: { label: table },
      style: {
        background: '#1677ff', color: '#fff', borderRadius: '6px',
        padding: '8px 16px', border: 'none', fontWeight: 'bold'
      }
    }));

    const newEdges: Edge[] = [];
    if (sqlData.joins?.length) {
      sqlData.joins.forEach((join, i) => {
        const match =
          join.match(/(\w+)\.F_BLH\s*=\s*(\w+)\.F_BLH/) ||
          join.match(/(\w+)\s+.*?\s+(\w+)/);
        if (match && tables.includes(match[1]) && tables.includes(match[2])) {
          newEdges.push({
            id: `e${i}`, source: match[1], target: match[2],
            label: 'F_BLH', animated: true,
            style: { stroke: '#52c41a' }, labelStyle: { fontSize: '10px' }
          });
        }
      });
      if (newEdges.length === 0 && tables.length > 1) {
        tables.slice(1).forEach((table, i) => {
          newEdges.push({
            id: `e${i}`, source: tables[0], target: table,
            label: 'F_BLH', animated: true,
            style: { stroke: '#52c41a' }, labelStyle: { fontSize: '10px' }
          });
        });
      }
    } else if (tables.length > 1) {
      tables.slice(1).forEach((table, i) => {
        newEdges.push({
          id: `e${i}`, source: tables[0], target: table,
          label: 'F_BLH', animated: true,
          style: { stroke: '#52c41a' }, labelStyle: { fontSize: '10px' }
        });
      });
    }

    setNodes(newNodes);
    setEdges(newEdges);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sqlData]);

  if (!sqlData?.tables_used?.length) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '300px' }}>
        <Empty description="发送问题后查看表关系图" />
      </div>
    );
  }

  return (
    <div style={{ height: '400px', width: '100%' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
      >
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
};

export default TableRelationDiagram;
