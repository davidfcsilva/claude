import { useEffect, useState } from "react";

const API_URL = import.meta.env.VITE_API_URL || "";

export default function App() {
  const [items, setItems] = useState([]);
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const healthRes = await fetch(`${API_URL}/health`);
        if (healthRes.ok) setHealth(await healthRes.json());

        const itemsRes = await fetch(`${API_URL}/api/items`);
        if (itemsRes.ok) setItems(await itemsRes.json());
      } catch {
        // Backend not available — show empty state
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <div style={{ fontFamily: "sans-serif", maxWidth: 600, margin: "40px auto" }}>
      <h1>ArgoCD Demo</h1>

      {health && (
        <section>
          <h2>Backend Status</h2>
          <p>Version: {health.version}</p>
          <p>Status: <strong>{health.status}</strong></p>
        </section>
      )}

      <section>
        <h2>Items ({loading ? "..." : items.length})</h2>
        {loading && <p>Loading...</p>}
        {!loading && items.length > 0 && (
          <ul>
            {items.map((item) => (
              <li key={item.id}>{item.name}</li>
            ))}
          </ul>
        )}
        {!loading && items.length === 0 && <p>No items available.</p>}
      </section>

      <footer style={{ marginTop: 40, fontSize: 14, color: "#888" }}>
        Built with React + FastAPI · Dockerized for ArgoCD
      </footer>
    </div>
  );
}
