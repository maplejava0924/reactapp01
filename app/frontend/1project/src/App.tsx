// App.tsx
import { useState, useEffect, useRef } from "react";
import doraemonIcon from "./assets/doraemon.png";

const App = () => {
  const [messages, setMessages] = useState<{ sender: string; text: string }[]>(
    []
  );
  const [isStreaming, setIsStreaming] = useState(false);
  const chatEndRef = useRef<HTMLDivElement | null>(null);

  // 発言者によって吹き出し色を切り替え
  const getBubbleStyle = (sender: string) => {
    switch (sender) {
      case "司会":
        return "bg-blue-100 text-blue-900";
      case "要約エージェント":
        return "bg-yellow-100 text-yellow-900";
      case "A子":
        return "bg-pink-100 text-pink-900";
      case "B太":
        return "bg-green-100 text-green-900";
      case "C助":
        return "bg-purple-100 text-purple-900";
      default:
        return "bg-gray-100 text-gray-900";
    }
  };

  // メッセージが追加されたら最下部へスクロール
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "auto" });
  }, [messages]);

  const startStreaming = () => {
    setIsStreaming(true);
    const eventSource = new EventSource("http://127.0.0.1:5000/chat/stream");

    // 通常のメッセージ受信
    eventSource.onmessage = (e) => {
      const parsed = JSON.parse(e.data);
      const speaker = parsed.last_speaker;
      const text = parsed.text;

      setMessages((prev) => [...prev, { sender: speaker, text }]);
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
            className={`flex items-end mb-4 ${
              msg.sender === "user" ? "justify-end" : "justify-start"
            }`}
          >
            {msg.sender !== "user" && (
              <div className="flex items-center">
                <div className="flex flex-col items-center mr-2 w-14">
                  <img
                    src={doraemonIcon}
                    alt={msg.sender}
                    className="w-10 h-10 rounded-full"
                  />
                  <p className="text-xs font-bold text-gray-700 mt-1 text-center">
                    {msg.sender}
                  </p>
                </div>

                <div
                  className={`p-3 rounded-xl max-w-md whitespace-pre-wrap break-words shadow ${getBubbleStyle(
                    msg.sender
                  )}`}
                >
                  {msg.text}
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
