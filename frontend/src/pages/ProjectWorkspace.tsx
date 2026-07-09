import React, { useEffect, useState, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import apiClient from '../api/client';
import GraphView from '../components/GraphView';
import { FileText, Lightbulb, Activity, ArrowLeft, Upload, Loader2, RefreshCw } from 'lucide-react';

interface Project {
    id: number;
    name: string;
    domain: string;
    status: string;
    problem_statement: string;
}

interface Task {
    id: number;
    title: string;
    due_datetime: string | null;
    severity: number;
    importance: number;
    status: string;
}

interface GraphData {
    nodes: any[];
    links: any[];
}

// Transform API edges → react-force-graph links
function transformGraphData(raw: { nodes: any[]; edges: any[] }): GraphData {
    const nodes = (raw.nodes || []).map((n: any) => ({
        id: n.id,
        name: n.properties?.name || n.id,
        labels: n.labels,
        ...n.properties,
    }));
    const links = (raw.edges || []).map((e: any) => ({
        source: e.start_node,
        target: e.end_node,
        type: e.type,
    }));
    return { nodes, links };
}

const ProjectWorkspace: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const [project, setProject] = useState<Project | null>(null);
    const [graphData, setGraphData] = useState<GraphData>({ nodes: [], links: [] });  // Fix #22
    const [graphLoading, setGraphLoading] = useState(false);
    const [activeTab, setActiveTab] = useState<'activity' | 'ideas'>('activity');
    const [tasks, setTasks] = useState<Task[]>([]);
    const [uploadFile, setUploadFile] = useState<File | null>(null);
    const [uploading, setUploading] = useState(false);
    const [uploadMsg, setUploadMsg] = useState('');

    // Fix #22: Fetch project graph data
    const fetchGraph = useCallback(() => {
        if (!id) return;
        setGraphLoading(true);
        apiClient.get(`/research/kg`, { params: { project_id: id, depth: 2 } })
            .then(res => setGraphData(transformGraphData(res.data)))
            .catch(err => console.error('Graph fetch error:', err))
            .finally(() => setGraphLoading(false));
    }, [id]);

    useEffect(() => {
        if (!id) return;
        // Fetch Project Details
        apiClient.get(`/projects/${id}`).then(res => setProject(res.data));
        // Fetch project tasks
        apiClient.get('/tasks/', { params: { project_id: id } }).then(res => setTasks(res.data));
        // Fix #22: Fetch project graph
        fetchGraph();
    }, [id, fetchGraph]);

    const handleUpload = async () => {
        if (!uploadFile || !id) return;
        setUploading(true);
        setUploadMsg('');
        const form = new FormData();
        form.append('file', uploadFile);
        form.append('scope', 'project');
        form.append('project_id', id);
        try {
            const res = await apiClient.post('/papers/upload', form, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            setUploadMsg(`✓ Queued (Job #${res.data.job_id})`);
            setUploadFile(null);
        } catch {
            setUploadMsg('✗ Upload failed');
        } finally {
            setUploading(false);
        }
    };

    if (!project) {
        return (
            <div className="flex items-center justify-center h-full">
                <Loader2 className="animate-spin text-primary" size={32} />
            </div>
        );
    }

    const pendingTasks = tasks.filter(t => t.status !== 'done').slice(0, 5);

    return (
        <div className="flex flex-col h-full overflow-hidden">
            {/* Workspace Header */}
            <header className="h-14 border-b flex items-center px-4 justify-between bg-card">
                <div className="flex items-center gap-4">
                    <Link to="/projects" className="text-muted-foreground hover:text-foreground">
                        <ArrowLeft size={18} />
                    </Link>
                    <h1 className="font-semibold text-lg">{project.name}</h1>
                    <span className="text-xs bg-secondary px-2 py-1 rounded-full">{project.status}</span>
                </div>
                <div className="flex gap-6 text-sm text-muted-foreground">
                    <span>{graphData.nodes.length} Nodes</span>
                    <span>{graphData.links.length} Relations</span>
                </div>
            </header>

            {/* 3-Pane Layout */}
            <div className="flex-1 flex overflow-hidden">

                {/* Left: Papers Upload Panel */}
                <div className="w-80 border-r bg-slate-50 flex flex-col">
                    <div className="p-3 border-b font-medium flex items-center gap-2 text-sm text-muted-foreground">
                        <FileText size={16} /> Papers
                    </div>
                    <div className="flex-1 p-4 overflow-y-auto space-y-3">
                        <p className="text-xs text-muted-foreground">Upload a PDF to extract concepts into this project's knowledge graph.</p>
                        <label className="flex flex-col items-center gap-2 border-2 border-dashed rounded-lg p-4 cursor-pointer hover:border-primary/50 transition-colors">
                            <Upload size={20} className="text-muted-foreground" />
                            <span className="text-xs text-muted-foreground">
                                {uploadFile ? uploadFile.name : 'Choose PDF'}
                            </span>
                            <input
                                type="file"
                                accept=".pdf"
                                className="hidden"
                                onChange={e => {
                                    setUploadFile(e.target.files?.[0] || null);
                                    setUploadMsg('');
                                }}
                            />
                        </label>
                        {uploadFile && (
                            <button
                                onClick={handleUpload}
                                disabled={uploading}
                                className="w-full bg-primary text-primary-foreground py-2 rounded-md text-sm font-medium hover:opacity-90 disabled:opacity-50 flex items-center justify-center gap-2"
                            >
                                {uploading ? <><Loader2 size={14} className="animate-spin" /> Uploading...</> : 'Upload & Ingest'}
                            </button>
                        )}
                        {uploadMsg && (
                            <p className="text-xs text-center text-muted-foreground">{uploadMsg}</p>
                        )}
                    </div>
                </div>

                {/* Center: KG — Fix #22: shows real project graph data */}
                <div className="flex-1 bg-white relative">
                    <div className="absolute top-4 left-4 z-10 bg-white/80 backdrop-blur p-2 rounded border shadow-sm text-xs flex items-center gap-2">
                        <span className="font-semibold">Context:</span> {project.domain}
                        <button
                            onClick={fetchGraph}
                            title="Refresh graph"
                            className="ml-2 text-muted-foreground hover:text-primary"
                        >
                            <RefreshCw size={12} className={graphLoading ? 'animate-spin' : ''} />
                        </button>
                    </div>

                    <GraphView data={graphData} />

                    {graphData.nodes.length === 0 && !graphLoading && (
                        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                            <p className="text-muted-foreground text-sm opacity-50">
                                No concepts yet. Upload papers to build the graph.
                            </p>
                        </div>
                    )}

                    <div className="absolute bottom-0 left-0 right-0 h-8 bg-white border-t flex items-center px-4 text-xs text-muted-foreground">
                        {graphData.nodes.length} Nodes • {graphData.links.length} Relations
                    </div>
                </div>

                {/* Right: Activity / Ideas */}
                <div className="w-80 border-l bg-slate-50 flex flex-col">
                    <div className="flex border-b">
                        <button
                            onClick={() => setActiveTab('activity')}
                            className={`flex-1 p-3 text-sm font-medium flex items-center justify-center gap-2 ${activeTab === 'activity' ? 'bg-white border-b-2 border-primary text-primary' : 'text-muted-foreground'}`}
                        >
                            <Activity size={16} /> Activity
                        </button>
                        <button
                            onClick={() => setActiveTab('ideas')}
                            className={`flex-1 p-3 text-sm font-medium flex items-center justify-center gap-2 ${activeTab === 'ideas' ? 'bg-white border-b-2 border-primary text-primary' : 'text-muted-foreground'}`}
                        >
                            <Lightbulb size={16} /> Ideas
                        </button>
                    </div>
                    <div className="flex-1 p-4 overflow-y-auto">
                        {activeTab === 'activity' && (
                            <div className="space-y-4">
                                <h3 className="text-xs font-semibold uppercase text-muted-foreground">Pending Tasks</h3>
                                {pendingTasks.length === 0 ? (
                                    <p className="text-sm text-muted-foreground text-center mt-6">No pending tasks.</p>
                                ) : (
                                    pendingTasks.map(task => (
                                        <div key={task.id} className="p-3 bg-white border rounded shadow-sm text-sm">
                                            <div className="flex justify-between mb-1">
                                                <span className="font-medium line-clamp-1">{task.title}</span>
                                                <span className={`text-xs font-bold ${task.severity >= 4 ? 'text-red-500' : 'text-muted-foreground'}`}>
                                                    S{task.severity}
                                                </span>
                                            </div>
                                            {task.due_datetime && (
                                                <div className="text-xs text-muted-foreground">
                                                    Due: {new Date(task.due_datetime).toLocaleDateString()}
                                                </div>
                                            )}
                                        </div>
                                    ))
                                )}
                            </div>
                        )}

                        {activeTab === 'ideas' && (
                            <div className="text-sm text-muted-foreground text-center mt-10">
                                No ideas linked to this project yet.
                            </div>
                        )}
                    </div>
                </div>

            </div>
        </div>
    );
};

export default ProjectWorkspace;
