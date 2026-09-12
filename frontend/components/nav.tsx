import Link from "next/link";

export function Nav() {
  return (
    <nav className="border-b border-zinc-200 bg-white">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <Link href="/" className="text-lg font-semibold">Розклад</Link>
        <div className="flex gap-1 text-sm">
          <Link className="px-3 py-2 hover:bg-zinc-100" href="/">Сегодня</Link>
          <Link className="px-3 py-2 hover:bg-zinc-100" href="/tomorrow">Завтра</Link>
          <Link className="px-3 py-2 hover:bg-zinc-100" href="/week">Неделя</Link>
          <Link className="px-3 py-2 hover:bg-zinc-100" href="/admin">Admin</Link>
        </div>
      </div>
    </nav>
  );
}
