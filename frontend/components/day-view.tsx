"use client";

import { useEffect, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiGet, type DaySchedule } from "@/lib/api";
import { LessonCard } from "@/components/lesson-card";

function remain(end: string) {
  const seconds = Math.max(0, Math.floor((new Date(end).getTime() - Date.now()) / 1000));
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  return `${h.toString().padStart(2, "0")}:${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
}

export function DayView({ endpoint, emptyText }: { endpoint: string; emptyText: string }) {
  const { data, refetch } = useQuery({ queryKey: [endpoint], queryFn: () => apiGet<DaySchedule>(endpoint), refetchInterval: 60000 });
  const [, tick] = useState(0);
  useEffect(() => {
    const timer = setInterval(() => tick((value) => value + 1), 1000);
    return () => clearInterval(timer);
  }, []);
  useEffect(() => {
    if (!data?.current_lesson) return;
    const ms = new Date(data.current_lesson.ends_at).getTime() - Date.now() + 500;
    if (ms > 0) {
      const timer = setTimeout(() => refetch(), ms);
      return () => clearTimeout(timer);
    }
  }, [data?.current_lesson, refetch]);
  const headline = useMemo(() => data?.current_lesson ?? data?.next_lesson, [data]);
  if (!data) return <main className="mx-auto max-w-6xl px-4 py-8">Загрузка...</main>;
  return (
    <main className="mx-auto max-w-6xl px-4 py-6">
      {headline ? (
        <section className="mb-6 grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
          <LessonCard lesson={headline} prominent />
          <div className="border border-zinc-200 bg-white p-4">
            <div className="text-sm text-zinc-500">Осталось</div>
            <div className="mt-2 text-4xl font-semibold tabular-nums">{headline.status === "current" ? remain(headline.ends_at) : "—"}</div>
            <div className="mt-5 grid grid-cols-2 gap-3 text-sm">
              <div><span className="text-zinc-500">Начало</span><br />{headline.starts_at.slice(11, 16)}</div>
              <div><span className="text-zinc-500">Конец</span><br />{headline.ends_at.slice(11, 16)}</div>
            </div>
          </div>
        </section>
      ) : null}
      <section className="grid gap-3">
        {data.lessons.length ? data.lessons.map((lesson) => <LessonCard key={lesson.id + lesson.date} lesson={lesson} />) : <div className="border border-zinc-200 bg-white p-6">{emptyText}</div>}
      </section>
    </main>
  );
}
