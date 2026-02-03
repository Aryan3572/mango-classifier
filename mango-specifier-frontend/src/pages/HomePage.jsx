// src/pages/HomePage.jsx
import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import UploadArea from "../components/UploadArea";
import { getToken, removeToken } from "../utils/auth";
import { savePredictionAPI } from "../utils/savePrediction";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

export default function HomePage() {
  const nav = useNavigate();
  const [results, setResults] = useState([null, null, null]);
  const [metadata, setMetadata] = useState([null, null, null]);
  const [metrics, setMetrics] = useState(null);

  // ✅ NEW – statistical analysis state
  const [classStats, setClassStats] = useState(null);

  const API_BASE = "http://localhost:5000";

  const fixText = (str) => {
    if (str === null || str === undefined) return "Not available";
    if (typeof str !== "string") return str;
    return str
      .replace(/â€”/g, "—")
      .replace(/â€“/g, "–")
      .replace(/â€˜/g, "‘")
      .replace(/â€™/g, "’")
      .replace(/â€œ/g, "“")
      .replace(/â€/g, "”")
      .replace(/Â°/g, "°")
      .replace(/Â/g, "");
  };

  useEffect(() => {
    fetch(`${API_BASE}/metrics`)
      .then((r) => r.json())
      .then((d) => setMetrics(d))
      .catch(() => {});
  }, []);

  // ✅ NEW – load class distribution statistics once
  useEffect(() => {
    fetch(`${API_BASE}/stats/class-distribution`)
      .then((r) => r.json())
      .then((d) => setClassStats(d))
      .catch(() => {});
  }, []);

  const parsePossiblyDoubleEncodedJSON = (raw) => {
    try {
      return JSON.parse(raw);
    } catch {
      try {
        const fixed = decodeURIComponent(escape(raw));
        return JSON.parse(fixed);
      } catch {
        return null;
      }
    }
  };

  const handleFileUpload = async (file, index) => {
    const newResults = [...results];
    const newMeta = [...metadata];

    newResults[index] = { loading: true };
    newMeta[index] = null;
    setResults(newResults);
    setMetadata(newMeta);

    try {
      const form = new FormData();
      form.append("file", file);

      const res = await fetch(`${API_BASE}/predict`, {
        method: "POST",
        body: form,
      });

      const data = await res.json();
      if (!res.ok && data.error) throw new Error(data.error);

      newResults[index] = data;

      const metaRes = await fetch(
        `${API_BASE}/variety/${data.normalized_class}`
      );
      const raw = await metaRes.text();
      const parsed = parsePossiblyDoubleEncodedJSON(raw) || {};
      newMeta[index] = parsed;

      setResults([...newResults]);
      setMetadata([...newMeta]);
    } catch (err) {
      newResults[index] = { error: err.message || "Prediction failed" };
      setResults([...newResults]);
    }
  };

  const handleSavePrediction = async (i) => {
    try {
      const payload = {
        predicted_class: results[i].predicted_class,
        confidence: results[i].confidence,
        image_name: `upload_${Date.now()}.jpg`,
        metadata: metadata[i],
      };
      await savePredictionAPI(payload);
      alert("Saved!");
    } catch (err) {
      alert("Save failed — please login.");
      nav("/login");
    }
  };

  // ✅ NEW – chart data for class distribution
  const classDistChart =
    classStats?.images_per_class
      ? Object.entries(classStats.images_per_class).map(([k, v]) => ({
          label: k,
          count: v,
        }))
      : [];

  return (
    <div className="app-root">
      <nav className="top-nav">
        <div className="logo">🥭 Mango Specifier</div>
        <div className="nav-right">
          {!getToken() ? (
            <>
              <Link className="nav-btn" to="/login">Login</Link>
              <Link className="nav-btn" to="/signup">Signup</Link>
            </>
          ) : (
            <>
              <button
                className="nav-btn"
                onClick={() => {
                  removeToken();
                  nav("/login");
                }}
              >
                Logout
              </button>
            </>
          )}
        </div>
      </nav>

      <header className="hero">
        <div className="hero-inner">
          <div className="hero-left">
            <h1 className="hero-title">
              Mango Specifier — AI-powered Variety & Market Insights
            </h1>

            <p className="hero-sub">
              Upload a photo of a mango and instantly identify its variety,
              size, sweetness, ideal growing & ripening temps, plus export/demand
              data — backed by horticulture sources.
            </p>

            <div className="hero-cta">
              <a className="btn primary" href="#upload">Try it now</a>
              <Link className="btn ghost" to="/login">Login</Link>
            </div>

            <div className="hero-notes">
              <span>Model accuracy:</span>
              <strong>{metrics ? `${metrics.accuracy}%` : "—"}</strong>
            </div>
          </div>

          <div className="hero-right">
            <div className="hero-card glass">
              <h4>Quick demo</h4>
              <p className="muted">
                Drop an image below — results appear with confidence & market value.
              </p>
              <UploadArea
                title="Try a Demo"
                onFileSelected={(file) => handleFileUpload(file, 0)}
              />
            </div>
          </div>
        </div>
      </header>

      <main className="main" id="upload">
        <section className="upload-section">
          <h2 className="section-title">Upload Images</h2>
          <p className="section-sub muted">
            You can upload up to 3 images. Each will be analyzed individually.
          </p>

          <div className="upload-grid">
            {[0, 1, 2].map((i) => (
              <div key={i} className="upload-column">
                <UploadArea
                  title={`Image ${i + 1}`}
                  onFileSelected={(file) => handleFileUpload(file, i)}
                />

                {results[i]?.loading && (
                  <div className="small-muted">Analyzing image…</div>
                )}
                {results[i]?.error && (
                  <div className="error-text">
                    Error: {results[i].error}
                  </div>
                )}

                {results[i]?.predicted_class && metadata[i] && (
                  <div className="result-card">
                    <div className="result-head">
                      <h3>
                        {fixText(
                          metadata[i].name || results[i].predicted_class
                        )}
                      </h3>
                      <div className="conf">
                        {results[i].confidence}%
                      </div>
                    </div>

                    <div className="result-grid">
                      <div>
                        <small className="muted">Origin</small>
                        <div>{fixText(metadata[i].origin)}</div>

                        <small className="muted">Regions</small>
                        <div>
                          {(metadata[i].regions || [])
                            .map(fixText)
                            .join(", ")}
                        </div>

                        <small className="muted">Sweetness (°Brix)</small>
                        <div>{fixText(metadata[i].avg_brix)}</div>
                      </div>

                      <div>
                        <small className="muted">Avg Weight</small>
                        <div>{fixText(metadata[i].avg_weight_g)} g</div>

                        <small className="muted">Avg Size</small>
                        <div>{fixText(metadata[i].avg_size_cm)}</div>

                        <small className="muted">Season</small>
                        <div>{fixText(metadata[i].season)}</div>
                      </div>
                    </div>

                    <div className="market">
                      <h4>📦 Market Value</h4>
                      <p className="muted">
                        {fixText(metadata[i].demand_value)}
                      </p>
                      <p>
                        <strong>Demand Score:</strong>{" "}
                        {metadata[i].demand_score ?? "N/A"} / 10
                      </p>
                      <p className="muted">
                        <strong>Export:</strong>{" "}
                        {fixText(metadata[i].export_info)}
                      </p>
                    </div>

                    <div style={{ marginTop: 12 }}>
                      {getToken() ? (
                        <button
                          className="btn primary"
                          onClick={() => handleSavePrediction(i)}
                        >
                          Save Result
                        </button>
                      ) : (
                        <Link className="btn ghost" to="/login">
                          Login to Save
                        </Link>
                      )}
                    </div>

                    {results[i].top_predictions && (
                      <div className="chart" style={{ marginTop: 12 }}>
                        <h5>Confidence Breakdown</h5>
                        <ResponsiveContainer width="100%" height={160}>
                          <BarChart data={results[i].top_predictions}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="label" />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Bar
                              dataKey="confidence"
                              fill="#ffb300"
                              barSize={18}
                            />
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    )}

                    {/* ✅ DATASET SPECIFICATIONS */}
                    {results[i]?.dataset_info && (
                      <div
                        className="glass"
                        style={{ marginTop: 14, padding: 12 }}
                      >
                        <h4>📊 Dataset Specifications</h4>

                        <table
                          style={{
                            width: "100%",
                            borderCollapse: "collapse",
                          }}
                        >
                          <tbody>
                            <tr>
                              <td><strong>Camera model</strong></td>
                              <td>{results[i].dataset_info.camera_model}</td>
                            </tr>
                            <tr>
                              <td><strong>Capture settings</strong></td>
                              <td>{results[i].dataset_info.capture_settings}</td>
                            </tr>
                            <tr>
                              <td><strong>Capture environments</strong></td>
                              <td>{results[i].dataset_info.capture_environments}</td>
                            </tr>
                            <tr>
                              <td><strong>Background</strong></td>
                              <td>{results[i].dataset_info.background_standardization}</td>
                            </tr>
                            <tr>
                              <td><strong>Capture angles</strong></td>
                              <td>{results[i].dataset_info.capture_angles}</td>
                            </tr>
                            <tr>
                              <td><strong>Collection location</strong></td>
                              <td>{results[i].dataset_info.collection_location}</td>
                            </tr>
                            <tr>
                              <td><strong>Season</strong></td>
                              <td>{results[i].dataset_info.season}</td>
                            </tr>
                            <tr>
                              <td><strong>Collection stage</strong></td>
                              <td>{results[i].dataset_info.collection_stage}</td>
                            </tr>
                            <tr>
                              <td><strong>Labeling protocol</strong></td>
                              <td>{results[i].dataset_info.labeling_protocol}</td>
                            </tr>
                            <tr>
                              <td><strong>Total varieties</strong></td>
                              <td>{results[i].dataset_info.total_varieties}</td>
                            </tr>
                          </tbody>
                        </table>
                      </div>
                    )}

                    {/* ✅ STATISTICAL ANALYSIS – CLASS DISTRIBUTION */}
                    {classStats && (
                      <div
                        className="glass"
                        style={{ marginTop: 16, padding: 12 }}
                      >
                        <h4>📈 Dataset Class Distribution</h4>

                        <p className="muted">
                          Total images: {classStats.total_images} | Classes:{" "}
                          {classStats.total_classes}
                        </p>

                        <p className="muted">
                          Imbalance ratio (max / min):{" "}
                          {classStats.imbalance_ratio}
                        </p>

                        <div style={{ width: "100%", height: 220 }}>
                          <ResponsiveContainer>
                            <BarChart data={classDistChart}>
                              <CartesianGrid strokeDasharray="3 3" />
                              <XAxis dataKey="label" />
                              <YAxis />
                              <Tooltip />
                              <Bar dataKey="count" fill="#66bb6a" />
                            </BarChart>
                          </ResponsiveContainer>
                        </div>
                      </div>
                    )}

                    <div className="sources" style={{ marginTop: 10 }}>
                      <h5>Sources</h5>
                      <ul>
                        {(metadata[i].export_sources || []).map((s, idx) => (
                          <li key={idx}>
                            <a
                              href={s.url}
                              target="_blank"
                              rel="noreferrer"
                            >
                              {fixText(s.label)}
                            </a>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>

        <section className="about" id="about">
          <div className="about-inner glass">
            <h3>About Mango Specifier</h3>
            <p className="muted">
              Uses a MobileNet-based model to classify mango varieties.
              Metadata is collected from NHB, APEDA, and cultivar literature.
              Save predictions to your account for later reference.
            </p>
          </div>
        </section>
      </main>

      <footer className="footer">
        <div>
          © {new Date().getFullYear()} Mango Specifier · Built by Aryan Raj
        </div>
        <div className="muted">
          Model accuracy: {metrics ? `${metrics.accuracy}%` : "—"}
        </div>
      </footer>
    </div>
  );
}
