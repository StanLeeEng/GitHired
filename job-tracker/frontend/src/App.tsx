import { useState } from "react";
import { Toaster } from "react-hot-toast";
import Dashboard from "@/pages/Dashboard";
import JobsList from "@/pages/JobsList";
import Repos from "@/pages/Repos";
import { LayoutDashboard, Briefcase, FolderGit2 } from "lucide-react";

type Page = "dashboard" | "jobs" | "repos";

const navItems: { id: Page; label: string; icon: typeof LayoutDashboard }[] = [
  { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
  { id: "jobs", label: "Jobs", icon: Briefcase },
  { id: "repos", label: "Repos", icon: FolderGit2 },
];

function App() {
  const [page, setPage] = useState<Page>("dashboard");

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100">
      {/* Header */}
      <header className="border-b border-zinc-800">
        <div className="mx-auto max-w-5xl flex items-center justify-between px-6 py-4">
          <h1 className="text-lg font-semibold tracking-tight">GitHired</h1>
          <nav className="flex gap-1">
            {navItems.map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setPage(id)}
                className={`inline-flex items-center gap-2 rounded-md px-3 py-1.5 text-sm transition-colors ${
                  page === id
                    ? "bg-zinc-800 text-zinc-100"
                    : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900"
                }`}
              >
                <Icon size={14} />
                {label}
              </button>
            ))}
          </nav>
        </div>
      </header>

      {/* Content */}
      <main className="mx-auto max-w-5xl px-6 py-8">
        {page === "dashboard" && <Dashboard />}
        {page === "jobs" && <JobsList />}
        {page === "repos" && <Repos />}
      </main>

      <Toaster
        position="bottom-right"
        toastOptions={{
          style: {
            background: "#18181b",
            color: "#f4f4f5",
            border: "1px solid #27272a",
            fontSize: "14px",
          },
        }}
      />
    </div>
  );
}

export default App;
