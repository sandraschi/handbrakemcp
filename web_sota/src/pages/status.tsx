import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Activity, Cpu, HardDrive, Zap } from "lucide-react";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/common/utils";

export function Status() {
    const { data, isLoading } = useQuery({
        queryKey: ["health"],
        queryFn: async () => {
            const resp = await fetch("http://127.0.0.1:10875/health");
            return resp.json();
        },
        refetchInterval: 2000,
    });

    const { data: jobsData } = useQuery({
        queryKey: ["jobs"],
        queryFn: async () => {
            const resp = await fetch("http://127.0.0.1:10875/api/jobs");
            return resp.json();
        },
        refetchInterval: 1000, // Faster updates for jobs
    });

    const system = data?.system || {};
    const jobs = jobsData?.jobs || [];

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight text-white">System Status</h2>
                    <p className="text-slate-400">Real-time performance metrics</p>
                </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                <Card className="border-slate-800 bg-slate-950/50 backdrop-blur-xl">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-slate-200">CPU Usage</CardTitle>
                        <Cpu className="h-4 w-4 text-blue-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-white">{system.cpu_percent || 0}%</div>
                        <div className="mt-4">
                            <Progress
                                value={system.cpu_percent || 0}
                                className="h-2"
                                indicatorClassName="bg-blue-500"
                            />
                        </div>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50 backdrop-blur-xl">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-slate-200">Memory (RAM)</CardTitle>
                        <Zap className="h-4 w-4 text-purple-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-white">
                            {system.memory ? Math.round(system.memory.percent) : 0}%
                        </div>
                        <div className="mt-4">
                            <Progress
                                value={system.memory ? system.memory.percent : 0}
                                className="h-2"
                                indicatorClassName="bg-purple-500"
                            />
                        </div>
                        <p className="mt-2 text-xs text-slate-500">
                            {system.memory ? `${Math.round(system.memory.used / 1024 / 1024 / 1024 * 10) / 10}GB used` : "N/A"}
                        </p>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50 backdrop-blur-xl">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-slate-200">Disk Usage</CardTitle>
                        <HardDrive className="h-4 w-4 text-emerald-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-white">
                            {system.disk ? Math.round(system.disk.percent) : 0}%
                        </div>
                        <div className="mt-4">
                            <Progress
                                value={system.disk ? system.disk.percent : 0}
                                className="h-2"
                                indicatorClassName="bg-emerald-500"
                            />
                        </div>
                    </CardContent>
                </Card>
            </div>

            {jobs.length > 0 && (
                <Card className="border-slate-800 bg-slate-950/50 backdrop-blur-xl">
                    <CardHeader>
                        <CardTitle className="text-white flex items-center gap-2">
                            <Activity className="h-5 w-5 text-blue-400" />
                            Transcoding Queue
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            {jobs.map((job: any) => (
                                <div key={job.job_id} className="rounded-lg border border-slate-800 bg-slate-900/30 p-4 space-y-2">
                                    <div className="flex justify-between items-start">
                                        <div className="space-y-1 overflow-hidden">
                                            <div className="text-sm font-medium text-slate-100 italic truncate max-w-[250px]">
                                                {job.input?.split(/[/\\]/).pop() || 'Unknown File'}
                                            </div>
                                            <div className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">{job.preset || 'Default Preset'}</div>
                                        </div>
                                        <div className={cn(
                                            "text-[10px] uppercase font-bold px-2 py-0.5 rounded border",
                                            job.status === 'processing' ? "text-blue-400 border-blue-400/20 bg-blue-400/10" :
                                            job.status === 'completed' ? "text-emerald-400 border-emerald-400/20 bg-emerald-400/10" :
                                            "text-slate-400 border-slate-400/20 bg-slate-400/10"
                                        )}>
                                            {job.status}
                                        </div>
                                    </div>
                                    <Progress value={job.progress} className="h-1.5" indicatorClassName="bg-blue-500" />
                                    <div className="text-[10px] text-right text-slate-500">{Math.round(job.progress)}%</div>
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>
            )}

            <Card className="border-slate-800 bg-slate-950/50 backdrop-blur-xl">
                <CardHeader>
                    <CardTitle className="text-white flex items-center gap-2">
                        <Activity className="h-5 w-5 text-blue-400" />
                        Infrastructure Health
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="space-y-4">
                        <HealthItem label="FastAPI Backend" status={!isLoading && data?.status === "ok" ? "healthy" : "error"} />
                        <HealthItem label="HandBrake Engine" status={system.gpu?.model !== "Not Detected" ? "healthy" : "warning"} />
                        <HealthItem label="FastMCP Bridge" status="healthy" />
                        <HealthItem label="Watch Service" status="healthy" />
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}

function HealthItem({ label, status }: { label: string; status: "healthy" | "warning" | "error" }) {
    const statusColors = {
        healthy: "bg-emerald-500",
        warning: "bg-orange-500",
        error: "bg-red-500",
    };

    return (
        <div className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-900/30 p-4">
            <span className="text-sm font-medium text-slate-300">{label}</span>
            <div className="flex items-center gap-2">
                <span className="text-xs text-slate-500 capitalize">{status}</span>
                <div className={`h-2.5 w-2.5 rounded-full ${statusColors[status]}`} />
            </div>
        </div>
    );
}
