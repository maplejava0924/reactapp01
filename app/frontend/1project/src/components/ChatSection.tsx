import { useEffect, useRef } from "react";
import characterStylesJson from "../assets/character_styles.json";
const characterStyles: Record<
  string,
  { bubbleClass: string; headerClass: string; imagePath: string }
> = characterStylesJson;

type Message = {
  sender: string;
  text: string;
};

type Props = {
  messages: Message[];
  isStreaming: boolean;
  thinkingAgent: string | null;
  thinkingDots: string;
};

const ChatSection = ({
  messages,
  isStreaming,
  thinkingAgent,
  thinkingDots,
}: Props) => {
  const chatEndRef = useRef<HTMLDivElement | null>(null);

  // 発言者によって吹き出し色を切り替え
  const getBubbleStyle = (sender: string) =>
    characterStyles[sender]?.bubbleClass || "bg-gray-100 text-gray-900";
  // 各吹き出しに使う画像を取得
  const getImagePath = (sender: string) =>
    characterStyles[sender]?.imagePath || "/assets/default.png";

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "auto" });
  }, [messages]);

  return (
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
                  src={getImagePath(msg.sender)}
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

      <div ref={chatEndRef} />
    </div>
  );
};

export default ChatSection;
