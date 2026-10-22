import { useQuery } from "@tanstack/react-query";

import { fetchConfig } from "./api/client";
import { ModeBadge } from "./components/ModeBadge";

export function App() {
  const config = useQuery({ queryKey: ["config"], queryFn: fetchConfig });

  return (
    <main className="shell">
      <header className="masthead">
        <h1>AgentShelf</h1>
        {config.data && <ModeBadge mode={config.data.mode} />}
      </header>
      <p className="tagline">
        Make sure AI shopping agents choose your products, then prove it with a PayPal checkout.
      </p>
      {config.isPending && <p role="status">Connecting to the backend…</p>}
      {config.isError && <p role="alert">Backend unreachable: {config.error.message}</p>}
      {config.data && (
        <p className="note">Scaffold ready. Features arrive in the next build sessions.</p>
      )}
    </main>
  );
}
