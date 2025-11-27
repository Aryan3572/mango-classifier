// src/pages/Signup.jsx
import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./Auth.css";

export default function Signup() {
  const navigate = useNavigate();
  const API_BASE = "http://localhost:5000";

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const submitSignup = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API_BASE}/auth/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, password }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.error);

      alert("Account created successfully!");
      navigate("/login");
    } catch (err) {
      alert("Signup error: " + err.message);
    }
  };

  return (
    <div className="auth-wrapper">
      <div className="info-panel glass">
        <h1>Join Mango Specifier AI 🥭</h1>
        <p className="info-text">
          Create your account to unlock <strong>powerful AI mango insights</strong> and
          save all your analysis in one place.
        </p>

        <div className="benefits">
          <p>✔ Save unlimited predictions</p>
          <p>✔ Track mango insights over time</p>
          <p>✔ Export your analysis history</p>
          <p>✔ Unlock advanced data (export markets, temp ranges, brix levels)</p>
        </div>
      </div>

      <div className="auth-card glass">
        <h2 className="auth-title">Create Your Account ✨</h2>

        <form className="auth-form" onSubmit={submitSignup}>
          <input
            type="text"
            placeholder="Full Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />

          <input
            type="email"
            placeholder="Email Address"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />

          <input
            type="password"
            placeholder="Create Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          <button className="auth-btn">Sign Up</button>
        </form>

        <p className="auth-footer">
          Already have an account? <Link to="/login">Login</Link>
        </p>
      </div>
    </div>
  );
}
