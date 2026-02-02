import React, { useEffect, useRef, useState } from 'react';
import ForceGraph2D, { type ForceGraphMethods } from 'react-force-graph-2d';

interface GraphData {
    nodes: any[];
    links: any[];
}

interface GraphViewProps {
    data: GraphData;
    onNodeClick?: (node: any) => void;
}

const GraphView: React.FC<GraphViewProps> = ({ data, onNodeClick }) => {
    const containerRef = useRef<HTMLDivElement>(null);
    const fgRef = useRef<ForceGraphMethods>();
    const [dimensions, setDimensions] = useState({ width: 800, height: 600 });

    useEffect(() => {
        // Simple resize observer
        if (!containerRef.current) return;
        const resizeObserver = new ResizeObserver((entries) => {
            for (const entry of entries) {
                setDimensions({
                    width: entry.contentRect.width,
                    height: entry.contentRect.height
                });
            }
        });
        resizeObserver.observe(containerRef.current);
        return () => resizeObserver.disconnect();
    }, []);

    return (
        <div ref={containerRef} className="w-full h-full bg-slate-50 overflow-hidden relative border rounded-lg">
            <ForceGraph2D
                ref={fgRef}
                width={dimensions.width}
                height={dimensions.height}
                graphData={data}
                nodeLabel="name"
                nodeColor={(node: any) => {
                    if (node.labels?.includes('Project')) return '#ef4444'; // Red
                    if (node.labels?.includes('Idea')) return '#a855f7'; // Purple
                    if (node.labels?.includes('Paper')) return '#3b82f6'; // Blue
                    return '#10b981'; // Green (Concept)
                }}
                nodeRelSize={6}
                linkColor={() => '#cbd5e1'}
                onNodeClick={(node) => {
                    fgRef.current?.centerAt(node.x, node.y, 1000);
                    fgRef.current?.zoom(3, 2000);
                    if (onNodeClick) onNodeClick(node);
                }}
                cooldownTicks={100}
            />
            <div className="absolute bottom-4 right-4 bg-white/90 p-2 text-xs rounded border shadow-sm">
                <div className="flex items-center gap-2"><div className="w-3 h-3 bg-emerald-500 rounded-full"></div> Concept</div>
                <div className="flex items-center gap-2"><div className="w-3 h-3 bg-blue-500 rounded-full"></div> Paper</div>
                <div className="flex items-center gap-2"><div className="w-3 h-3 bg-purple-500 rounded-full"></div> Idea</div>
            </div>
        </div>
    );
};

export default GraphView;
