# try_py_struct

Pythonのstructモジュールとconstructモジュールを使用したバイナリデータ処理ユーティリティ集

## 概要

- **struct_size.py**: structフォーマット文字列のサイズ計算ツール
- **generate_records.py**: 固定長レコードのサンプルデータ生成ツール
- **record_parser.py**: 固定長レコードのバイナリデータパーサー

---

## struct_size.py

フォーマット文字列からデータ長を計算するコマンドラインツールです。

### 機能

- structフォーマット文字列のバイト数を計算
- バイトオーダー情報の表示
- フォーマット構成の解析と表示

### 使用方法

```bash
# 実行権限を付与
chmod +x struct_size.py

# 基本的な使い方
./struct_size.py "i"           # int型 (4バイト)
./struct_size.py "2i"          # int型 x 2 (8バイト)
./struct_size.py "ihb"         # int + short + char (7バイト)

# バイトオーダーを指定
./struct_size.py "<2H"         # リトルエンディアンでunsigned short x 2
./struct_size.py "!iHH"        # ネットワーク順序でint + short x 2

# 文字列フォーマット
./struct_size.py "10s"         # 10バイトの文字列

# シンプル出力（サイズのみ）
./struct_size.py -s "iHH"

# 詳細モード
./struct_size.py -v "!iHH"
```

### オプション

- `-s, --simple`: サイズのみを出力（詳細情報を省略）
- `-v, --verbose`: 詳細情報を表示（使用例も含む）
- `-h, --help`: ヘルプを表示

### フォーマット文字の例

| 文字 | C型 | Pythonサイズ | 説明 |
|------|-----|--------------|------|
| x | - | 1 | パディングバイト |
| c | char | 1 | 文字 |
| b | signed char | 1 | 符号付き整数 |
| B | unsigned char | 1 | 符号なし整数 |
| ? | _Bool | 1 | bool値 |
| h | short | 2 | 符号付き短整数 |
| H | unsigned short | 2 | 符号なし短整数 |
| i | int | 4 | 符号付き整数 |
| I | unsigned int | 4 | 符号なし整数 |
| l | long | 4 | 符号付き長整数 |
| L | unsigned long | 4 | 符号なし長整数 |
| q | long long | 8 | 符号付き長長整数 |
| Q | unsigned long long | 8 | 符号なし長長整数 |
| f | float | 4 | 浮動小数点数 |
| d | double | 8 | 倍精度浮動小数点数 |
| s | char[] | - | 文字列 |
| p | char[] | - | Pascal文字列 |
| P | void* | - | ポインタ |

### バイトオーダー文字

| 文字 | 意味 |
|------|------|
| @ | ネイティブ（デフォルト） |
| = | ネイティブ標準 |
| < | リトルエンディアン |
| > | ビッグエンディアン |
| ! | ネットワーク（ビッグエンディアン） |

---

## generate_records.py

固定長レコード（120バイト）のサンプルバイナリデータを標準出力に生成するツールです。

### 機能

- ヘッダ、データ、トレーラレコードを含む固定長バイナリデータの生成
- レコード区分: 1=ヘッダ, 2=データ, 8=トレーラ
- 各レコードは120バイト固定長
- constructモジュールを使用した構造化データの生成
- Shift_JISエンコーディング対応

### 依存パッケージ

```bash
pip install construct
```

### 使用方法

```bash
# 実行権限を付与
chmod +x generate_records.py

# デフォルト設定でサンプルデータ生成（10件のデータレコード）
python generate_records.py > sample.bin

# データレコード数を指定（5件）
python generate_records.py -n 5 > sample.bin

# パイプでパーサーに直接送る
python generate_records.py -n 10 | python record_parser.py
```

### オプション

- `-n, --num-records N`: 生成するデータレコード数 (デフォルト: 10)
- `-h, --help`: ヘルプを表示

### レコード構造

