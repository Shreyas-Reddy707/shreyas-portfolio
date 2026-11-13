"use client";

import React, { Component, type ErrorInfo, type ReactNode } from "react";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
}

export class SceneErrorBoundary extends Component<Props, State> {
  public state: State = { hasError: false };

  public static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  public componentDidCatch(error: Error, info: ErrorInfo): void {
    console.warn("WebGL scene fallback activated:", error.message, info.componentStack);
  }

  public componentDidUpdate(prevProps: Props): void {
    if (prevProps.children !== this.props.children && this.state.hasError) {
      this.setState({ hasError: false });
    }
  }

  public render(): ReactNode {
    if (this.state.hasError) {
      return (
        <div
          aria-hidden="true"
          className="pointer-events-none fixed inset-0 z-0 cad-grid-bg opacity-40"
        >
          <svg
            className="h-full w-full opacity-30"
            xmlns="http://www.w3.org/2000/svg"
          >
            <defs>
              <pattern
                id="cad-blueprint"
                width="96"
                height="96"
                patternUnits="userSpaceOnUse"
              >
                <path
                  d="M 96 0 L 0 0 0 96"
                  fill="none"
                  stroke="#06B6D4"
                  strokeWidth="0.5"
                />
                <circle cx="48" cy="48" r="2" fill="#10B981" />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#cad-blueprint)" />
          </svg>
        </div>
      );
    }
    return this.props.children;
  }
}

