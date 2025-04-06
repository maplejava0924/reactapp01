// App.tsx
import { useState, useEffect, useRef } from "react";
import doraemonIcon from "./assets/doraemon.png";
import WhiteboardSection from "./WhiteboardSection";
import FormSection from "./FormSection";

//ホワイトボード用
type SpeakerName = "司会" | "A子" | "B太" | "C助";
type WhiteboardState = Record<SpeakerName, string[]>;

const App = () => {
  const initialBoardState: WhiteboardState = {
    司会: ["（未回答）"],
    A子: ["（未回答）"],
    B太: ["（未回答）"],
    C助: ["（未回答）"],
  };

  //ホワイトボード用
  const [whiteboard, setWhiteboard] =
    useState<WhiteboardState>(initialBoardState);

  const [messages, setMessages] = useState<{ sender: string; text: string }[]>(
    []
  );
  const [isStreaming, setIsStreaming] = useState(false);
  const chatEndRef = useRef<HTMLDivElement | null>(null);
  const [userMessage, setUserMessage] = useState(""); // 送信フォームの入力値
  const [thinkingAgent, setThinkingAgent] = useState<string | null>(null); //考え中のエージェント名
  const [thinkingDots, setThinkingDots] = useState(""); //「○○が入力しています…」の「.」→「..」→「...」のアニメーション用

  const [selectedGenres, setSelectedGenres] = useState<string[]>([]);
  const [seenMovies, setSeenMovies] = useState<string>("");

  // 発言者によって吹き出し色を切り替え
  const getBubbleStyle = (sender: string) => {
    switch (sender) {
      case "司会":
        return "bg-blue-100 text-blue-900";
      case "A子":
        return "bg-pink-100 text-pink-900";
      case "B太":
        return "bg-yellow-100 text-yellow-900";
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

  const handleUserMessage = () => {
    if (!userMessage.trim()) return;

    // チャット画面にユーザーメッセージを先に表示
    setMessages((prev) => [...prev, { sender: "user", text: userMessage }]);

    // ストリーミング開始
    startStreaming();

    // 入力クリア
    setUserMessage("");
  };

  const startStreaming = () => {
    setIsStreaming(true);
    const eventSource = new EventSource(
      `http://127.0.0.1:5000/chat/stream?user_message=${encodeURIComponent(
        userMessage
      )}&genres=${encodeURIComponent(
        selectedGenres.join(",")
      )}&seen_movies=${encodeURIComponent(seenMovies)}`
    );

    // 通常のメッセージ受信
    eventSource.onmessage = (e) => {
      const parsed = JSON.parse(e.data);
      const speaker = parsed.last_speaker;
      const text = parsed.text;
      const isSummary = parsed.is_summary;

      //ホワイトボードの表示
      if (isSummary) {
        const target = speaker as SpeakerName;
        setWhiteboard((prev) => {
          const current = prev[target];
          return {
            ...prev,
            [target]:
              current?.[0] === "（未回答）"
                ? [`${text}`]
                : [...current, `${text}`],
          };
        });
        return; // チャット画面には出さない
      }

      //通常のメッセージ表示
      setThinkingAgent(speaker); // エージェント名をセット
      setMessages((prev) => [...prev, { sender: speaker, text }]);
    };

    // フロー正常終了（イベント名 'end'）
    eventSource.addEventListener("end", () => {
      console.log("✅ フロー正常終了");
      eventSource.close();
      setIsStreaming(false);
      setThinkingAgent(null);
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
      setThinkingAgent(null);
    };
  };

  //「○○が入力しています…」の「…」のアニメーション表示
  useEffect(() => {
    if (!isStreaming) return;

    const dotStates = [".", "..", "..."];
    let index = 0;

    const interval = setInterval(() => {
      index = (index + 1) % dotStates.length;
      setThinkingDots(dotStates[index]);
    }, 500);

    return () => clearInterval(interval);
  }, [isStreaming]);

  return (
    <div className="flex h-screen">
      {/* 左カラム：フォーム */}
      <FormSection
        selectedGenres={selectedGenres}
        setSelectedGenres={setSelectedGenres}
        seenMovies={seenMovies}
        setSeenMovies={setSeenMovies}
      />
      <div className="flex flex-col w-2/4">
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
              {msg.sender !== "user" ? (
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
              ) : (
                <div className="bg-blue-900 text-white p-2 rounded-lg max-w-xs whitespace-pre-wrap break-words">
                  {msg.text}
                </div>
              )}
            </div>
          ))}

          {isStreaming && thinkingAgent && (
            <div className="flex items-center mt-2 text-gray-500 text-sm">
              <p>
                {thinkingAgent}が入力しています{thinkingDots}
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
            className="input input-bordered flex-1 mr-2 disabled:bg-gray-200"
            placeholder="メッセージを入力..."
            value={userMessage}
            onChange={(e) => setUserMessage(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !isStreaming) {
                handleUserMessage();
              }
            }}
            disabled={isStreaming}
          />
          <button
            className="btn text-white disabled:bg-gray-400 bg-blue-500 hover:bg-blue-600"
            onClick={handleUserMessage}
            disabled={isStreaming}
          >
            送信
          </button>
        </div>
      </div>
      <WhiteboardSection whiteboard={whiteboard} />
    </div>
  );
};

export default App;
