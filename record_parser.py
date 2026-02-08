#!/usr/bin/env python3
"""
constructモジュールを使用した固定長レコードパーサー

120バイトの固定長レコードを標準入力から読み込んでパースします。
レコード区分: 1=ヘッダ, 2=データ, 8=トレーラ
"""

import sys
from construct import *


# レコード区分の定義
RECORD_TYPE_HEADER = 1
RECORD_TYPE_DATA = 2
RECORD_TYPE_TRAILER = 8

RECORD_SIZE = 120  # 固定長レコードサイズ


# shift_jisエンコーディングをサポートするカスタムアダプター
class ShiftJISString(Adapter):
    """shift_jisエンコーディングの固定長文字列フィールド"""
    def __init__(self, length):
        super().__init__(Bytes(length))
        self.length = length
    
    def _decode(self, obj, context, path):
        # バイト列から文字列にデコード（NULLバイトで終端を削除）
        return obj.rstrip(b'\x00').decode('shift_jis', errors='ignore')
    
    def _encode(self, obj, context, path):
        # 文字列をshift_jisでエンコードして、指定長にNULLパディング
        encoded = obj.encode('shift_jis')
        if len(encoded) > self.length:
            raise ValueError(f"文字列が長すぎます: {len(encoded)} > {self.length}")
        return encoded.ljust(self.length, b'\x00')


# ヘッダレコードの構造定義（120バイト）
HeaderRecord = Struct(
    "record_type" / Const(RECORD_TYPE_HEADER, Int8ul),  # レコード区分: 1
    "file_name" / ShiftJISString(30),  # ファイル名
    "creation_date" / PaddedString(8, "ascii"),  # 作成日 YYYYMMDD
    "creation_time" / PaddedString(6, "ascii"),  # 作成時刻 HHMMSS
    "total_records" / Int32ul,  # 総レコード数
    "version" / PaddedString(10, "ascii"),  # バージョン
    "reserved" / Padding(61),  # 予約領域
)


# データレコードの構造定義（120バイト）
DataRecord = Struct(
    "record_type" / Const(RECORD_TYPE_DATA, Int8ul),  # レコード区分: 2
    "record_id" / Int32ul,  # レコードID
    "name" / ShiftJISString(50),  # 名前
    "value" / Int32ul,  # 値
    "status" / Int8ul,  # ステータス (0=無効, 1=有効)
    "timestamp" / PaddedString(14, "ascii"),  # タイムスタンプ YYYYMMDDHHmmss
    "description" / ShiftJISString(40),  # 説明
    "reserved" / Padding(6),  # 予約領域
)


# トレーラレコードの構造定義（120バイト）
TrailerRecord = Struct(
    "record_type" / Const(RECORD_TYPE_TRAILER, Int8ul),  # レコード区分: 8
    "data_record_count" / Int32ul,  # データレコード数
    "total_value_sum" / Int64ul,  # 値の合計
    "checksum" / Int32ul,  # チェックサム
    "reserved" / Padding(103),  # 予約領域
)


def detect_record_type(data):
    """
    レコードの先頭バイトからレコード区分を判定
    """
    if len(data) < 1:
        return None
    return data[0]


def parse_record(data):
    """
    レコードデータをパースして適切な構造体で解析
    
    Args:
        data: 120バイトのバイナリデータ
        
    Returns:
        パース結果の辞書とレコード区分のタプル
    """
    if len(data) != RECORD_SIZE:
        raise ValueError(f"レコードサイズが不正です。期待値: {RECORD_SIZE}バイト、実際: {len(data)}バイト")
    
    record_type = detect_record_type(data)
    
    if record_type == RECORD_TYPE_HEADER:
        parsed = HeaderRecord.parse(data)
        return parsed, "HEADER"
    elif record_type == RECORD_TYPE_DATA:
        parsed = DataRecord.parse(data)
        return parsed, "DATA"
    elif record_type == RECORD_TYPE_TRAILER:
        parsed = TrailerRecord.parse(data)
        return parsed, "TRAILER"
    else:
        raise ValueError(f"不明なレコード区分: {record_type}")


def parse_stream(stream):
    """
    バイナリストリームを読み込んで全レコードをパース
    
    Args:
        stream: バイナリストリーム（標準入力など）
        
    Returns:
        パース結果のリスト
    """
    results = []
    record_num = 1
    
    while True:
        data = stream.read(RECORD_SIZE)
        if not data:
            break
        
        if len(data) != RECORD_SIZE:
            print(f"警告: レコード#{record_num}のサイズが不足しています ({len(data)}バイト)", file=sys.stderr)
            break
        
        try:
            parsed, rec_type = parse_record(data)
            results.append({
                "record_number": record_num,
                "record_type": rec_type,
                "data": parsed
            })
        except Exception as e:
            print(f"エラー: レコード#{record_num}のパースに失敗しました: {e}", file=sys.stderr)
            raise
        
        record_num += 1
    
    return results


def print_record(record_info, verbose=False):
    """
    パース結果を整形して出力
    """
    rec_num = record_info["record_number"]
    rec_type = record_info["record_type"]
    data = record_info["data"]
    
    print(f"\n{'='*60}")
    print(f"レコード #{rec_num} [{rec_type}]")
    print(f"{'='*60}")
    
    if rec_type == "HEADER":
        print(f"  ファイル名: {data.file_name.strip()}")
        print(f"  作成日時: {data.creation_date.strip()} {data.creation_time.strip()}")
        print(f"  総レコード数: {data.total_records}")
        print(f"  バージョン: {data.version.strip()}")
        
    elif rec_type == "DATA":
        print(f"  レコードID: {data.record_id}")
        print(f"  名前: {data.name.strip()}")
        print(f"  値: {data.value}")
        print(f"  ステータス: {'有効' if data.status == 1 else '無効'}")
        print(f"  タイムスタンプ: {data.timestamp.strip()}")
        if verbose:
            print(f"  説明: {data.description.strip()}")
        
    elif rec_type == "TRAILER":
        print(f"  データレコード数: {data.data_record_count}")
        print(f"  値の合計: {data.total_value_sum}")
        print(f"  チェックサム: {data.checksum}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="固定長レコード（120バイト）のバイナリデータを標準入力からパース"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="詳細情報を表示"
    )
    parser.add_argument(
        "-s", "--summary",
        action="store_true",
        help="サマリー情報のみ表示"
    )
    
    args = parser.parse_args()
    
    try:
        # 標準入力から読み込み
        results = parse_stream(sys.stdin.buffer)
        
        if args.summary:
            # サマリー情報のみ表示
            header_count = sum(1 for r in results if r["record_type"] == "HEADER")
            data_count = sum(1 for r in results if r["record_type"] == "DATA")
            trailer_count = sum(1 for r in results if r["record_type"] == "TRAILER")
            
            print(f"\n総レコード数: {len(results)}")
            print(f"  ヘッダレコード: {header_count}")
            print(f"  データレコード: {data_count}")
            print(f"  トレーラレコード: {trailer_count}")
        else:
            # 全レコードを表示
            for record in results:
                print_record(record, verbose=args.verbose)
        
        print()  # 最後に改行
        
    except Exception as e:
        print(f"エラー: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
