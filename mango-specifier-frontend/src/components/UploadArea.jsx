import { useState } from "react";

export default function UploadArea({ onResult }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);

  // ⬇️ Change this to your Python backend port
  const BACKEND_URL = "http://127.0.0.1:5000/predict"; // Flask
  // const BACKEND_URL = "http://127.0.0.1:8000/predict"; // FastAPI

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setSelectedFile(file);
    if (file) {
      setPreview(URL.createObjectURL(file));
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return alert("Please select a file first!");

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      setLoading(true);
      const res = await fetch(BACKEND_URL, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error("Prediction failed");
      const data = await res.json();

      onResult({
        ...data,
        fileName: selectedFile.name,
        image: preview,
      });
    } catch (err) {
      console.error(err);
      alert("❌ Could not connect to backend. Make sure Python backend is running!");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center gap-4 p-6 border-2 border-dashed rounded-2xl bg-white dark:bg-gray-800 shadow-lg hover:shadow-2xl transition">
      <input
        type="file"
        accept="image/*"
        onChange={handleFileChange}
        className="block w-full text-sm text-gray-500 dark:text-gray-300"
      />

      {preview && (
        <img
          src={preview}
          alt="preview"
          className="w-40 h-40 object-cover rounded-lg border shadow"
        />
      )}

      <button
        onClick={handleUpload}
        disabled={loading}
        className="px-6 py-2 bg-gradient-to-r from-yellow-400 to-orange-500 text-white rounded-lg shadow-lg hover:scale-105 transition disabled:opacity-50"
      >
        {loading ? "🔄 Analyzing..." : "Upload & Predict"}
      </button>
    </div>
  );
}
