import { Activity, Zap } from "lucide-react";
import { FLEET_REGISTRY } from '@/common/apps-catalog';
import { FleetCard } from '@/common/FleetCard';

export function Apps() {
    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight text-white">Fleet Navigation</h2>
                    <p className="text-slate-400">Connect to other SOTA standard applications with one-click orchestration.</p>
                </div>
                <div className="flex items-center gap-2 rounded-md bg-slate-800/50 px-3 py-1 text-xs text-slate-300 border border-slate-700">
                    <Activity className="h-3 w-3 text-emerald-500" />
                    Fleet Sync Active
                </div>
            </div>

            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                {FLEET_REGISTRY.map((member) => (
                    <FleetCard
                        key={member.id}
                        member={member}
                        currentAppId="handbrake-mcp"
                    />
                ))}

                <div className="h-full border-dashed border-slate-800 bg-transparent hover:border-slate-700 border rounded-xl transition-colors flex flex-col items-center justify-center p-6 text-center group">
                    <Zap className="h-10 w-10 text-slate-800 group-hover:text-blue-500/20 transition-colors mb-4" />
                    <p className="text-xs text-slate-600 group-hover:text-slate-500 transition-colors">
                        More apps arriving soon...
                    </p>
                </div>
            </div>
        </div>
    );
}
