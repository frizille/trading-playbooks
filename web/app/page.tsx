import { Shell } from "@/components/Shell";
import { TopBar } from "@/components/TopBar";

export default function Home() {
  return (
    <Shell
      topBar={<TopBar />}
      drawer={<div className="text-muted text-xs p-2">Chat history will appear here</div>}
      chat={
        <div className="flex-1 flex items-center justify-center text-muted text-sm">
          Chat pane (Task 14)
        </div>
      }
      rightPane={
        <div className="flex-1 flex items-center justify-center text-muted text-sm">
          Right pane (Task 16)
        </div>
      }
    />
  );
}
