// Firebase コンソール →「プロジェクトの設定」→「マイアプリ」に表示される値を貼り付けてください。
// apiKey が空のままだと「デモモード」（このブラウザだけに保存）で動きます。
// ※ この値は公開されても問題ない設計です。データの保護は firestore.rules が担います。
export const firebaseConfig = {
  apiKey: "AIzaSyBJ-PTEwRxkpqZi-jOph72bqFsqrHFmSW8",
  authDomain: "kawasemi-rock.firebaseapp.com",
  projectId: "kawasemi-rock",
  storageBucket: "kawasemi-rock.firebasestorage.app",
  messagingSenderId: "430556426148",
  appId: "1:430556426148:web:5e09b99210224bce8cdb31"
};

// 任意：自分のメールアドレスを入れると、それ以外のアカウントはログイン直後に締め出します。
// （本当の守りは firestore.rules。こちらは画面上の案内用です）
export const ALLOWED_EMAIL = "";
