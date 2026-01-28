"use client";

import { usePathname } from "next/navigation";
import AgentWidget from "./agent-widget";

// Paths where the widget should NOT appear
const EXCLUDED_PATHS = ["/auth"];

export default function AgentWidgetWrapper() {
  const pathname = usePathname();

  // Check if current path starts with any excluded path
  const shouldHideWidget = EXCLUDED_PATHS.some((path) =>
    pathname.startsWith(path)
  );

  if (shouldHideWidget) {
    return null;
  }

  return <AgentWidget />;
}
