"use client";

import { useQuery } from "@tanstack/react-query";
import { apiGet, type WeekSchedule } from "@/lib/api";
import { LessonCard } from "@/components/lesson-card";

export default function WeekPage() {
  const { data } = useQuery({ queryKey: ["week"], queryFn: () => apiGet<WeekSchedule>("/api/schedule/week") });
  if (!data) return <main className="mx-auto max-w-6xl px-4 py-8">Загрузка...</main>;
  return (
    <main className="mx-auto max-w-6xl px-4 py-6">
      <div className="grid gap-4 lg:grid-cols-7">
        {data.days.map((day) => (
          <section key={day.date} className="min-w-0">
            <h2 className="mb-2 text-sm font-semibold text-zinc-600">{day.date}</h2>
            <div className="grid gap-2">
              {day.lessons.map((lesson) => <LessonCard key={lesson.id + day.date} lesson={lesson} />)}
              {!day.lessons.length && <div className="border border-zinc-200 bg-white p-3 text-sm text-zinc-500">Нет занятий</div>}
            </div>
          </section>
        ))}
      </div>
    </main>
  );
}
