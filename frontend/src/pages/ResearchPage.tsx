import React, { useState } from 'react';
import { Search } from 'lucide-react';
import GraphView from '../components/GraphView';

const ResearchPage: React.FC = () => {
    const [query, setQuery] = useState('');

    return (
        <div className="h-full flex flex-col">
            <div className="h-16 border-b flex items-center px-8 bg-card gap-4">
                <Search className="text-muted-foreground" />
                <input
                    className="bg-transparent outline-none flex-1 text-lg"
                    placeholder="Search global knowledge (e.g. 'Diffusion Models')..."
                    value={query}
                    onChange={e => setQuery(e.target.value)}
                />
            </div>
            <div className="flex-1 bg-slate-50 relative">
                <GraphView data={{ nodes: [], links: [] }} />
                <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                    <div className="text-center text-muted-foreground opacity-50">
                        <p className="text-xl font-medium">Global Knowledge Graph</p>
                        <p className="text-sm">Start searching to explore concepts</p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ResearchPage;
