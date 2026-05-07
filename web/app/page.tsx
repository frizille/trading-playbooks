import { Shell } from "@/components/Shell";
import { TopBar } from "@/components/TopBar";
import { ChatPane } from "@/components/chat/ChatPane";

export default function Home() {
  return (
    <Shell
      topBar={<TopBar />}
      drawer={<div className="text-muted text-xs p-2">Chat history (Task 15)</div>}
      chat={<ChatPane />}
      rightPane={
        <div className="flex-1 flex items-center justify-center text-muted text-sm">
          Right pane (Task 16)
        </div>
      }
    />
  );
}
