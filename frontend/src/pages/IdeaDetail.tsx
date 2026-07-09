import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import apiClient from '../api/client';
import {
    ArrowLeft, Sparkles, CheckCircle, XCircle, ArrowUpCircle,
    Loader2, AlertCircle, BarChart2
} from 'lucide-react';

interface Idea {
    id: number;
    title: string;
    summary: string;
    status: string;
    origin: string;
    created_at: string;
    updated_at: string;
}

const STATUS_CONFIG: Record<string, { label: string; className: string }> = {
    draft:    { label: 'Draft',    className: 'bg-gray-100 text-gray-700 border-gray-200' },
    mature:   { label: 'Mature',   className: 'bg-blue-100 text-blue-700 border-blue-200' },
    rejected: { label: 'Rejected', className: 'bg-red-100 text-red-700 border-red-200' },
    promoted: { label: 'Promoted', className: 'bg-purple-100 text-purple-700 border-purple-200' },
};

const IdeaDetail: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const [idea, setIdea] = useState<Idea | null>(null);
    const [loading, setLoading] = useState(true);
    const [actionLoading, setActionLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const fetchIdea = () => {
        if (!id) return;
        setLoading(true);
        apiClient.get(`/ideas/${id}`)
            .then(res => setIdea(res.data))
            .catch(() => setError('Idea not found.'))
            .finally(() => setLoading(false));
    };

    useEffect(() => {
        fetchIdea();
    }, [id]);

    const updateStatus = async (newStatus: string) => {
        if (!id) return;
        setActionLoading(true);
        try {
            const res = await apiClient.patch(`/ideas/${id}/status`, { status: newStatus });
            setIdea(res.data);
        } catch {
            setError('Failed to update status.');
        } finally {
            setActionLoading(false);
        }
    };

    const promoteIdea = async () => {
        if (!id) return;
        setActionLoading(true);
        try {
            const res = await apiClient.post(`/ideas/${id}/promote`);
            const { new_project_id } = res.data;
            navigate(`/projects/${new_project_id}`);
        } catch {
            setError('Promotion failed. Ensure idea is set to "mature" first.');
            setActionLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-full">
                <Loader2 className="animate-spin text-primary" size={32} />
            </div>
        );
    }

    if (error || !idea) {
        return (
            <div className="flex flex-col items-center justify-center h-full gap-4 text-muted-foreground">
                <AlertCircle size={40} className="text-red-500" />
                <p>{error || 'Something went wrong.'}</p>
                <Link to="/ideas" className="text-primary hover:underline">← Back to Ideas</Link>
            </div>
        );
    }

    const statusMeta = STATUS_CONFIG[idea.status] ?? STATUS_CONFIG.draft;

    return (
        <div className="p-8 max-w-4xl mx-auto w-full">
            {/* Header */}
            <div className="flex items-center gap-3 mb-8">
                <Link to="/ideas" className="text-muted-foreground hover:text-foreground transition-colors">
                    <ArrowLeft size={20} />
                </Link>
                <h1 className="text-3xl font-bold tracking-tight flex-1">{idea.title}</h1>
                <span className={`text-xs px-2 py-1 rounded-full border font-medium ${statusMeta.className}`}>
                    {statusMeta.label}
                </span>
            </div>

            {/* Summary Card */}
            <div className="p-6 bg-card border rounded-xl mb-6">
                <h2 className="text-sm font-semibold uppercase text-muted-foreground mb-3 flex items-center gap-2">
                    <Sparkles size={14} /> Summary
                </h2>
                <p className="text-foreground leading-relaxed">
                    {idea.summary || <span className="text-muted-foreground italic">No summary available.</span>}
                </p>
            </div>

            {/* Metadata */}
            <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="p-4 bg-card border rounded-lg">
                    <p className="text-xs text-muted-foreground uppercase font-semibold mb-1">Origin</p>
                    <p className="font-medium capitalize">{idea.origin || '—'}</p>
                </div>
                <div className="p-4 bg-card border rounded-lg">
                    <p className="text-xs text-muted-foreground uppercase font-semibold mb-1">Created</p>
                    <p className="font-medium">
                        {idea.created_at ? new Date(idea.created_at).toLocaleDateString() : '—'}
                    </p>
                </div>
            </div>

            {/* Novelty / Feasibility Placeholder */}
            <div className="p-4 bg-card border rounded-lg mb-6">
                <h2 className="text-sm font-semibold uppercase text-muted-foreground mb-3 flex items-center gap-2">
                    <BarChart2 size={14} /> Scores (from Knowledge Graph)
                </h2>
                <p className="text-xs text-muted-foreground italic">
                    Novelty and feasibility scores are stored in Neo4j. Add a <code>/api/ideas/{'{id}'}/scores</code> endpoint to surface them here.
                </p>
            </div>

            {/* Actions */}
            <div className="flex flex-wrap gap-3 pt-4 border-t">
                {idea.status === 'draft' && (
                    <button
                        onClick={() => updateStatus('mature')}
                        disabled={actionLoading}
                        className="flex items-center gap-2 px-4 py-2 rounded-md bg-blue-600 text-white hover:bg-blue-700 transition-colors disabled:opacity-50"
                    >
                        <CheckCircle size={16} /> Mark as Mature
                    </button>
                )}

                {idea.status === 'mature' && (
                    <button
                        onClick={promoteIdea}
                        disabled={actionLoading}
                        className="flex items-center gap-2 px-4 py-2 rounded-md bg-purple-600 text-white hover:bg-purple-700 transition-colors disabled:opacity-50"
                    >
                        <ArrowUpCircle size={16} /> Promote to Project
                    </button>
                )}

                {idea.status !== 'rejected' && idea.status !== 'promoted' && (
                    <button
                        onClick={() => updateStatus('rejected')}
                        disabled={actionLoading}
                        className="flex items-center gap-2 px-4 py-2 rounded-md border border-red-300 text-red-600 hover:bg-red-50 transition-colors disabled:opacity-50"
                    >
                        <XCircle size={16} /> Reject
                    </button>
                )}

                {idea.status === 'rejected' && (
                    <button
                        onClick={() => updateStatus('draft')}
                        disabled={actionLoading}
                        className="flex items-center gap-2 px-4 py-2 rounded-md border text-muted-foreground hover:bg-muted transition-colors disabled:opacity-50"
                    >
                        Restore to Draft
                    </button>
                )}

                {actionLoading && <Loader2 className="animate-spin text-muted-foreground self-center" size={18} />}
            </div>
        </div>
    );
};

export default IdeaDetail;
