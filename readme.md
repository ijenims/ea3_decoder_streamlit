# 📊 EA3 File Decoder & Viewer

計測器（EddyStationなど）が出力するバイナリ形式ファイル (`.ea3`) を解析し、波形データの可視化とCSV変換を行うWebアプリケーションです。

Streamlit上で動作し、ブラウザだけで独自のバイナリデータを汎用的なCSV形式（ACT001互換）に変換可能です。

## ✨ 機能

*   **バイナリ解析**: ヘッダー情報を自動解析し、有効な計測データのみを抽出。
*   **電圧変換**: 16bit符号付き整数値を物理量（電圧 ±10V）にスケーリング変換。
*   **波形可視化**: Plotlyを用いたインタラクティブなX-Yリサージュ波形表示（ズーム・パンが可能）。
*   **CSVエクスポート**: メーカー純正ソフト互換（ACT001形式 / Shift-JIS）でのダウンロード機能。

## 🚀 使い方 (Webアプリ)

1.  アプリを開きます（Streamlit Cloud等にデプロイされている場合）。
2.  サイドバーに `.ea3` ファイルをドラッグ＆ドロップします。
3.  自動的に解析が行われ、リサージュ波形が表示されます。
4.  「📥 CSVをダウンロード」ボタンを押すと、変換済みのファイルが保存されます。

## 🛠️ ローカルでの実行方法

手元のPCで開発・実行する場合の手順です。

### 1. リポジトリのクローン
```bash
git clone https://github.com/ijenims/ea3_decoder_streamlit.git
cd ea3_decoder_streamlit
```

### 2. 環境構築
Python 3.11以上の環境を推奨します。

```bash
# 仮想環境の作成と有効化 (Condaの場合)
conda create -n ea3-decoder python=3.11
conda activate ea3-decoder

# 依存ライブラリのインストール
pip install -r requirements.txt
```

### 3. アプリの起動
```bash
streamlit run app.py
```
ブラウザが自動的に立ち上がり、アプリが表示されます。

## 📂 プロジェクト構成

```text
ea3_decoder_streamlit/
├── app.py             # アプリケーションのエントリーポイント (UI処理)
├── src/
│   └── decoder.py     # バイナリ解析ロジック (コア機能)
├── requirements.txt   # 依存ライブラリ一覧
└── README.md          # ドキュメント
```

## 📝 技術仕様メモ (解析結果)

本ツールは以下の仕様に基づいてデコードを行っています。

*   **ファイル形式**: リトルエンディアン (Little Endian)
*   **データ開始位置**: オフセット `0x0100` (256 byte)
*   **データ点数**: ヘッダー `0x0008` (UInt32) の値 - 1
*   **データ構造**: X, Y 成分のインターリーブ (Int16)
*   **スケーリング**:
    $$ Voltage = \frac{RawValue}{3276.8} $$
    (Int16範囲 ±32768 を ±10V レンジにマッピング)

## ⚠️ 注意事項

*   本ツールは非公式の解析ツールです。メーカーの公式サポートを受けることはできません。
*   変換結果の正確性については万全を期していますが、利用は自己責任でお願いします。

## License

MIT License
```

---

### 作業手順
1.  VS Codeで `README.md` を開く（なければ新規作成）。
2.  上の内容を全部ペーストして保存。
3.  ターミナルで以下のコマンドを打ってGitHubに反映。

```powershell
git add README.md
git commit -m "Add README documentation"
git push
```
