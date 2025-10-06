import { useState } from "react";

export default function UploadArea({ onResult }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);

  // Ensure VITE_BACKEND_URL is a base URL (no trailing slash, no /predict)
  const BASE = import.meta.env.VITE_BACKEND_URL || "http://localhost:5000";
  const BACKEND_URL = `${BASE.replace(/\/$/, "")}/predict`; // safe concat
  console.log("uploading to : ",BACKEND_URL);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setSelectedFile(file);
    if (file) setPreview(URL.createObjectURL(file));
  };

  const handleUpload = async () => {
    if (!selectedFile) return alert("Please select a file first!");

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      setLoading(true);
      console.log("Uploading to:", BACKEND_URL);

      const res = await fetch(BACKEND_URL, {
        method: "POST",
        body: formData,
      });

      console.log("Response status:", res.status);
      if (!res.ok) {
        const text = await res.text();
        console.error("Server returned non-OK:", res.status, text);
        throw new Error(`Prediction failed: ${res.status}`);
      }
      const data = await res.json();

      // data must contain mangoType and confidence (see backend changes below)
      onResult({
        ...data,
        fileName: selectedFile.name,
        image: preview,
      });
    } catch (err) {
      console.error("Upload error:", err);
      alert(
        "❌ Could not connect to backend or prediction failed. Check console and backend logs."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center gap-5 p-8 border-2 border-dashed rounded-3xl bg-white dark:bg-gray-800 shadow-lg hover:shadow-2xl transition-all duration-300 w-full max-w-lg mx-auto">
      <label className="w-full text-sm font-medium text-gray-700 dark:text-gray-300 text-center">
        Choose an image of a mango 🍋
      </label>
      <input
        type="file"
        accept="image/*"
        onChange={handleFileChange}
        className="block w-full text-sm text-gray-700 dark:text-gray-300 
          file:mr-4 file:py-2 file:px-5 file:rounded-lg file:border-0 
          file:text-sm file:font-semibold 
          file:bg-gradient-to-r file:from-yellow-400 file:to-orange-500 file:text-white 
          hover:file:scale-105 transform transition-all duration-300"
      />

      {preview && (
        <div className="mt-4">
          <img
            src={preview}
            alt="Preview"
            className="w-48 h-48 mx-auto rounded-xl border shadow-lg hover:shadow-2xl hover:scale-105 transition-transform duration-300"
          />
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
            {selectedFile?.name}
          </p>
        </div>
      )}

      <button
        onClick={handleUpload}
        disabled={loading}
        className="px-8 py-2 bg-gradient-to-r from-yellow-400 to-orange-500 
          text-white rounded-xl shadow-lg hover:shadow-2xl hover:scale-105 
          transform transition-all duration-300 disabled:opacity-60 disabled:cursor-not-allowed mt-4"
      >
        {loading ? "🔄 Predicting..." : "Upload & Predict"}
      </button>
    </div>
  );
}
