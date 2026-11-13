import crypto from "node:crypto";
import { revalidateTag } from "next/cache";
import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  const expected = process.env.NEXTJS_REVALIDATE_SECRET || "";
  const provided = request.headers.get("x-revalidate-secret") || "";

  if (!expected || !provided) {
    return NextResponse.json(
      { error_code: "UNAUTHORIZED", message: "Missing revalidation secret." },
      { status: 401 }
    );
  }

  const expectedBuf = Buffer.from(expected, "utf-8");
  const providedBuf = Buffer.from(provided, "utf-8");
  if (
    expectedBuf.length !== providedBuf.length ||
    !crypto.timingSafeEqual(expectedBuf, providedBuf)
  ) {
    return NextResponse.json(
      { error_code: "UNAUTHORIZED", message: "Invalid revalidation secret." },
      { status: 401 }
    );
  }

  revalidateTag("portfolio");
  return NextResponse.json({ revalidated: true, tag: "portfolio" });
}

