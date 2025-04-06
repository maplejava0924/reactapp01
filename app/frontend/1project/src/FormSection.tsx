// FormSection.tsx
import { FC } from "react";

type FormProps = {
  selectedGenres: string[];
  setSelectedGenres: (genres: string[]) => void;
  seenMovies: string;
  setSeenMovies: (text: string) => void;
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

const FormSection: FC<FormProps> = ({
  selectedGenres,
  setSelectedGenres,
  seenMovies,
  setSeenMovies,
}) => {
  const toggleGenre = (genre: string) => {
    if (selectedGenres.includes(genre)) {
      setSelectedGenres(selectedGenres.filter((g) => g !== genre));
    } else {
      setSelectedGenres([...selectedGenres, genre]);
    }
  };

  return (
    <div className="w-1/4 p-4 bg-gray-50 border-r border-gray-300">
      <h2 className="text-lg font-bold mb-2">🎬 映画ジャンル（必須）</h2>
      <div className="flex flex-wrap gap-2 mb-4">
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
        className="textarea textarea-bordered w-full h-32"
        placeholder="作品名を自由に入力..."
        value={seenMovies}
        onChange={(e) => setSeenMovies(e.target.value)}
      />
    </div>
  );
};

export default FormSection;
