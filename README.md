# 🥗 ダイエットレシピ管理アプリ（管理栄養士監修）

> RAG（Retrieval-Augmented Generation）技術と LLM を活用した、個人向けダイエットサポート Web アプリケーション

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.54-red?logo=streamlit)
![LangChain](https://img.shields.io/badge/LangChain-0.3-green)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-412991?logo=openai)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_DB-orange)
![SQLite](https://img.shields.io/badge/SQLite-Local_DB-003B57?logo=sqlite)

**[► ライブデモを試す](https://diet-recipe-rag.streamlit.app/)**

---

## 📌 概要

急激な体重増加をきっかけに、**食事改善を継続的にサポートするツール**が必要と感じ個人開発しました。
単なるレシピ検索ではなく、**管理栄養士視点のアドバイス・栄養計算・記録管理**を統合した、毎日使えるアプリを目指しました。

### 開発の背景と工夫した点

- **RAG の実装**：レシピデータをベクトル化して意味検索し、LLM がコンテキストに基づいた回答を生成するパイプラインをゼロから構築
- **ハルシネーション防止**：キーワードマッチングによるガードレールとシステムプロンプトの設計で、データに存在しない回答を抑制
- **管理栄養士プロンプト設計**：PFC バランス・科学的根拠・推奨頻度を含む専門的なアドバイスを返す prompt engineering を実施
- **個人データの永続化**：SQLite でユーザープロフィール・食事ログ・体重ログをローカルに保存し、プライバシーを確保

---

## 🖥️ 機能一覧

### 🔍 レシピ検索タブ
- 自然言語でのレシピ検索（例：「低カロリーで高たんぱくの夕食は？」）
- GPT-4o-mini が管理栄養士視点で栄養アドバイスを回答
- 参照レシピのPFCバランス（カロリー・たんぱく質・脂質・炭水化物）をバッジ表示
- 「食事ログに追加」ボタンでワンクリック記録

### 👤 プロフィールタブ
- 身長・体重・目標体重・年齢・性別・活動量を入力
- Mifflin-St Jeor 式により BMR・TDEE・目標カロリーを自動計算
- PFC 目標（たんぱく質 1.6g/kg・脂質 25%・炭水化物残り）を表示
- 目標達成までの推定週数を表示

### 📋 食事ログタブ
- 日付・食事種別（朝食/昼食/夕食/間食）・レシピの記録
- 41 品のレシピから選択または自由入力に対応
- 今日の摂取カロリー合計と目標値の比較・進捗バーで可視化

### ⚖️ 体重ログタブ
- 日次体重・体脂肪率の記録
- 過去 60 日の折れ線グラフで推移を可視化
- 目標体重の基準線を表示

### 📅 献立プランナータブ
- 残りカロリーから朝/昼/夕/間食の献立を自動提案
- 手持ち食材からレシピを逆引き検索
- 選択したレシピの買い物リストをカテゴリ別に自動生成

### サイドバー（常時表示）
- 今日の摂取カロリー進捗バー
- RAG 検索パラメータ（検索件数・回答の創造性）の調整

---

## 🏗️ システム構成

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit UI（5タブ）                  │
└─────────────┬──────────────────────────┬────────────────┘
              │                          │
    ┌─────────▼──────────┐   ┌──────────▼──────────┐
    │    RAG パイプライン   │   │   SQLite（diet.db）  │
    │                    │   │                     │
    │  質問               │   │  user_profile       │
    │   ↓                │   │  food_log           │
    │  Embedding 変換      │   │  weight_log         │
    │   ↓                │   └─────────────────────┘
    │  ChromaDB 検索      │
    │   ↓                │
    │  ガードレール判定     │
    │   ↓                │
    │  GPT-4o-mini 生成   │
    └────────────────────┘
```

---

## 🛠️ 技術スタック

| カテゴリ | 技術 | 用途 |
|---|---|---|
| フロントエンド | Streamlit 1.54 | マルチタブ Web UI |
| LLM | OpenAI GPT-4o-mini | 管理栄養士アドバイス生成 |
| Embedding | text-embedding-3-small | レシピのベクトル化 |
| RAG フレームワーク | LangChain 0.3 | LLM オーケストレーション |
| ベクトル DB | ChromaDB | セマンティック検索 |
| ローカル DB | SQLite（標準ライブラリ） | ユーザーデータ永続化 |
| データ処理 | pandas / matplotlib | 体重グラフ・集計 |
| 環境管理 | python-dotenv | API キー管理 |

---

## 📁 ディレクトリ構成

```
recipe-rag-app/
├── app.py                    # エントリーポイント（5タブ構成）
├── requirements.txt
├── src/
│   ├── config.py             # 設定管理
│   ├── sample_data.py        # レシピデータ（41品）
│   ├── db/                   # SQLite CRUD
│   │   ├── schema.py         # テーブル定義・初期化
│   │   ├── user_profile.py
│   │   ├── food_log.py
│   │   └── weight_log.py
│   ├── nutrition/            # 栄養計算ロジック
│   │   ├── tdee.py           # BMR・TDEE計算（Mifflin-St Jeor）
│   │   └── meal_planner.py   # 献立提案アルゴリズム
│   ├── rag/                  # RAGパイプライン
│   │   ├── build_index.py    # ChromaDB構築・ロード
│   │   ├── retriever.py      # セマンティック検索
│   │   └── qa_chain.py       # プロンプト設計・LLM呼び出し
│   └── ui/                   # タブ別UIコンポーネント
│       ├── sidebar.py
│       ├── tab_recipe.py
│       ├── tab_profile.py
│       ├── tab_log.py
│       ├── tab_weight.py
│       └── tab_planner.py
```

---

## 🚀 ローカル環境での起動方法

### 前提条件
- Python 3.11 以上
- OpenAI API キー

### セットアップ

```bash
# リポジトリのクローン
git clone https://github.com/1224tamura-hue/recipe-rag-app.git
cd recipe-rag-app

# 仮想環境の作成・有効化
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 依存パッケージのインストール
pip install -r requirements.txt

# 環境変数の設定
echo "OPENAI_API_KEY=your_api_key_here" > .env

# アプリの起動
streamlit run app.py
```

ブラウザで `http://localhost:8501` にアクセスしてください。

---

## 💡 設計上のこだわり

### ハルシネーション防止（3層ガードレール）
1. **検索チェック**：ベクトル検索でドキュメントが取得できない場合は即座に「該当なし」を返す
2. **キーワードマッチング**：質問のキーワードが取得ドキュメントに存在しない場合はLLMを呼ばない
3. **システムプロンプト**：「コンテキスト外の情報を生成しない」を明示的に指示

### パーソナライズされた回答
- ユーザープロフィール（目標カロリー・PFC目標）をプロンプトに注入し、個人の状況に合わせた栄養アドバイスを生成

### データの完全ローカル管理
- 食事・体重などの個人情報は SQLite でローカル保存し、外部サーバーに送信しない設計

---

## 📝 今後の改善予定

- [ ] レシピをアプリ内から追加・編集できる UI の実装
- [ ] 週次・月次のカロリー集計レポート
- [ ] ユーザー認証による複数人対応
- [ ] 食品データベース API との連携（外食・市販品のカロリー自動入力）