#### ヘッダレコード（120バイト）
- レコード区分: 1バイト（値=1）
- ファイル名: 30バイト（Shift_JIS）
- 作成日: 8バイト（YYYYMMDD）
- 作成時刻: 6バイト（HHMMSS）
- 総レコード数: 4バイト（符号なし整数）
- バージョン: 10バイト
- 予約領域: 61バイト

#### データレコード（120バイト）
- レコード区分: 1バイト（値=2）
- レコードID: 4バイト（符号なし整数）
- 名前: 50バイト（Shift_JIS）
- 値: 4バイト（符号なし整数）
- ステータス: 1バイト（0=無効, 1=有効）
- タイムスタンプ: 14バイト（YYYYMMDDHHmmss）
- 説明: 40バイト（Shift_JIS）
- 予約領域: 6バイト

#### トレーラレコード（120バイト）
- レコード区分: 1バイト（値=8）
- データレコード数: 4バイト（符号なし整数）
- 値の合計: 8バイト（符号なし64bit整数）
- チェックサム: 4バイト（符号なし整数）
- 予約領域: 103バイト

---

## record_parser.py

固定長レコード（120バイト）のバイナリデータを標準入力から読み込んでパースするツールです。

### 機能

- 標準入力からの固定長バイナリレコードの読み込みとパース
- レコード区分の自動判別
- ヘッダ、データ、トレーラレコードの構造化解析
- サマリー表示および詳細表示モード
- Shift_JISエンコーディング対応

### 依存パッケージ

```bash
pip install construct
```

### 使用方法

```bash
# 実行権限を付与
chmod +x record_parser.py

# 標準入力から読み込み（全レコードを表示）
python generate_records.py | python record_parser.py

# サマリー情報のみ表示
python generate_records.py -n 5 | python record_parser.py -s

# 詳細情報を表示
python generate_records.py -n 5 | python record_parser.py -v
```

### オプション

- `-s, --summary`: サマリー情報のみ表示（各レコードタイプの件数）
- `-v, --verbose`: 詳細情報を表示（説明フィールドなども含む）
- `-h, --help`: ヘルプを表示

### 実行例

```bash
# サンプルデータを生成してパース
$ python generate_records.py -n 3 | python record_parser.py

============================================================
レコード #1 [HEADER]
============================================================
  ファイル名: sample_data.bin
  作成日時: 20260208 062425
  総レコード数: 5
  バージョン: 1.0

============================================================
レコード #2 [DATA]
============================================================
  レコードID: 1
  名前: 田中太郎
  値: 1000
  ステータス: 無効
  タイムスタンプ: 20260208062425

============================================================
レコード #3 [DATA]
============================================================
  レコードID: 2
  名前: 佐藤花子
  値: 2000
  ステータス: 有効
  タイムスタンプ: 20260208062425

...

# サマリー表示
$ python generate_records.py -n 10 | python record_parser.py -s

総レコード数: 12
  ヘッダレコード: 1
  データレコード: 10
  トレーラレコード: 1
```

---

## 開発フロー

```bash
# 仮想環境の作成
python -m venv .venv

# 仮想環境の有効化
source .venv/bin/activate

# pip upgrade
pip install --upgrade pip

# パッケージのインストール
pip install <必要なパッケージ>
```

## モジュールの確認とインストール

```bash
# structモジュール（標準ライブラリ）
python -c "import struct" && echo "Installed" || echo "Not installed"

# constructモジュール
python -c "import construct" && echo "Installed" || echo "Not installed"

# constructのインストール
pip install construct
```

## 使用例

```bash
# サンプルデータを生成してファイルに保存
python generate_records.py -n 20 > records.bin

# ファイルの16進数ダンプを確認
xxd records.bin | head -n 20

# パイプでパースして内容を確認
python generate_records.py -n 5 | python record_parser.py

# サマリーを表示
python generate_records.py -n 100 | python record_parser.py -s

# 詳細情報を表示
python generate_records.py -n 5 | python record_parser.py -v
```
