import React, { useState, useEffect, useCallback } from 'react';
import { Search, Loader2 } from 'lucide-react';
import GraphView from '../components/GraphView';
import apiClient from '../api/client';

interface GraphData {
    nodes: any[];
    links: any[];
}

// Transform API response (edges with start_node/end_node) into react-force-graph links
function transformGraphData(raw: { nodes: any[]; edges: any[] }): GraphData {
    const nodeMap: Record<string, any> = {};
    const nodes = (raw.nodes || []).map((n: any) => {
        const node = {
            id: n.id,
            name: n.properties?.name || n.id,
            labels: n.labels,
            ...n.properties,
        };
        nodeMap[n.id] = node;
        return node;
    });
    const links = (raw.edges || []).map((e: any) => ({
        source: e.start_node,
        target: e.end_node,
        type: e.type,
    }));
    return { nodes, links };
}

const ResearchPage: React.FC = () => {
    const [query, setQuery] = useState('');
    const [graphData, setGraphData] = useState<GraphData>({ nodes: [], links: [] });
    const [loading, setLoading] = useState(false);
    const [selectedNode, setSelectedNode] = useState<any>(null);

    // Fix #21: Debounced search that calls /api/research/kg
    const fetchGraph = useCallback((searchQuery: string) => {
        setLoading(true);
        const params: Record<string, any> = { depth: 2 };
        if (searchQuery.trim()) params['center_node'] = searchQuery.trim();

        apiClient.get('/research/kg', { params })
            .then(res => setGraphData(transformGraphData(res.data)))
            .catch(err => console.error('Graph fetch error:', err))
            .finally(() => setLoading(false));
    }, []);

    // Load full global graph on mount
    useEffect(() => {
        fetchGraph('');
    }, [fetchGraph]);

    // Debounce the search input
    useEffect(() => {
        const timer = setTimeout(() => {
            fetchGraph(query);
        }, 600);
        return () => clearTimeout(timer);
    }, [query, fetchGraph]);

    return (
        <div className="h-full flex flex-col">
            {/* Search Bar */}
            <div className="h-16 border-b flex items-center px-8 bg-card gap-4">
                <Search className="text-muted-foreground shrink-0" />
                <input
                    className="bg-transparent outline-none flex-1 text-lg"
                    placeholder="Search global knowledge (e.g. 'Diffusion Models')..."
                    value={query}
                    onChange={e => setQuery(e.target.value)}
                />
                {loading && <Loader2 className="animate-spin text-muted-foreground shrink-0" size={20} />}
                <span className="text-xs text-muted-foreground">
                    {graphData.nodes.length} nodes · {graphData.links.length} edges
                </span>
            </div>

            {/* Graph + Detail pane */}
            <div className="flex-1 flex overflow-hidden">
                <div className="flex-1 bg-slate-50 relative">
                    <GraphView
                        data={graphData}
                        onNodeClick={(node) => setSelectedNode(node)}
                    />
                    {graphData.nodes.length === 0 && !loading && (
                        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                            <div className="text-center text-muted-foreground opacity-50">
                                <p className="text-xl font-medium">Global Knowledge Graph</p>
                                <p className="text-sm">
                                    {query ? 'No concepts found for that search.' : 'Ingest papers to build your knowledge graph.'}
                                </p>
                            </div>
                        </div>
                    )}
                </div>

                {/* Node Detail Sidebar */}
                {selectedNode && (
                    <div className="w-72 border-l bg-card p-5 overflow-y-auto flex flex-col gap-3">
                        <div className="flex justify-between items-start">
                            <h3 className="font-semibold text-lg leading-tight">{selectedNode.name}</h3>
                            <button
                                onClick={() => setSelectedNode(null)}
                                className="text-muted-foreground hover:text-foreground text-lg leading-none"
                            >
                                ✕
                            </button>
                        </div>
                        {selectedNode.labels?.length > 0 && (
                            <div className="flex flex-wrap gap-1">
                                {selectedNode.labels.map((l: string) => (
                                    <span key={l} className="text-xs px-2 py-0.5 bg-primary/10 text-primary rounded-full">
                                        {l}
                                    </span>
                                ))}
                            </div>
                        )}
                        {selectedNode.description && (
                            <p className="text-sm text-muted-foreground leading-relaxed">
                                {selectedNode.description}
                            </p>
                        )}
                        {selectedNode.confidence !== undefined && (
                            <div className="text-xs text-muted-foreground">
                                Confidence: <span className="font-mono font-semibold">{(selectedNode.confidence * 100).toFixed(0)}%</span>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default ResearchPage;
