import { useState, useEffect } from 'react';
import { Terminal, Activity, Wifi, WifiOff, ChevronUp, ChevronDown } from 'lucide-react';

export function LoggerPanel() {
    const [expanded, setExpanded] = useState(false);
    const [status, setStatus] = useState<'online' | 'offline' | 'loading'>('loading');
    const [logs, setLogs] = useState<{ id: string; time: string; msg: string; type: 'info' | 'warn' | 'error' }[]>([]);

    useEffect(() => {
        const addLog = (msg: string, type: 'info' | 'warn' | 'error' = 'info') => {
            const time = new Date().toLocaleTimeString();
            setLogs(prev => [
                { id: Math.random().toString(36).substr(2, 9), time, msg, type },
                ...prev.slice(0, 49)
            ]);
        };

        const checkStatus = async () => {
            try {
                const res = await fetch('http://127.0.0.1:10875/health');
                if (res.ok) {
                    setStatus('online');
                    addLog('Backend connected successfully', 'info');
                } else {
                    setStatus('offline');
                }
            } catch (error) {
                setStatus('offline');
            }
        };

        checkStatus();
        const interval = setInterval(checkStatus, 5000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div 
            className={`fixed bottom-0 right-0 left-0 z-50 transition-all duration-300 ease-in-out border-t border-emerald-500/20 bg-slate-900/90 backdrop-blur-md ${
                expanded ? 'h-64' : 'h-10'
            }`}
        >
            {/* Header / Trigger */}
            <div 
                className="flex h-10 cursor-pointer items-center justify-between px-4"
                onClick={() => setExpanded(!expanded)}
            >
                <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2">
                        {status === 'online' ? (
                            <Wifi className="h-4 w-4 text-emerald-400" />
                        ) : status === 'offline' ? (
                            <WifiOff className="h-4 w-4 text-rose-400" />
                        ) : (
                            <Activity className="h-4 w-4 animate-pulse text-amber-400" />
                        )}
                        <span className={`text-xs font-bold uppercase tracking-widest ${
                            status === 'online' ? 'text-emerald-400' : 
                            status === 'offline' ? 'text-rose-400' : 'text-amber-400'
                        }`}>
                            Backend: {status}
                        </span>
                    </div>
                    {logs.length > 0 && !expanded && (
                        <div className="hidden items-center gap-2 text-[10px] text-slate-400 md:flex">
                            <span className="opacity-50">[{logs[0].time}]</span>
                            <span className="truncate max-w-[400px]">{logs[0].msg}</span>
                        </div>
                    )}
                </div>
                
                <div className="flex items-center gap-2">
                    <Terminal className="h-3 w-3 text-slate-500" />
                    {expanded ? <ChevronDown className="h-4 w-4 text-slate-500" /> : <ChevronUp className="h-4 w-4 text-slate-500" />}
                </div>
            </div>

            {/* Content */}
            {expanded && (
                <div className="h-54 overflow-y-auto p-4 font-mono text-[11px] leading-relaxed selection:bg-emerald-500/30">
                    {logs.length === 0 ? (
                        <div className="flex h-full items-center justify-center text-slate-500 italic">
                            No active logs detected in current vault.
                        </div>
                    ) : (
                        <div className="space-y-1">
                            {logs.map(log => (
                                <div key={log.id} className="group flex items-start gap-4">
                                    <span className="shrink-0 text-slate-600">[{log.time}]</span>
                                    <span className={`shrink-0 font-bold uppercase ${
                                        log.type === 'error' ? 'text-rose-400' : 
                                        log.type === 'warn' ? 'text-amber-400' : 'text-emerald-400'
                                    }`}>
                                        {log.type}
                                    </span>
                                    <span className="text-slate-300 group-hover:text-white">{log.msg}</span>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
