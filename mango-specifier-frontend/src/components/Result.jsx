export default function Result({ prediction }) {
  if (!prediction) return null; // ✅ Handle empty or null predictions safely

  return (
    <div className="mt-8 p-8 bg-white dark:bg-gray-800 rounded-3xl shadow-xl hover:shadow-2xl transform hover:scale-105 transition-all duration-300 w-full max-w-lg mx-auto">
      <h2 className="text-2xl font-bold mb-6 text-center bg-gradient-to-r from-yellow-500 to-orange-500 bg-clip-text text-transparent">
        🥭 Prediction Result
      </h2>

      {prediction.image && (
        <img
          src={prediction.image}
          alt={`Preview of ${prediction.fileName || "mango image"}`}
          className="w-48 h-48 mx-auto rounded-xl shadow-lg mb-4 hover:shadow-2xl transition-transform duration-300"
        />
      )}

      <div className="text-center space-y-2">
        <p className="text-lg">
          <span className="font-medium text-gray-700 dark:text-gray-300">Mango Type:</span>{" "}
          <span className="font-semibold text-orange-600 dark:text-yellow-400">
            {prediction.mangoType || "Unknown"}
          </span>
        </p>

        <p className="text-lg">
          <span className="font-medium text-gray-700 dark:text-gray-300">Confidence:</span>{" "}
          <span className="font-semibold">
            {prediction.confidence
              ? (prediction.confidence * 100).toFixed(2) + "%"
              : "N/A"}
          </span>
        </p>

        {prediction.fileName && (
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
            File: {prediction.fileName}
          </p>
        )}
      </div>
    </div>
  );
}
