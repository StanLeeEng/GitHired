import axios from "axios";

const api = axios.create({
  baseURL: "/api",
});

export type Job = {
  id: string;
  company: string;
  role: string;
  location: string;
  link: string;
  repo: string;
  notified: number;
  seen_at: string;
  notified_at: string | null;
  date_posted: string | null;
};

export type Repo = {
  id: number;
  owner: string;
  name: string;
  active: number;
  added_at: string;
};

export type RunLog = {
  id: number;
  repo: string;
  ran_at: string;
  jobs_found: number;
  jobs_new: number;
  status: string;
  error_msg: string | null;
};

export type HealthResponse = {
  status: string;
  jobs_total: number;
  last_run: { ran_at: string; status: string } | null;
};

export type JobsResponse = {
  jobs: Job[];
  page: number;
  per_page: number;
  total: number;
};

export const getHealth = () => api.get<HealthResponse>("/health");
export const getJobs = (params?: Record<string, string | number>) =>
  api.get<JobsResponse>("/jobs", { params });
export const getNewJobs = (minHours = 0, maxHours = 24) =>
  api.get<Job[]>("/jobs/new", { params: { min_hours: minHours, max_hours: maxHours } });
export const getRepos = () => api.get<Repo[]>("/repos");
export const addRepo = (owner: string, name: string) =>
  api.post("/repos", { owner, name });
export const triggerRun = () => api.post<{ message: string }>("/run");
export const clearJobs = () => api.delete<{ message: string }>("/jobs");
export const getRuns = () => api.get<RunLog[]>("/runs");
