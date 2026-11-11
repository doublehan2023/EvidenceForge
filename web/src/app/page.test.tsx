import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import Home from "./page";

const mockedFetch = vi.fn();

describe("Home", () => {
  beforeEach(() => {
    mockedFetch.mockReset();
    vi.stubGlobal("fetch", mockedFetch);
  });

  afterEach(cleanup);

  it("shows healthy dependency state", async () => {
    mockedFetch.mockResolvedValue({
      ok: true,
      json: async () => ({ status: "healthy", dependencies: { database: "healthy", object_storage: "healthy", queue: "healthy" } }),
    });
    render(<Home />);
    expect(await screen.findByText("database: healthy")).toBeInTheDocument();
    expect(screen.getByText("object storage: healthy")).toBeInTheDocument();
  });

  it("shows an unreachable API", async () => {
    mockedFetch.mockRejectedValue(new Error("network down"));
    render(<Home />);
    expect(await screen.findByRole("alert")).toHaveTextContent("API unreachable");
  });

  it("shows unhealthy dependency state and retries", async () => {
    mockedFetch.mockResolvedValue({
      ok: false,
      status: 503,
      json: async () => ({ status: "unhealthy", dependencies: { database: "unhealthy", object_storage: "healthy", queue: "healthy" } }),
    });
    render(<Home />);
    expect(await screen.findByText("database: unhealthy")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Retry health check" }));
    await waitFor(() => expect(mockedFetch).toHaveBeenCalledTimes(2));
  });
});
