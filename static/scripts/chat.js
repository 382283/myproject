const sendBtn = document.getElementById("send-btn");
      const voiceBtn = document.getElementById("voice-btn");
      const userInput = document.getElementById("user-input");
      const chatHistory = document.getElementById("chat-history");

      // チャット履歴にメッセージを追加
      function addMessage(sender, message) {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add(
          "chat-message",
          sender === "user" ? "user-message" : "bot-message"
        );
        messageDiv.textContent = message;
        chatHistory.appendChild(messageDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight; // スクロールを最下部に
      }

      // 音声認識
      function listenToAudio() {
        // Web Speech APIを使用した音声認識
        const recognition = new (window.SpeechRecognition ||
          window.webkitSpeechRecognition)();
        recognition.lang = "ja-JP";

        recognition.onstart = function () {
          console.log("音声認識を開始しました...");
        };

        recognition.onresult = function (event) {
          const transcript = event.results[0][0].transcript;
          userInput.value = transcript;
          sendMessage();
        };

        recognition.onerror = function (event) {
          alert("音声認識エラー: " + event.error);
        };

        recognition.start();
      }

      // 送信ボタンが押された時
      function sendMessage() {
        const message = userInput.value.trim();
        if (message !== "") {
          addMessage("user", message); // ユーザーのメッセージを表示
          userInput.value = "";

          // サーバーにメッセージを送信
          fetch("/chat", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ message: message }),
          })
            .then((response) => response.json())
            .then((data) => {
              addMessage("bot", data.response); // ボットの返答を表示
            })
            .catch((error) => console.error("エラー:", error));
        }
      }

      // 送信ボタンのクリックイベント
      sendBtn.addEventListener("click", sendMessage);

      // 音声入力ボタンのクリックイベント
      voiceBtn.addEventListener("click", listenToAudio);