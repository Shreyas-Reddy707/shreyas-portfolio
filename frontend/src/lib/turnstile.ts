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
          size?: "invisible" | "normal" | "compact";
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

  scriptLoadPromise = new Promise((resolve) => {
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
      }, 3500);
      return;
    }

    const script = document.createElement("script");
    script.src = TURNSTILE_SCRIPT_SRC;
    script.async = true;
    script.defer = true;
    script.onload = () => resolve();
    script.onerror = () => {
      console.warn("Turnstile script unavailable. Using fallback test token.");
      resolve();
    };
    document.head.appendChild(script);

    setTimeout(() => resolve(), 3500);
  });

  return scriptLoadPromise;
}

/**
 * Obtains a fresh Cloudflare Turnstile verification token.
 * If running on localhost or with local test keys, returns DEV_TURNSTILE_TOKEN.
 * If configured with a live Cloudflare site key (0x4...), runs an invisible offscreen challenge.
 */
export async function getTurnstileToken(action = "general"): Promise<string> {
  if (typeof window === "undefined") {
    return DEV_TURNSTILE_TOKEN;
  }

  const siteKey = process.env.NEXT_PUBLIC_TURNSTILE_SITE_KEY;
  const isRealKey = Boolean(siteKey && siteKey.startsWith("0x4"));

  // Development / dummy key fast-path
  if (!isRealKey) {
    return DEV_TURNSTILE_TOKEN;
  }

  try {
    await loadTurnstileScript();

    const turnstile = window.turnstile;
    if (!turnstile) {
      return DEV_TURNSTILE_TOKEN;
    }

    return await new Promise<string>((resolve) => {
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

      const timer = setTimeout(() => {
        cleanup();
        resolve(DEV_TURNSTILE_TOKEN);
      }, 4000);

      try {
        widgetId = turnstile.render(container, {
          sitekey: siteKey!,
          size: "invisible",
          action,
          callback: (token: string) => {
            clearTimeout(timer);
            cleanup();
            resolve(token);
          },
          "error-callback": () => {
            clearTimeout(timer);
            cleanup();
            resolve(DEV_TURNSTILE_TOKEN);
          },
        });
      } catch {
        clearTimeout(timer);
        cleanup();
        resolve(DEV_TURNSTILE_TOKEN);
      }
    });
  } catch {
    return DEV_TURNSTILE_TOKEN;
  }
}
