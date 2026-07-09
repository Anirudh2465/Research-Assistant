import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import apiClient from '../api/client';
import { Plus, ArrowRight, Loader2, X } from 'lucide-react';

interface Project {
    id: number;
    name: string;
    domain: string;
    status: string;
    problem_statement: string;
}

const defaultForm = { name: '', domain: '', problem_statement: '', constraints: '' };

const ProjectsPage: React.FC = () => {
    const [projects, setProjects] = useState<Project[]>([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);  // Fix #23
    const [form, setForm] = useState(defaultForm);
    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState('');

    const fetchProjects = () => {
        setLoading(true);
        apiClient.get('/projects/')
            .then(res => setProjects(res.data))
            .catch(err => console.error(err))
            .finally(() => setLoading(false));
    };

    useEffect(() => { fetchProjects(); }, []);

    const handleCreate = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!form.name.trim() || !form.domain.trim() || !form.problem_statement.trim()) {
            setError('Name, domain, and problem statement are required.');
            return;
        }
        setSubmitting(true);
        setError('');
        try {
            await apiClient.post('/projects/create', form);
            setShowModal(false);
            setForm(defaultForm);
            fetchProjects();
        } catch {
            setError('Failed to create project. Please try again.');
        } finally {
            setSubmitting(false);
        }
    };

    if (loading) return <div className="flex items-center justify-center h-full"><Loader2 className="animate-spin" /></div>;

    return (
        <div className="p-8 max-w-7xl mx-auto w-full">
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Projects</h1>
                    <p className="text-muted-foreground mt-1">Manage your active research contexts.</p>
                </div>
                {/* Fix #23: Button now opens a modal */}
                <button
                    onClick={() => { setShowModal(true); setError(''); }}
                    className="bg-primary text-primary-foreground px-4 py-2 rounded-md flex items-center gap-2 hover:opacity-90 transition-opacity"
                >
                    <Plus size={18} /> New Project
                </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {projects.map((project) => (
                    <Link
                        key={project.id}
                        to={`/projects/${project.id}`}
                        className="group block p-6 bg-card border rounded-xl hover:shadow-md transition-all active:scale-[0.99] border-border hover:border-primary/50"
                    >
                        <div className="flex justify-between items-start mb-4">
                            <span className="text-xs font-semibold px-2 py-1 bg-secondary text-secondary-foreground rounded-full uppercase tracking-wide">
                                {project.domain}
                            </span>
                            <span className={`text-xs px-2 py-1 rounded-full ${project.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'}`}>
                                {project.status}
                            </span>
                        </div>
                        <h3 className="text-xl font-semibold mb-2 group-hover:text-primary transition-colors">
                            {project.name}
                        </h3>
                        <p className="text-muted-foreground text-sm line-clamp-2 mb-4">
                            {project.problem_statement}
                        </p>
                        <div className="flex items-center text-sm text-primary font-medium mt-auto">
                            Open Workspace <ArrowRight size={16} className="ml-1 transition-transform group-hover:translate-x-1" />
                        </div>
                    </Link>
                ))}

                {projects.length === 0 && (
                    <div className="col-span-full text-center py-20 text-muted-foreground border-2 border-dashed rounded-xl">
                        No projects yet. Create one to get started.
                    </div>
                )}
            </div>

            {/* Fix #23: New Project Modal */}
            {showModal && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                    <div className="bg-card border rounded-xl shadow-2xl w-full max-w-lg">
                        <div className="flex items-center justify-between p-6 border-b">
                            <h2 className="text-xl font-semibold">New Research Project</h2>
                            <button onClick={() => setShowModal(false)} className="text-muted-foreground hover:text-foreground">
                                <X size={20} />
                            </button>
                        </div>
                        <form onSubmit={handleCreate} className="p-6 space-y-4">
                            <div>
                                <label className="block text-sm font-medium mb-1">Project Name *</label>
                                <input
                                    className="w-full border rounded-md px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-primary/30"
                                    value={form.name}
                                    onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
                                    placeholder="e.g. Efficient Diffusion Sampling"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-1">Research Domain *</label>
                                <input
                                    className="w-full border rounded-md px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-primary/30"
                                    value={form.domain}
                                    onChange={e => setForm(f => ({ ...f, domain: e.target.value }))}
                                    placeholder="e.g. Generative AI, NLP, Robotics"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-1">Problem Statement *</label>
                                <textarea
                                    className="w-full border rounded-md px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-primary/30 min-h-[80px] resize-none"
                                    value={form.problem_statement}
                                    onChange={e => setForm(f => ({ ...f, problem_statement: e.target.value }))}
                                    placeholder="Describe the research problem you're tackling..."
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-1">Constraints <span className="text-muted-foreground font-normal">(optional)</span></label>
                                <input
                                    className="w-full border rounded-md px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-primary/30"
                                    value={form.constraints}
                                    onChange={e => setForm(f => ({ ...f, constraints: e.target.value }))}
                                    placeholder="e.g. Limited compute, must use public datasets"
                                />
                            </div>

                            {error && <p className="text-sm text-red-500">{error}</p>}

                            <div className="flex gap-3 pt-2">
                                <button
                                    type="button"
                                    onClick={() => setShowModal(false)}
                                    className="flex-1 border rounded-md px-4 py-2 text-sm hover:bg-muted transition-colors"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    disabled={submitting}
                                    className="flex-1 bg-primary text-primary-foreground rounded-md px-4 py-2 text-sm font-medium hover:opacity-90 disabled:opacity-50 flex items-center justify-center gap-2"
                                >
                                    {submitting ? <><Loader2 size={14} className="animate-spin" /> Creating...</> : 'Create Project'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default ProjectsPage;
