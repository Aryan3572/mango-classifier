import React, { useState, useRef } from "react";
import "./UploadArea.css";
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

function UploadArea({ title }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const resultRef = useRef(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      setPreview(URL.createObjectURL(file));
      setResult(null);
    }
  };

  const handleReupload = () => {
    setSelectedFile(null);
    setPreview("");
    setResult(null);
  };

  const handlePredict = async () => {
    if (!selectedFile) {
      alert("Please upload a mango image first!");
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);

    setLoading(true);
    setResult(null);

    try {
      const response = await fetch("http://localhost:5000/predict", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("Server error");

      const data = await response.json();

      setResult({
        prediction: data.predicted_class || "Unknown Mango",
        confidence: data.confidence
          ? `${parseFloat(data.confidence).toFixed(2)}%`
          : "N/A",
        topPredictions: data.top_predictions || [],
      });

      setTimeout(() => {
        resultRef.current?.scrollIntoView({ behavior: "smooth" });
      }, 300);
    } catch (error) {
      console.error("Error predicting mango:", error);
      setResult({
        prediction: "Error identifying mango",
        confidence: null,
        topPredictions: [],
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="upload-box fade-in">
      <h2 className="upload-title">{title}</h2>

      {!preview ? (
        <div className="upload-zone">
          <p className="upload-text">
            <span className="highlight">Drag & drop</span> a mango image
            <br /> or click below to browse
          </p>
          <label htmlFor={`fileInput-${title}`} className="file-label">
            Choose Image
          </label>
          <input
            type="file"
            id={`fileInput-${title}`}
            accept="image/*"
            onChange={handleFileChange}
          />
        </div>
      ) : (
        <div className="preview-area">
          <img src={preview} alt="preview" className="preview" />
          <div className="btn-group">
            <button onClick={handlePredict} disabled={loading} className="btn">
              {loading ? <div className="spinner"></div> : "Identify Mango"}
            </button>
            <button onClick={handleReupload} className="btn reupload">
              Re-upload
            </button>
          </div>
        </div>
      )}

      {result && (
        <div className="result-card" ref={resultRef}>
          <h3 className="result-title">🥭 {result.prediction}</h3>
          {result.confidence && (
            <p className="result-confidence">
              Confidence: <span>{result.confidence}</span>
            </p>
          )}

          {/* Confidence Breakdown Chart */}
          {result.topPredictions && result.topPredictions.length > 0 && (
            <div className="chart-section">
              <h3>Confidence Breakdown</h3>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart
                  data={result.topPredictions}
                  margin={{ top: 10, right: 20, left: 0, bottom: 10 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="label" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="confidence" fill="#ffb300" barSize={50} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default UploadArea;
