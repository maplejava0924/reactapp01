// WhiteboardSection.tsx

type WhiteboardProps = {
  whiteboard: Record<string, string[]>;
};

const WhiteboardSection = ({ whiteboard }: WhiteboardProps) => {
  return (
    <div className="w-1/3 overflow-auto p-4 bg-white border-l border-gray-300">
      <h2 className="text-xl font-bold mb-4 text-center">ホワイトボード</h2>
      {Object.entries(whiteboard).map(([name, comments]) => (
        <div key={name} className="mb-4 p-2 border rounded shadow">
          <h3 className="font-bold text-lg text-gray-800 mb-2">{name}の意見</h3>
          <ul className="list-disc list-inside text-gray-700 text-sm">
            {comments.map((line, i) => (
              <li key={i}>{line}</li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
};

export default WhiteboardSection;
