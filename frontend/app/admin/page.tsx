"use client";

import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Upload } from "lucide-react";
import { apiGet, apiPost } from "@/lib/api";

export default function AdminPage() {
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("");
  const [importId, setImportId] = useState<number | null>(null);
  const preview = useQuery({ queryKey: ["preview", importId], queryFn: () => apiGet<any>(`/api/admin/import/${importId}/preview`), enabled: Boolean(importId) });
  const versions = useQuery({ queryKey: ["versions"], queryFn: () => apiGet<any[]>("/api/admin/versions"), retry: false });
  const login = useMutation({ mutationFn: () => apiPost("/api/admin/login", { username, password }), onSuccess: () => versions.refetch() });
  const upload = useMutation({
    mutationFn: async (file: File) => {
      const form = new FormData();
      form.append("file", file);
      return apiPost<any>("/api/admin/import", form);
    },
    onSuccess: (data) => setImportId(data.id),
  });
  const confirm = useMutation({ mutationFn: () => apiPost(`/api/admin/import/${importId}/confirm`), onSuccess: () => versions.refetch() });
  return (
    <main className="mx-auto grid max-w-6xl gap-5 px-4 py-6">
      <section className="border border-zinc-200 bg-white p-4">
        <h1 className="text-xl font-semibold">Admin</h1>
        <div className="mt-4 flex flex-wrap gap-2">
          <input className="border border-zinc-300 px-3 py-2" value={username} onChange={(event) => setUsername(event.target.value)} />
          <input className="border border-zinc-300 px-3 py-2" type="password" value={password} onChange={(event) => setPassword(event.target.value)} />
          <button className="bg-ink px-4 py-2 text-white" onClick={() => login.mutate()}>Войти</button>
        </div>
      </section>
      <section className="border border-zinc-200 bg-white p-4">
        <h2 className="font-semibold">DOCX импорт</h2>
        <label className="mt-3 inline-flex cursor-pointer items-center gap-2 border border-zinc-300 px-4 py-2">
          <Upload size={16} /> Загрузить
          <input className="hidden" type="file" accept=".docx" onChange={(event) => event.target.files?.[0] && upload.mutate(event.target.files[0])} />
        </label>
        {preview.data && (
          <div className="mt-4">
            <div className="text-sm">Строк: {preview.data.row_count}; валидных: {preview.data.valid_rows}; ошибок: {preview.data.invalid_rows}</div>
            <div className="mt-2 grid gap-1 text-sm text-amberline">{preview.data.warnings.map((item: string) => <div key={item}>{item}</div>)}</div>
            <div className="mt-2 grid gap-1 text-sm text-red-700">{preview.data.errors.map((item: string) => <div key={item}>{item}</div>)}</div>
            <button disabled={preview.data.status !== "parsed"} className="mt-3 bg-mint px-4 py-2 text-white disabled:bg-zinc-300" onClick={() => confirm.mutate()}>Подтвердить импорт</button>
            <div className="mt-4 max-h-80 overflow-auto border border-zinc-200">
              <table className="w-full text-left text-sm">
                <tbody>{preview.data.preview.slice(0, 60).map((item: any, index: number) => <tr className="border-b" key={index}><td className="p-2">{item.group_name}</td><td>{item.day_of_week}</td><td>{item.lesson_number}</td><td>{item.subject}</td></tr>)}</tbody>
              </table>
            </div>
          </div>
        )}
      </section>
      <section className="border border-zinc-200 bg-white p-4">
        <h2 className="font-semibold">Версии</h2>
        <div className="mt-3 grid gap-2 text-sm">
          {(versions.data ?? []).map((version) => <div className="flex justify-between border border-zinc-200 p-2" key={version.id}><span>{version.filename}</span><span>{version.is_active ? "active" : ""}</span></div>)}
        </div>
      </section>
    </main>
  );
}
