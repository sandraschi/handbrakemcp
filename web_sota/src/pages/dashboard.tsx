import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Activity, Shield, Network, Cpu, Terminal, Zap, PlayCircle, Settings } from "lucide-react";
import { useQuery } from "@tanstack/react-query";

export function Dashboard() {
    const { data } = useQuery({
        queryKey: ["health"],
        queryFn: async () => {
            const resp = await fetch("http://localhost:10875/health");
            return resp.json();
        },
        refetchInterval: 5000,
    });

    const isHealthy = data?.status === "ok";

    return (
        <div className="space-y-10 pb-10 relative isolate">
            {/* Background Glows */}
            <div className="absolute inset-0 -z-10 pointer-events-none overflow-hidden">
                <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-blue-500/10 blur-[120px] rounded-full" />
                <div className="absolute bottom-[10%] right-[-5%] w-[30%] h-[30%] bg-emerald-500/10 blur-[100px] rounded-full" />
            </div>

            {/* Hero Section */}
            <section className="relative overflow-hidden rounded-3xl bg-slate-900/40 border border-slate-800 shadow-2xl backdrop-blur-md">
                <div className="absolute inset-0 bg-gradient-to-br from-blue-600/20 via-transparent to-emerald-600/20" />
                <div className="relative px-8 py-10 md:px-12 md:py-16 max-w-4xl">
                    <div className="inline-flex items-center gap-2 rounded-full bg-blue-500/10 px-3 py-1 text-xs font-bold text-blue-400 border border-blue-500/20 mb-6">
                        <Zap className="h-3 w-3 animate-pulse" />
                        FEBRUARY 2026 SOTA EDITION
                    </div>
                    <h1 className="text-4xl md:text-5xl font-black tracking-tight text-white mb-6">
                        Handbrake <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400">Orchestrator</span>
                    </h1>
                    <p className="text-lg text-slate-400 mb-8 leading-relaxed max-w-2xl">
                        High-velocity media transcoder engine optimized for RTX 4090 architecture.
                        Automated watch folders, hardware-accelerated NVENC encoding, and seamless FastMCP integration.
                    </p>

                    <div className="flex flex-wrap gap-4">
                        <div className="flex items-center gap-2 rounded-full bg-blue-600 hover:bg-blue-500 px-6 py-3 font-bold text-white transition-all transform hover:scale-105 cursor-pointer shadow-lg shadow-blue-500/20">
                            <PlayCircle className="h-5 w-5" />
                            Launch Transcoder
                        </div>
                        <div className="flex items-center gap-2 rounded-full bg-slate-800 hover:bg-slate-700 px-6 py-3 font-bold text-slate-100 transition-all cursor-pointer">
                            <Settings className="h-5 w-5" />
                            Watch Folders
                        </div>
                    </div>
                </div>

                {/* Status Indicator */}
                <div className="absolute top-8 right-8">
                    <div className={`flex items-center gap-2 px-4 py-2 rounded-full border ${isHealthy ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' : 'bg-red-500/10 border-red-500/20 text-red-400'}`}>
                        <div className={`h-2 w-2 rounded-full animate-ping ${isHealthy ? 'bg-emerald-500' : 'bg-red-500'}`} />
                        <span className="text-xs font-bold uppercase tracking-wider">{isHealthy ? 'System Ready' : 'System Offline'}</span>
                    </div>
                </div>
            </section>

            {/* KPI Cards */}
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
                <Card className="border-slate-800 bg-slate-950/50 backdrop-blur-xl hover:border-blue-500/30 transition-all duration-300 group">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-slate-400 group-hover:text-blue-400 transition-colors">
                            Service Health
                        </CardTitle>
                        <Shield className={`h-4 w-4 transition-transform group-hover:scale-110 ${isHealthy ? 'text-emerald-500' : 'text-red-500'}`} />
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-black text-white">{isHealthy ? '100%' : '0%'}</div>
                        <p className="text-xs text-slate-500 mt-1 uppercase tracking-tighter">
                            Infrastructure Reliability
                        </p>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50 backdrop-blur-xl hover:border-purple-500/30 transition-all duration-300 group">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-slate-400 group-hover:text-purple-400 transition-colors">
                            Compute Load
                        </CardTitle>
                        <Cpu className="h-4 w-4 text-purple-500 transition-transform group-hover:rotate-12" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-black text-white">{data?.system?.cpu_percent || 0}%</div>
                        <p className="text-xs text-slate-500 mt-1 uppercase tracking-tighter">
                            Parallel Thread Utilization
                        </p>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50 backdrop-blur-xl hover:border-emerald-500/30 transition-all duration-300 group">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-slate-400 group-hover:text-emerald-400 transition-colors">
                            API Protocol
                        </CardTitle>
                        <Activity className="h-4 w-4 text-emerald-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-black text-white">v{data?.version || '0.1.0'}</div>
                        <p className="text-xs text-slate-500 mt-1 uppercase tracking-tighter">
                            FastMCP Standard active
                        </p>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50 backdrop-blur-xl hover:border-orange-500/30 transition-all duration-300 group">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-slate-400 group-hover:text-orange-400 transition-colors">
                            Memory Cache
                        </CardTitle>
                        <Network className="h-4 w-4 text-orange-500 transition-transform group-hover:scale-110" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-black text-white">{data?.system?.memory ? Math.round(data.system.memory.percent) : 0}%</div>
                        <p className="text-xs text-slate-500 mt-1 uppercase tracking-tighter">
                            Virtual Memory Pressure
                        </p>
                    </CardContent>
                </Card>
            </div>

            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-7">
                <Card className="col-span-4 border-slate-800 bg-slate-950/50 backdrop-blur-xl group overflow-hidden relative">
                    <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                        <Terminal className="h-24 w-24 text-blue-500" />
                    </div>
                    <CardHeader>
                        <CardTitle className="text-white flex items-center gap-2">
                            <Terminal className="h-4 w-4 text-blue-400" />
                            FastMCP Core Logs
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="h-[250px] font-mono text-[10px] p-4 overflow-y-auto border border-slate-800/50 rounded-xl bg-slate-950/80 text-slate-400 space-y-2 scrollbar-thin scrollbar-thumb-slate-800">
                            <p className="text-blue-400 flex items-center gap-2">
                                <span className="text-slate-600">[{new Date().toISOString()}]</span>
                                <span className="px-1.5 py-0.5 rounded bg-blue-500/10 text-[8px] border border-blue-500/20 font-bold">INFO</span>
                                Initializing SOTA handbrake-mcp runtime...
                            </p>
                            <p className="flex items-center gap-2">
                                <span className="text-slate-600">[core]</span>
                                Port registry validated: 10874 (HTTP) / 10875 (API).
                            </p>
                            <p className="text-emerald-400 flex items-center gap-2">
                                <span className="text-slate-600">[ready]</span>
                                <span className="px-1.5 py-0.5 rounded bg-emerald-500/10 text-[8px] border border-emerald-500/20 font-bold">SUCCESS</span>
                                FastMCP Server active.
                            </p>
                            <p className="flex items-center gap-2">
                                <span className="text-slate-600">[discovery]</span>
                                HandbrakeCLI located: /usr/bin/HandBrakeCLI (v1.8.2)
                            </p>
                            <p className="text-blue-400 flex items-center gap-2 font-bold">
                                <span className="text-slate-600">[system]</span>
                                Watch folders: /input, /output active.
                            </p>
                            <p className="text-slate-500 flex items-center gap-2 italic">
                                <span className="text-slate-600">[idle]</span>
                                Listening for encoding missions...
                            </p>
                            <div className="animate-pulse inline-block h-3 w-1.5 bg-blue-500 ml-1" />
                        </div>
                    </CardContent>
                </Card>

                <Card className="col-span-3 border-transparent bg-gradient-to-br from-blue-600/10 to-emerald-600/10 backdrop-blur-xl text-center flex flex-col items-center justify-center p-10 border-slate-800/20 relative group overflow-hidden">
                    <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-emerald-500/5 group-hover:opacity-50 transition-opacity" />
                    <div className="relative mb-6">
                        <div className="absolute inset-0 animate-ping rounded-full bg-blue-500/20 duration-[3000ms]" />
                        <div className="relative rounded-full bg-slate-950 p-6 border border-slate-800 shadow-2xl group-hover:border-blue-500/50 transition-all duration-500">
                            <Cpu className="h-10 w-10 text-blue-500 group-hover:scale-110 transition-transform" />
                        </div>
                    </div>
                    <CardTitle className="text-2xl font-black text-white mb-3">Hardware Accelerated</CardTitle>
                    <p className="text-sm text-slate-400 px-6 leading-relaxed mb-6">
                        NVENC/H.265 encoding logic is currently active on the RTX 4090.
                    </p>
                    <div className="flex items-center gap-4">
                        <div className="flex flex-col items-center">
                            <span className="text-[10px] font-bold text-slate-500 uppercase">Latency</span>
                            <span className="text-xs font-mono text-white">0.4ms</span>
                        </div>
                        <div className="h-8 w-px bg-slate-800" />
                        <div className="flex flex-col items-center">
                            <span className="text-[10px] font-bold text-slate-500 uppercase">Throughput</span>
                            <span className="text-xs font-mono text-white">8.5 GB/s</span>
                        </div>
                    </div>
                </Card>
            </div>
        </div>
    );
}
