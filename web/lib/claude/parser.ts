import type { ClaudeEvent } from "./types";

export function parseLine(line: string): ClaudeEvent[] {
  const s = line.trim();
  if (!s) return [];
  let data: unknown;
  try {
    data = JSON.parse(s);
  } catch (err) {
    return [{ kind: "parse_error", raw: s, reason: (err as Error).message }];
  }
  return parseEvent(data as Record<string, unknown>);
}

function parseEvent(data: Record<string, unknown>): ClaudeEvent[] {
  const t = (data?.type as string | undefined) ?? "";

  // System init — detected by subtype, NOT by line position
  if (t === "system" && (data.subtype as string) === "init") {
    return [
      {
        kind: "system_init",
        session_id: (data.session_id as string) ?? "",
        model: data.model as string | undefined,
        cwd: data.cwd as string | undefined,
      },
    ];
  }

  // Other system events (hook_started, hook_response, etc.) — pass through as unknown
  if (t === "system") {
    return [{ kind: "unknown", raw: data }];
  }

  // stream_event wraps content_block_delta when partial-message streaming is enabled.
  // We currently spawn claude without that flag (only whole-message turns), so this
  // branch is defensive — preserved for forward compatibility / fixture parity.
  if (t === "stream_event") {
    const ev = data.event as Record<string, unknown> | undefined;
    if (ev?.type === "content_block_delta") {
      const delta = ev.delta as Record<string, unknown> | undefined;
      if (delta?.type === "text_delta") {
        return [{ kind: "text_delta", text: (delta.text as string) ?? "" }];
      }
    }
    return [{ kind: "unknown", raw: data }];
  }

  // assistant — whole-message text or tool_use; may contain multiple blocks
  if (t === "assistant") {
    const message = data.message as Record<string, unknown> | undefined;
    const blocks = (message?.content as Array<Record<string, unknown>> | undefined) ?? [];
    const events: ClaudeEvent[] = [];
    for (const block of blocks) {
      if (block?.type === "text") {
        events.push({ kind: "text_delta", text: (block.text as string) ?? "" });
      } else if (block?.type === "tool_use") {
        events.push({
          kind: "tool_use_start",
          id: (block.id as string) ?? "",
          name: (block.name as string) ?? "",
          input: block.input ?? {},
        });
      } else {
        // thinking blocks and anything else: unknown
        events.push({ kind: "unknown", raw: block });
      }
    }
    if (events.length === 0) return [{ kind: "unknown", raw: data }];
    return events;
  }

  // user — wraps tool_result blocks; may contain multiple blocks
  if (t === "user") {
    const message = data.message as Record<string, unknown> | undefined;
    const blocks = (message?.content as Array<Record<string, unknown>> | undefined) ?? [];
    const events: ClaudeEvent[] = [];
    for (const block of blocks) {
      if (block?.type === "tool_result") {
        events.push({
          kind: "tool_result",
          tool_use_id: (block.tool_use_id as string) ?? "",
          content: block.content ?? "",
          is_error: !!block.is_error,
        });
      } else {
        events.push({ kind: "unknown", raw: block });
      }
    }
    if (events.length === 0) return [{ kind: "unknown", raw: data }];
    return events;
  }

  if (t === "result") {
    return [
      {
        kind: "result",
        session_id: (data.session_id as string) ?? "",
        duration_ms: data.duration_ms as number | undefined,
        cost_usd:
          (data.total_cost_usd as number | undefined) ?? (data.cost_usd as number | undefined),
        permission_denials:
          (data.permission_denials as Array<{
            tool_name: string;
            tool_use_id: string;
            tool_input: unknown;
          }> | undefined) ?? [],
      },
    ];
  }

  return [{ kind: "unknown", raw: data }];
}
