import React, { useEffect, useState } from 'react';
import apiClient from '../api/client';
import { Calendar, CheckSquare, Plus, AlertCircle, Clock } from 'lucide-react';

interface Task {
    id: number;
    title: string;
    due_datetime: string;
    severity: number;
    importance: number;
    status: string;
    task_type: string;
}

const TasksPage: React.FC = () => {
    const [tasks, setTasks] = useState<Task[]>([]);
    const [filter, setFilter] = useState('active');

    useEffect(() => {
        fetchTasks();
    }, []);

    const fetchTasks = () => {
        apiClient.get('/tasks/').then(res => setTasks(res.data));
    };

    const handleStatusChange = async (id: number, newStatus: string) => {
        await apiClient.patch(`/tasks/${id}`, { status: newStatus });
        fetchTasks();
    };

    const activeTasks = tasks.filter(t => filter === 'all' || (filter === 'active' && t.status !== 'done'));

    return (
        <div className="flex h-full">
            {/* Sidebar / Filters (Simple Calendar Placeholder) */}
            <div className="w-80 border-r bg-slate-50 p-6 flex flex-col gap-6">
                <div>
                    <h2 className="font-semibold mb-4 flex items-center gap-2"><Calendar size={20} /> Schedule</h2>
                    <div className="bg-white border rounded-lg p-4 text-center text-muted-foreground text-sm shadow-sm">
                        Calendar View Placeholder
                        <br />
                        (Phase 7 Specification)
                    </div>
                </div>

                <div>
                    <h2 className="font-semibold mb-4 flex items-center gap-2"><Clock size={20} /> Upcoming</h2>
                    <ul className="space-y-2 text-sm">
                        <li className="p-2 bg-white border rounded shadow-sm flex justify-between">
                            <span>Paper Submission</span>
                            <span className="text-red-500 font-bold">2d</span>
                        </li>
                    </ul>
                </div>
            </div>

            {/* Main Task List */}
            <div className="flex-1 p-8 overflow-y-auto">
                <div className="flex justify-between items-center mb-8">
                    <div>
                        <h1 className="text-3xl font-bold tracking-tight">Execution</h1>
                        <p className="text-muted-foreground mt-1">Focus on what matters. Severity × Importance.</p>
                    </div>
                    <button className="bg-primary text-primary-foreground px-4 py-2 rounded-md flex items-center gap-2">
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

                <div className="space-y-3">
                    {activeTasks.map(task => (
                        <div key={task.id} className="group flex items-center gap-4 p-4 bg-card border rounded-lg hover:shadow-sm transition-all">
                            <button
                                onClick={() => handleStatusChange(task.id, task.status === 'done' ? 'pending' : 'done')}
                                className={`w-5 h-5 rounded border flex items-center justify-center ${task.status === 'done' ? 'bg-primary border-primary text-white' : 'border-muted-foreground/30 hover:border-primary'}`}
                            >
                                {task.status === 'done' && <CheckSquare size={14} />}
                            </button>

                            <div className="flex-1">
                                <div className="flex items-center gap-2 mb-1">
                                    <span className={`font-medium ${task.status === 'done' ? 'line-through text-muted-foreground' : ''}`}>
                                        {task.title}
                                    </span>
                                    {task.severity >= 4 && <AlertCircle size={14} className="text-red-500" />}
                                </div>
                                <div className="flex gap-3 text-xs text-muted-foreground">
                                    <span className="capitalize bg-muted px-1.5 py-0.5 rounded">{task.task_type}</span>
                                    {task.due_datetime && <span>Due: {new Date(task.due_datetime).toLocaleDateString()}</span>}
                                </div>
                            </div>

                            <div className="text-right">
                                <div className="text-xs font-mono bg-slate-100 px-2 py-1 rounded">
                                    S{task.severity} • I{task.importance}
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
            </div>
        </div>
    );
};

export default TasksPage;
