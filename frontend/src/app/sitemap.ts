import type { MetadataRoute } from "next";

export default function sitemap(): MetadataRoute.Sitemap {
  const baseUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://shreyasreddy.dev";
  const now = new Date();
  const routes = [
    "",
    "/projects",
    "/experience",
    "/hackathons",
    "/certificates",
    "/privacy",
    "/terms",
  ];
  return routes.map((route) => ({
    url: `${baseUrl}${route}`,
    lastModified: now,
    changeFrequency: route === "/projects" ? "daily" : "weekly",
    priority: route === "" ? 1.0 : 0.8,
  }));
}

