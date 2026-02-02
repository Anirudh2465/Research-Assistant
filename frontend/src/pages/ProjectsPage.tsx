import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import apiClient from '../api/client';
import { Plus, ArrowRight, Loader2 } from 'lucide-react';

interface Project {
    id: number;
    name: string;
    domain: string;
    status: string;
    problem_statement: string;
}

const ProjectsPage: React.FC = () => {
    const [projects, setProjects] = useState<Project[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        apiClient.get('/projects/')
            .then(res => setProjects(res.data))
            .catch(err => console.error(err))
            .finally(() => setLoading(false));
    }, []);

    if (loading) return <div className="flex items-center justify-center h-full"><Loader2 className="animate-spin" /></div>;

    return (
        <div className="p-8 max-w-7xl mx-auto w-full">
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Projects</h1>
                    <p className="text-muted-foreground mt-1">Manage your active research contexts.</p>
                </div>
                <button className="bg-primary text-primary-foreground px-4 py-2 rounded-md flex items-center gap-2 hover:opacity-90">
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
                            <span className={`text-xs px-2 py-1 rounded-full ${project.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
                                }`}>
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
                        No projects found. Create one to get started.
                    </div>
                )}
            </div>
        </div>
    );
};

export default ProjectsPage;
