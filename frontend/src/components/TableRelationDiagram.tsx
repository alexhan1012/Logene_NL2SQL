import React, { useEffect } from 'react';
import ReactFlow, {
  type Node, type Edge, useNodesState, useEdgesState, Background, Controls, MarkerType,
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
      position: {
        x: (i % 2) * 200 + (i % 2 === 0 ? 0 : 20),
        y: Math.floor(i / 2) * 100 + 20
      },
      data: { label: table },
      style: {
        background: '#1677ff', color: '#fff', borderRadius: '8px',
        padding: '10px 20px', border: '2px solid #0958d9', fontWeight: 'bold',
        fontSize: '13px', minWidth: '120px', textAlign: 'center' as const,
        boxShadow: '0 2px 8px rgba(22,119,255,0.3)'
      }
    }));

    const newEdges: Edge[] = [];
    const addedPairs = new Set<string>();

    const addEdge = (source: string, target: string, label: string, index: number) => {
      const key = [source, target].sort().join('-');
      if (!addedPairs.has(key) && tables.includes(source) && tables.includes(target)) {
        addedPairs.add(key);
        newEdges.push({
          id: `e${index}-${key}`,
          source,
          target,
          label,
          animated: true,
          style: { stroke: '#52c41a', strokeWidth: 2 },
          labelStyle: { fontSize: '11px', fontWeight: 'bold', fill: '#389e0d' },
          labelBgStyle: { fill: '#f6ffed', stroke: '#b7eb8f' },
          labelBgPadding: [4, 4] as [number, number],
          markerEnd: { type: MarkerType.ArrowClosed, color: '#52c41a' },
        });
      }
    };

    if (sqlData.joins?.length) {
      sqlData.joins.forEach((join, i) => {
        // Try to match table.field = table.field pattern
        const match = join.match(/(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)/);
        if (match) {
          addEdge(match[1], match[3], match[2], i);
        } else {
          // Try to match table names mentioned
          const tableMatches = tables.filter(t => join.includes(t));
          if (tableMatches.length >= 2) {
            addEdge(tableMatches[0], tableMatches[1], 'F_BLH', i);
          }
        }
      });
    }

    // If no edges were created but multiple tables exist, connect via F_BLH
    if (newEdges.length === 0 && tables.length > 1) {
      tables.slice(1).forEach((table, i) => {
        addEdge(tables[0], table, 'F_BLH', 100 + i);
      });
    }

    setNodes(newNodes);
    setEdges(newEdges);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sqlData]);

  if (!sqlData?.tables_used?.length) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '250px' }}>
        <Empty description="发送问题后查看表关系图" />
      </div>
    );
  }

  return (
    <div style={{ height: '280px', width: '100%', border: '1px solid #f0f0f0', borderRadius: '8px', overflow: 'hidden' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
        fitViewOptions={{ padding: 0.3 }}
        minZoom={0.5}
        maxZoom={2}
      >
        <Background gap={16} size={1} />
        <Controls showInteractive={false} />
      </ReactFlow>
    </div>
  );
};

export default TableRelationDiagram;
