import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import apiClient from '../api/client';
import GraphView from '../components/GraphView';
import { FileText, Lightbulb, Activity, ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';

const ProjectWorkspace: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const [project, setProject] = useState<any>(null);
    const [graphData, setGraphData] = useState({ nodes: [], links: [] });
    // Placeholders for side panels
    const [papers, setPapers] = useState([]);
    const [activeTab, setActiveTab] = useState<'papers' | 'ideas'>('papers');

    useEffect(() => {
        if (!id) return;

        // Fetch Project Details
        apiClient.get(`/projects/${id}`).then(res => setProject(res.data));
    }, [id]);

    if (!project) return <div>Loading...</div>;

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
                <div className="flex gap-4 text-sm text-muted-foreground">
                    <div>Progress: Literature 10%</div>
                    <div>Method 0%</div>
                </div>
            </header>

            {/* 3-Pane Layout */}
            <div className="flex-1 flex overflow-hidden">

                {/* Left: Papers Panel */}
                <div className="w-80 border-r bg-slate-50 flex flex-col">
                    <div className="p-3 border-b font-medium flex items-center gap-2 text-sm text-muted-foreground">
                        <FileText size={16} /> Papers
                    </div>
                    <div className="flex-1 p-4 overflow-y-auto">
                        <div className="text-sm text-muted-foreground text-center mt-10">
                            No papers uploaded yet.
                            <br />
                            <button className="mt-2 text-primary hover:underline">Upload Paper</button>
                        </div>
                    </div>
                </div>

                {/* Center: KG */}
                <div className="flex-1 bg-white relative">
                    <div className="absolute top-4 left-4 z-10 bg-white/80 backdrop-blur p-2 rounded border shadow-sm text-xs">
                        <span className="font-semibold">Context:</span> {project.domain}
                    </div>

                    <GraphView data={graphData} />

                    <div className="absolute bottom-0 left-0 right-0 h-8 bg-white border-t flex items-center px-4 text-xs text-muted-foreground">
                        {graphData.nodes.length} Nodes • {graphData.links.length} Relations
                    </div>
                </div>

                {/* Right: Ideas/Signals */}
                <div className="w-80 border-l bg-slate-50 flex flex-col">
                    <div className="flex border-b">
                        <button
                            onClick={() => setActiveTab('papers')}
                            className={`flex-1 p-3 text-sm font-medium flex items-center justify-center gap-2 ${activeTab === 'papers' ? 'bg-white border-b-2 border-primary text-primary' : 'text-muted-foreground'}`}
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
                        {activeTab === 'papers' && (
                            <div className="space-y-4">
                                <h3 className="text-xs font-semibold uppercase text-muted-foreground">Upcoming Tasks</h3>
                                <div className="p-3 bg-white border rounded shadow-sm text-sm">
                                    <div className="flex justify-between mb-1">
                                        <span className="font-medium">Define Model</span>
                                        <span className="text-xs text-red-500 font-bold">High Priority</span>
                                    </div>
                                    <div className="text-xs text-muted-foreground">Due: Tomorrow</div>
                                </div>

                                <div className="text-center py-6 text-sm text-muted-foreground">
                                    <button className="text-primary hover:underline">+ Add Task</button>
                                </div>
                            </div>
                        )}

                        {activeTab === 'ideas' && (
                            <div className="text-sm text-muted-foreground text-center mt-10">
                                No active ideas.
                            </div>
                        )}
                    </div>
                </div>

            </div>
        </div>
    );
};

export default ProjectWorkspace;
