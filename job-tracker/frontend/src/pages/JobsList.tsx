import { useEffect, useState } from "react";
import { getJobs, type Job, type JobsResponse } from "@/lib/api";
import { Search, ExternalLink, ChevronLeft, ChevronRight } from "lucide-react";

const TIME_RANGES = [
  { label: "All time", minHours: undefined, maxHours: undefined },
  { label: "Last 24h", minHours: 0, maxHours: 24 },
  { label: "24 – 48h", minHours: 24, maxHours: 48 },
  { label: "Last 7d", minHours: 0, maxHours: 168 },
] as const;

export default function JobsList() {
  const [data, setData] = useState<JobsResponse | null>(null);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [rangeIdx, setRangeIdx] = useState(0);
  const perPage = 25;

  useEffect(() => {
    const range = TIME_RANGES[rangeIdx];
    const params: Record<string, string | number> = {
      page,
      per_page: perPage,
    };
    if (search.trim()) {
      params.company = search.trim();
      params.role = search.trim();
    }
    if (range.minHours !== undefined) params.min_hours = range.minHours;
    if (range.maxHours !== undefined) params.max_hours = range.maxHours;
    getJobs(params).then((r) => setData(r.data));
  }, [page, search, rangeIdx]);

  const totalPages = data ? Math.ceil(data.total / perPage) : 1;

  const formatDate = (iso: string) => new Date(iso).toLocaleDateString();

  return (
    <div className="space-y-4">
      {/* Search + time range filter */}
      <div className="flex gap-3">
        <div className="relative flex-1">
          <Search
            size={16}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500"
          />
          <input
            type="text"
            placeholder="Search companies or roles..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
            className="w-full rounded-md border border-zinc-800 bg-zinc-900 py-2 pl-9 pr-3 text-sm text-zinc-100 placeholder-zinc-500 outline-none focus:border-zinc-600 transition-colors"
          />
        </div>
        <select
          value={rangeIdx}
          onChange={(e) => {
            setRangeIdx(Number(e.target.value));
            setPage(1);
          }}
          className="rounded-md border border-zinc-800 bg-zinc-900 px-3 py-2 text-sm text-zinc-100 outline-none focus:border-zinc-600 transition-colors"
        >
          {TIME_RANGES.map((r, i) => (
            <option key={i} value={i}>
              {r.label}
            </option>
          ))}
        </select>
      </div>

      {/* Table */}
      <div className="rounded-lg border border-zinc-800 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-zinc-900 text-zinc-400 text-left">
            <tr>
              <th className="px-4 py-3 font-medium">Company</th>
              <th className="px-4 py-3 font-medium">Role</th>
              <th className="px-4 py-3 font-medium">Location</th>
              <th className="px-4 py-3 font-medium">Link</th>
              <th className="px-4 py-3 font-medium">Posted</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800">
            {!data || data.jobs.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-zinc-500">
                  {data ? "No jobs found" : "Loading..."}
                </td>
              </tr>
            ) : (
              data.jobs.map((job: Job) => (
                <tr key={job.id} className="hover:bg-zinc-900/50">
                  <td className="px-4 py-3 text-zinc-100 font-medium">
                    {job.company}
                  </td>
                  <td className="px-4 py-3 text-zinc-300">{job.role}</td>
                  <td className="px-4 py-3 text-zinc-400">{job.location}</td>
                  <td className="px-4 py-3">
                    {job.link ? (
                      <a
                        href={job.link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 text-zinc-400 hover:text-zinc-100 transition-colors"
                      >
                        Apply <ExternalLink size={12} />
                      </a>
                    ) : (
                      <span className="text-zinc-600">—</span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-zinc-500 text-xs">
                    {job.date_posted ?? formatDate(job.seen_at)}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {data && totalPages > 1 && (
        <div className="flex items-center justify-between text-sm text-zinc-400">
          <span>
            Page {page} of {totalPages} ({data.total} jobs)
          </span>
          <div className="flex gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1}
              className="inline-flex items-center gap-1 rounded-md border border-zinc-800 px-3 py-1.5 text-xs hover:bg-zinc-900 disabled:opacity-30 transition-colors"
            >
              <ChevronLeft size={14} /> Prev
            </button>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page >= totalPages}
              className="inline-flex items-center gap-1 rounded-md border border-zinc-800 px-3 py-1.5 text-xs hover:bg-zinc-900 disabled:opacity-30 transition-colors"
            >
              Next <ChevronRight size={14} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
