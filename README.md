# 研究開発支援システム（研究ログ）

研究で「その日、どの部分を、どうやって、**なぜ**進めたか」を残すための Web アプリです。
コードの変更履歴（GitHub）・発表資料や論文・日々の記録を 1 か所でつなぎます。

- ブラウザで動くので、PC・スマホのどちらからでも使えます
- サーバー代は 0 円（GitHub Pages と Firebase の無料枠で動きます）
- データは**自分専用の Firebase** に入るので、他の人と混ざりません

> **困ったら AI に聞いてください**：同梱の `FOR_AI_ASSISTANT.md` の中身を Claude や ChatGPT に貼ってから質問すると、このシステムの構成を理解した上で、セットアップやトラブル対応を1ステップずつ案内してくれます。

---

## 目次

1. [できること](#できること)
2. [必要なもの](#必要なもの)
3. [まず試す（デモモード）](#まず試すデモモード)
4. [セットアップ（30〜40分）](#セットアップ3040分)
5. [普段の使い方](#普段の使い方)
6. [研究コードを GitHub で管理する準備](#研究コードを-github-で管理する準備)
7. [資料・成果物の扱い](#資料成果物の扱い)
8. [スマホで使う](#スマホで使う)
9. [アプリの更新・カスタマイズ](#アプリの更新カスタマイズ)
10. [困ったとき](#困ったとき)
11. [仕組みと制限](#仕組みと制限)

---

## できること

| 機能 | 内容 |
|---|---|
| 日々の記録 | 研究テーマ（カテゴリ）ごとに、作業内容／**なぜそうしたか**／結果・次にやること／コード断片／リンク／写真を記録。一覧ではひとことだけ表示し、クリックで詳細が開く |
| 前回の続き | 新しい記録を書くとき、前回の「次にやること」が上に表示される |
| GitHub 連携 | 記録の日付のコミットが自動で一覧に出て、チェックするだけで記録に紐づく |
| 詳細 | 目的・最終期限・ロードマップ（マイルストーンと残り日数）・研究の流れ（Word を取り込んで表示） |
| 成果物・資料 | 発表スライドや論文の PDF・Word・画像を、アプリの中でそのまま閲覧 |
| ホーム | 研究テーマ一覧・近い期限・最近の記録 |
| 週次まとめ | 1 週間の記録から、ゼミ報告の下書きを作る（AI に貼る依頼文を自動作成） |
| バックアップ | Markdown／JSON で書き出し、JSON から復元 |
| 使い方 | アプリ左メニューの「使い方」でいつでも確認できる |

---

## 必要なもの

- **Google アカウント**（Firebase とログインに使います）
- **GitHub アカウント**（https://github.com で無料作成）
- PC（Windows / Mac / Linux どれでも可）
- 研究コードを GitHub で管理する場合は **VS Code**（無料）

---

## まず試す（デモモード）

`js/config.js` が空のままだと、**このブラウザの中だけに保存するデモモード**で動きます。セットアップ前に雰囲気を見たいときに使ってください。

`index.html` をダブルクリックで開くと動きません（ブラウザの制限）。次のどちらかで開いてください。

**方法A：Python があるPC**
```bash
cd research-support
python -m http.server 8000      # Windows で動かなければ  py -m http.server 8000
```
ブラウザで http://localhost:8000 を開く。

**方法B：先に GitHub Pages に置く**
下の「セットアップ 2」まで進めると、そのままデモモードで開けます。

---

## セットアップ（30〜40分）

### 1. Firebase（データの保存先）を作る

Firebase は Google のサービスで、ログイン機能とデータベースを無料枠で使えます。

1. https://console.firebase.google.com/ を開き、「プロジェクトを作成」
   - プロジェクト名は自由（例：`research-log`）
   - Google アナリティクスは**オフ**でOK
   - プランは **Spark（無料）** のまま
2. **Google ログインを有効にする**
   - 左メニュー「セキュリティ」→「Authentication」→「始める」
   - 「ログイン方法」タブ →「Google」→「有効にする」をオン → サポートメールを選んで「保存」
3. **データベースを作る**
   - 左メニュー「Database と Storage」→「Firestore」→「データベースを作成」
   - エディション：Standard（聞かれた場合）／データベース ID：`(default)` のまま
   - ロケーション：**`asia-northeast1`（東京）** ※後から変更できません
   - セキュリティルール：**本番環境モード**
4. **ルールを設定する**
   - Firestore の「ルール」タブで、中身を全部消して、このフォルダの `firestore.rules` の中身を貼り付け →「公開」
   - ※右上の「開発とテスト」ボタンは押さないこと（誰でも読み書きできる設定になります）
5. **Web アプリを登録する**
   - 左上「設定（歯車）」→「全般」→ 下の「マイアプリ」で `</>`（ウェブ）を押す
   - ニックネームは自由。「Firebase Hosting も設定する」は**チェックしない**
   - 表示された `firebaseConfig` の値（apiKey〜appId）を、`js/config.js` の同じ項目に貼り付けて保存
   - `measurementId` や `getAnalytics` の行は不要です
   - npm / script タグなどの選択肢は表示形式を変えるだけなので、どれでも構いません

> `config.js` の値は公開されても問題ない設計です。データは手順4のルールで守られます。

### 2. GitHub Pages で公開する（コマンド不要）

1. GitHub 右上「＋」→「New repository」
   - Repository name：好きな名前（例：`research-log`）※サイトの URL になります。半角英小文字推奨
   - **Public** を選ぶ（無料プランの GitHub Pages は公開リポジトリが必要。公開されるのはアプリのプログラムだけで、記録の中身は Firebase にあるので見えません）
   - 「Add a README file」などのチェックは付けない
2. 作成直後の画面の「**uploading an existing file**」リンクを押す
3. このフォルダの**中身を全部**（フォルダごとではなく、`index.html` などを選んで）ドラッグ＆ドロップ
   - 一覧に `js/app.js`、`js/vendor/…`、`css/style.css` があることを確認
4. 「Commit changes」
5. リポジトリの「Settings」→ 左メニュー「Pages」
   - Source：**Deploy from a branch** ／ Branch：**main**、**/(root)** →「Save」
6. 1〜3分後に同じページを再読み込みすると、上部に `https://<ユーザー名>.github.io/<リポジトリ名>/` が表示されます

### 3. ログインできるようにする

1. Firebase の「Authentication」→「設定」タブ →「承認済みドメイン」→「ドメインを追加」
   - `<ユーザー名>.github.io` だけを入力（`https://` やリポジトリ名は付けない）
2. サイトを開いて「Google でログイン」
3. **自分専用にする（推奨）**
   - アプリの「設定・バックアップ」に表示される **UID** をコピー（手で打たずにコピーすること）
   - Firestore のルールの `allow` の行を次のようにして「公開」

```
      allow read, write: if request.auth != null
                         && request.auth.uid == uid
                         && uid == "ここにコピーしたUID";
```

これで、他の Google アカウントでログインされても一切読み書きできません。

### 4. 任意の設定（アプリの「設定・バックアップ」画面）

| 項目 | 何に使う | 作り方 |
|---|---|---|
| GitHub トークン | **非公開**リポジトリのコミット一覧・資料閲覧。公開リポジトリだけなら不要 | 下の「GitHub トークンの作り方」 |
| Anthropic API キー | 週次まとめをボタン 1 つで作る。**無くても**「依頼文をコピー」→ claude.ai や ChatGPT に貼れば使える | https://console.anthropic.com/ で発行。従量課金なので利用上限を設定しておく |

トークンや API キーは**その端末のブラウザにだけ**保存されます（Firebase には送りません）。PC とスマホで使うなら、それぞれで入力してください。

#### GitHub トークンの作り方

1. https://github.com/settings/personal-access-tokens/new を開く
2. 次のように設定

| 項目 | 設定 |
|---|---|
| Token name | 例：`research-log-PC` |
| Expiration | 1 年程度 |
| Repository access | **Only select repositories** → 研究コードのリポジトリを選ぶ |
| Permissions | 「Add permissions」→ **Contents** → **Read-only**（Metadata は自動で付く） |

3. 「Generate token」→ 表示された `github_pat_…` を**画面を閉じる前に**アプリの設定に貼って保存
   - トークンは一度しか表示されません。失くしたら作り直せば OK
   - パスワードと同じ扱いなので、メモ帳やチャットには貼らないこと
   - 端末ごとに別のトークンを作っておくと、失くした端末の分だけ無効化できます
   - 新しい研究リポジトリを作ったら、トークンの対象に追加が必要です

---

## 普段の使い方

コードの「**何を**変えたか」は Git が正確に覚えます。人が書くのは「**なぜ**そうしたか」だけ、という役割分担です。

```
【GitHub】このアプリのリポジトリ …… アプリ本体（公開）
【GitHub】研究コードのリポジトリ …… コードと変更履歴（非公開でOK）
【Firebase】Firestore …………………… 日々の記録・研究の流れ・アップロードした資料
```

### 1 日の流れ

1. **作業を始める**：VS Code を開いたら、左下のぐるっと回る矢印（Sync）を押して GitHub 側の変更を取り込む
2. **研究する**：いつも通りコードを直して、動かして、結果を見る
3. **キリのいいところで GitHub に送る**（何回やっても OK）
   - 左の「Source Control」（枝分かれのアイコン）を開く
   - Message 欄に何を変えたかを短く書く（例：`閾値を0.6→0.5に変更`）
   - 「Commit」→ 青いボタンが「Sync Changes 1↑」に変わるので押す
4. **アプリで記録を書く**
   - カテゴリで「＋ 追加」→ 前回の「次にやること」が上に出る
   - 「この日のコミット」に 3 の履歴が並ぶので、関係するものにチェック
   - 「なぜそうしたか」を書いて保存（Ctrl+Enter でも保存）
   - 疲れた日は「ひとことで」だけでも保存できます
5. **振り返る**：記録のコミットのリンクから、その日どの行をどう変えたかが GitHub で見られる。週末は「週次まとめ」でゼミ報告の下書き

### VS Code の英語表記

| 日本語で言うと | VS Code の表示 |
|---|---|
| コミット（手元に保存） | Commit |
| 同期（取り込み＋送信） | Sync Changes ／ 左下のぐるっと回る矢印 |
| 取り込みだけ | Source Control 右上「…」→ Pull |
| 送信だけ | Source Control 右上「…」→ Push |
| 全部をコミット対象に入れる | 「Changes」の見出しにマウスを乗せて「＋」（Stage All Changes） |
| 直前のコミットを取り消す | Source Control 右上「…」→ Commit → Undo Last Commit |

---

## 研究コードを GitHub で管理する準備

研究ごとに 1 回だけ。全体で 20〜30 分です。

1. **VS Code をインストール**：https://code.visualstudio.com/
   - Jetson など ARM の Linux なら「.deb」の **Arm64** 版
2. **Git をインストールして名前を登録**（ターミナルで）
   ```bash
   # Linux の場合（Windows/Mac は https://git-scm.com/ からインストール）
   sudo apt install git
   git config --global user.name "GitHubのユーザー名"
   git config --global user.email "GitHubに登録したメール"
   ```
3. **VS Code で GitHub にログイン**：左下の人型アイコン →「GitHub でサインイン」→ ブラウザで「Authorize」
4. **大きいファイルを除外する設定を作る**（重要）
   - 同梱の `gitignore-template.txt` を研究フォルダにコピーし、名前を **`.gitignore`** に変える
   - GitHub は 1 ファイル 100MB まで。重み・動画・データセット・出力は Git で管理しません
   - 送られる予定のファイルを事前に確認するには：
     ```bash
     cd 研究フォルダ
     git init -b main
     git add -A --dry-run
     ```
5. **GitHub に公開**
   - VS Code で「File → Open Folder」→ 研究フォルダ
   - 「Trust」（このフォルダを信頼）を押す
   - Source Control で Message を書いて「Commit」→「Publish Branch」
   - リポジトリ名を入れて **「private」**（非公開）を選ぶ
6. **アプリと接続**
   - カテゴリの「詳細」→「GitHub リポジトリ」に `ユーザー名/リポジトリ名` を入れて保存
   - 非公開リポジトリなので、「設定・バックアップ」に GitHub トークンを入れる
   - 記録の「＋ 追加」で「この日のコミット」に初回コミットが出れば完成

> `.gitignore` で除外したファイル（学習済みの重みなど）は GitHub にバックアップされません。大事な重みは Google Drive や USB にもコピーしておいてください。

---

## 資料・成果物の扱い

カテゴリ画面上部の「成果物」（発表スライド・予稿・ポスター等）と、「詳細」の中の「関連資料」に登録できます。置き場所は 3 通りです。

| 置き場所 | 向いているもの | 注意 |
|---|---|---|
| **GitHub のファイル**（おすすめ） | 発表資料・論文など、版を遡りたいもの | 研究リポジトリの `docs/` などに置く。版の履歴が残る |
| **アプリにアップロード** | 手早く上げたいもの、Git に入れたくないもの | 1 ファイル 15MB まで。差し替えると前の版は残らない |
| **リンクだけ** | Google Drive や学会ページ | アプリ内では閲覧できない |

- **PC から GitHub に資料を上げる**：ブラウザで研究リポジトリの `docs` フォルダを開き（先にフォルダの中に入る）、「Add file」→「Upload files」→「Commit changes」。その後、アプリで「＋ 成果物を追加」→「GitHub のファイル」→「ファイル一覧を読み込む」から選ぶ
  - ブラウザから上げた後は、次に VS Code で作業するとき最初に Sync を押して取り込む
- **閲覧できる形式**：PDF・Word（.docx）・画像・Markdown
- **PowerPoint** はブラウザで表示できないので、「エクスポート → PDF」したものも一緒に置いて PDF の方を登録するのがおすすめ
- **研究の流れ**：「詳細」→「書く・Word から取り込む」で、Word のロードマップ等を見出し・表・チェックボックス付きの文章に変換して保存できます

---

## スマホで使う

1. Safari（Android は Chrome）でサイトの URL を開いて Google でログイン
2. 共有ボタン →「ホーム画面に追加」でアプリのように使える
   - iPhone では、ホーム画面から開いた場合にもう一度ログインが必要です
   - ホーム画面から開くとログインがうまくいかないことがあります。その場合は Safari のブックマークから使ってください
3. 記録の読み書き、写真の添付、アプリへの資料アップロードはトークン無しで使えます。GitHub のコミット一覧や GitHub 上の資料の閲覧には、スマホにもトークンが必要です

---

## アプリの更新・カスタマイズ

### 修正版を反映する

アプリのリポジトリで「Add file」→「Upload files」に、新しいファイルを（フォルダ構成ごと）ドラッグ →「Commit changes」。1〜2 分後に **Ctrl+Shift+R** で再読み込み。

- 入力欄を増やす・見た目を変えるなどは、ファイルを差し替えるだけで OK。Firebase 側の作業は不要です
- 既存の項目の名前や意味を変える場合だけ、過去のデータの移行が必要になります
- 変更前に「設定・バックアップ」→「JSON で全データ書き出し」をしておくと安心

### 名前・アイコン・色を変える

| 変えたいもの | 場所 |
|---|---|
| ブラウザのタブの名前 | `index.html` の `<title>` |
| 画面左上・ログイン画面の名前 | `js/app.js` の「研究開発支援システム」の文字（2 か所） |
| ホーム画面に追加したときの名前 | `manifest.webmanifest` の `name` / `short_name`、`index.html` の `apple-mobile-web-app-title` |
| アイコン | `icon.svg` を差し替え。PNG にする場合は `index.html` と `manifest.webmanifest` の参照も合わせて変える |
| 色 | `css/style.css` の先頭（`:root` の `--navy` などの色の定義） |

---

## 困ったとき

| 症状 | 対処 |
|---|---|
| 変更が反映されない | Ctrl+Shift+R で再読み込み（スマホはタブを開き直す）。アイコンはブラウザを再起動しないと変わらないことがある |
| 画面上部に赤い帯「拒否されています」 | Firestore のルールが「公開」済みか、ルールの UID が「設定・バックアップ」の UID と一字一句同じか確認。切り分けには UID の条件を一度外して公開してみる |
| ログインできない | Authentication の「承認済みドメイン」に `<ユーザー名>.github.io` があるか／「ログイン方法」で Google が有効か／ポップアップがブロックされていないか |
| コミットが一覧に出ない | VS Code で Sync まで押したか／記録の日付とコミットした日が合っているか／「詳細」にリポジトリを登録したか／この端末にトークンを入れたか。表示されるのは既定ブランチ（main）のコミットだけ |
| 「トークンが無効です」 | 有効期限切れ。作り直して入れ直す |
| VS Code の Commit を押しても何も起きない | Message 欄が空。何を変えたかを書いてから押す |
| 間違ったファイル（zip 等）をコミットしてしまった | **Sync する前なら**：「…」→ Commit → Undo Last Commit → そのファイルを「−」で外す → 右クリック「Add to .gitignore」→ もう一度 Commit。Sync した後だと履歴から消すのが大変なので、Sync 前に Graph で中身を確認する習慣を |
| リポジトリを間違えて Public にした | GitHub のリポジトリ → Settings → 一番下の Danger Zone →「Change visibility」→ Make private |
| VS Code で「Authentication required（keyring）」 | Linux のパスワード保管庫。PC のログインパスワードを入れて Unlock |
| VS Code で「Extension host cannot start: version mismatch」 | VS Code が裏で更新された。「Relaunch VS Code」を押す |
| 「You must be signed in to use AI features」 | AI（Copilot）機能用で Git とは無関係。Cancel で OK。消したければ Settings で `disable AI` を検索し「Chat: Disable AI Features」にチェック |
| VS Code で「Restricted Mode」 | 自分のフォルダなら「Trust」を押す。押さないと Git が使えない |

---

## 仕組みと制限

### フォルダ構成

```
README.md               この説明書
FOR_AI_ASSISTANT.md     AI に貼る用の説明書
index.html              画面の土台
manifest.webmanifest    ホーム画面に追加したときの設定
icon.svg                アイコン
firestore.rules         Firestore のルール（Firebase に貼る用）
gitignore-template.txt  研究コード用 .gitignore のひな形
css/style.css           見た目
js/config.js            Firebase の設定（自分の値を貼る）
js/app.js               画面と操作
js/store.js             データ保存（Firebase／デモモード）
js/github.js            GitHub 連携（読み取りのみ）
js/docs.js              Word・PDF・Markdown の表示、資料のアップロード
js/summary.js           週次まとめ
js/vendor/              Word・Markdown 表示用ライブラリ（同梱。ライセンスは LICENSES.txt）
```

### データの置き場所（Firestore）

```
users/{uid}/categories    研究テーマ（目的・期限・リポジトリ・ロードマップ・研究の流れ）
users/{uid}/logs          日々の記録
users/{uid}/attachments   記録の添付（写真など）
users/{uid}/docs          資料・成果物の登録情報
users/{uid}/blobs         アプリにアップロードした資料の本体（分割保存）
users/{uid}/summaries     週次まとめの下書き
```

### 制限・注意

- Firebase 無料枠：保存 1GiB、読み取り 5 万回/日、書き込み 2 万回/日（個人利用なら十分）
- 記録の添付：画像は自動縮小、それ以外は 600KB まで。資料のアップロードは 15MB まで
- 週次まとめの API 呼び出しはブラウザから直接行います。自分専用サイトで、キーを自分の端末にだけ置く前提の設計です
- **月に 1 回は「JSON で全データ書き出し」でバックアップ**を取ってください（添付・資料も含めて復元できます）
