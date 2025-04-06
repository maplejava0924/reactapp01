// App.tsx
import { useRef, useState, useEffect } from "react";
import FormSection from "./components/FormSection";
import ChatSection from "./components/ChatSection";
import WhiteboardSection from "./components/WhiteboardSection";
import Header from "./components/Header";
import characterStylesJson from "./assets/character_styles.json";
import { useStreamingChat } from "./hooks/useStreamingChat";

const characterStyles = characterStylesJson as Record<
  string,
  { bubbleClass: string; headerClass: string; imagePath: string }
>;

const App = () => {
  const initialBoardState = Object.fromEntries(
    Object.keys(characterStyles).map((name) => [name, ["（未回答）"]])
  );

  const [whiteboard, setWhiteboard] = useState(initialBoardState);
  const [messages, setMessages] = useState<{ sender: string; text: string }[]>(
    []
  );
  const [userMessage, setUserMessage] = useState("");
  const [selectedGenres, setSelectedGenres] = useState<string[]>([]);
  const [seenMovies, setSeenMovies] = useState("");
  const chatEndRef = useRef<HTMLDivElement | null>(null);

  const [selectedCharacters, setSelectedCharacters] = useState<string[]>([]);

  const { startStreaming, isStreaming, thinkingAgent, thinkingDots } =
    useStreamingChat({
      userMessage,
      selectedGenres,
      seenMovies,
      onReceiveMessage: (speaker, text) => {
        setMessages((prev) => [...prev, { sender: speaker, text }]);
      },
      onReceiveSummary: (speaker, text) => {
        setWhiteboard((prev) => {
          const current = prev[speaker];
          return {
            ...prev,
            [speaker]:
              current?.[0] === "（未回答）" ? [text] : [...current, text],
          };
        });
      },
      onStreamEnd: () => {},
    });

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "auto" });
  }, [messages]);

  const handleUserMessage = () => {
    if (!userMessage.trim()) return;
    setMessages((prev) => [...prev, { sender: "user", text: userMessage }]);
    startStreaming();
    setUserMessage("");
  };

  return (
    <div className="flex h-screen">
      {/* 入力フォーム */}
      <FormSection
        selectedGenres={selectedGenres}
        setSelectedGenres={setSelectedGenres}
        seenMovies={seenMovies}
        setSeenMovies={setSeenMovies}
        selectedCharacters={selectedCharacters}
        setSelectedCharacters={setSelectedCharacters}
      />
      <div className="flex flex-col w-2/4">
        {/* ヘッダー */}
        <Header
          selectedCharacters={selectedCharacters}
          characterStyles={characterStyles}
        />

        {/* チャット画面 */}
        <ChatSection
          messages={messages}
          isStreaming={isStreaming}
          thinkingAgent={thinkingAgent}
          thinkingDots={thinkingDots}
        />
        <div className="p-4 bg-white flex">
          <input
            type="text"
            className="input input-bordered flex-1 mr-2 disabled:bg-gray-200"
            placeholder="メッセージを入力..."
            value={userMessage}
            onChange={(e) => setUserMessage(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !isStreaming) handleUserMessage();
            }}
            disabled={isStreaming}
          />
          {/* グループチャット中と3つキャラクターを選択していない状態だと送信できない*/}
          <button
            className="btn text-white disabled:bg-gray-400 bg-blue-500 hover:bg-blue-600"
            onClick={handleUserMessage}
            disabled={isStreaming || selectedCharacters.length !== 3}
          >
            送信
          </button>
        </div>
        {/* ホワイトボード */}
      </div>
      <WhiteboardSection whiteboard={whiteboard} />
    </div>
  );
};

export default App;
