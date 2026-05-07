"use client";
import { useEffect, useRef } from "react";
import { useChatStore } from "@/stores/chatStore";

type Server =
  | { type: "session_started"; session_id: string }
  | { type: "subscribed"; session_id: string }
  | { type: "replay_user_msg"; session_id: string; content: string }
  | { type: "replay_done"; session_id: string }
  | { type: "text_delta"; session_id: string; content: string }
  | { type: "tool_use_start"; session_id: string; id: string; name: string; args: unknown }
  | { type: "tool_use_result"; session_id: string; id: string; result: unknown; error?: string }
  | {
      type: "result";
      session_id: string;
      permission_denials: Array<{ tool_name: string; tool_use_id: string; tool_input: unknown }>;
    }
  | { type: "error"; session_id?: string; reason: string; detail?: string };

export type SendOpts =
  | { kind: "user_msg"; content: string }
  | { kind: "subscribe"; session_id: string }
  | { kind: "cancel" };

export function useChatSocket() {
  const ws = useRef<WebSocket | null>(null);
  const reconnectAttempts = useRef(0);

  useEffect(() => {
    let cancelled = false;
    const open = () => {
      if (cancelled) return;
      const sock = new WebSocket(`ws://${location.host}/ws`);
      ws.current = sock;

      sock.onopen = () => {
        reconnectAttempts.current = 0;
        useChatStore.getState().setConnected(true);
      };
      sock.onclose = () => {
        useChatStore.getState().setConnected(false);
        if (cancelled) return;
        const delay = Math.min(1000 * 2 ** reconnectAttempts.current++, 10_000);
        setTimeout(open, delay);
      };
      sock.onerror = () => sock.close();
      sock.onmessage = (e) => handle(JSON.parse(e.data) as Server);
    };
    open();
    return () => {
      cancelled = true;
      ws.current?.close();
    };
  }, []);

  function handle(m: Server) {
    const s = useChatStore.getState();
    switch (m.type) {
      case "session_started":
      case "subscribed":
        s.setSessionId(m.session_id);
        s.setError(null);
        break;

      case "replay_user_msg": {
        // Finalize any unfinished assistant turn before starting the next user turn,
        // so each turn renders as its own bubble cluster.
        const last = s.messages[s.messages.length - 1];
        if (last?.role === "assistant" && !last.done) s.finishAssistant();
        s.appendUser(m.content);
        break;
      }

      case "replay_done": {
        // Mark trailing assistant turn as done if not already
        const last = s.messages[s.messages.length - 1];
        if (last?.role === "assistant" && !last.done) s.finishAssistant();
        break;
      }

      case "text_delta": {
        const last = s.messages[s.messages.length - 1];
        if (!last || last.role === "user" || (last.role === "assistant" && last.done)) {
          s.startAssistant();
        }
        s.appendDelta(m.content);
        break;
      }

      case "tool_use_start": {
        const last = s.messages[s.messages.length - 1];
        if (!last || last.role === "user" || (last.role === "assistant" && last.done)) {
          s.startAssistant();
        }
        s.addToolStart({ id: m.id, name: m.name, args: m.args });
        break;
      }

      case "tool_use_result":
        s.addToolResult(m.id, m.result, m.error);
        break;

      case "result":
        s.setPermissionDenials(m.permission_denials);
        s.finishAssistant();
        break;

      case "error":
        // eslint-disable-next-line no-console
        console.warn("[ws error]", m.reason, m.detail);
        useChatStore
          .getState()
          .setError(`${m.reason}${m.detail ? `: ${m.detail}` : ""}`);
        break;
    }
  }

  function send(opts: SendOpts) {
    const sock = ws.current;
    if (!sock || sock.readyState !== WebSocket.OPEN) return;
    const sessionId = useChatStore.getState().sessionId;
    if (opts.kind === "user_msg") {
      useChatStore.getState().appendUser(opts.content);
      sock.send(
        JSON.stringify(
          sessionId
            ? { type: "user_msg", session_id: sessionId, content: opts.content }
            : { type: "user_msg", content: opts.content },
        ),
      );
    } else if (opts.kind === "subscribe") {
      sock.send(JSON.stringify({ type: "subscribe", session_id: opts.session_id }));
    } else if (opts.kind === "cancel") {
      if (!sessionId) return;
      sock.send(JSON.stringify({ type: "cancel", session_id: sessionId }));
    }
  }

  return { send };
}
