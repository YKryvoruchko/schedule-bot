export type Lesson = {
  id: number;
  date: string;
  group: string;
  lesson_number: number;
  starts_at: string;
  ends_at: string;
  subject: string;
  teacher?: string | null;
  meeting_url?: string | null;
  room?: string | null;
  lesson_type?: string | null;
  week_parity: string;
  status: "upcoming" | "current" | "finished";
};

export type DaySchedule = {
  date: string;
  timezone: string;
  server_now: string;
  lessons: Lesson[];
  current_lesson?: Lesson | null;
  next_lesson?: Lesson | null;
};

export type WeekSchedule = { days: DaySchedule[]; timezone: string; server_now: string };

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${API}${path}`, { credentials: "include", cache: "no-store" });
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

export async function apiPost<T>(path: string, body?: BodyInit | object): Promise<T> {
  const init: RequestInit = { method: "POST", credentials: "include" };
  if (body instanceof FormData) init.body = body;
  else if (body) {
    init.body = JSON.stringify(body);
    init.headers = { "Content-Type": "application/json" };
  }
  const response = await fetch(`${API}${path}`, init);
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}
