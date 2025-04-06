// App.tsx
import { useState, useEffect, useRef } from "react";
import WhiteboardSection from "./WhiteboardSection";
import FormSection from "./FormSection";
import characterStylesJson from "./assets/character_styles.json";
import ChatSection from "./ChatSection";

// 型定義をつけてインデックスアクセスできるようにする
const characterStyles: Record<
  string,
  { bubbleClass: string; headerClass: string; imagePath: string }
> = characterStylesJson;

//ホワイトボード用
type SpeakerName = string;

type WhiteboardState = Record<SpeakerName, string[]>;

const App = () => {
  const initialBoardState: WhiteboardState = Object.fromEntries(
    Object.keys(characterStyles).map((name) => [name, ["（未回答）"]])
  );

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

  //バックエンドの呼び出し処理
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
        <ChatSection
          messages={messages}
          isStreaming={isStreaming}
          thinkingAgent={thinkingAgent}
          thinkingDots={thinkingDots}
        />

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
