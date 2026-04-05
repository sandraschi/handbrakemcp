import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ExternalLink, Play, Loader2, AlertCircle } from 'lucide-react';
import { FleetMember } from './apps-catalog';
import { cn } from '@/common/utils';

interface FleetCardProps {
    member: FleetMember;
    currentAppId?: string;
}

export function FleetCard({ member, currentAppId }: FleetCardProps) {
    const isCurrent = member.id === currentAppId;
    const [status, setStatus] = useState<'checking' | 'online' | 'offline'>('checking');
    const [isLaunching, setIsLaunching] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const checkStatus = async () => {
        try {
            const controller = new AbortController();
            const id = setTimeout(() => controller.abort(), 2000);
            const resp = await fetch(`http://localhost:${member.port}/health`, { signal: controller.signal });
            clearTimeout(id);
            setStatus(resp.ok ? 'online' : 'offline');
        } catch {
            setStatus('offline');
        }
    };

    useEffect(() => {
        checkStatus();
        const interval = setInterval(checkStatus, 10000);
        return () => clearInterval(interval);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const launchApp = async () => {
        setIsLaunching(true);
        setError(null);
        try {
            const resp = await fetch('/api/fleet/launch', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ repo_path: member.repo_path })
            });

            const data = await resp.json();
            if (!data.success) throw new Error(data.error);

            // Poll for online status
            let attempts = 0;
            const poll = setInterval(async () => {
                attempts++;
                try {
                    const check = await fetch(`http://localhost:${member.port}/health`);
                    if (check.ok) {
                        clearInterval(poll);
                        setIsLaunching(false);
                        setStatus('online');
                        window.location.href = `http://localhost:${member.port}`;
                    }
                } catch {
                    if (attempts > 30) {
                        clearInterval(poll);
                        setIsLaunching(false);
                        setError("Launch timed out. Start manually.");
                    }
                }
            }, 1000);

        } catch (e: any) {
            setError(e.message);
            setIsLaunching(false);
        }
    };

    return (
        <motion.div
            layout
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className={cn(
                "group relative overflow-hidden rounded-xl border p-5 transition-all duration-300",
                isCurrent
                    ? "border-blue-500/50 bg-blue-500/5 shadow-[0_0_20px_rgba(59,130,246,0.1)]"
                    : "border-slate-800 bg-slate-900/40 hover:border-slate-700 hover:bg-slate-900/60"
            )}
        >
            <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                    <div className={cn(
                        "flex h-10 w-10 items-center justify-center rounded-lg",
                        isCurrent ? "bg-blue-500/20 text-blue-400" : "bg-slate-800 text-slate-400 group-hover:text-slate-200"
                    )}>
                        <member.icon className="h-5 w-5" />
                    </div>
                    <div>
                        <h3 className="font-semibold text-slate-100">{member.name}</h3>
                        <p className="text-xs text-slate-500">{member.category}</p>
                    </div>
                </div>

                <div className="flex items-center gap-1.5">
                    <div className={cn(
                        "h-2 w-2 rounded-full",
                        status === 'online' ? "bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]" :
                            status === 'offline' ? "bg-slate-700" : "bg-blue-500 animate-pulse"
                    )} />
                    <span className="text-[10px] font-medium uppercase tracking-wider text-slate-500">
                        {status}
                    </span>
                </div>
            </div>

            <p className="mt-4 text-xs leading-relaxed text-slate-400 line-clamp-2">
                {member.description}
            </p>

            <div className="mt-6 flex gap-2">
                {status === 'online' ? (
                    <a
                        href={`http://localhost:${member.port}`}
                        className="flex flex-1 items-center justify-center gap-2 rounded-lg bg-slate-800 py-2 text-xs font-medium text-slate-200 transition-colors hover:bg-slate-700 active:scale-95"
                    >
                        <ExternalLink className="h-3.5 w-3.5" />
                        Enter Dashboard
                    </a>
                ) : (
                    <button
                        onClick={launchApp}
                        disabled={isLaunching || isCurrent}
                        className={cn(
                            "flex flex-1 items-center justify-center gap-2 rounded-lg py-2 text-xs font-medium transition-all active:scale-95",
                            isLaunching
                                ? "bg-blue-500/20 text-blue-400 cursor-not-allowed"
                                : "bg-blue-600 text-white hover:bg-blue-500 hover:shadow-[0_0_15px_rgba(59,130,246,0.3)] disabled:opacity-50 disabled:cursor-not-allowed"
                        )}
                    >
                        {isLaunching ? (
                            <>
                                <Loader2 className="h-3.5 w-3.5 animate-spin" />
                                Launching...
                            </>
                        ) : (
                            <>
                                <Play className="h-3.5 w-3.5" />
                                Start Service
                            </>
                        )}
                    </button>
                )}
            </div>

            <AnimatePresence>
                {error && (
                    <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="mt-3 flex items-center gap-2 text-[10px] text-red-400"
                    >
                        <AlertCircle className="h-3 w-3" />
                        {error}
                    </motion.div>
                )}
            </AnimatePresence>

            {isCurrent && (
                <div className="absolute top-2 right-2">
                    <span className="flex items-center gap-1 rounded-full bg-blue-500/10 px-2 py-0.5 text-[9px] font-bold uppercase text-blue-400 border border-blue-500/20">
                        Current
                    </span>
                </div>
            )}
        </motion.div>
    );
}
