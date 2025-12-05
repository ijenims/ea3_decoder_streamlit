import struct
import pandas as pd
import io

def parse_ea3(file_bytes):
    # 定数定義
    DATA_START_OFFSET = 256
    SCALE_FACTOR = 3276.8
    
    f = io.BytesIO(file_bytes)
    
    # --- 1. ヘッダー解析 ---
    header_bytes = f.read(256)
    num_points_raw = struct.unpack_from('<I', header_bytes, 8)[0]
    sampling_rate = struct.unpack_from('<H', header_bytes, 16)[0]
    num_channels = struct.unpack_from('<B', header_bytes, 18)[0]
    
    # データ点数の補正 (-1点分は区切り等の可能性が高いので除外)
    valid_points = num_points_raw - 1
    
    # --- 2. データ読み込み ---
    f.seek(DATA_START_OFFSET)
    
    if num_channels != 1:
        return None, {"error": f"未対応のチャンネル数: {num_channels}ch"}

    read_size = valid_points * 4
    binary_data = f.read(read_size)
    
    fmt = '<' + 'h' * (valid_points * 2)
    try:
        values = struct.unpack(fmt, binary_data)
    except struct.error:
        return None, {"error": "データ読込失敗"}

    # --- 3. データ変換 ---
    raw_x = values[0::2]
    raw_y = values[1::2]
    final_x = [x / SCALE_FACTOR for x in raw_x]
    final_y = [y / SCALE_FACTOR for y in raw_y]
    
    df = pd.DataFrame({'データＹ': final_y, 'データＸ': final_x})

    # --- 4. フッター解析 (バグ修正版) ---
    title_str = ""
    comment_str = ""
    
    try:
        # ★ここが修正ポイント！
        # 波形データの直後に "0x12345678" (区切り文字) がある場合はスキップする
        
        # 現在位置を保存
        current_pos = f.tell()
        # 4バイト試し読み
        check_bytes = f.read(4)
        
        if len(check_bytes) == 4:
            val = struct.unpack('<I', check_bytes)[0]
            
            # もし区切り文字(0x12345678) だったら、読み捨てて次へ進む
            # ※ 305419896 = 0x12345678
            if val == 305419896:
                pass # スキップ成功
            else:
                # 区切り文字じゃなかったら、読み込み位置を戻す（それが文字数かもしれない）
                f.seek(current_pos)
        
        # --- タイトル読み込み ---
        len_bytes = f.read(4)
        if len(len_bytes) == 4:
            title_len = struct.unpack('<I', len_bytes)[0]
            
            # 安全装置: 文字数が異常に大きい(1000文字以上)場合はバグとみなして空にする
            if 0 < title_len < 1000:
                title_str = f.read(title_len).decode('shift_jis', errors='replace')
            elif title_len == 0:
                pass
            else:
                title_str = "(文字数異常のためスキップ)"
                # リカバリできそうならここでシークしてもいいが、一旦スキップ
        
        # --- コメント読み込み ---
        len_bytes = f.read(4)
        if len(len_bytes) == 4:
            comment_len = struct.unpack('<I', len_bytes)[0]
            
            if 0 < comment_len < 5000: # コメントは少し長めを許容
                comment_str = f.read(comment_len).decode('shift_jis', errors='replace')
        
    except Exception as e:
        title_str = f"(解析エラー: {e})"

    # メタデータ作成
    metadata = {
        "raw_points": num_points_raw,
        "valid_points": valid_points,
        "sampling_rate": sampling_rate,
        "num_channels": num_channels,
        "title": title_str,
        "comment": comment_str,
        "scale_factor": SCALE_FACTOR
    }
    
    return df, metadata

def convert_df_to_csv(df, meta):
    output = io.StringIO()
    output.write("DV,\n")
    # タイトルなどもCSVに入れたければここで追加可能
    # output.write(f"タイトル,{meta['title']}\n")
    output.write(f"データ点数,{meta['valid_points']}\n")
    df.to_csv(output, index=False, float_format='%.3f')
    return output.getvalue()