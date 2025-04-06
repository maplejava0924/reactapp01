// FormSection.tsx
import { FC } from "react";
import characterStylesJson from "./assets/character_styles.json";

type FormProps = {
  selectedGenres: string[];
  setSelectedGenres: (genres: string[]) => void;
  seenMovies: string;
  setSeenMovies: (text: string) => void;
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
];
const characters = [
  "ルフィ",
  "ケロロ軍曹",
  "ナルト",
  "ミッキー",
  "五条悟",
  "サトシ",
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
  const toggleGenre = (genre: string) => {
    if (selectedGenres.includes(genre)) {
      setSelectedGenres(selectedGenres.filter((g) => g !== genre));
    } else {
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
      <h2 className="text-lg font-bold mb-2">🎬 映画ジャンル（必須）</h2>
      <div className="flex flex-wrap gap-2 mb-6">
        {genres.map((genre) => (
          <button
            key={genre}
            className={`px-3 py-1 rounded-full border text-sm ${
              selectedGenres.includes(genre)
                ? "bg-blue-500 text-white"
                : "bg-white text-gray-700"
            }`}
            onClick={() => toggleGenre(genre)}
            type="button"
          >
            {genre}
          </button>
        ))}
      </div>

      <h2 className="text-lg font-bold mb-2">📽 今まで見た映画（任意）</h2>
      <textarea
        className="textarea textarea-bordered w-full h-32 mb-6"
        placeholder="作品名を自由に入力..."
        value={seenMovies}
        onChange={(e) => setSeenMovies(e.target.value)}
      />

      <h2 className="text-lg font-bold mb-2">
        👥 グループチャット参加キャラ（3人選んでね）
      </h2>
      <div className="grid grid-cols-3 gap-4">
        {characters.map((char) => {
          const isSelected = selectedCharacters.includes(char);
          const isDisabled = selectedCharacters.length === 3 && !isSelected;

          const imagePath =
            characterStyles[char]?.imagePath || "/assets/default.png";

          return (
            <div
              key={char}
              onClick={() => !isDisabled && toggleCharacter(char)}
              className={`cursor-pointer flex flex-col items-center border rounded-xl p-2 transition-all duration-200 ${
                isSelected
                  ? "border-purple-500 shadow-md bg-purple-50"
                  : "border-gray-300 bg-white hover:border-purple-300 hover:bg-purple-50 hover:shadow"
              } ${isDisabled ? "opacity-40 cursor-not-allowed" : ""}`}
            >
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
