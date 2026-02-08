#!/usr/bin/env python3
"""
structモジュールを使用してフォーマット文字列のデータ長を計算するツール
"""

import struct
import argparse
import sys


def calculate_format_size(format_string):
    """
    フォーマット文字列のサイズを計算する
    
    Args:
        format_string: struct形式のフォーマット文字列
    
    Returns:
        計算されたバイト数
    """
    try:
        size = struct.calcsize(format_string)
        return size
    except struct.error as e:
        raise ValueError(f"無効なフォーマット文字列: {e}")


def print_format_details(format_string):
    """
    フォーマット文字列の詳細情報を出力する
    """
    size = calculate_format_size(format_string)
    
    # バイトオーダーとサイズの情報
    byte_order_map = {
        '@': 'ネイティブ (native)',
        '=': 'ネイティブ標準 (native standard)',
        '<': 'リトルエンディアン (little-endian)',
        '>': 'ビッグエンディアン (big-endian)',
        '!': 'ネットワーク (big-endian)',
    }
    
    byte_order = format_string[0] if format_string and format_string[0] in byte_order_map else '@'
    byte_order_name = byte_order_map.get(byte_order, 'ネイティブ')
    
    print(f"フォーマット文字列: {format_string}")
    print(f"データ長: {size} バイト")
    print(f"バイトオーダー: {byte_order_name}")
    
    # フォーマット文字の説明
    format_chars = {
        'x': 'パディングバイト',
        'c': 'char (1バイト)',
        'b': 'signed char (1バイト)',
        'B': 'unsigned char (1バイト)',
        '?': 'bool (1バイト)',
        'h': 'short (2バイト)',
        'H': 'unsigned short (2バイト)',
        'i': 'int (4バイト)',
        'I': 'unsigned int (4バイト)',
        'l': 'long (4バイト)',
        'L': 'unsigned long (4バイト)',
        'q': 'long long (8バイト)',
        'Q': 'unsigned long long (8バイト)',
        'f': 'float (4バイト)',
        'd': 'double (8バイト)',
        's': 'char[]',
        'p': 'char[] (Pascal文字列)',
        'P': 'void* (ポインタ)',
    }
    
    print("\nフォーマット構成:")
    # バイトオーダー文字を除外
    format_body = format_string[1:] if format_string and format_string[0] in byte_order_map else format_string
    
    i = 0
    while i < len(format_body):
        # 繰り返し回数の解析
        count = ''
        while i < len(format_body) and format_body[i].isdigit():
            count += format_body[i]
            i += 1
        
        if i < len(format_body):
            char = format_body[i]
            repeat = int(count) if count else 1
            desc = format_chars.get(char, '不明')
            print(f"  {repeat}x {char} - {desc}")
            i += 1


def main():
    parser = argparse.ArgumentParser(
        description='structモジュールのフォーマット文字列を評価してデータ長を出力します',
        epilog='''
例:
  %(prog)s "i"           # int型 (4バイト)
  %(prog)s "2i"          # int型 x 2 (8バイト)
  %(prog)s "ihb"         # int + short + char (7バイト)
  %(prog)s "<2H"         # リトルエンディアンでunsigned short x 2
  %(prog)s "!iHH"        # ネットワーク順序でint + short x 2
  %(prog)s "10s"         # 10バイトの文字列
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'format',
        help='struct形式のフォーマット文字列 (例: "i", "2H", "<ifq")'
    )
    
    parser.add_argument(
        '-s', '--simple',
        action='store_true',
        help='サイズのみを出力（詳細情報を省略）'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='詳細情報を表示'
    )
    
    args = parser.parse_args()
    
    try:
        if args.simple:
            size = calculate_format_size(args.format)
            print(size)
        else:
            print_format_details(args.format)
            
            if args.verbose:
                # 詳細モードではパック/アンパックの例も表示
                print("\n使用例:")
                print(f"  data = struct.pack('{args.format}', ...)")
                print(f"  values = struct.unpack('{args.format}', data)")
        
        return 0
    
    except ValueError as e:
        print(f"エラー: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"予期しないエラー: {e}", file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
