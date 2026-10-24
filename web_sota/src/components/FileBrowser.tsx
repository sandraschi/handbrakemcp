import { ArrowUp, File, Folder, X } from "lucide-react";
import { useCallback, useEffect, useState } from "react";

type Entry = {
  name: string;
  path: string;
  type: "file" | "dir" | "drive";
  size?: number | null;
};

/**
 * Server-side file picker. The webapp and the video files live on the same
 * machine, so the dialog browses server paths via GET /api/browse — a
 * browser <input type=file> would only yield fake paths the backend cannot
 * open. Works identically in plain browsers and in the Tauri shell.
 */
export function FileBrowser({
  open,
  mode,
  onSelect,
  onClose,
  apiBase,
}: {
  open: boolean;
  mode: "file" | "dir";
  onSelect: (path: string) => void;
  onClose: () => void;
  apiBase: string;
}) {
  const [cwd, setCwd] = useState<string | null>(null);
  const [parent, setParent] = useState<string | null>(null);
  const [entries, setEntries] = useState<Entry[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(
    async (path: string | null) => {
      setLoading(true);
      setError(null);
      try {
        const url = path
          ? `${apiBase}/api/browse?path=${encodeURIComponent(path)}`
          : `${apiBase}/api/browse`;
        const r = await fetch(url);
        const d = await r.json();
        if (d.status === "error") throw new Error(d.message || "Browse failed");
        setCwd(d.cwd || "");
        setParent(d.parent ?? null);
        setEntries(Array.isArray(d.entries) ? d.entries : []);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Browse failed");
        setEntries([]);
      } finally {
        setLoading(false);
      }
    },
    [apiBase],
  );

  useEffect(() => {
    if (open) load(null);
  }, [open, load]);

  if (!open) return null;

  const visible = entries.filter((e) =>
    mode === "file" ? true : e.type !== "file",
  );

  return (
    <div
      className="fixed inset-0 bg-black/60 flex items-center justify-center z-50"
      data-testid="file-browser"
    >
      <div
        className="bg-slate-900 border border-slate-700 rounded-xl w-full max-w-lg max-h-[70vh] flex flex-col"
        role="dialog"
        aria-modal="true"
        aria-label="Choose a file or folder"
      >
        <div className="flex items-center justify-between px-4 py-3 border-b border-slate-800">
          <span className="text-sm font-bold text-slate-200 uppercase tracking-widest">
            {mode === "file" ? "Choose input file" : "Choose folder"}
          </span>
          <button
            type="button"
            onClick={onClose}
            className="text-slate-400 hover:text-white"
            aria-label="Close"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
        <div className="px-4 py-2 flex items-center gap-2 border-b border-slate-800">
          <button
            type="button"
            data-testid="file-browser-up"
            disabled={!parent}
            onClick={() => parent && load(parent)}
            className="p-1 rounded hover:bg-slate-800 disabled:opacity-30 text-slate-300"
            aria-label="Up one folder"
          >
            <ArrowUp className="h-4 w-4" />
          </button>
          <span className="text-xs text-slate-400 font-mono truncate">
            {cwd || "Drives"}
          </span>
        </div>
        <div className="overflow-y-auto p-2 flex-1">
          {loading && <p className="text-xs text-slate-500 p-3">Loading…</p>}
          {error && <p className="text-xs text-red-400 p-3">{error}</p>}
          {!loading &&
            !error &&
            visible.map((e) => (
              <button
                key={e.path}
                type="button"
                onClick={() => {
                  if (e.type === "file") {
                    if (mode === "file") {
                      onSelect(e.path);
                      onClose();
                    }
                  } else {
                    load(e.path);
                  }
                }}
                onDoubleClick={() => {
                  if (e.type !== "file" && mode === "dir") {
                    onSelect(e.path);
                    onClose();
                  }
                }}
                className="w-full flex items-center gap-2 px-3 py-1.5 rounded text-sm text-slate-200 hover:bg-slate-800 text-left"
              >
                {e.type === "file" ? (
                  <File className="h-4 w-4 text-slate-500 shrink-0" />
                ) : (
                  <Folder className="h-4 w-4 text-amber-500 shrink-0" />
                )}
                <span className="truncate">{e.name}</span>
              </button>
            ))}
          {!loading && !error && visible.length === 0 && (
            <p className="text-xs text-slate-500 p-3">Empty folder.</p>
          )}
        </div>
        {mode === "dir" && (
          <div className="p-3 border-t border-slate-800 flex justify-end">
            <button
              type="button"
              data-testid="file-browser-select"
              disabled={!cwd}
              onClick={() => {
                if (cwd) {
                  onSelect(cwd);
                  onClose();
                }
              }}
              className="px-4 py-2 rounded bg-blue-600 hover:bg-blue-500 disabled:opacity-40 text-white text-sm"
            >
              Select this folder
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
