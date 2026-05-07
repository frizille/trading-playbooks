"use client";
import { useEffect, useRef } from "react";
import { useChatStore } from "@/stores/chatStore";
import { MessageBubble } from "./MessageBubble";

export function MessageList() {
  const messages = useChatStore((s) => s.messages);
  const scrollerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollerRef.current?.scrollTo({ top: scrollerRef.current.scrollHeight });
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center text-muted text-sm">
        Ask Claude something to begin.
      </div>
    );
  }
  return (
    <div
      ref={scrollerRef}
      className="flex-1 overflow-y-auto px-4 py-4 flex flex-col gap-4 min-h-0"
    >
      {messages.map((m) => (
        <MessageBubble key={m.id} message={m} />
      ))}
    </div>
  );
}
