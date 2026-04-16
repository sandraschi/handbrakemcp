import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Activity, Shield, HardDrive, Cpu, Zap, PlayCircle } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { cn } from "@/common/utils";

/**
 * HandBrake MCP Industrial Dashboard (v13.1)
 * Optimized for stability following the OSC MCP 'Gold Standard' pattern.
 * Provides a high-fidelity control plane overview for transcoding operations.
 */
export function Dashboard() {
    const { data: healthData } = useQuery({
        queryKey: ["health"],
        queryFn: async () => {
            const resp = await fetch("http://127.0.0.1:10875/health");
            return resp.json();
        },
        refetchInterval: 5000,
    });

    const { data: jobsData } = useQuery({
        queryKey: ["jobs"],
        queryFn: async () => {
            const resp = await fetch("http://127.0.0.1:10875/api/jobs");
            return resp.json();
        },
        refetchInterval: 2000,
    });

    const system = healthData?.system || {};
    const jobs = Array.isArray(jobsData?.jobs) ? jobsData.jobs : [];
    const activeJobs = jobs.filter((j: any) => j && j.status === 'processing');
    const completedJobsCount = jobs.filter((j: any) => j && j.status === 'completed').length;
    return (
        <div className="space-y-6 animate-in fade-in duration-700">
            {/* Header Section */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight text-white uppercase italic">
                        HB <span className="text-emerald-500">Orchestration</span>
                    </h2>
                    <p className="text-slate-400 text-xs font-bold uppercase tracking-widest mt-1">Real-time media ingestion and telemetry</p>
                </div>
            </div>

            {/* Fleet-Standard KPI Grid */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <Card className="border-slate-800 bg-slate-950/50 backdrop-blur-sm">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-xs font-black uppercase tracking-widest text-slate-200">
                            Active Encoders
                        </CardTitle>
                        <Cpu className="h-4 w-4 text-emerald-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-white">{activeJobs.length}</div>
                        <p className="text-[10px] font-medium text-slate-500 uppercase mt-1">
                            {system.gpu?.model || "Detecting Hardware..."}
                        </p>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50 backdrop-blur-sm">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-xs font-black uppercase tracking-widest text-slate-200">
                            Jobs Completed
                        </CardTitle>
                        <Activity className="h-4 w-4 text-blue-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-white">{completedJobsCount}</div>
                        <p className="text-[10px] font-medium text-slate-500 uppercase mt-1">
                            Current session throughput
                        </p>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50 backdrop-blur-sm">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-xs font-black uppercase tracking-widest text-slate-200">
                            Storage Vault
                        </CardTitle>
                        <HardDrive className="h-4 w-4 text-purple-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-white">82%</div>
                        <p className="text-[10px] font-medium text-slate-500 uppercase mt-1">
                            ZFS Pool: alsergrund-01
                        </p>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50 backdrop-blur-sm">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-xs font-black uppercase tracking-widest text-slate-200">
                            System Status
                        </CardTitle>
                        <Zap className="h-4 w-4 text-amber-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-white">{healthData?.status === 'ok' ? "ONLINE" : "OFFLINE"}</div>
                        <p className="text-[10px] font-medium text-slate-500 uppercase mt-1">
                            FastMCP 3.2.0 Active
                        </p>
                    </CardContent>
                </Card>
            </div>

            {/* Industrial Event Stream */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
                <Card className="col-span-4 border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <CardTitle className="text-white text-sm font-black uppercase tracking-widest flex items-center gap-2">
                            <Shield className="h-4 w-4 text-blue-500" />
                            Ingestion Pipeline
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="h-[200px] flex items-center justify-center border border-dashed border-slate-800 rounded-md bg-slate-900/20 font-mono text-xs text-slate-500">
                            Awaiting real-time task telemetry...
                        </div>
                    </CardContent>
                </Card>
                
                <Card className="col-span-3 border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <CardTitle className="text-white text-sm font-black uppercase tracking-widest flex items-center gap-2">
                            <PlayCircle className="h-4 w-4 text-emerald-500" />
                            Active Job Stream
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            {jobs.slice(0, 5).map((job: any) => (
                                <div key={job.job_id || Math.random()} className="flex items-center">
                                    <span className="relative flex h-2 w-2 mr-2">
                                        {job.status === 'processing' && <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>}
                                        <span className={cn(
                                            "relative inline-flex rounded-full h-2 w-2",
                                            job.status === 'processing' ? "bg-emerald-500" :
                                            job.status === 'completed' ? "bg-blue-500" : "bg-slate-700"
                                        )}></span>
                                    </span>
                                    <div className="ml-2 space-y-1 overflow-hidden">
                                        <p className="text-sm font-medium leading-none text-white truncate max-w-[150px]">
                                            {job.input?.split(/[/\\]/).pop() || 'Unknown'}
                                        </p>
                                        <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">{job.preset || 'Default'}</p>
                                    </div>
                                    <div className="ml-auto font-mono text-[10px] text-slate-400">
                                        {job.status === 'processing' ? `${Math.round(job.progress || 0)}%` : (job.status?.toUpperCase() || 'IDLE')}
                                    </div>
                                </div>
                            ))}
                            {jobs.length === 0 && (
                                <div className="text-center py-8 text-slate-500 text-xs italic">
                                    No active jobs in stream.
                                </div>
                            )}
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
