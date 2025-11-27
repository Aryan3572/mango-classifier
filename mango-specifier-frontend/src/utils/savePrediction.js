// src/utils/savePrediction.js
import { getToken } from "./auth";

export async function savePredictionAPI(payload) {
  const token = getToken();
  if (!token) throw new Error("Not authenticated");

  const res = await fetch("http://localhost:5000/predictions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || "Save failed");
  }

  return res.json();
}
