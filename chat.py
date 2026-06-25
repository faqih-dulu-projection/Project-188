import os

# Define the HTML content combining Firebase and the local custom representation logic
html_content = """<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>E2EE Chat Space - YTTA</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #121212;
            color: #ffffff;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            height: 100vh;
        }
        header {
            background-color: #1e1e1e;
            padding: 15px;
            text-align: center;
            border-bottom: 2px solid #ff007f;
            box-shadow: 0 2px 10px rgba(0,0,0,0.5);
        }
        header h2 { margin: 0; color: #ff007f; font-size: 1.4rem; }
        .subtitle { font-size: 0.8rem; color: #888; margin-top: 3px; }
        
        #identity-section {
            background-color: #252525;
            padding: 10px;
            display: flex;
            gap: 10px;
            align-items: center;
            justify-content: center;
            border-bottom: 1px solid #333;
        }
        #identity-section input {
            padding: 8px;
            background-color: #121212;
            border: 1px solid #444;
            color: #fff;
            border-radius: 4px;
            text-align: center;
        }

        #chat-box {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 12px;
            background-color: #161616;
        }
        
        .message {
            max-width: 75%;
            padding: 12px 16px;
            border-radius: 12px;
            line-height: 1.4;
            position: relative;
            word-wrap: break-word;
        }
        .message .username {
            font-size: 0.75rem;
            font-weight: bold;
            margin-bottom: 4px;
            display: block;
        }
        
        /* Gaya chat dari diri sendiri (Disamarkan jadi kode waktu secara lokal) */
        .message.sent {
            background-color: #004d40;
            color: #00e5ff;
            align-self: flex-end;
            border-bottom-right-radius: 2px;
            border-left: 4px solid #00e5ff;
        }
        .message.sent .username { color: #00e5ff; }
        
        /* Gaya chat dari orang lain (Tetap teks biasa asli) */
        .message.received {
            background-color: #2d2d2d;
            color: #ffffff;
            align-self: flex-start;
            border-bottom-left-radius: 2px;
            border-left: 4px solid #ff9800;
        }
        .message.received .username { color: #ff9800; }

        #input-area {
            background-color: #1e1e1e;
            padding: 15px;
            display: flex;
            gap: 10px;
            border-top: 1px solid #333;
        }
        #message-input {
            flex: 1;
            padding: 12px;
            border: 2px solid #444;
            border-radius: 6px;
            background-color: #121212;
            color: #fff;
            font-size: 1rem;
        }
        #message-input:focus {
            border-color: #ff007f;
            outline: none;
        }
        #send-btn {
            background-color: #ff007f;
            color: #121212;
            border: none;
            padding: 0 20px;
            font-size: 1rem;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
        }
        #send-btn:hover { background-color: #e0006c; }
    </style>
</head>
<body>

<header>
    <h2>Sandi E2EE Chat Engine</h2>
    <div class="subtitle">Pesan lu tersamar otomatis di layar lu sendiri 🎭</div>
</header>

<div id="identity-section">
    <label for="username-input">Nickname Lu:</label>
    <input type="text" id="username-input" value="User_Anon">
</div>

<div id="chat-box"></div>

<div id="input-area">
    <input type="text" id="message-input" placeholder="Ketik sesuatu di sini..." onkeypress="handleKeyPress(event)">
    <button id="send-btn" onclick="sendMessage()">KIRIM</button>
</div>

<script type="module">
    import { initializeApp } from "https://www.gstatic.com/firebasejs/12.15.0/firebase-app.js";
    import { getDatabase, ref, push, onChildAdded } from "https://www.gstatic.com/firebasejs/12.15.0/firebase-database.js";

    const firebaseConfig = {
        apiKey: "AIzaSyD3tna4rUSr_FH0eb08aI3AX3Z-fVcqaj8",
        authDomain: "fruitsmasmaster.firebaseapp.com",
        databaseURL: "https://fruitsmasmaster-default-rtdb.firebaseio.com",
        projectId: "fruitsmasmaster",
        storageBucket: "fruitsmasmaster.firebasestorage.app",
        messagingSenderId: "673530855742",
        appId: "1:673530855742:web:0e580efc3a318efa4cac6f",
        measurementId: "G-2CYKYD9M3S"
    };

    // Inisialisasi Firebase
    const app = initializeApp(firebaseConfig);
    const db = getDatabase(app);
    const chatRef = ref(db, "e2ee_chats");

    // ALGORITMA ENKRIPSI LOKAL (Teks -> Angka Kode Waktu)
    const MINGGU = 604800n, HARI = 86400n, JAM = 3600n, MENIT = 60n;

    function enkripsiUltimate(input) {
        let hasil = "";
        const karakterArray = Array.from(input);
        for (let char of karakterArray) {
            const codePoint = char.codePointAt(0);
            const strCode = String(codePoint);
            const panjang = strCode.length;
            const penandaNol = "0".repeat(String(panjang).length);
            hasil += `${penandaNol}${panjang}${strCode}`;
        }
        return hasil;
    }

    function encodeKeWaktu(angkaString) {
        if (!angkaString) return "-";
        const totalDetik = BigInt("9" + angkaString);
        const minggu = totalDetik / MINGGU;
        let sisa = totalDetik % MINGGU;
        const hari = sisa / HARI; sisa %= HARI;
        const jam = sisa / JAM; sisa %= JAM;
        const menit = sisa / MENIT;
        const detik = sisa % MENIT;
        return `${minggu}${String(hari).padStart(2,'0')}${String(jam).padStart(2,'0')}${String(menit).padStart(2,'0')}${String(detik).padStart(2,'0')}`;
    }

    // Fungsi Kirim Pesan ke Firebase
    window.sendMessage = function() {
        const inputEl = document.getElementById("message-input");
        const userEl = document.getElementById("username-input");
        const text = inputEl.value.trim();
        const username = userEl.value.trim() || "Anonim";

        if (!text) return;

        // Kirim teks asli murni ke database (biar temen bisa baca)
        push(chatRef, {
            sender: username,
            message: text,
            timestamp: Date.now()
        });

        inputEl.value = "";
    };

    window.handleKeyPress = function(e) {
        if (e.key === 'Enter') {
            window.sendMessage();
        }
    };

    // Dengarkan pesan masuk dari Firebase
    onChildAdded(chatRef, (snapshot) => {
        const data = snapshot.val();
        const currentUser = document.getElementById("username-input").value.trim() || "Anonim";
        
        const chatBox = document.getElementById("chat-box");
        const msgDiv = document.createElement("div");
        
        if (data.sender === currentUser) {
            // JIKA DIRI SENDIRI: Ubah teks asli menjadi kode waktu di sisi client (Local Only)
            msgDiv.className = "message sent";
            const kodeWaktuLokal = encodeKeWaktu(enkripsiUltimate(data.message));
            
            msgDiv.innerHTML = `
                <span class="username">${data.sender} (Lu)</span>
                <div class="msg-text">🔒 ${kodeWaktuLokal}</div>
            `;
        } else {
            // JIKA ORANG LAIN: Tampilkan teks normal biasa tanpa diubah
            msgDiv.className = "message received";
            msgDiv.innerHTML = `
                <span class="username">${data.sender}</span>
                <div class="msg-text">${data.message}</div>
            `;
        }
        
        chatBox.appendChild(msgDiv);
        chatBox.scrollTop = chatBox.scrollHeight; // Auto scroll ke bawah
    });
</script>
</body>
</html>"""

# Write code to a local file
file_name = "e2ee_chat_firebase.html"
with open(file_name, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"File {file_name} successfully generated.")

