// hooks/useStreamingChat.ts
import { useState, useEffect } from "react";

export const useStreamingChat = ({
  userMessage,
  selectedGenres,
  seenMovies,
  onReceiveMessage,
  onReceiveSummary,
  onStreamEnd,
}: {
  userMessage: string;
  selectedGenres: string[];
  seenMovies: string;
  onReceiveMessage: (speaker: string, text: string) => void;
  onReceiveSummary: (speaker: string, text: string) => void;
  onStreamEnd: () => void;
}) => {
  const [isStreaming, setIsStreaming] = useState(false);
  const [thinkingAgent, setThinkingAgent] = useState<string | null>(null);
  const [thinkingDots, setThinkingDots] = useState("");

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
      const { last_speaker: speaker, text, is_summary: isSummary } = parsed;

      if (isSummary) {
        onReceiveSummary(speaker, text);
      } else {
        setThinkingAgent(speaker);
        onReceiveMessage(speaker, text);
      }
    };

    // フロー正常終了（イベント名 'end'）
    eventSource.addEventListener("end", () => {
      console.log("✅ フロー正常終了");
      eventSource.close();
      setIsStreaming(false);
      setThinkingAgent(null);
      onStreamEnd();
    });

    // エラー発生時（接続異常）
    eventSource.onerror = (err) => {
      console.error("❌ SSE接続エラー:", err);
      eventSource.close();
      setIsStreaming(false);
      setThinkingAgent(null);
    };
  };

  return { startStreaming, isStreaming, thinkingAgent, thinkingDots };
};
