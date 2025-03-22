import { useState, useEffect, useRef } from "react";
import doraemonIcon from "./assets/doraemon.png";
import axios from "axios";

const App = () => {
  const [messages, setMessages] = useState<{ sender: string; text: string }[]>(
    []
  );
  const [input, setInput] = useState("");
  const [isThinking, setIsThinking] = useState(false);
  const chatEndRef = useRef<HTMLDivElement | null>(null);
  const [thinkingDots, setThinkingDots] = useState(".");

  // メッセージが追加されたら最下部へスクロール
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "auto" });
  }, [messages, isThinking]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    // ユーザーメッセージを追加
    const userMessage = { sender: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    // エージェントが考えている状態をセット
    setIsThinking(true);

    // エージェントの応答
    try {
      const res = await axios.post("http://localhost:5000/chat", {
        message: input,
      });

      const agentMessage = { sender: "agent", text: res.data.reply };
      setMessages((prev) => [...prev, agentMessage]);
    } catch (error) {
      console.error("APIエラー:", error);
      setMessages((prev) => [
        ...prev,
        {
          sender: "agent",
          text: "エラー：サーバーと通信できませんでした。",
        },
      ]);
    } finally {
      setIsThinking(false);
    }
  };

  useEffect(() => {
    if (!isThinking) return;

    const dotStates = [".", "..", "..."];
    let index = 0;

    const interval = setInterval(() => {
      index = (index + 1) % dotStates.length;
      setThinkingDots(dotStates[index]);
    }, 500); // 0.5秒ごとに切り替え

    return () => clearInterval(interval); // クリーンアップ
  }, [isThinking]);

  return (
    <div className="flex flex-col h-screen bg-green-50">
      {/* ヘッダー */}
      <header className="p-4 bg-green-800 text-white text-xl font-bold text-center">
        AIチャット
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
                  <p className="text-xs text-gray-600">ドラえもん</p>
                  <div className="bg-pink-100 text-black p-2 rounded-lg max-w-md whitespace-pre-wrap break-words">
                    {msg.text}
                  </div>
                </div>
              </div>
            )}
            {msg.sender === "user" && (
              <div className="bg-blue-900 text-white p-2 rounded-lg max-w-xs whitespace-pre-wrap break-words">
                {msg.text}
              </div>
            )}
          </div>
        ))}

        {/* 「ドラえもんが入力しています」表示 */}
        {isThinking && (
          <div className="flex items-center justify-start mt-2">
            <img
              src={doraemonIcon}
              alt="Agent"
              className="w-10 h-10 rounded-full mr-2"
            />
            <p className="text-gray-500 text-sm">
              ドラえもんが入力しています{thinkingDots}
            </p>
          </div>
        )}

        {/* スクロール位置調整 */}
        <div ref={chatEndRef} />
      </div>

      {/* 入力フォーム */}
      <div className="p-4 bg-white flex">
        <input
          type="text"
          className="input input-bordered flex-1 mr-2"
          placeholder="メッセージを入力..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
        />
        <button
          className="btn bg-blue-500 text-white hover:bg-blue-600"
          onClick={sendMessage}
        >
          送信
        </button>
      </div>
    </div>
  );
};

export default App;
