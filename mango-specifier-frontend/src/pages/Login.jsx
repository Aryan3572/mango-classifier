// src/pages/Login.jsx
import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./Auth.css";
import { saveToken } from "../utils/auth";

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const API_BASE = "http://localhost:5000";

  const submitLogin = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.error);

      saveToken(data.token);
      navigate("/");
    } catch (err) {
      alert("Login failed: " + err.message);
    }
  };

  return (
    <div className="auth-wrapper">
      <div className="info-panel glass">
        <h1>Mango Specifier AI 🥭</h1>
        <p className="info-text">
          Mango Specifier is an <strong>AI-powered mango classifier</strong> that identifies
          the exact mango variety from an image.
        </p>

        <p className="info-text">
          It gives you <strong>sweetness levels, average size, region grown, export data, market demand,</strong>
          and temperature requirements — all from a picture.
        </p>

        <div className="benefits">
          <p>⚡ Instant Mango Variety Detection</p>
          <p>📊 Detailed Horticulture-backed Insights</p>
          <p>🌍 Export & Market Demand Trends</p>
          <p>🪪 Login to save your analysis history</p>
        </div>
      </div>

      <div className="auth-card glass">
        <h2 className="auth-title">Welcome Back 👋</h2>
        <p className="auth-desc-sm">Log in to continue your AI mango analysis journey.</p>

        <form className="auth-form" onSubmit={submitLogin}>
          <input
            type="email"
            placeholder="Enter email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />

          <input
            type="password"
            placeholder="Enter password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          <button className="auth-btn">Login</button>
        </form>

        <p className="auth-footer">
          New here? <Link to="/signup">Create an account</Link>
        </p>
      </div>
    </div>
  );
}
