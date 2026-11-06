export type DependencyName = "database" | "object_storage" | "queue";

export interface DependencyHealth {
  status: "healthy" | "unhealthy";
  dependencies: Record<DependencyName, "healthy" | "unhealthy">;
}

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function getDependencyHealth(fetcher: typeof fetch = fetch): Promise<DependencyHealth> {
  const response = await fetcher(`${apiUrl}/api/v1/health/dependencies`, { cache: "no-store" });
  if (!response.ok && response.status !== 503) {
    throw new Error("The API is unreachable.");
  }
  return (await response.json()) as DependencyHealth;
}
