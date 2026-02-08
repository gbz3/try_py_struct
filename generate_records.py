#!/usr/bin/env python3
"""
固定長レコードのサンプルバイナリデータを生成

ヘッダ、データ、トレーラレコードを含む120バイト固定長のバイナリデータを標準出力に出力します。
"""

import sys
from datetime import datetime
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


def create_header_record(file_name, total_records, version="1.0"):
    """ヘッダレコードを生成"""
    now = datetime.now()
    
    header_data = {
        "file_name": file_name,
        "creation_date": now.strftime("%Y%m%d"),
        "creation_time": now.strftime("%H%M%S"),
        "total_records": total_records,
        "version": version,
    }
    
    return HeaderRecord.build(header_data)


def create_data_record(record_id, name, value, status, description=""):
    """データレコードを生成"""
    now = datetime.now()
    
    data_record = {
        "record_id": record_id,
        "name": name,
        "value": value,
        "status": status,
        "timestamp": now.strftime("%Y%m%d%H%M%S"),
        "description": description,
    }
    
    return DataRecord.build(data_record)


def create_trailer_record(data_record_count, total_value_sum, checksum=0):
    """トレーラレコードを生成"""
    trailer_data = {
        "data_record_count": data_record_count,
        "total_value_sum": total_value_sum,
        "checksum": checksum,
    }
    
    return TrailerRecord.build(trailer_data)


def generate_sample_data(num_data_records=10):
    """
    サンプルの固定長レコードデータを標準出力に出力
    
    Args:
        num_data_records: 生成するデータレコード数
    """
    # 総レコード数 = ヘッダ(1) + データ(n) + トレーラ(1)
    total_records = 1 + num_data_records + 1
    
    # サンプルデータの準備
    sample_names = [
        "田中太郎", "佐藤花子", "鈴木一郎", "高橋次郎", "伊藤美咲",
        "渡辺健太", "山本由美", "中村陽子", "小林大輔", "加藤愛",
        "吉田智子", "山田孝之", "佐々木真", "松本優子", "井上誠"
    ]
    
    sample_descriptions = [
        "通常処理",
        "特別処理",
        "優先処理",
        "定期処理",
        "緊急処理",
    ]
    
    data_records = []
    total_value_sum = 0
    
    # データレコードを生成
    for i in range(num_data_records):
        record_id = i + 1
        name = sample_names[i % len(sample_names)]
        value = (i + 1) * 1000
        status = 1 if i % 3 != 0 else 0  # 一部を無効にする
        description = sample_descriptions[i % len(sample_descriptions)]
        
        record = create_data_record(record_id, name, value, status, description)
        data_records.append(record)
        total_value_sum += value
    
    # チェックサムを簡易計算（全レコードIDの合計）
    checksum = sum(range(1, num_data_records + 1))
    
    # 標準出力（バイナリモード）に書き込み
    output = sys.stdout.buffer
    
    # ヘッダレコード
    header = create_header_record("sample_data.bin", total_records)
    output.write(header)
    
    # データレコード
    for record in data_records:
        output.write(record)
    
    # トレーラレコード
    trailer = create_trailer_record(num_data_records, total_value_sum, checksum)
    output.write(trailer)
    
    output.flush()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="固定長レコード（120バイト）のサンプルバイナリデータを標準出力に生成"
    )
    parser.add_argument(
        "-n", "--num-records",
        type=int,
        default=10,
        help="生成するデータレコード数 (デフォルト: 10)"
    )
    
    args = parser.parse_args()
    
    # データレコード数のバリデーション
    if args.num_records < 1:
        print("エラー: データレコード数は1以上を指定してください。", file=sys.stderr)
        sys.exit(1)
    
    if args.num_records > 1000:
        print("警告: 大量のレコードを生成します...", file=sys.stderr)
    
    try:
        # サンプルデータを生成
        generate_sample_data(args.num_records)
        
    except Exception as e:
        print(f"エラー: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
