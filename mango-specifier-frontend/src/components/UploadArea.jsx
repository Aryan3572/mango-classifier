// src/components/UploadArea.jsx
import React, { useState, useRef } from "react";
import "./UploadArea.css";

export default function UploadArea({ title, onFileSelected }) {
  const [dragOver, setDragOver] = useState(false);
  const [preview, setPreview] = useState("");
  const fileRef = useRef();

  const handleFile = (file) => {
    if (!file) {
      setPreview("");
      if (typeof onFileSelected === "function") onFileSelected(null);
      return;
    }
    setPreview(URL.createObjectURL(file));
    if (typeof onFileSelected === "function") onFileSelected(file);
  };

  const onInputChange = (e) => {
    const f = e.target.files && e.target.files[0];
    if (f) handleFile(f);
  };

  const onDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const f = e.dataTransfer.files && e.dataTransfer.files[0];
    if (f) handleFile(f);
  };

  return (
    <div
      className={`uploader ${dragOver ? "drag" : ""}`}
      onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
      onDragLeave={() => setDragOver(false)}
      onDrop={onDrop}
    >
      <label className="uploader-inner">
        {!preview ? (
          <>
            <div className="upload-graphic" aria-hidden>
              <svg width="44" height="44" viewBox="0 0 24 24" fill="none"><path d="M12 3v12" stroke="currentColor" strokeWidth="1.5"/><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" stroke="currentColor" strokeWidth="1.5"/><path d="M7 9l5-6 5 6" stroke="currentColor" strokeWidth="1.5"/></svg>
            </div>
            <div className="upload-title">{title}</div>
            <div className="upload-sub muted">Drag & drop or click to upload an image</div>
            <input ref={fileRef} type="file" accept="image/*" onChange={onInputChange} />
          </>
        ) : (
          <div className="preview-wrap">
            <img src={preview} alt="preview" className="preview-img" />
            <div className="preview-actions">
              <button className="btn small" onClick={() => fileRef.current && fileRef.current.click()}>Replace</button>
              <button className="btn small ghost" onClick={() => handleFile(null)}>Remove</button>
            </div>
            <input ref={fileRef} type="file" accept="image/*" onChange={onInputChange} />
          </div>
        )}
      </label>
    </div>
  );
}
