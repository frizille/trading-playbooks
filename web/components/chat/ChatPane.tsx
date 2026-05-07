"use client";
import { useChatSocket } from "@/hooks/useChatSocket";
import { MessageList } from "./MessageList";
import { Composer } from "./Composer";

export function ChatPane() {
  const { send } = useChatSocket();
  return (
    <>
      <MessageList />
      <Composer onSend={(text) => send({ kind: "user_msg", content: text })} />
    </>
  );
}
