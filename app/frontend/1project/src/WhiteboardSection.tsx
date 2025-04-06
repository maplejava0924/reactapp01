import characterStylesJson from "./assets/character_styles.json";

// 型定義をつけてインデックスアクセスできるようにする
const characterStyles: Record<
  string,
  { bubbleClass: string; headerClass: string }
> = characterStylesJson;

type SpeakerName = string;

type WhiteboardProps = {
  whiteboard: Record<SpeakerName, string[]>;
};

// ラベル部分（「◯◯の意見」）用の背景色
const getHeaderStyle = (name: string) => {
  return (
    characterStyles[name]?.headerClass ||
    "bg-gray-100 text-gray-900 border-gray-300"
  );
};

const WhiteboardSection = ({ whiteboard }: WhiteboardProps) => {
  return (
    <div className="w-1/3 overflow-auto p-4 bg-white border-l border-gray-300">
      {Object.entries(whiteboard).map(([name, comments]) => {
        const typedName = name as SpeakerName;
        const isPending = comments.length === 1 && comments[0] === "（未回答）";
        return (
          <div key={name} className="mb-4 border rounded shadow bg-white">
            {/* ラベル部分に色をつける */}
            <div
              className={`px-3 py-2 font-bold border-b ${getHeaderStyle(
                typedName
              )}`}
            >
              {typedName}の意見
            </div>

            {/* 意見表示部分は常に白背景 */}
            <div className="px-4 py-2 text-sm text-gray-800 whitespace-pre-wrap">
              {isPending ? (
                <span className="text-gray-400">（未回答）</span>
              ) : (
                <ul className="list-disc list-inside">
                  {comments.map((line, i) => (
                    <li key={i}>{line}</li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default WhiteboardSection;
