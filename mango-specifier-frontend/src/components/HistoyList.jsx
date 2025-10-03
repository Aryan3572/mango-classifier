export default function HistoryList({ history }) {
  if (history.length === 0) return null;

  return (
    <div className="w-80 mt-6">
      <h2 className="text-lg font-bold mb-2">📜 Upload History</h2>
      <ul className="space-y-2 max-h-40 overflow-y-auto">
        {history.map((item, index) => (
          <li key={index} className="p-3 border rounded-md bg-gray-100 dark:bg-gray-800">
            <p className="font-medium">{item.mangoType} ({item.confidence})</p>
            <p className="text-xs text-gray-500">{item.fileName}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}
