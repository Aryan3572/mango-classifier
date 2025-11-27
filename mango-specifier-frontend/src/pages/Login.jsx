// src/pages/Login.jsx
import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./Auth.css";
import { saveToken } from "../utils/auth";

export default function Login() {
  const navigate = useNavigate();
  const API_BASE = "http://localhost:5000";
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");

  const submitLogin = async (e) => {
    e.preventDefault();
    setErr("");
    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Login failed");

      saveToken(data.token);
      navigate("/");
    } catch (err) {
      setErr(err.message);
    }
  };

  return (
    <div className="auth-wrapper">
      <div className="auth-card glass">
        <h1 className="auth-title">Welcome Back 👋</h1>
        <p className="auth-desc">Mango Specifier uses AI to identify mango varieties, analyze sweetness, size, and market demand.</p>

        <form className="auth-form" onSubmit={submitLogin}>
          <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          <button className="auth-btn">Login</button>
          {err && <p className="error-text">{err}</p>}
        </form>

        <p className="auth-footer">Don’t have an account? <Link to="/signup">Create one</Link></p>
      </div>
    </div>
  );
}
