import { useEffect, useState } from "react";

export default function DatasetInfo() {
  const [data, setData] = useState(null);
  const API_BASE = "http://localhost:5000";

  useEffect(() => {
    fetch(`${API_BASE}/dataset-info`)
      .then(res => res.json())
      .then(setData)
      .catch(console.error);
  }, []);

  if (!data) return <p>Loading dataset information...</p>;

  return (
    <div style={{ padding: "20px" }}>
      <h2>Dataset Specifications</h2>

      <table border="1" cellPadding="8">
        <tbody>
          <tr><td>Camera model</td><td>{data.camera_model}</td></tr>
          <tr><td>Capture settings</td><td>{data.capture_settings}</td></tr>
          <tr><td>Capture environments</td><td>{data.capture_environments}</td></tr>
          <tr><td>Background</td><td>{data.background_standardization}</td></tr>
          <tr><td>Capture angles</td><td>{data.capture_angles}</td></tr>
          <tr><td>Collection location</td><td>{data.collection_location}</td></tr>
          <tr><td>Season</td><td>{data.season}</td></tr>
          <tr><td>Collection stage</td><td>{data.collection_stage}</td></tr>
          <tr><td>Labeling protocol</td><td>{data.labeling_protocol}</td></tr>
          <tr><td>Total varieties</td><td>{data.total_varieties}</td></tr>
        </tbody>
      </table>

      <h3 style={{ marginTop: "20px" }}>Images per variety</h3>

      <ul>
        {Object.entries(data.images_per_variety).map(([k, v]) => (
          <li key={k}>
            {k} : {v === null ? "N/A" : v}
          </li>
        ))}
      </ul>
    </div>
  );
}
