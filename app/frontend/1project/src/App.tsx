import { useState, useEffect, useRef } from "react";
import doraemonIcon from "./assets/doraemon.png";

const App = () => {
  const [messages, setMessages] = useState<{ sender: string; text: string }[]>(
    []
  );
  const [input, setInput] = useState("");
  const [isThinking, setIsThinking] = useState(false);
  const chatEndRef = useRef<HTMLDivElement | null>(null);
  const [thinkingDots, setThinkingDots] = useState(".");

  // メッセージが追加されたら最下部へスクロール
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "auto" });
  }, [messages, isThinking]);

  const sendMessage = () => {
    if (!input.trim()) return;

    // ユーザーメッセージを追加
    const userMessage = { sender: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    // エージェントが考えている状態をセット
    setIsThinking(true);

    // 仮のエージェントの応答（2.5秒後に返答）
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          sender: "agent",
          text: `のび太くん！何をそんなに困った顔してるんだい？また宿題を忘れちゃったとか、ジャイアンにからかわれたとか？まったく、キミは相変わらずだねぇ。でも安心して！ぼくがいる限り、どんなことでも解決してみせるよ！

たとえば、時間が足りなくて宿題が終わらないなら、「どこでもドア」で未来の自分に会いに行って、完成した宿題を見せてもらえばいいんだ。でも、それじゃあ勉強にならないよね。うーん、じゃあ「暗記パン」を使って、教科書の内容をペタペタ写しちゃえば、あっという間に覚えられる！でもこれも、ちゃんと努力しないと身につかないか……。

よし、それなら「努力が楽しくなるクスリ」を使おう！これを飲むと、どんなに面倒くさい勉強や練習でも、ワクワクしながら取り組めるようになるんだ！ほら、これでキミも立派な優等生に……って、あれ？何をそんなに疑わしそうな顔してるんだい？キミはぼくのひみつ道具を使うとき、いつも楽をしようとしてばかりだからなぁ。だから、今回は特別に道具なしでやる方法を教えてあげよう！

大事なのは「今できることを精一杯やること」なんだ。未来のことを心配してばかりいても何も変わらないし、過去の失敗をくよくよ悩んでいても意味がないよ。今ここでできることをしっかり積み重ねていけば、いつかきっと大きな力になる。ほら、のび太くんだって、射撃は誰にも負けないくらい上手だし、昼寝の才能なら世界一だし、優しい心だって持ってる。自分の良いところを伸ばしていけば、何だってできるんだよ！

……え？やっぱり道具を貸してほしい？もう、しょうがないなぁ。じゃあ今回は特別に「やる気スイッチ」を押してあげるよ！ポチッ！これでキミも頑張れるはず！さぁ、のび太くん、今日も一緒にがんばろう！`,
        },
      ]);
      setIsThinking(false);
    }, 5500);
  };

  useEffect(() => {
    if (!isThinking) return;

    const dotStates = [".", "..", "..."];
    let index = 0;

    const interval = setInterval(() => {
      index = (index + 1) % dotStates.length;
      setThinkingDots(dotStates[index]);
    }, 500); // 0.5秒ごとに切り替え

    return () => clearInterval(interval); // クリーンアップ
  }, [isThinking]);

  return (
    <div className="flex flex-col h-screen bg-green-50">
      {/* ヘッダー */}
      <header className="p-4 bg-green-800 text-white text-xl font-bold text-center">
        AIチャット
      </header>

      {/* チャット画面 */}
      <div className="flex-1 overflow-auto p-4 bg-green-100">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`flex items-end mb-2 ${
              msg.sender === "user" ? "justify-end" : "justify-start"
            }`}
          >
            {msg.sender === "agent" && (
              <div className="flex items-start">
                <img
                  src={doraemonIcon}
                  alt="Agent"
                  className="w-10 h-10 rounded-full mr-2"
                />
                <div>
                  <p className="text-xs text-gray-600">ドラえもん</p>
                  <div className="bg-pink-100 text-black p-2 rounded-lg max-w-md whitespace-pre-wrap">
                    {msg.text}
                  </div>
                </div>
              </div>
            )}
            {msg.sender === "user" && (
              <div className="bg-blue-900 text-white p-2 rounded-lg max-w-xs whitespace-pre-wrap">
                {msg.text}
              </div>
            )}
          </div>
        ))}

        {/* 「ドラえもんが入力しています」表示 */}
        {isThinking && (
          <div className="flex items-center justify-start mt-2">
            <img
              src={doraemonIcon}
              alt="Agent"
              className="w-10 h-10 rounded-full mr-2"
            />
            <p className="text-gray-500 text-sm">
              ドラえもんが入力しています{thinkingDots}
            </p>
          </div>
        )}

        {/* スクロール位置調整 */}
        <div ref={chatEndRef} />
      </div>

      {/* 入力フォーム */}
      <div className="p-4 bg-white flex">
        <input
          type="text"
          className="input input-bordered flex-1 mr-2"
          placeholder="メッセージを入力..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
        />
        <button
          className="btn bg-blue-500 text-white hover:bg-blue-600"
          onClick={sendMessage}
        >
          送信
        </button>
      </div>
    </div>
  );
};

export default App;
