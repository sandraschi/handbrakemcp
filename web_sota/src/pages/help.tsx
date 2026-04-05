import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Command, Terminal, MessageSquare, Info } from "lucide-react";

export function Help() {
    return (
        <div className="space-y-6">
            <div className="items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight text-white">Documentation & Help</h2>
                    <p className="text-slate-400">Learn how to master the Handbrake MCP ecosystem</p>
                </div>
            </div>

            <div className="grid gap-6 md:grid-cols-2">
                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2 text-white">
                            <Command className="h-5 w-5 text-blue-400" />
                            Core Concept
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="text-sm text-slate-400 leading-relaxed">
                        Handbrake MCP is an AI-native interface for video transcoding. It bridges high-level AI reasoning with low-level ffmpeg/HandbrakeCLI operations through a secure FastMCP transport layer.
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2 text-white">
                            <Terminal className="h-5 w-5 text-purple-400" />
                            CLI Usage
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="text-sm text-slate-400 leading-relaxed">
                        <pre className="rounded bg-slate-900 p-2 text-xs text-slate-300 border border-slate-800">
                            uv run handbrake-mcp stdio
                        </pre>
                        <p className="mt-2 text-[10px] text-slate-500 italic">
                            Used by AI agents like Cursor, Windsurf, and Claude Desktop.
                        </p>
                    </CardContent>
                </Card>
            </div>

            <Card className="border-slate-800 bg-slate-950/50">
                <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-white">
                        <MessageSquare className="h-5 w-5 text-emerald-400" />
                        Common Workflows
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="space-y-4">
                        <WorkflowItem
                            title="4K to HEVC"
                            desc="Optimize high-resolution video for web streaming without losing quality."
                        />
                        <WorkflowItem
                            title="Watch Folder Sync"
                            desc="Automatically transcode any file dropped into the designated input folder."
                        />
                        <WorkflowItem
                            title="Batch Processing"
                            desc="Queue multiple files for sequential background encoding."
                        />
                    </div>
                </CardContent>
            </Card>

            <div className="flex items-center gap-2 rounded-lg bg-blue-500/5 p-4 border border-blue-500/10">
                <Info className="h-5 w-5 text-blue-500 shrink-0" />
                <p className="text-xs text-blue-300">
                    Need more help? Check out the <a href="#" className="underline font-bold">Official Protocol Specs</a> or the <a href="#" className="underline font-bold">Developer Guide</a>.
                </p>
            </div>
        </div>
    );
}

function WorkflowItem({ title, desc }: { title: string; desc: string }) {
    return (
        <div className="group rounded-md border border-slate-800 bg-slate-900/20 p-3 hover:bg-slate-800/30 transition-colors">
            <h4 className="text-sm font-semibold text-slate-200 group-hover:text-white transition-colors">{title}</h4>
            <p className="text-xs text-slate-500 group-hover:text-slate-400 transition-colors">{desc}</p>
        </div>
    );
}
