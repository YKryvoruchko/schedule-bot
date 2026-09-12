import { DayView } from "@/components/day-view";

export default function Page() {
  return <DayView endpoint="/api/schedule/today" emptyText="Сегодня пар нет 🎉" />;
}
