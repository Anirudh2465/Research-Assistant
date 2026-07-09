import React, { useEffect, useState } from 'react';
import apiClient from '../api/client';
import { Calendar, CheckSquare, Plus, AlertCircle, Clock, Loader2, X } from 'lucide-react';

interface Task {
    id: number;
    title: string;
    description?: string;
    due_datetime: string | null;
    severity: number;
    importance: number;
    status: string;
    task_type: string;
    linked_project_id?: number | null;
    linked_idea_id?: number | null;
}

const defaultTask = {
    title: '',
    description: '',
    due_datetime: '',
    importance: 3,
    severity: 3,
    task_type: 'generic',
    linked_project_id: null as number | null,
    linked_idea_id: null as number | null,
};

function daysUntil(dateStr: string | null): number | null {
    if (!dateStr) return null;
    const diff = new Date(dateStr).getTime() - Date.now();
    return Math.ceil(diff / (1000 * 60 * 60 * 24));
}

const TasksPage: React.FC = () => {
    const [tasks, setTasks] = useState<Task[]>([]);
    const [filter, setFilter] = useState('active');
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [form, setForm] = useState(defaultTask);
    const [submitting, setSubmitting] = useState(false);
    const [formError, setFormError] = useState('');

    const fetchTasks = () => {
        setLoading(true);
        apiClient.get('/tasks/').then(res => setTasks(res.data)).finally(() => setLoading(false));
    };

    useEffect(() => { fetchTasks(); }, []);

    const handleStatusChange = async (id: number, newStatus: string) => {
        await apiClient.patch(`/tasks/${id}`, { status: newStatus });
        fetchTasks();
    };

    const handleCreate = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!form.title.trim()) { setFormError('Title is required.'); return; }
        if (!form.linked_project_id && !form.linked_idea_id) {
            setFormError('Must be linked to a Project ID or Idea ID.');
            return;
        }
        setSubmitting(true);
        setFormError('');
        try {
            await apiClient.post('/tasks/create', {
                ...form,
                due_datetime: form.due_datetime || null,
                importance: Number(form.importance),
                severity: Number(form.severity),
            });
            setShowModal(false);
            setForm(defaultTask);
            fetchTasks();
        } catch {
            setFormError('Failed to create task.');
        } finally {
            setSubmitting(false);
        }
    };

    const activeTasks = tasks.filter(t =>
        filter === 'all' || (filter === 'active' && t.status !== 'done')
    );

    // Fix #24: Compute upcoming tasks from real data (due within 7 days, not done)
    const upcomingTasks = tasks
        .filter(t => t.status !== 'done' && t.due_datetime !== null)
        .map(t => ({ ...t, daysLeft: daysUntil(t.due_datetime) }))
        .filter(t => t.daysLeft !== null && t.daysLeft <= 7)
        .sort((a, b) => (a.daysLeft ?? 0) - (b.daysLeft ?? 0))
        .slice(0, 5);

    return (
        <div className="flex h-full">
            {/* Sidebar */}
            <div className="w-80 border-r bg-slate-50 p-6 flex flex-col gap-6">
                <div>
                    <h2 className="font-semibold mb-4 flex items-center gap-2"><Calendar size={20} /> Schedule</h2>
                    <div className="bg-white border rounded-lg p-4 text-center text-muted-foreground text-sm shadow-sm">
                        Calendar View
                        <br />
                        <span className="text-xs">(Coming Soon)</span>
                    </div>
                </div>

                <div>
                    {/* Fix #24: Upcoming tasks from real API data */}
                    <h2 className="font-semibold mb-4 flex items-center gap-2"><Clock size={20} /> Upcoming (7 days)</h2>
                    {upcomingTasks.length === 0 ? (
                        <p className="text-sm text-muted-foreground">No upcoming deadlines.</p>
                    ) : (
                        <ul className="space-y-2 text-sm">
                            {upcomingTasks.map(task => (
                                <li key={task.id} className="p-2 bg-white border rounded shadow-sm flex justify-between items-center">
                                    <span className="line-clamp-1 flex-1">{task.title}</span>
                                    <span className={`ml-2 font-bold shrink-0 ${(task.daysLeft ?? 99) <= 2 ? 'text-red-500' : 'text-amber-500'}`}>
                                        {task.daysLeft === 0 ? 'Today' : `${task.daysLeft}d`}
                                    </span>
                                </li>
                            ))}
                        </ul>
                    )}
                </div>
            </div>

            {/* Main Task List */}
            <div className="flex-1 p-8 overflow-y-auto">
                <div className="flex justify-between items-center mb-8">
                    <div>
                        <h1 className="text-3xl font-bold tracking-tight">Execution</h1>
                        <p className="text-muted-foreground mt-1">Focus on what matters. Severity × Importance.</p>
                    </div>
                    <button
                        onClick={() => { setShowModal(true); setFormError(''); }}
                        className="bg-primary text-primary-foreground px-4 py-2 rounded-md flex items-center gap-2 hover:opacity-90 transition-opacity"
                    >
                        <Plus size={18} /> New Task
                    </button>
                </div>

                <div className="flex gap-4 mb-6 border-b pb-1">
                    <button
                        onClick={() => setFilter('active')}
                        className={`pb-2 px-1 ${filter === 'active' ? 'border-b-2 border-primary text-primary font-medium' : 'text-muted-foreground'}`}
                    >
                        Active
                    </button>
                    <button
                        onClick={() => setFilter('all')}
                        className={`pb-2 px-1 ${filter === 'all' ? 'border-b-2 border-primary text-primary font-medium' : 'text-muted-foreground'}`}
                    >
                        All History
                    </button>
                </div>

                {loading ? (
                    <div className="flex justify-center py-20"><Loader2 className="animate-spin text-primary" /></div>
                ) : (
                    <div className="space-y-3">
                        {activeTasks.map(task => (
                            <div key={task.id} className="group flex items-center gap-4 p-4 bg-card border rounded-lg hover:shadow-sm transition-all">
                                <button
                                    onClick={() => handleStatusChange(task.id, task.status === 'done' ? 'pending' : 'done')}
                                    className={`w-5 h-5 rounded border flex items-center justify-center shrink-0 ${task.status === 'done' ? 'bg-primary border-primary text-white' : 'border-muted-foreground/30 hover:border-primary'}`}
                                >
                                    {task.status === 'done' && <CheckSquare size={14} />}
                                </button>

                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2 mb-1">
                                        <span className={`font-medium ${task.status === 'done' ? 'line-through text-muted-foreground' : ''}`}>
                                            {task.title}
                                        </span>
                                        {task.severity >= 4 && <AlertCircle size={14} className="text-red-500 shrink-0" />}
                                    </div>
                                    <div className="flex gap-3 text-xs text-muted-foreground">
                                        <span className="capitalize bg-muted px-1.5 py-0.5 rounded">{task.task_type}</span>
                                        {task.due_datetime && <span>Due: {new Date(task.due_datetime).toLocaleDateString()}</span>}
                                    </div>
                                </div>

                                <div className="text-right shrink-0">
                                    <div className="text-xs font-mono bg-slate-100 px-2 py-1 rounded">
                                        S{task.severity} · I{task.importance}
                                    </div>
                                </div>
                            </div>
                        ))}

                        {activeTasks.length === 0 && (
                            <div className="text-center py-20 text-muted-foreground border-2 border-dashed rounded-xl">
                                No active tasks. You are free!
                            </div>
                        )}
                    </div>
                )}
            </div>

            {/* New Task Modal */}
            {showModal && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                    <div className="bg-card border rounded-xl shadow-2xl w-full max-w-md">
                        <div className="flex items-center justify-between p-6 border-b">
                            <h2 className="text-xl font-semibold">New Task</h2>
                            <button onClick={() => setShowModal(false)} className="text-muted-foreground hover:text-foreground">
                                <X size={20} />
                            </button>
                        </div>
                        <form onSubmit={handleCreate} className="p-6 space-y-4">
                            <div>
                                <label className="block text-sm font-medium mb-1">Title *</label>
                                <input
                                    className="w-full border rounded-md px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-primary/30"
                                    value={form.title}
                                    onChange={e => setForm(f => ({ ...f, title: e.target.value }))}
                                    placeholder="e.g. Read attention mechanism paper"
                                />
                            </div>
                            <div className="grid grid-cols-2 gap-3">
                                <div>
                                    <label className="block text-sm font-medium mb-1">Severity (1–5)</label>
                                    <input type="number" min={1} max={5}
                                        className="w-full border rounded-md px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-primary/30"
                                        value={form.severity}
                                        onChange={e => setForm(f => ({ ...f, severity: Number(e.target.value) }))}
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium mb-1">Importance (1–5)</label>
                                    <input type="number" min={1} max={5}
                                        className="w-full border rounded-md px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-primary/30"
                                        value={form.importance}
                                        onChange={e => setForm(f => ({ ...f, importance: Number(e.target.value) }))}
                                    />
                                </div>
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-1">Due Date</label>
                                <input type="datetime-local"
                                    className="w-full border rounded-md px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-primary/30"
                                    value={form.due_datetime}
                                    onChange={e => setForm(f => ({ ...f, due_datetime: e.target.value }))}
                                />
                            </div>
                            <div className="grid grid-cols-2 gap-3">
                                <div>
                                    <label className="block text-sm font-medium mb-1">Project ID</label>
                                    <input type="number"
                                        className="w-full border rounded-md px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-primary/30"
                                        value={form.linked_project_id ?? ''}
                                        onChange={e => setForm(f => ({ ...f, linked_project_id: e.target.value ? Number(e.target.value) : null }))}
                                        placeholder="optional"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium mb-1">Idea ID</label>
                                    <input type="number"
                                        className="w-full border rounded-md px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-primary/30"
                                        value={form.linked_idea_id ?? ''}
                                        onChange={e => setForm(f => ({ ...f, linked_idea_id: e.target.value ? Number(e.target.value) : null }))}
                                        placeholder="optional"
                                    />
                                </div>
                            </div>
                            {formError && <p className="text-sm text-red-500">{formError}</p>}
                            <div className="flex gap-3 pt-2">
                                <button type="button" onClick={() => setShowModal(false)}
                                    className="flex-1 border rounded-md px-4 py-2 text-sm hover:bg-muted transition-colors">
                                    Cancel
                                </button>
                                <button type="submit" disabled={submitting}
                                    className="flex-1 bg-primary text-primary-foreground rounded-md px-4 py-2 text-sm font-medium hover:opacity-90 disabled:opacity-50 flex items-center justify-center gap-2">
                                    {submitting ? <><Loader2 size={14} className="animate-spin" /> Creating...</> : 'Create Task'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default TasksPage;
