"use client";

import { ArrowUpRight, Bot, Send, Sparkles, X } from "lucide-react";
import Link from "next/link";
import React, { useState, type FormEvent } from "react";
import { askShreyasAgent } from "@/lib/api";
import type { AgentCitation } from "@/lib/types";

interface MessageEntry {
  role: "user" | "assistant";
  text: string;
  citations?: AgentCitation[];
}

function citationHref(c: AgentCitation): string {
  const hash = c.slug ? `#${c.slug}` : "";
  switch (c.source_type) {
    case "project":
      return `/projects${hash}`;
    case "experience":
      return `/experience${hash}`;
    case "hackathon":
      return `/hackathons${hash}`;
    case "certificate":
      return `/certificates${hash}`;
    default:
      return `/${hash}`;
  }
}

function renderInlineFormatting(line: string): React.ReactNode[] {
  const parts = line.split(/(\*\*[^*]+\*\*|`[^`]+`)/g);
  return parts.map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return (
        <strong key={i} className="font-semibold text-white">
          {part.slice(2, -2)}
        </strong>
      );
    }
    if (part.startsWith("`") && part.endsWith("`")) {
      return (
        <code
          key={i}
          className="rounded border border-hairline bg-obsidian px-1.5 py-0.5 font-mono text-xs text-cyanPulse"
        >
          {part.slice(1, -1)}
        </code>
      );
    }
    return part;
  });
}

function FormattedMessage({ text }: { text: string }) {
  const lines = text.split("\n");
  const blocks: React.ReactNode[] = [];
  let currentList: {
    type: "bullet" | "numbered";
    items: { prefix?: string; content: string }[];
  } | null = null;

  function flushList() {
    if (!currentList) return;
    if (currentList.type === "bullet") {
      blocks.push(
        <ul key={`list-${blocks.length}`} className="my-2 space-y-2 pl-0.5">
          {currentList.items.map((item, idx) => (
            <li
              key={idx}
              className="flex items-start text-sm leading-relaxed text-slate-200"
            >
              <span className="mr-2.5 mt-1.5 inline-block h-1.5 w-1.5 shrink-0 rounded-full bg-cyanPulse shadow-[0_0_6px_#00F0FF]" />
              <div className="flex-1">{renderInlineFormatting(item.content)}</div>
            </li>
          ))}
        </ul>
      );
    } else {
      blocks.push(
        <ol key={`list-${blocks.length}`} className="my-2 space-y-2 pl-0.5">
          {currentList.items.map((item, idx) => (
            <li
              key={idx}
              className="flex items-start text-sm leading-relaxed text-slate-200"
            >
              <span className="mr-2 mt-0.5 shrink-0 font-mono text-xs font-semibold text-cyanPulse">
                {item.prefix || `${idx + 1}.`}
              </span>
              <div className="flex-1">{renderInlineFormatting(item.content)}</div>
            </li>
          ))}
        </ol>
      );
    }
    currentList = null;
  }

  for (let i = 0; i < lines.length; i++) {
    const rawLine = lines[i];
    const trimmed = rawLine.trim();

    if (!trimmed) {
      flushList();
      continue;
    }

    const bulletMatch = trimmed.match(/^[-*•]\s+(.*)$/);
    if (bulletMatch) {
      if (currentList && currentList.type !== "bullet") {
        flushList();
      }
      if (!currentList) {
        currentList = { type: "bullet", items: [] };
      }
      currentList.items.push({ content: bulletMatch[1] });
      continue;
    }

    const numberMatch = trimmed.match(/^(\d+[\.\)])\s+(.*)$/);
    if (numberMatch) {
      if (currentList && currentList.type !== "numbered") {
        flushList();
      }
      if (!currentList) {
        currentList = { type: "numbered", items: [] };
      }
      currentList.items.push({
        prefix: numberMatch[1],
        content: numberMatch[2],
      });
      continue;
    }

    flushList();
    blocks.push(
      <p
        key={`p-${blocks.length}`}
        className="my-1 text-sm leading-relaxed text-slate-200"
      >
        {renderInlineFormatting(trimmed)}
      </p>
    );
  }

  flushList();

  return <div className="space-y-1">{blocks}</div>;
}

export function AskShreyasDrawer() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<MessageEntry[]>([
    {
      role: "assistant",
      text: "Hi! I know everything about Shreyas's projects, work experience, skills, hackathons, and certifications. What would you like to know?",
    },
  ]);

  async function runQuery(text: string) {
    const trimmed = text.trim();
    if (trimmed.length < 3 || loading) return;

    setMessages((prev) => [...prev, { role: "user", text: trimmed }]);
    setQuery("");
    setLoading(true);
    try {
      const res = await askShreyasAgent(trimmed);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: res.answer, citations: res.citations },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text:
            err instanceof Error
              ? err.message
              : "Rate limit or connection issue. Please try again shortly.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    void runQuery(query);
  }

  function handleCitationClick(e: React.MouseEvent, c: AgentCitation) {
    const href = citationHref(c);
    const targetSlug = c.slug;
    const targetPath = href.split("#")[0] || "/";
    const currentPath = typeof window !== "undefined" ? window.location.pathname : "";

    if (currentPath === targetPath) {
      e.preventDefault();
      if (targetSlug) {
        const el = document.getElementById(targetSlug);
        if (el) {
          el.scrollIntoView({ behavior: "smooth", block: "center" });
          el.classList.add("ring-2", "ring-cyanPulse", "transition-all");
          setTimeout(() => el.classList.remove("ring-2", "ring-cyanPulse"), 2500);
        }
      }
    } else {
      if (typeof window !== "undefined" && window.innerWidth < 768) {
        setOpen(false);
      }
    }
  }

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="fixed bottom-5 right-5 z-40 flex items-center gap-2 rounded-full border border-cyanPulse/40 bg-surface/95 px-4 py-2.5 text-sm font-medium text-[#FAFAFA] shadow-lg backdrop-blur transition hover:border-cyanPulse hover:bg-slate-800"
      >
        <Bot className="h-4 w-4 text-cyanPulse" />
        <span>Shreyas AI</span>
      </button>

      {open && (
        <div className="fixed inset-y-0 right-0 z-50 flex w-full max-w-md flex-col border-l border-hairline bg-obsidian/95 shadow-2xl backdrop-blur-md">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-hairline px-5 py-4">
            <div className="flex items-center gap-2.5">
              <Bot className="h-5 w-5 text-cyanPulse" />
              <div>
                <h2 className="text-sm font-semibold text-[#FAFAFA]">
                  Shreyas AI
                </h2>
                <div className="flex items-center gap-1.5">
                  <span className="inline-block h-1.5 w-1.5 animate-pulse rounded-full bg-emeraldSignal" />
                  <p className="font-mono text-[11px] text-emeraldSignal">
                    Portfolio Assistant
                  </p>
                </div>
              </div>
            </div>
            <button
              type="button"
              onClick={() => setOpen(false)}
              aria-label="Close Shreyas AI"
              className="rounded-md p-1 text-slate-400 hover:bg-slate-800 hover:text-white"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 space-y-4 overflow-y-auto p-5">
            {messages.map((m, idx) => (
              <div
                key={idx}
                className={
                  m.role === "user"
                    ? "ml-8 rounded-lg border border-cyanPulse/30 bg-cyanPulse/10 p-3 text-sm text-[#FAFAFA]"
                    : "mr-3 rounded-lg border border-hairline bg-surface p-3.5"
                }
              >
                {m.role === "user" ? (
                  <p className="leading-relaxed">{m.text}</p>
                ) : (
                  <FormattedMessage text={m.text} />
                )}

                {m.citations && m.citations.length > 0 && (
                  <div className="mt-3 flex flex-wrap items-center gap-1.5 border-t border-hairline pt-2">
                    <span className="font-mono text-[10px] uppercase tracking-wider text-slate-400">
                      Sources:
                    </span>
                    {m.citations.map((c, cIdx) => (
                      <Link
                        key={cIdx}
                        href={citationHref(c)}
                        onClick={(e) => handleCitationClick(e, c)}
                        className="group inline-flex items-center gap-1 rounded border border-hairline bg-obsidian px-2.5 py-1 font-mono text-[11px] text-cyanPulse transition hover:border-cyanPulse hover:bg-surface"
                      >
                        <span>{c.title}</span>
                        <ArrowUpRight className="h-3 w-3 text-cyanPulse/70 transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            ))}
            {loading && (
              <div className="mr-3 flex items-center gap-2 rounded-lg border border-hairline bg-surface p-3 text-xs font-mono text-cyanPulse">
                <Sparkles className="h-3.5 w-3.5 animate-spin text-cyanPulse" />
                <span>Synthesizing answer...</span>
              </div>
            )}
          </div>

          {/* Input Bar (Clean without chips) */}
          <div className="border-t border-hairline bg-surface/80 p-4">
            <form onSubmit={handleSubmit} className="flex gap-2">
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                maxLength={500}
                placeholder="Ask anything about Shreyas..."
                className="flex-1 rounded-lg border border-hairline bg-obsidian px-3 py-2 text-sm text-[#FAFAFA] placeholder:text-slate-500 focus:border-cyanPulse focus:outline-none"
              />
              <button
                type="submit"
                disabled={loading || query.trim().length < 3}
                aria-label="Send query"
                className="rounded-lg bg-cyanPulse px-3.5 py-2 text-obsidian transition hover:bg-cyan-400 disabled:opacity-40"
              >
                <Send className="h-4 w-4" />
              </button>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
