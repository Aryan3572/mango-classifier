import React, { useEffect, useState } from "react";
import "./ExportSnapshot.css";

export default function ExportSnapshot() {
  const [snap, setSnap] = useState(null);

  useEffect(() => {
    fetch("http://localhost:5000/apeda_snapshot")
      .then(r => r.json())
      .then(setSnap)
      .catch(err => {
        console.error(err);
        setSnap({ source: "https://apeda.gov.in/Mango", note: "Could not fetch snapshot" });
      });
  }, []);

  if (!snap) return <div className="export-snap">Loading export snapshot…</div>;

  return (
    <div className="export-snap">
      <h3>India Mango Export Snapshot</h3>
      {snap.total_volume_mt ? (
        <>
          <p><b>Export volume (latest):</b> {snap.total_volume_mt} MT</p>
          <p><b>Export value (latest):</b> USD {snap.total_value_usd} million</p>
        </>
      ) : (
        <p>{snap.note}</p>
      )}
      <p>Sources: <a href="https://apeda.gov.in/Mango" target="_blank" rel="noreferrer">APEDA Mango portal</a></p>
    </div>
  );
}
