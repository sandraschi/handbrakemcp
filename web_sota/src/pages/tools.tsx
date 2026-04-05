import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Wrench, Search, Box, ChevronRight } from "lucide-react";

export function Tools() {
    const { data: toolsData, isLoading } = useQuery({
        queryKey: ["tools"],
        queryFn: async () => {
            const resp = await fetch("http://localhost:10875/mcp/tools");
            return resp.json();
        },
    });

    const tools = toolsData?.tools || [];

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight text-white">Toolbox Explorer</h2>
                    <p className="text-slate-400">Inventory of available Handbrake MCP capabilities</p>
                </div>
                <div className="flex items-center gap-2 rounded-md bg-slate-800/50 px-3 py-1 text-xs text-slate-300 border border-slate-700">
                    <Box className="h-3 w-3" />
                    {tools.length} Tools Available
                </div>
            </div>

            <div className="relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
                <input
                    type="text"
                    placeholder="Search tools..."
                    className="w-full rounded-md border border-slate-800 bg-slate-950/50 py-2 pl-10 pr-4 text-sm text-slate-300 outline-none focus:ring-2 focus:ring-blue-500/50 transition-all"
                />
            </div>

            <div className="grid gap-4">
                {isLoading ? (
                    Array(5).fill(0).map((_, i) => (
                        <div key={i} className="h-24 w-full animate-pulse rounded-lg bg-slate-900/50 border border-slate-800" />
                    ))
                ) : (
                    tools.map((tool: { name: string; description: string; inputSchema: { properties: Record<string, any> } }) => (
                        <Card key={tool.name} className="border-slate-800 bg-slate-950/50 hover:bg-slate-900/50 transition-colors group cursor-pointer">
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <div className="flex items-center gap-3">
                                    <div className="rounded-lg bg-blue-500/10 p-2 text-blue-500 group-hover:bg-blue-500 group-hover:text-white transition-colors">
                                        <Wrench className="h-5 w-5" />
                                    </div>
                                    <div>
                                        <CardTitle className="text-md font-semibold text-slate-100">{tool.name}</CardTitle>
                                        <p className="text-xs text-slate-500">{tool.description}</p>
                                    </div>
                                </div>
                                <ChevronRight className="h-5 w-5 text-slate-700 group-hover:text-slate-300 transition-colors" />
                            </CardHeader>
                            <CardContent>
                                <div className="mt-2 flex flex-wrap gap-2">
                                    {Object.keys(tool.inputSchema?.properties || {}).map((param) => (
                                        <span key={param} className="rounded bg-slate-800/80 px-2 py-0.5 text-[10px] text-slate-400 border border-slate-700">
                                            {param}
                                        </span>
                                    ))}
                                </div>
                            </CardContent>
                        </Card>
                    ))
                )}
            </div>
        </div>
    );
}
