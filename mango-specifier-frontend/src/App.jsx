import React, { useState, useEffect } from "react";

function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [darkMode, setDarkMode] = useState(false);

  // Add dark mode class to <html>
  useEffect(() => {
    if (darkMode) document.documentElement.classList.add("dark");
    else document.documentElement.classList.remove("dark");
  }, [darkMode]);

  const handleUpload = async () => {
    if (!file) {
      alert("Please select an image first");
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://localhost:5000/predict", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error("Error:", error);
      alert("Could not connect to backend. Make sure Flask is running.");
    }

    setLoading(false);
  };

  return (
    <div
      className={`min-h-screen transition-all ${
        darkMode ? "bg-gray-900 text-white" : "bg-gradient-to-r from-yellow-100 to-orange-100 text-gray-900"
      }`}
    >
      <div className="container mx-auto p-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-4xl font-extrabold bg-gradient-to-r from-yellow-500 to-orange-600 bg-clip-text text-transparent drop-shadow-md">
            🥭 Mango Specifier
          </h1>
          <button
            onClick={() => setDarkMode(!darkMode)}
            className="px-4 py-2 rounded-lg border shadow hover:bg-gray-200 dark:hover:bg-gray-700 transition"
          >
            {darkMode ? "🌙 Dark Mode" : "☀️ Light Mode"}
          </button>
        </div>

        {/* Upload Section */}
        <div className="flex flex-col items-center gap-4 p-6 border-2 border-dashed rounded-2xl bg-white dark:bg-gray-800 shadow-lg hover:shadow-2xl transition">
          <input
            type="file"
            accept="image/*"
            onChange={(e) => setFile(e.target.files[0])}
            className="block w-full text-sm text-gray-500 dark:text-gray-300 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-gradient-to-r file:from-yellow-400 file:to-orange-500 file:text-white hover:file:scale-105 transition"
          />

          {file && (
            <img
              src={URL.createObjectURL(file)}
              alt="preview"
              className="w-40 h-40 object-cover rounded-lg border shadow-md"
            />
          )}

          <button
            onClick={handleUpload}
            disabled={loading}
            className="px-6 py-2 bg-gradient-to-r from-yellow-400 to-orange-500 text-white rounded-lg shadow-lg hover:scale-105 transform transition disabled:opacity-50"
          >
            {loading ? "🔄 Predicting..." : "Upload & Predict"}
          </button>
        </div>

        {/* Result Section */}
        {result && (
          <div className="mt-6 p-6 bg-white dark:bg-gray-800 rounded-2xl shadow-xl hover:shadow-2xl transition duration-300">
            <h2 className="text-2xl font-bold mb-4 text-center">🍋 Prediction Result</h2>
            <p className="text-lg text-center">
              Mango Type:{" "}
              <span className="font-semibold text-orange-600 dark:text-yellow-400">{result.label}</span>
            </p>
            <p className="text-lg text-center">
              Confidence: <span className="font-semibold">{(result.confidence * 100).toFixed(2)}%</span>
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400 text-center mt-2">File: {file.name}</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
