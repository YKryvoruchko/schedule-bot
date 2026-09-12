"use client";

import { ExternalLink } from "lucide-react";
import type { Lesson } from "@/lib/api";

export function LessonCard({ lesson, prominent = false }: { lesson: Lesson; prominent?: boolean }) {
  const status = lesson.status === "current" ? "Сейчас идет" : lesson.status === "upcoming" ? "Следующая" : "Завершена";
  return (
    <article className={`border bg-white p-4 ${prominent ? "border-mint shadow-sm" : "border-zinc-200"}`}>
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <div className="text-sm text-zinc-500">Пара {lesson.lesson_number} · {lesson.starts_at.slice(11, 16)}-{lesson.ends_at.slice(11, 16)} · {lesson.group}</div>
          <h2 className={prominent ? "mt-1 text-2xl font-semibold" : "mt-1 text-lg font-semibold"}>{lesson.subject}</h2>
        </div>
        <span className="border border-zinc-300 px-2 py-1 text-sm">{status}</span>
      </div>
      <div className="mt-3 text-sm text-zinc-700">
        {lesson.teacher && <div>{lesson.teacher}</div>}
        {lesson.room && <div>{lesson.room}</div>}
        {lesson.lesson_type && <div>{lesson.lesson_type} · {lesson.week_parity}</div>}
      </div>
      {lesson.meeting_url && (
        <a className="mt-4 inline-flex items-center gap-2 bg-ink px-3 py-2 text-sm font-medium text-white hover:bg-zinc-700" href={lesson.meeting_url} target="_blank">
          <ExternalLink size={16} /> Подключиться
        </a>
      )}
    </article>
  );
}
