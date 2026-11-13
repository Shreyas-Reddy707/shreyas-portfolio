"use client";

import { Download, ExternalLink, FileText, X } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";

interface PdfViewerModalProps {
  isOpen: boolean;
  onClose: () => void;
  pdfUrl?: string | null;
  title: string;
  subtitle?: string;
}

export function PdfViewerModal({
  isOpen,
  onClose,
  pdfUrl,
  title,
  subtitle,
}: PdfViewerModalProps) {
  const [mounted, setMounted] = useState(false);
  const dialogRef = useRef<HTMLDivElement>(null);
  const previouslyFocusedElementRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    const isVisible = isOpen && Boolean(pdfUrl) && mounted;
    if (!isVisible) return;

    previouslyFocusedElementRef.current = document.activeElement as HTMLElement | null;
    document.body.style.overflow = "hidden";

    const mainElement = document.querySelector("main");
    const canHideMain = Boolean(mainElement && !mainElement.contains(dialogRef.current));
    if (canHideMain && mainElement) {
      mainElement.setAttribute("aria-hidden", "true");
    }

    const focusableSelector =
      'button, [href], input, select, textarea, iframe, [tabindex]:not([tabindex="-1"])';

    const focusable = dialogRef.current?.querySelectorAll<HTMLElement>(focusableSelector);
    if (focusable && focusable.length > 0) {
      focusable[0].focus();
    } else {
      dialogRef.current?.focus();
    }

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.preventDefault();
        onClose();
        return;
      }
      if (e.key === "Tab" && dialogRef.current) {
        const focusableNodes = Array.from(
          dialogRef.current.querySelectorAll<HTMLElement>(focusableSelector)
        ).filter((el) => !el.hasAttribute("disabled"));

        if (focusableNodes.length === 0) return;

        const first = focusableNodes[0];
        const last = focusableNodes[focusableNodes.length - 1];

        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault();
          last.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();
          first.focus();
        }
      }
    };

    window.addEventListener("keydown", handleKeyDown);

    return () => {
      document.body.style.overflow = "auto";
      window.removeEventListener("keydown", handleKeyDown);
      if (canHideMain && mainElement) {
        mainElement.removeAttribute("aria-hidden");
      }
      previouslyFocusedElementRef.current?.focus();
    };
  }, [isOpen, pdfUrl, mounted, onClose]);

  if (!isOpen || !pdfUrl || !mounted) return null;

  const modalContent = (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-black/85 backdrop-blur-md transition-opacity duration-200"
      onClick={onClose}
    >
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="pdf-modal-title"
        tabIndex={-1}
        className="relative flex flex-col w-full max-w-5xl h-[88vh] rounded-2xl border border-hairline bg-[#0B0F17] shadow-2xl shadow-black/80 overflow-hidden focus:outline-none"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-hairline bg-surface/90">
          <div className="flex items-center gap-3 min-w-0 pr-4">
            <div className="p-2 rounded-lg border border-hairline bg-obsidian text-cyanPulse shrink-0">
              <FileText className="h-5 w-5" />
            </div>
            <div className="min-w-0">
              <h3
                id="pdf-modal-title"
                className="text-sm sm:text-base font-bold text-[#FAFAFA] truncate"
              >
                {title}
              </h3>
              {subtitle && (
                <p className="text-xs font-mono text-slate-400 truncate">
                  {subtitle}
                </p>
              )}
            </div>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <a
              href={pdfUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-hairline bg-obsidian hover:bg-surface text-xs font-mono text-slate-300 hover:text-white transition"
              title="Open PDF in new tab"
            >
              <ExternalLink className="h-3.5 w-3.5 text-cyanPulse" />
              <span className="hidden sm:inline">New Tab</span>
            </a>
            <a
              href={pdfUrl}
              download
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-hairline bg-obsidian hover:bg-surface text-xs font-mono text-slate-300 hover:text-white transition"
              title="Download PDF"
            >
              <Download className="h-3.5 w-3.5 text-emeraldSignal" />
              <span className="hidden sm:inline">Download</span>
            </a>
            <button
              type="button"
              onClick={onClose}
              className="p-1.5 rounded-lg border border-hairline bg-obsidian text-slate-400 hover:text-white hover:border-slate-500 transition"
              aria-label="Close modal"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Modal Iframe Content */}
        <div className="relative flex-1 bg-obsidian/90 overflow-hidden">
          <iframe
            src={`${pdfUrl}#toolbar=0&navpanes=0`}
            className="w-full h-full border-0 focus:outline-none focus:ring-1 focus:ring-cyanPulse/50"
            title={title}
            tabIndex={0}
          />
        </div>

        {/* Modal Footer */}
        <div className="flex items-center justify-between px-5 py-2.5 border-t border-hairline bg-surface/70 font-mono text-[11px] text-slate-400">
          <span>Asset: {pdfUrl}</span>
          <span>Press ESC or click outside to dismiss</span>
        </div>
      </div>
    </div>
  );

  return typeof document !== "undefined" ? createPortal(modalContent, document.body) : null;
}
