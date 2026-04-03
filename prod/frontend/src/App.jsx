import React, { useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export default function App() {
  const [city, setCity] = useState("");
  const [minPrice, setMinPrice] = useState("");
  const [maxPrice, setMaxPrice] = useState("");
  const [limit, setLimit] = useState("10");
  const [searchData, setSearchData] = useState(null);

  const [propertyId, setPropertyId] = useState("");
  const [auditData, setAuditData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function postJson(path, payload) {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}${path}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Request failed");
      }
      return data;
    } finally {
      setLoading(false);
    }
  }

  async function handleSearch(e) {
    e.preventDefault();
    setError("");
    setAuditData(null);

    try {
      const data = await postJson("/api/search", {
        city: city || null,
        price_min: minPrice ? Number(minPrice) : null,
        price_max: maxPrice ? Number(maxPrice) : null,
        limit: Number(limit) || 10,
      });

      setSearchData(data);
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleAudit(e) {
    e.preventDefault();
    setError("");
    setSearchData(null);

    try {
      if (!propertyId.trim()) {
        setError("Property ID is required");
        return;
      }
      const data = await postJson("/api/audit", { property_id: propertyId });
      setAuditData(data);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <main style={{ color: "#111", background: "#fff", minHeight: "100vh", padding: "12px" }}>
      <h1>Real Estate</h1>

      <h2>Search</h2>
      <form onSubmit={handleSearch}>
        <input placeholder="City" value={city} onChange={(e) => setCity(e.target.value)} />
        <input placeholder="Min price" type="number" value={minPrice} onChange={(e) => setMinPrice(e.target.value)} />
        <input placeholder="Max price" type="number" value={maxPrice} onChange={(e) => setMaxPrice(e.target.value)} />
        <input placeholder="Limit" type="number" value={limit} onChange={(e) => setLimit(e.target.value)} />
        <button type="submit">Search</button>
      </form>

      {searchData && (
        <div>
          <p>Found {searchData.count} properties</p>
          <ul>
            {searchData.results.map((item) => (
              <li key={item.id}>
                {item.address} - {item.city} (${item.asking_price})
              </li>
            ))}
          </ul>
        </div>
      )}

      <h2>Audit</h2>
      <form onSubmit={handleAudit}>
        <input placeholder="Property ID" value={propertyId} onChange={(e) => setPropertyId(e.target.value)} />
        <button type="submit">Audit</button>
      </form>

      {auditData && (
        <div>
          <p>
            Audit {auditData.action}: {auditData.address} ({auditData.yield.toFixed(2)}%)
          </p>
        </div>
      )}

      {loading && <p>Loading...</p>}
      {error && <p>{error}</p>}
    </main>
  );
}
