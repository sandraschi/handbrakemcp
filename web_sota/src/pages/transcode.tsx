import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  AlertCircle,
  CheckCircle2,
  FolderOpen,
  Loader2,
  Play,
  Video,
} from "lucide-react";
import { useState } from "react";
import { FileBrowser } from "@/components/FileBrowser";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { API_BASE } from "@/lib/api";

const ENCODERS = [
  "x264",
  "x265",
  "x264_10bit",
  "x265_10bit",
  "x265_12bit",
  "nvenc_h264",
  "nvenc_h265",
  "nvenc_av1",
  "vce_h264",
  "vce_h265",
  "qsv_h264",
  "qsv_h265",
  "qsv_av1",
  "mf_h264",
  "mf_h265",
];

const AUDIO_ENCODERS = [
  "av_aac",
  "copy",
  "ac3",
  "eac3",
  "opus",
  "flac",
  "vorbis",
  "mp3",
];

type PickerTarget = "input" | "output" | null;

export function Transcode() {
  const queryClient = useQueryClient();
  const [inputPath, setInputPath] = useState("");
  const [outputPath, setOutputPath] = useState("");
  const [selectedPreset, setSelectedPreset] = useState("Fast 1080p30");
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [picker, setPicker] = useState<PickerTarget>(null);

  // Video
  const [encoder, setEncoder] = useState("");
  const [quality, setQuality] = useState("");
  const [videoBitrate, setVideoBitrate] = useState("");
  // Resolution
  const [width, setWidth] = useState("");
  const [height, setHeight] = useState("");
  const [maxWidth, setMaxWidth] = useState("");
  const [maxHeight, setMaxHeight] = useState("");
  // Audio
  const [audioTracks, setAudioTracks] = useState("");
  const [allAudio, setAllAudio] = useState(false);
  const [audioEncoder, setAudioEncoder] = useState("");
  const [audioBitrate, setAudioBitrate] = useState("");
  const [audioLang, setAudioLang] = useState("");
  // Subtitles
  const [subtitle, setSubtitle] = useState("none");
  const [subtitleBurned, setSubtitleBurned] = useState(false);
  const [srtFile, setSrtFile] = useState("");
  const [srtLang, setSrtLang] = useState("");

  const { data: presetsData } = useQuery({
    queryKey: ["presets"],
    queryFn: async () => {
      const resp = await fetch(`${API_BASE}/api/presets`);
      return resp.json();
    },
  });

  const buildOptions = (): Record<string, string | number | boolean> => {
    const o: Record<string, string | number | boolean> = {};
    if (encoder) o.encoder = encoder;
    if (quality.trim()) o.quality = quality.trim();
    if (videoBitrate.trim()) o.vb = videoBitrate.trim();
    if (width.trim()) o.width = width.trim();
    if (height.trim()) o.height = height.trim();
    if (maxWidth.trim()) o.maxWidth = maxWidth.trim();
    if (maxHeight.trim()) o.maxHeight = maxHeight.trim();
    if (allAudio) o["all-audio"] = true;
    else if (audioTracks.trim()) o.audio = audioTracks.trim();
    if (audioEncoder) o.aencoder = audioEncoder;
    if (audioBitrate.trim()) o.ab = audioBitrate.trim();
    if (audioLang.trim()) o["audio-lang-list"] = audioLang.trim();
    if (subtitle && subtitle !== "none") o.subtitle = subtitle;
    if (subtitleBurned) o["subtitle-burned"] = true;
    if (srtFile.trim()) o["srt-file"] = srtFile.trim();
    if (srtLang.trim()) o["srt-lang"] = srtLang.trim();
    return o;
  };

  const transcodeMutation = useMutation({
    mutationFn: async () => {
      const resp = await fetch(`${API_BASE}/api/transcode`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          input: inputPath,
          output: outputPath,
          preset: selectedPreset,
          options: buildOptions(),
        }),
      });
      const data = await resp.json();
      if (data.status === "error") throw new Error(data.message);
      return data;
    },
    onSuccess: (data) => {
      setSuccessMessage(`Transcoding job queued: ${data.job_id ?? ""}`.trim());
      setErrorMessage(null);
      queryClient.invalidateQueries({ queryKey: ["jobs"] });
      setInputPath("");
      setOutputPath("");
    },
    onError: (error: Error) => {
      setErrorMessage(error.message);
      setSuccessMessage(null);
    },
  });

  const presets = presetsData?.presets || [
    "Fast 1080p30",
    "HQ 1080p30 Surround",
  ];

  const numField = (
    id: string,
    label: string,
    value: string,
    set: (v: string) => void,
    placeholder: string,
  ) => (
    <div className="space-y-1">
      <Label
        htmlFor={id}
        className="text-xs font-bold uppercase text-slate-400"
      >
        {label}
      </Label>
      <Input
        id={id}
        inputMode="numeric"
        placeholder={placeholder}
        value={value}
        onChange={(e) => set(e.target.value.replace(/[^\d.]/g, ""))}
        className="bg-slate-900/50 border-slate-800 text-slate-200"
      />
    </div>
  );

  const textField = (
    id: string,
    label: string,
    value: string,
    set: (v: string) => void,
    placeholder: string,
  ) => (
    <div className="space-y-1">
      <Label
        htmlFor={id}
        className="text-xs font-bold uppercase text-slate-400"
      >
        {label}
      </Label>
      <Input
        id={id}
        placeholder={placeholder}
        value={value}
        onChange={(e) => set(e.target.value)}
        className="bg-slate-900/50 border-slate-800 text-slate-200"
      />
    </div>
  );

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white uppercase italic">
            Media <span className="text-blue-500">Transcoder</span>
          </h2>
          <p className="text-slate-400 text-xs font-bold uppercase tracking-widest mt-1">
            Manual job orchestration
          </p>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card className="border-slate-800 bg-slate-950/50 backdrop-blur-xl md:col-span-2">
          <CardHeader>
            <CardTitle className="text-sm font-black uppercase tracking-widest text-slate-200 flex items-center gap-2">
              <Video className="h-4 w-4 text-blue-500" />
              Job Configuration
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-1">
                <Label
                  htmlFor="input"
                  className="text-xs font-bold uppercase text-slate-400"
                >
                  Input File Path
                </Label>
                <div className="flex gap-2">
                  <Input
                    id="input"
                    placeholder="C:\Videos\movie.mp4"
                    value={inputPath}
                    onChange={(e) => setInputPath(e.target.value)}
                    className="bg-slate-900/50 border-slate-800 text-slate-200"
                  />
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setPicker("input")}
                    aria-label="Browse for input file"
                  >
                    <FolderOpen className="h-4 w-4" />
                  </Button>
                </div>
              </div>
              <div className="space-y-1">
                <Label
                  htmlFor="output"
                  className="text-xs font-bold uppercase text-slate-400"
                >
                  Output File Path (Optional)
                </Label>
                <div className="flex gap-2">
                  <Input
                    id="output"
                    placeholder="C:\Videos\movie_fixed.mkv"
                    value={outputPath}
                    onChange={(e) => setOutputPath(e.target.value)}
                    className="bg-slate-900/50 border-slate-800 text-slate-200"
                  />
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setPicker("output")}
                    aria-label="Browse for output file"
                  >
                    <FolderOpen className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>

            <div className="space-y-1">
              <Label
                htmlFor="preset"
                className="text-xs font-bold uppercase text-slate-400"
              >
                Transcoding Preset
              </Label>
              <select
                id="preset"
                value={selectedPreset}
                onChange={(e) => setSelectedPreset(e.target.value)}
                className="flex h-10 w-full rounded-md border border-slate-800 bg-slate-900/50 px-3 py-2 text-sm text-slate-200"
              >
                {presets.map((preset: string) => (
                  <option
                    key={preset}
                    value={preset}
                    className="bg-slate-900 text-slate-200"
                  >
                    {preset}
                  </option>
                ))}
              </select>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <Card className="border-slate-800 bg-slate-900/40">
                <CardHeader>
                  <CardTitle className="text-xs font-black uppercase tracking-widest text-slate-300">
                    Video
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="space-y-1">
                    <Label
                      htmlFor="encoder"
                      className="text-xs font-bold uppercase text-slate-400"
                    >
                      Encoder (blank = preset default)
                    </Label>
                    <select
                      id="encoder"
                      value={encoder}
                      onChange={(e) => setEncoder(e.target.value)}
                      className="flex h-10 w-full rounded-md border border-slate-800 bg-slate-900/50 px-3 py-2 text-sm text-slate-200"
                    >
                      <option value="">Preset default</option>
                      {ENCODERS.map((enc) => (
                        <option
                          key={enc}
                          value={enc}
                          className="bg-slate-900 text-slate-200"
                        >
                          {enc}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    {numField(
                      "quality",
                      "Quality RF",
                      quality,
                      setQuality,
                      "e.g. 22",
                    )}
                    {numField(
                      "videobitrate",
                      "Video kbps",
                      videoBitrate,
                      setVideoBitrate,
                      "e.g. 4000",
                    )}
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    {numField(
                      "width",
                      "Width px",
                      width,
                      setWidth,
                      "e.g. 1920",
                    )}
                    {numField(
                      "height",
                      "Height px",
                      height,
                      setHeight,
                      "e.g. 1080",
                    )}
                    {numField(
                      "maxwidth",
                      "Max width",
                      maxWidth,
                      setMaxWidth,
                      "e.g. 1920",
                    )}
                    {numField(
                      "maxheight",
                      "Max height",
                      maxHeight,
                      setMaxHeight,
                      "e.g. 1080",
                    )}
                  </div>
                </CardContent>
              </Card>

              <Card className="border-slate-800 bg-slate-900/40">
                <CardHeader>
                  <CardTitle className="text-xs font-black uppercase tracking-widest text-slate-300">
                    Audio
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {textField(
                    "audiotracks",
                    "Audio tracks (1,2,3)",
                    audioTracks,
                    setAudioTracks,
                    "e.g. 1,2",
                  )}
                  <label className="flex items-center gap-2 text-xs text-slate-300">
                    <input
                      type="checkbox"
                      checked={allAudio}
                      onChange={(e) => setAllAudio(e.target.checked)}
                    />
                    Include all audio tracks
                  </label>
                  <div className="space-y-1">
                    <Label
                      htmlFor="aencoder"
                      className="text-xs font-bold uppercase text-slate-400"
                    >
                      Audio encoder
                    </Label>
                    <select
                      id="aencoder"
                      value={audioEncoder}
                      onChange={(e) => setAudioEncoder(e.target.value)}
                      className="flex h-10 w-full rounded-md border border-slate-800 bg-slate-900/50 px-3 py-2 text-sm text-slate-200"
                    >
                      <option value="">Preset default</option>
                      {AUDIO_ENCODERS.map((enc) => (
                        <option
                          key={enc}
                          value={enc}
                          className="bg-slate-900 text-slate-200"
                        >
                          {enc}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    {numField(
                      "audiobitrate",
                      "Audio kbps",
                      audioBitrate,
                      setAudioBitrate,
                      "e.g. 160",
                    )}
                    {textField(
                      "audiolang",
                      "Audio lang",
                      audioLang,
                      setAudioLang,
                      "e.g. eng",
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>

            <Card className="border-slate-800 bg-slate-900/40">
              <CardHeader>
                <CardTitle className="text-xs font-black uppercase tracking-widest text-slate-300">
                  Subtitles
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="grid gap-3 md:grid-cols-3">
                  <div className="space-y-1">
                    <Label
                      htmlFor="subtitle"
                      className="text-xs font-bold uppercase text-slate-400"
                    >
                      Track
                    </Label>
                    <select
                      id="subtitle"
                      value={subtitle}
                      onChange={(e) => setSubtitle(e.target.value)}
                      className="flex h-10 w-full rounded-md border border-slate-800 bg-slate-900/50 px-3 py-2 text-sm text-slate-200"
                    >
                      <option value="none">None</option>
                      <option value="scan">Scan (foreign audio)</option>
                      <option value="first">First track</option>
                      <option value="1">Track 1</option>
                      <option value="2">Track 2</option>
                      <option value="3">Track 3</option>
                    </select>
                  </div>
                  {textField(
                    "srtfile",
                    "External .srt file",
                    srtFile,
                    setSrtFile,
                    "optional path",
                  )}
                  {textField(
                    "srtlang",
                    "SRT language",
                    srtLang,
                    setSrtLang,
                    "e.g. eng",
                  )}
                </div>
                <label className="flex items-center gap-2 text-xs text-slate-300">
                  <input
                    type="checkbox"
                    checked={subtitleBurned}
                    onChange={(e) => setSubtitleBurned(e.target.checked)}
                  />
                  Burn subtitles into video
                </label>
              </CardContent>
            </Card>

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
              <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">
                Selected Preset
              </div>
              <div className="text-sm font-medium text-slate-100">
                {selectedPreset}
              </div>
            </div>
            <p className="text-xs text-slate-500 leading-relaxed italic">
              Industrial transcoding utilizes NVENC or QSV hardware acceleration
              where available for maximum frames-per-second throughput.
            </p>
          </CardContent>
        </Card>
      </div>

      <FileBrowser
        open={picker !== null}
        mode="file"
        apiBase={API_BASE}
        onSelect={(p) => {
          if (picker === "input") setInputPath(p);
          else if (picker === "output") setOutputPath(p);
          setPicker(null);
        }}
        onClose={() => setPicker(null)}
      />
    </div>
  );
}
