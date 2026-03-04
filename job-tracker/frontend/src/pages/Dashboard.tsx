import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import {
  getHealth,
  getRuns,
  triggerRun,
  clearJobs,
  type HealthResponse,
  type RunLog,
} from "@/lib/api";
import {
  Activity,
  Briefcase,
  Clock,
  Play,
  Loader2,
  Trash2,
} from "lucide-react";

export default function Dashboard() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [runs, setRuns] = useState<RunLog[]>([]);
  const [running, setRunning] = useState(false);
  const [clearing, setClearing] = useState(false);

  const fetchData = () => {
    getHealth().then((r) => setHealth(r.data));
    getRuns().then((r) => setRuns(r.data));
  };

  useEffect(fetchData, []);

  const handleRun = async () => {
    setRunning(true);
    try {
      const res = await triggerRun();
      toast.success(res.data.message);
      fetchData();
    } catch {
      toast.error("Run failed");
    } finally {
      setRunning(false);
    }
  };

  const handleClear = async () => {
    if (!window.confirm("Delete all jobs from the database?")) return;
    setClearing(true);
    try {
      const res = await clearJobs();
      toast.success(res.data.message);
      fetchData();
    } catch {
      toast.error("Clear failed");
    } finally {
      setClearing(false);
    }
  };

  const formatTime = (iso: string) => new Date(iso).toLocaleString();

  return (
    <div className="space-y-8">
      {/* Stats row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-5">
          <div className="flex items-center gap-3 text-zinc-400 text-sm mb-2">
            <Briefcase size={16} />
            Total Jobs Tracked
          </div>
          <p className="text-3xl font-semibold text-zinc-50">
            {health?.jobs_total ?? "—"}
          </p>
        </div>

        <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-5">
          <div className="flex items-center gap-3 text-zinc-400 text-sm mb-2">
            <Clock size={16} />
            Last Run
          </div>
          <p className="text-sm text-zinc-50">
            {health?.last_run ? formatTime(health.last_run.ran_at) : "Never"}
          </p>
          {health?.last_run && (
            <span
              className={`inline-block mt-1 text-xs font-medium px-2 py-0.5 rounded ${
                health.last_run.status === "success"
                  ? "bg-emerald-900/50 text-emerald-400"
                  : "bg-red-900/50 text-red-400"
              }`}
            >
              {health.last_run.status}
            </span>
          )}
        </div>

        <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-5">
          <div className="flex items-center gap-3 text-zinc-400 text-sm mb-2">
            <Activity size={16} />
            Manual Run
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleRun}
              disabled={running}
              className="inline-flex items-center gap-2 rounded-md bg-zinc-50 px-3 py-1.5 text-sm font-medium text-zinc-900 hover:bg-zinc-200 transition-colors disabled:opacity-50"
            >
              {running ? (
                <Loader2 size={14} className="animate-spin" />
              ) : (
                <Play size={14} />
              )}
              {running ? "Running..." : "Run Now"}
            </button>
            <button
              onClick={handleClear}
              disabled={clearing}
              className="inline-flex items-center gap-2 rounded-md border border-red-800 px-3 py-1.5 text-sm font-medium text-red-400 hover:bg-red-900/30 transition-colors disabled:opacity-50"
            >
              {clearing ? (
                <Loader2 size={14} className="animate-spin" />
              ) : (
                <Trash2 size={14} />
              )}
              {clearing ? "Clearing..." : "Clear Jobs"}
            </button>
          </div>
        </div>
      </div>

      {/* Recent runs table */}
      <div>
        <h2 className="text-lg font-medium text-zinc-100 mb-3">Recent Runs</h2>
        <div className="rounded-lg border border-zinc-800 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-zinc-900 text-zinc-400 text-left">
              <tr>
                <th className="px-4 py-3 font-medium">Time</th>
                <th className="px-4 py-3 font-medium">Repo</th>
                <th className="px-4 py-3 font-medium">Found</th>
                <th className="px-4 py-3 font-medium">New</th>
                <th className="px-4 py-3 font-medium">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800">
              {runs.length === 0 ? (
                <tr>
                  <td
                    colSpan={5}
                    className="px-4 py-6 text-center text-zinc-500"
                  >
                    No runs yet
                  </td>
                </tr>
              ) : (
                runs.map((run) => (
                  <tr key={run.id} className="hover:bg-zinc-900/50">
                    <td className="px-4 py-3 text-zinc-300">
                      {formatTime(run.ran_at)}
                    </td>
                    <td className="px-4 py-3 text-zinc-300 font-mono text-xs">
                      {run.repo}
                    </td>
                    <td className="px-4 py-3 text-zinc-300">
                      {run.jobs_found}
                    </td>
                    <td className="px-4 py-3 text-zinc-300">{run.jobs_new}</td>
                    <td className="px-4 py-3">
                      <span
                        className={`text-xs font-medium px-2 py-0.5 rounded ${
                          run.status === "success"
                            ? "bg-emerald-900/50 text-emerald-400"
                            : "bg-red-900/50 text-red-400"
                        }`}
                      >
                        {run.status}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
