import { Shell } from "@/components/Shell";
import { TopBar } from "@/components/TopBar";
import { ChatPane } from "@/components/chat/ChatPane";
import { SessionDrawer } from "@/components/sessions/SessionDrawer";

export default function Home() {
  return (
    <Shell
      topBar={<TopBar />}
      drawer={<SessionDrawer />}
      chat={<ChatPane />}
      rightPane={
        <div className="flex-1 flex items-center justify-center text-muted text-sm">
          Right pane (Task 16)
        </div>
      }
    />
  );
}
