import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import { getRepos, addRepo, type Repo } from "@/lib/api";
import { Plus, Github, Loader2 } from "lucide-react";

export default function Repos() {
  const [repos, setRepos] = useState<Repo[]>([]);
  const [owner, setOwner] = useState("");
  const [name, setName] = useState("");
  const [adding, setAdding] = useState(false);

  const fetchRepos = () => {
    getRepos().then((r) => setRepos(r.data));
  };

  useEffect(fetchRepos, []);

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!owner.trim() || !name.trim()) return;

    setAdding(true);
    try {
      await addRepo(owner.trim(), name.trim());
      toast.success(`Added ${owner.trim()}/${name.trim()}`);
      setOwner("");
      setName("");
      fetchRepos();
    } catch {
      toast.error("Failed to add repo");
    } finally {
      setAdding(false);
    }
  };

  const formatDate = (iso: string) => new Date(iso).toLocaleDateString();

  return (
    <div className="space-y-6">
      {/* Add repo form */}
      <form
        onSubmit={handleAdd}
        className="flex flex-col sm:flex-row gap-3 items-end"
      >
        <div className="flex-1">
          <label className="block text-xs text-zinc-400 mb-1">Owner</label>
          <input
            type="text"
            placeholder="SimplifyJobs"
            value={owner}
            onChange={(e) => setOwner(e.target.value)}
            className="w-full rounded-md border border-zinc-800 bg-zinc-900 py-2 px-3 text-sm text-zinc-100 placeholder-zinc-500 outline-none focus:border-zinc-600 transition-colors"
          />
        </div>
        <div className="flex-1">
          <label className="block text-xs text-zinc-400 mb-1">Repo Name</label>
          <input
            type="text"
            placeholder="New-Grad-Positions"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full rounded-md border border-zinc-800 bg-zinc-900 py-2 px-3 text-sm text-zinc-100 placeholder-zinc-500 outline-none focus:border-zinc-600 transition-colors"
          />
        </div>
        <button
          type="submit"
          disabled={adding}
          className="inline-flex items-center gap-2 rounded-md bg-zinc-50 px-4 py-2 text-sm font-medium text-zinc-900 hover:bg-zinc-200 transition-colors disabled:opacity-50"
        >
          {adding ? (
            <Loader2 size={14} className="animate-spin" />
          ) : (
            <Plus size={14} />
          )}
          Add Repo
        </button>
      </form>

      {/* Repos list */}
      <div className="rounded-lg border border-zinc-800 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-zinc-900 text-zinc-400 text-left">
            <tr>
              <th className="px-4 py-3 font-medium">Repository</th>
              <th className="px-4 py-3 font-medium">Status</th>
              <th className="px-4 py-3 font-medium">Added</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800">
            {repos.length === 0 ? (
              <tr>
                <td colSpan={3} className="px-4 py-8 text-center text-zinc-500">
                  No repos monitored yet — add one above
                </td>
              </tr>
            ) : (
              repos.map((repo) => (
                <tr key={repo.id} className="hover:bg-zinc-900/50">
                  <td className="px-4 py-3">
                    <a
                      href={`https://github.com/${repo.owner}/${repo.name}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-2 text-zinc-100 hover:text-zinc-300 transition-colors"
                    >
                      <Github size={14} className="text-zinc-500" />
                      <span className="font-mono text-sm">
                        {repo.owner}/{repo.name}
                      </span>
                    </a>
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`text-xs font-medium px-2 py-0.5 rounded ${
                        repo.active
                          ? "bg-emerald-900/50 text-emerald-400"
                          : "bg-zinc-800 text-zinc-500"
                      }`}
                    >
                      {repo.active ? "Active" : "Paused"}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-zinc-500 text-xs">
                    {formatDate(repo.added_at)}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
