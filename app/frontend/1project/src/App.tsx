import { useState } from "react";
import reactLogo from "./assets/react.svg";
import viteLogo from "/vite.svg";
import "./App.css";

function App() {
  const [count, setCount] = useState(0);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-white p-6">
      {/* ロゴ部分 */}
      <div className="flex space-x-6">
        <a
          href="https://vite.dev"
          target="_blank"
          className="hover:scale-110 transition-transform"
        >
          <img src={viteLogo} className="w-20 h-20" alt="Vite logo" />
        </a>
        <a
          href="https://react.dev"
          target="_blank"
          className="hover:scale-110 transition-transform"
        >
          <img src={reactLogo} className="w-20 h-20" alt="React logo" />
        </a>
      </div>

      {/* タイトル */}
      <h1 className="text-4xl font-extrabold text-primary mt-4">
        Vite + React + DaisyUI
      </h1>

      {/* メインのカード */}
      <div className="card w-96 bg-base-100 shadow-xl border border-gray-200 mt-6 p-6">
        <div className="card-body items-center text-center">
          <p className="text-lg font-semibold text-gray-700">
            Current Count:{" "}
            <span className="text-primary text-2xl">{count}</span>
          </p>
          <button
            className="btn btn-primary btn-lg w-full mt-3 hover:shadow-md"
            onClick={() => setCount(count + 1)}
          >
            Click Me!
          </button>
          <p className="text-gray-500 text-sm mt-2">
            Edit <code className="bg-gray-200 px-1 rounded">src/App.tsx</code>{" "}
            and save to test HMR.
          </p>
        </div>
      </div>

      {/* フッター */}
      <p className="text-gray-600 mt-6 text-sm">
        Click on the Vite and React logos to learn more
      </p>
    </div>
  );
}

export default App;
