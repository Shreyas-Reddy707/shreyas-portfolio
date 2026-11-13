const TURNSTILE_SCRIPT_SRC =
  "https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit";

export const DEV_TURNSTILE_TOKEN = "test_valid_turnstile_token";

declare global {
  interface Window {
    turnstile?: {
      render: (
        container: string | HTMLElement,
        params: {
          sitekey: string;
          callback?: (token: string) => void;
          "error-callback"?: (error: unknown) => void;
          "expired-callback"?: () => void;
          size?: "normal" | "flexible" | "compact";
          theme?: "auto" | "light" | "dark";
          action?: string;
        }
      ) => string;
      reset: (widgetId: string) => void;
      remove: (widgetId: string) => void;
    };
  }
}

let scriptLoadPromise: Promise<void> | null = null;

function loadTurnstileScript(): Promise<void> {
  if (typeof window === "undefined") {
    return Promise.resolve();
  }
  if (window.turnstile) {
    return Promise.resolve();
  }
  if (scriptLoadPromise) {
    return scriptLoadPromise;
  }

  scriptLoadPromise = new Promise<void>((resolve, reject) => {
    const existing = document.querySelector(`script[src*="turnstile/v0/api.js"]`);
    if (existing) {
      const checkInterval = setInterval(() => {
        if (window.turnstile) {
          clearInterval(checkInterval);
          resolve();
        }
      }, 50);
      setTimeout(() => {
        clearInterval(checkInterval);
        resolve();
      }, 5000);
      return;
    }

    const script = document.createElement("script");
    script.src = TURNSTILE_SCRIPT_SRC;
    script.async = true;
    script.defer = true;
    script.onload = () => resolve();
    script.onerror = () => {
      console.warn("Turnstile script unavailable.");
      if (script.parentNode) {
        script.parentNode.removeChild(script);
      }
      scriptLoadPromise = null;
      reject(new Error("Failed to load Turnstile script."));
    };
    document.head.appendChild(script);

    setTimeout(() => resolve(), 5000);
  });

  return scriptLoadPromise;
}

/**
 * Obtains a fresh Cloudflare Turnstile verification token.
 *
 * In development or when using test keys (e.g. 1x00000000000000000000AA), returns DEV_TURNSTILE_TOKEN.
 * In production with a live Cloudflare site key (0x4...), runs an invisible offscreen challenge.
 *
 * MANDATORY REQUIREMENT:
 * The deployed NEXT_PUBLIC_TURNSTILE_SITE_KEY must be created in Cloudflare Dashboard with mode "Invisible".
 * Managed mode challenges require visual user interaction and will fail inside offscreen containers.
 */
export async function getTurnstileToken(action = "general"): Promise<string> {
  if (typeof window === "undefined") {
    return DEV_TURNSTILE_TOKEN;
  }

  const siteKey = process.env.NEXT_PUBLIC_TURNSTILE_SITE_KEY;
  const isDev = process.env.NODE_ENV !== "production";
  const isConfiguredKey = Boolean(
    siteKey &&
      (siteKey.startsWith("0x4") ||
        siteKey.startsWith("1x") ||
        siteKey.startsWith("2x") ||
        siteKey.startsWith("3x"))
  );

  // Return test token only in development when no valid Cloudflare site key is configured
  if (isDev && !isConfiguredKey) {
    return DEV_TURNSTILE_TOKEN;
  }

  await loadTurnstileScript();

  const turnstile = window.turnstile;
  if (!turnstile) {
    if (isDev) return DEV_TURNSTILE_TOKEN;
    throw new Error(
      "Cloudflare Turnstile verification is temporarily unavailable. Please retry."
    );
  }

  return await new Promise<string>((resolve, reject) => {
    const container = document.createElement("div");
    container.style.position = "fixed";
    container.style.left = "-9999px";
    container.style.top = "-9999px";
    container.style.width = "0";
    container.style.height = "0";
    container.style.opacity = "0";
    document.body.appendChild(container);

    let widgetId = "";
    let settled = false;

    const cleanup = () => {
      if (!settled) {
        settled = true;
        try {
          if (widgetId) {
            turnstile.remove(widgetId);
          }
        } catch {
          // Ignore widget teardown errors
        }
        if (container.parentNode) {
          container.parentNode.removeChild(container);
        }
      }
    };

    // 10-second deadline for genuine challenges over slow networks
    const timer = setTimeout(() => {
      cleanup();
      if (isDev) {
        resolve(DEV_TURNSTILE_TOKEN);
      } else {
        reject(new Error("Verification challenge timed out. Please try again."));
      }
    }, 10000);

    try {
      widgetId = turnstile.render(container, {
        sitekey: siteKey!,
        // NOTE: Invisible Turnstile widgets are configured via Cloudflare Dashboard (mode: Invisible).
        // The 'size' parameter is intentionally omitted to avoid invalid 'invisible' size warnings.
        action,
        callback: (token: string) => {
          clearTimeout(timer);
          cleanup();
          resolve(token);
        },
        "error-callback": () => {
          clearTimeout(timer);
          cleanup();
          if (isDev) {
            resolve(DEV_TURNSTILE_TOKEN);
          } else {
            reject(new Error("Verification challenge failed. Please try again."));
          }
        },
      });
    } catch (renderErr) {
      clearTimeout(timer);
      cleanup();
      if (isDev) {
        resolve(DEV_TURNSTILE_TOKEN);
      } else {
        reject(
          new Error(
            renderErr instanceof Error
              ? renderErr.message
              : "Failed to initialize verification challenge. Please retry."
          )
        );
      }
    }
  });
}
