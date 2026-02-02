import { useEffect } from 'react';

export const useResizeObserver = (ref: React.RefObject<HTMLElement>, callback: (entry: ResizeObserverEntry) => void) => {
    useEffect(() => {
        if (!ref.current) return;
        const observer = new ResizeObserver((entries) => {
            entries.forEach(callback);
        });
        observer.observe(ref.current);
        return () => observer.disconnect();
    }, [ref, callback]);
};
