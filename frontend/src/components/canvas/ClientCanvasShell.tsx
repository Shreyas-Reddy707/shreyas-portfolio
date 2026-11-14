"use client";

import dynamic from "next/dynamic";

const PersistentCanvas = dynamic(
  () => import("./PersistentCanvas").then((mod) => mod.PersistentCanvas),
  { ssr: false }
);

export function ClientCanvasShell() {
  return <PersistentCanvas />;
}

