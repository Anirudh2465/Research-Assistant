import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import apiClient from '../api/client';
import { Sparkles, ArrowRight, Loader2 } from 'lucide-react';

interface Idea {
    id: number;
    title: string;
    summary: string;
    status: string;
    novelty_score: number; // Not in SQL, but maybe backend returns it if joined? SQL Idea table doesn't have score. 
    // Phase 5 implementation put scores in Neo4j. SQLite Idea table is basic.
    // Backend API list_ideas only returns SQLite Idea model. 
    // For now we display status/title.
}

const IdeasPage: React.FC = () => {
    const [ideas, setIdeas] = useState<Idea[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        apiClient.get('/ideas/')
            .then(res => setIdeas(res.data))
            .catch(err => console.error(err))
            .finally(() => setLoading(false));
    }, []);

    if (loading) return <div className="flex items-center justify-center h-full"><Loader2 className="animate-spin" /></div>;

    return (
        <div className="p-8 max-w-7xl mx-auto w-full">
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Idea Backlog</h1>
                    <p className="text-muted-foreground mt-1">Manage, mature, and promote your research ideas.</p>
                </div>
                <button className="bg-primary text-primary-foreground px-4 py-2 rounded-md flex items-center gap-2 hover:opacity-90">
                    <Sparkles size={18} /> Generate Idea
                </button>
            </div>

            <div className="space-y-4">
                {ideas.map((idea) => (
                    <div
                        key={idea.id}
                        className="p-6 bg-card border rounded-lg flex justify-between items-center hover:bg-muted/30 transition-colors"
                    >
                        <div className="max-w-2xl">
                            <div className="flex items-center gap-3 mb-1">
                                <h3 className="text-lg font-semibold">{idea.title}</h3>
                                <span className={`text-xs px-2 py-0.5 rounded-full border ${idea.status === 'promoted' ? 'bg-purple-100 text-purple-700 border-purple-200' :
                                        idea.status === 'mature' ? 'bg-blue-100 text-blue-700 border-blue-200' :
                                            idea.status === 'rejected' ? 'bg-red-100 text-red-700 border-red-200' :
                                                'bg-gray-100 text-gray-700 border-gray-200'
                                    }`}>
                                    {idea.status}
                                </span>
                            </div>
                            <p className="text-muted-foreground text-sm line-clamp-1">
                                {idea.summary || "No summary provided."}
                            </p>
                        </div>

                        <Link
                            to={`/ideas/${idea.id}`}
                            className="text-sm font-medium text-primary hover:underline flex items-center"
                        >
                            Details <ArrowRight size={16} className="ml-1" />
                        </Link>
                    </div>
                ))}

                {ideas.length === 0 && (
                    <div className="text-center py-20 text-muted-foreground border-2 border-dashed rounded-xl">
                        No ideas yet. Synthesize new ones from your research.
                    </div>
                )}
            </div>
        </div>
    );
};

export default IdeasPage;
