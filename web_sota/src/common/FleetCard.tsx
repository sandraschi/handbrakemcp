import { useState, useEffect } from 'react';
import { ExternalLink, Play, Loader2, AlertCircle } from 'lucide-react';
import { FleetMember } from './apps-catalog';
import { cn } from '@/common/utils';

interface FleetCardProps {
    member: FleetMember;
    currentAppId?: string;
}

/**
 * HandBrake Fleet Card
 * Industrial-grade service tile. Refactored for maximum stability by removing
 * external heavy animation dependencies while retaining premium hover logic.
 */
export function FleetCard({ member, currentAppId }: FleetCardProps) {
    const isCurrent = member.id === currentAppId;
    const [status, setStatus] = useState<'checking' | 'online' | 'offline'>('checking');
    const [isLaunching, setIsLaunching] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const checkStatus = async () => {
        try {
            const controller = new AbortController();
            const id = setTimeout(() => controller.abort(), 2000);
            const resp = await fetch(`http://127.0.0.1:${member.port}/health`, { signal: controller.signal });
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
                    const check = await fetch(`http://127.0.0.1:${member.port}/health`);
                    if (check.ok) {
                        clearInterval(poll);
                        setIsLaunching(false);
                        setStatus('online');
                        window.location.href = `http://127.0.0.1:${member.port}`;
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
        <div
            className={cn(
                "group relative overflow-hidden rounded-xl border p-5 transition-all duration-300",
                isCurrent
                    ? "border-emerald-500/50 bg-emerald-500/5 shadow-[0_0_20px_rgba(16,185,129,0.1)]"
                    : "border-slate-800 bg-slate-900/40 hover:border-slate-700 hover:bg-slate-900/60"
            )}
        >
            <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                    <div className={cn(
                        "flex h-10 w-10 items-center justify-center rounded-lg",
                        isCurrent ? "bg-emerald-500/20 text-emerald-400" : "bg-slate-800 text-slate-400 group-hover:text-slate-200"
                    )}>
                        <member.icon className="h-5 w-5" />
                    </div>
                    <div>
                        <h3 className="font-bold text-slate-100 uppercase tracking-tight text-sm">{member.name}</h3>
                        <p className="text-[10px] text-slate-500 font-black uppercase tracking-widest">{member.category}</p>
                    </div>
                </div>

                <div className="flex items-center gap-1.5">
                    <div className={cn(
                        "h-2 w-2 rounded-full",
                        status === 'online' ? "bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]" :
                            status === 'offline' ? "bg-slate-700" : "bg-blue-500 animate-pulse"
                    )} />
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
                        {status}
                    </span>
                </div>
            </div>

            <p className="mt-4 text-xs font-medium leading-relaxed text-slate-400 line-clamp-2">
                {member.description}
            </p>

            <div className="mt-6 flex gap-2">
                {status === 'online' ? (
                    <a
                        href={`http://127.0.0.1:${member.port}`}
                        className="flex flex-1 items-center justify-center gap-2 rounded-lg bg-slate-800 py-2.5 text-xs font-black uppercase tracking-widest text-slate-200 transition-all hover:bg-slate-700 active:scale-95 border border-slate-700"
                    >
                        <ExternalLink className="h-3.5 w-3.5" />
                        Access Node
                    </a>
                ) : (
                    <button
                        onClick={launchApp}
                        disabled={isLaunching || isCurrent}
                        className={cn(
                            "flex flex-1 items-center justify-center gap-2 rounded-lg py-2.5 text-xs font-black uppercase tracking-widest transition-all active:scale-95",
                            isLaunching
                                ? "bg-emerald-500/20 text-emerald-400 cursor-not-allowed border border-emerald-500/20"
                                : "bg-emerald-600 text-white hover:bg-emerald-500 hover:shadow-[0_0_15px_rgba(16,185,129,0.3)] disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
                        )}
                    >
                        {isLaunching ? (
                            <>
                                <Loader2 className="h-3.5 w-3.5 animate-spin" />
                                Synchronizing...
                            </>
                        ) : (
                            <>
                                <Play className="h-3.5 w-3.5 fill-current" />
                                Launch Sequence
                            </>
                        )}
                    </button>
                )}
            </div>

            {error && (
                <div className="mt-3 flex items-center gap-2 text-[10px] font-bold text-red-400 animate-in slide-in-from-top-1 duration-300">
                    <AlertCircle className="h-3 w-3" />
                    {error}
                </div>
            )}

            {isCurrent && (
                <div className="absolute top-2 right-2">
                    <span className="flex items-center gap-1 rounded-full bg-emerald-500/10 px-2.5 py-1 text-[9px] font-black uppercase tracking-tighter text-emerald-400 border border-emerald-500/20">
                        CORE NODE
                    </span>
                </div>
            )}
        </div>
    );
}
