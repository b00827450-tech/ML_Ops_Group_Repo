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
  const [anomalyPropertyId, setAnomalyPropertyId] = useState("");
  const [anomalyData, setAnomalyData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function getJson(path, params = null) {
    setLoading(true);
    try {
      const url = new URL(`${API_BASE}${path}`);
      if (params) {
        for (const [key, value] of Object.entries(params)) {
          if (value != null && value !== "") {
            url.searchParams.set(key, value);
          }
        }
      }
      const response = await fetch(url);

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
    setAnomalyData(null);

    try {
      const data = await getJson("/api/search", {
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
      const data = await getJson(`/api/audit/${encodeURIComponent(propertyId)}`);
      setAuditData(data);
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleAnomaly(e) {
    e.preventDefault();
    setError("");

    try {
      if (!anomalyPropertyId.trim()) {
        setError("Property ID is required");
        return;
      }
      const data = await getJson(`/api/anomaly/${encodeURIComponent(anomalyPropertyId)}`);
      setAnomalyData(data);
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
                {item.address} - {item.city} (${item.asking_price}) - ID: {item.id}
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
          <p>Estimated rental income: ${auditData.estimated_rental_income.toFixed(2)} / year</p>
          <p>Estimated maintenance costs: ${auditData.estimated_maintenance_costs.toFixed(2)} / year</p>
        </div>
      )}

      <h2>Anomaly Detection</h2>
      <form onSubmit={handleAnomaly}>
        <input
          placeholder="Property ID"
          value={anomalyPropertyId}
          onChange={(e) => setAnomalyPropertyId(e.target.value)}
        />
        <button type="submit">Detect anomaly</button>
      </form>

      {anomalyData && (
        <div>
          <p>
            Anomaly {anomalyData.action}: {anomalyData.address} (
            {anomalyData.yield == null ? "yield n/a" : `${anomalyData.yield.toFixed(2)}%`})
          </p>
          <p>
            {anomalyData.red_flag
              ? `Red flag triggered (${anomalyData.comparables_analyzed} comparables analyzed)`
              : "No anomaly triggered"}
          </p>
          {anomalyData.price_per_square_meter != null && (
            <p>Price per sqm: ${anomalyData.price_per_square_meter.toFixed(2)}</p>
          )}
          {anomalyData.peer_average_price_per_square_meter != null && (
            <p>
              Peer average price per sqm: ${anomalyData.peer_average_price_per_square_meter.toFixed(2)}
            </p>
          )}
          {anomalyData.anomalies?.length > 0 && (
            <ul>
              {anomalyData.anomalies.map((item) => (
                <li key={`${item.flag_type}-${item.id}`}>
                  {item.flag_type}: {item.description}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      {loading && <p>Loading...</p>}
      {error && <p>{error}</p>}
    </main>
  );
}
