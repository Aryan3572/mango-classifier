import React, { useState, useEffect } from "react";
import UploadArea from "./components/UploadArea.jsx";
import ResultCard from "./components/Result.jsx";

function App() {
  const [result, setResult] = useState(null);
  const [darkMode, setDarkMode] = useState(false);

  // Apply dark mode class to <html>
  useEffect(() => {
    if (darkMode) document.documentElement.classList.add("dark");
    else document.documentElement.classList.remove("dark");
  }, [darkMode]);

  return (
    <div
      className={`min-h-screen flex flex-col justify-center items-center transition-all duration-700 ${
        darkMode
          ? "bg-gray-900 text-white"
          : "bg-gradient-to-r from-yellow-100 to-orange-100 text-gray-900"
      }`}
    >
      <div className="w-full max-w-2xl p-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-10">
          <h1 className="text-4xl font-extrabold bg-gradient-to-r from-yellow-500 to-orange-600 bg-clip-text text-transparent drop-shadow-lg animate-pulse">
            🥭 Mango Specifier
          </h1>
          <button
            onClick={() => setDarkMode(!darkMode)}
            className="px-4 py-2 rounded-xl border border-gray-300 dark:border-gray-700 shadow-md hover:shadow-lg hover:scale-105 transition bg-white dark:bg-gray-800"
          >
            {darkMode ? "☀️ Light Mode" : "🌙 Dark Mode"}
          </button>
        </div>

        {/* Upload Section */}
        <UploadArea onResult={setResult} />

        {/* Result Section */}
        {result && <ResultCard prediction={result} />}
      </div>
    </div>
  );
}

export default App;
