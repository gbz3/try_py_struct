# try_py_struct

Pythonのstructモジュールを使用したユーティリティスクリプト集

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
