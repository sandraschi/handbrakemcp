import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Video, Play, CheckCircle2, AlertCircle, Loader2 } from "lucide-react";

export function Transcode() {
    const queryClient = useQueryClient();
    const [inputPath, setInputPath] = useState("");
    const [outputPath, setOutputPath] = useState("");
    const [selectedPreset, setSelectedPreset] = useState("Fast 1080p30");
    const [successMessage, setSuccessMessage] = useState<string | null>(null);
    const [errorMessage, setErrorMessage] = useState<string | null>(null);

    const { data: presetsData } = useQuery({
        queryKey: ["presets"],
        queryFn: async () => {
            const resp = await fetch("http://127.0.0.1:10875/api/presets");
            return resp.json();
        },
    });

    const transcodeMutation = useMutation({
        mutationFn: async () => {
            const resp = await fetch("http://127.0.0.1:10875/api/transcode", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    input: inputPath,
                    output: outputPath,
                    preset: selectedPreset
                }),
            });
            const data = await resp.json();
            if (data.status === "error") throw new Error(data.message);
            return data;
        },
        onSuccess: () => {
            setSuccessMessage("Transcoding job queued successfully!");
            setErrorMessage(null);
            queryClient.invalidateQueries({ queryKey: ["jobs"] });
            // Clear inputs
            setInputPath("");
            setOutputPath("");
        },
        onError: (error: Error) => {
            setErrorMessage(error.message);
            setSuccessMessage(null);
        }
    });

    const presets = presetsData?.presets || ["Fast 1080p30", "HQ 1080p30 Surround"];

    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight text-white uppercase italic">
                        Media <span className="text-blue-500">Transcoder</span>
                    </h2>
                    <p className="text-slate-400 text-xs font-bold uppercase tracking-widest mt-1">Manual job orchestration</p>
                </div>
            </div>

            <div className="grid gap-6 md:grid-cols-2">
                <Card className="border-slate-800 bg-slate-950/50 backdrop-blur-xl md:col-span-2">
                    <CardHeader>
                        <CardTitle className="text-sm font-black uppercase tracking-widest text-slate-200 flex items-center gap-2">
                            <Video className="h-4 w-4 text-blue-500" />
                            Job Configuration
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-6">
                        <div className="grid gap-4 md:grid-cols-2">
                            <div className="space-y-2">
                                <Label htmlFor="input" className="text-xs font-bold uppercase text-slate-400">Input File Path</Label>
                                <Input
                                    id="input"
                                    placeholder="C:\Videos\movie.mp4"
                                    value={inputPath}
                                    onChange={(e) => setInputPath(e.target.value)}
                                    className="bg-slate-900/50 border-slate-800 text-slate-200"
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="output" className="text-xs font-bold uppercase text-slate-400">Output File Path (Optional)</Label>
                                <Input
                                    id="output"
                                    placeholder="C:\Videos\movie_fixed.mkv"
                                    value={outputPath}
                                    onChange={(e) => setOutputPath(e.target.value)}
                                    className="bg-slate-900/50 border-slate-800 text-slate-200"
                                />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="preset" className="text-xs font-bold uppercase text-slate-400">Transcoding Preset</Label>
                            <select
                                id="preset"
                                value={selectedPreset}
                                onChange={(e) => setSelectedPreset(e.target.value)}
                                className="flex h-10 w-full rounded-md border border-slate-800 bg-slate-900/50 px-3 py-2 text-sm text-slate-200 ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                            >
                                {presets.map((preset: string) => (
                                    <option key={preset} value={preset} className="bg-slate-900 text-slate-200">
                                        {preset}
                                    </option>
                                ))}
                            </select>
                        </div>

                        {successMessage && (
                            <div className="flex items-center gap-2 rounded-md bg-emerald-500/10 border border-emerald-500/20 p-3 text-sm text-emerald-400 animate-in slide-in-from-top-2">
                                <CheckCircle2 className="h-4 w-4" />
                                {successMessage}
                            </div>
                        )}

                        {errorMessage && (
                            <div className="flex items-center gap-2 rounded-md bg-red-500/10 border border-red-500/20 p-3 text-sm text-red-400 animate-in slide-in-from-top-2">
                                <AlertCircle className="h-4 w-4" />
                                {errorMessage}
                            </div>
                        )}

                        <Button
                            onClick={() => transcodeMutation.mutate()}
                            disabled={!inputPath || transcodeMutation.isPending}
                            className="w-full bg-blue-600 hover:bg-blue-500 text-white font-black uppercase tracking-widest h-12 transition-all rounded-md shadow-lg shadow-blue-900/20"
                        >
                            {transcodeMutation.isPending ? (
                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            ) : (
                                <Play className="mr-2 h-4 w-4" />
                            )}
                            Initialize Transcode Job
                        </Button>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50 backdrop-blur-xl">
                    <CardHeader>
                        <CardTitle className="text-xs font-black uppercase tracking-widest text-slate-200">
                            Preset Summary
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="rounded-lg border border-slate-800 p-4 space-y-2">
                            <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Selected Preset</div>
                            <div className="text-sm font-medium text-slate-100">{selectedPreset}</div>
                        </div>
                        <p className="text-xs text-slate-500 leading-relaxed italic">
                            Industrial transcoding utilizes NVENC or QSV hardware acceleration where available to ensure maximum frames-per-second throughput.
                        </p>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
