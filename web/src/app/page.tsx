"use client";

import { useCallback, useEffect, useState } from "react";

import { DependencyHealth, DependencyName, getDependencyHealth } from "../lib/api";

const dependencies: DependencyName[] = ["database", "object_storage", "queue"];

export default function Home() {
  const [health, setHealth] = useState<DependencyHealth | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setHealth(await getDependencyHealth());
    } catch (caught) {
      setHealth(null);
      setError(caught instanceof Error ? caught.message : "The API is unreachable.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  return (
    <main>
      <p className="eyebrow">EvidenceForge · Phase 0</p>
      <h1>Local platform status</h1>
      <p>Verify that the API and its foundational dependencies are ready for development.</p>
      <button onClick={() => void refresh()} disabled={loading}>
        {loading ? "Checking…" : "Retry health check"}
      </button>
      {error ? <p role="alert">API unreachable: {error}</p> : null}
      {health ? (
        <section aria-label="Dependency health">
          <p>API: {health.status}</p>
          <ul>
            {dependencies.map((dependency) => (
              <li key={dependency}>
                {dependency.replace("_", " ")}: {health.dependencies[dependency]}
              </li>
            ))}
          </ul>
        </section>
      ) : null}
    </main>
  );
}
