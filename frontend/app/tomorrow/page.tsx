import { DayView } from "@/components/day-view";

export default function TomorrowPage() {
  return <DayView endpoint="/api/schedule/tomorrow" emptyText="Завтра пар нет." />;
}
