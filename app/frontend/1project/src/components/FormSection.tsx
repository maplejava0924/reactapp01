import { FC, useState } from "react";
import characterStylesJson from "../assets/character_styles.json";
type FormProps = {
  selectedGenres: string[];
  setSelectedGenres: (genres: string[]) => void;
  seenMovies: string[]; // ← 文字列の配列に変更
  setSeenMovies: (movies: string[]) => void; // ← setterも配列
  selectedCharacters: string[];
  setSelectedCharacters: (chars: string[]) => void;
};

const genres = [
  "アクション",
  "コメディ",
  "ドラマ",
  "ホラー",
  "SF",
  "アニメ",
  "ファンタジー",
  "恋愛",
  "ドキュメンタリー",
  "サスペンス",
];
const characters = [
  "ルフィ",
  "ケロロ軍曹",
  "ナルト",
  "ミッキー",
  "五条悟",
  "サトシ",
  "トニー・スターク",
  "ガチャピン",
  "ムック",
  "ダースベイダー",
  "黒崎一護",
  "サイタマ",
  "ラファウ",
  "ピカチュウ",
  "緑谷出久",
  "オールマイト",
  "坂田銀時",
  "神楽",
  "志村新八",
  "星野アイ",
  "アンパンマン",
];

const characterStyles = characterStylesJson as Record<
  string,
  { imagePath: string }
>;

const FormSection: FC<FormProps> = ({
  selectedGenres,
  setSelectedGenres,
  seenMovies,
  setSeenMovies,
  selectedCharacters,
  setSelectedCharacters,
}) => {
  const [inputValue, setInputValue] = useState("");

  const toggleGenre = (genre: string) => {
    if (selectedGenres.includes(genre)) {
      setSelectedGenres(selectedGenres.filter((g) => g !== genre));
    } else if (selectedGenres.length < 3) {
      setSelectedGenres([...selectedGenres, genre]);
    }
  };

  const toggleCharacter = (char: string) => {
    if (selectedCharacters.includes(char)) {
      setSelectedCharacters(selectedCharacters.filter((c) => c !== char));
    } else if (selectedCharacters.length < 3) {
      setSelectedCharacters([...selectedCharacters, char]);
    }
  };

  return (
    <div className="w-1/4 p-4 bg-gray-50 border-r border-gray-300 overflow-y-auto">
      <h2 className="text-lg font-bold mb-2">
        🎬 映画ジャンル（必須 3つまで）
      </h2>
      <div className="flex flex-wrap gap-2 mb-6">
        {genres.map((genre) => {
          const isSelected = selectedGenres.includes(genre);
          const isDisabled = selectedGenres.length >= 3 && !isSelected;

          return (
            <button
              key={genre}
              className={`px-3 py-1 rounded-full border text-sm transition ${
                isSelected
                  ? "bg-blue-500 text-white"
                  : "bg-white text-gray-700 hover:bg-blue-100"
              } ${isDisabled ? "opacity-40 cursor-not-allowed" : ""}`}
              onClick={() => !isDisabled && toggleGenre(genre)}
              type="button"
            >
              {genre}
            </button>
          );
        })}
      </div>

      <h2 className="text-lg font-bold mb-2">📽 今まで見た映画（任意）</h2>
      <div className="flex flex-wrap gap-2 mb-2">
        {seenMovies.map((movie) => (
          <div
            key={movie}
            className="flex items-center bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm"
          >
            {movie}
            <button
              onClick={() =>
                setSeenMovies(seenMovies.filter((m) => m !== movie))
              }
              className="ml-2 text-xs text-blue-500 hover:text-red-500"
            >
              ✕
            </button>
          </div>
        ))}
      </div>
      <input
        type="text"
        placeholder="作品名を入力してEnter"
        className="input input-bordered w-full mb-6"
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter") {
            e.preventDefault();
            const trimmed = inputValue.trim();
            if (trimmed && !seenMovies.includes(trimmed)) {
              setSeenMovies([...seenMovies, trimmed]);
            }
            setInputValue("");
          }
        }}
      />

      <h2 className="text-lg font-bold mb-2">
        👥 グループチャット参加キャラ（3人選んでね）
      </h2>
      <div className="grid grid-cols-3 gap-4">
        {characters.map((char) => {
          const isSelected = selectedCharacters.includes(char);
          const isDisabled = selectedCharacters.length === 3 && !isSelected;
          const isHost = selectedCharacters[0] === char; // 👑司会フラグ

          const imagePath =
            characterStyles[char]?.imagePath || "/assets/default.png";

          return (
            <div
              key={char}
              onClick={() => !isDisabled && toggleCharacter(char)}
              className={`relative cursor-pointer flex flex-col items-center border rounded-xl p-2 transition-all duration-200 ${
                isSelected
                  ? "border-purple-500 shadow-md bg-purple-50"
                  : "border-gray-300 bg-white hover:border-purple-300 hover:bg-purple-50 hover:shadow"
              } ${isDisabled ? "opacity-40 cursor-not-allowed" : ""}`}
            >
              {/* 👑司会マーク */}
              {isHost && (
                <span className="absolute top-1 right-1 text-xs bg-yellow-300 text-black px-1 rounded z-10">
                  👑司会
                </span>
              )}

              <img
                src={imagePath}
                alt={char}
                className="w-16 h-16 rounded-full object-cover"
              />
              <span className="text-sm mt-1 text-center">{char}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default FormSection;
