// App.tsx
import { useState, useEffect, useRef } from "react";
import doraemonIcon from "./assets/doraemon.png";

const App = () => {
  const [messages, setMessages] = useState<{ sender: string; text: string }[]>(
    []
  );
  const [isStreaming, setIsStreaming] = useState(false);
  const chatEndRef = useRef<HTMLDivElement | null>(null);

  // メッセージが追加されたら最下部へスクロール
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "auto" });
  }, [messages]);

  const startStreaming = () => {
    setIsStreaming(true);
    const eventSource = new EventSource("http://127.0.0.1:5000/chat/stream");

    // 通常のメッセージ受信
    eventSource.onmessage = (e) => {
      const agentMessage = { sender: "agent", text: e.data };
      setMessages((prev) => [...prev, agentMessage]);
    };

    // フロー正常終了（イベント名 'end'）
    eventSource.addEventListener("end", () => {
      console.log("✅ フロー正常終了");
      eventSource.close();
      setIsStreaming(false);
    });

    // エラー発生時（接続異常）
    eventSource.onerror = (err) => {
      console.error("❌ SSE接続エラー:", err);
      // readyState が 2（CLOSED）かどうかで異常か判断できる
      if (eventSource.readyState === 2) {
        console.log("接続がクローズされました");
      }
      eventSource.close();
      setIsStreaming(false);
    };
  };

  return (
    <div className="flex flex-col h-screen bg-green-50">
      {/* ヘッダー */}
      <header className="p-4 bg-green-800 text-white text-xl font-bold text-center">
        AIグループチャット
      </header>

      {/* チャット画面 */}
      <div className="flex-1 overflow-auto p-4 bg-green-100">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`flex items-end mb-2 ${
              msg.sender === "user" ? "justify-end" : "justify-start"
            }`}
          >
            {msg.sender === "agent" && (
              <div className="flex items-start">
                <img
                  src={doraemonIcon}
                  alt="Agent"
                  className="w-10 h-10 rounded-full mr-2"
                />
                <div>
                  <p className="text-xs text-gray-600">エージェント</p>
                  <div className="bg-pink-100 text-black p-2 rounded-lg max-w-md whitespace-pre-wrap break-words">
                    {msg.text}
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}

        {/* スクロール位置調整 */}
        <div ref={chatEndRef} />
      </div>

      {/* 開始ボタン */}
      <div className="p-4 bg-white flex justify-center">
        <button
          className="btn bg-blue-500 text-white hover:bg-blue-600"
          onClick={startStreaming}
          disabled={isStreaming}
        >
          {isStreaming ? "チャット進行中..." : "チャット開始"}
        </button>
      </div>
    </div>
  );
};

export default App;
