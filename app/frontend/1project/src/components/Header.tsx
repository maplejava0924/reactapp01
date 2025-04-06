import { FC } from "react";

type HeaderProps = {
  selectedCharacters: string[];
  characterStyles: Record<
    string,
    { bubbleClass: string; headerClass: string; imagePath: string }
  >;
};

const Header: FC<HeaderProps> = ({ selectedCharacters, characterStyles }) => {
  return (
    <header className="h-16 px-4 bg-green-800 text-white text-xl font-bold flex justify-between items-center">
      <span>オススメ映画トークルーム</span>
      <div className="flex items-center">
        {selectedCharacters.map((char, index) => (
          <div key={char} className={`relative ${index !== 0 ? "-ml-3" : ""}`}>
            <div className="w-10 h-10 rounded-full bg-white flex items-center justify-center border border-white shadow">
              <img
                src={characterStyles[char]?.imagePath || "/assets/default.png"}
                alt={char}
                className="w-10 h-10 rounded-full object-cover bg-white"
              />
            </div>
          </div>
        ))}
      </div>
    </header>
  );
};

export default Header;
