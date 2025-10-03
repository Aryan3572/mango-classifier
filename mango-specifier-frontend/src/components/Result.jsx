export default function ResultCard({ prediction }) {
  return (
    <div className="mt-6 p-6 bg-white dark:bg-gray-800 rounded-2xl shadow-xl hover:shadow-2xl transform transition duration-300">
      <h2 className="text-2xl font-bold mb-4">🍋 Prediction Result</h2>

      {prediction.image && (
        <img
          src={prediction.image}
          alt="mango"
          className="w-48 h-48 mx-auto rounded-lg shadow mb-4"
        />
      )}

      <p className="text-lg">
        Mango Type:{" "}
        <span className="font-semibold text-orange-600 dark:text-yellow-400">
          {prediction.mangoType}
        </span>
      </p>
      <p className="text-lg">
        Confidence:{" "}
        <span className="font-semibold">
          {(prediction.confidence * 100).toFixed(2)}%
        </span>
      </p>
      <p className="text-sm text-gray-500 dark:text-gray-400">
        File: {prediction.fileName}
      </p>
    </div>
  );
}
