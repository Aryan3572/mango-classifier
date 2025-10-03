import { useState } from "react";
import UploadArea from "../components/UploadArea";
import ResultCard from "../components/Result";
import HistoryList from "../components/HistoyList";

export default function Home() {
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);

  // Handles new prediction result
  const handleResult = (prediction) => {
    setResult(prediction);
    setHistory([prediction, ...history]); // add to history
  };

  return (
    <div className="flex flex-col items-center gap-8">
      <h1 className="text-3xl font-bold">🥭 Mango Specifier</h1>
      <UploadArea onResult={handleResult} />
      {result && <ResultCard result={result} />}
      <HistoryList history={history} />
    </div>
  );
}
