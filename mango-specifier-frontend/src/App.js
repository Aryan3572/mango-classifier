import React, { useEffect, useState } from "react";
import UploadArea from "./components/UploadArea";
import "./App.css";

function App() {
  const [metrics, setMetrics] = useState(null);

  // Fetch model performance metrics
  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const res = await fetch("http://localhost:5000/metrics");
        const data = await res.json();
        setMetrics(data);
      } catch (err) {
        console.error("Error fetching metrics:", err);
      }
    };
    fetchMetrics();
  }, []);

  return (
    <div className="app">
      {/* 🌿 Landing Section */}
      <header className="header">
        <h1 className="main-title">Mango Specifier 🥭</h1>
        <p className="subtitle">
          Upload up to three mango images and identify their varieties instantly!
        </p>
      </header>

      {/* 📊 Model Performance Dashboard */}
      {metrics && (
        <section className="metrics-section fade-in">
          <h2 className="metrics-title">Model Performance Dashboard</h2>
          <div className="metrics-grid">
            <div className="metric-card">
              <h3>Accuracy</h3>
              <p>{metrics.accuracy}%</p>
            </div>
            <div className="metric-card">
              <h3>Precision</h3>
              <p>{metrics.precision}%</p>
            </div>
            <div className="metric-card">
              <h3>Recall</h3>
              <p>{metrics.recall}%</p>
            </div>
            <div className="metric-card">
              <h3>F1 Score</h3>
              <p>{metrics.f1_score}%</p>
            </div>
          </div>
        </section>
      )}

      {/* 🍃 Upload Section */}
      <div className="upload-grid">
        <UploadArea title="Mango Image 1" />
        <UploadArea title="Mango Image 2" />
        <UploadArea title="Mango Image 3" />
      </div>

      {/* 🌼 Footer */}
      <footer className="footer">
        <p>
          Built with ❤️ by <span className="highlight">Aryan Raj</span> · Mango
          Classification Project
        </p>
      </footer>
    </div>
  );
}

export default App;
