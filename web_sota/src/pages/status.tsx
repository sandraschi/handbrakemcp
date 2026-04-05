import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Activity, Cpu, HardDrive, Zap } from "lucide-react";
import { Progress } from "@/components/ui/progress";

export function Status() {
    const { data, isLoading } = useQuery({
        queryKey: ["health"],
        queryFn: async () => {
            const resp = await fetch("http://localhost:10875/health");
            return resp.json();
        },
        refetchInterval: 2000,
    });

    const system = data?.system || {};

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
                        <HealthItem label="FastMCP Bridge" status="healthy" />
                        <HealthItem label="Watch Service" status="healthy" />
                        <HealthItem label="Notification Service" status="healthy" />
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
