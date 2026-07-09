import React from 'react';
import { Link, Outlet, useLocation } from 'react-router-dom';
import { LayoutGrid, Lightbulb, Network, ListTodo } from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: (string | undefined | null | false)[]) {
    return twMerge(clsx(inputs));
}

const Layout: React.FC = () => {
    const location = useLocation();

    const navItems = [
        { name: 'Projects', path: '/projects', icon: LayoutGrid },
        { name: 'Ideas', path: '/ideas', icon: Lightbulb },
        { name: 'Research', path: '/research', icon: Network },
        { name: 'Tasks', path: '/tasks', icon: ListTodo },
    ];

    return (
        <div className="min-h-screen bg-background text-foreground flex flex-col">
            {/* Navbar */}
            <nav className="border-b h-14 flex items-center px-6 bg-card sticky top-0 z-10">
                <div className="text-xl font-bold mr-8 text-primary">Research OS</div>
                <div className="flex gap-1">
                    {navItems.map((item) => {
                        const isActive = location.pathname.startsWith(item.path);
                        return (
                            <Link
                                key={item.path}
                                to={item.path}
                                className={cn(
                                    "flex items-center gap-2 px-4 py-2 rounded-md transition-colors text-sm font-medium",
                                    isActive
                                        ? "bg-primary/10 text-primary"
                                        : "text-muted-foreground hover:bg-muted hover:text-foreground"
                                )}
                            >
                                <item.icon size={18} />
                                {item.name}
                            </Link>
                        );
                    })}
                </div>
            </nav>

            {/* Main Content */}
            <main className="flex-1 overflow-hidden flex flex-col">
                <Outlet />
            </main>
        </div>
    );
};

export default Layout;
