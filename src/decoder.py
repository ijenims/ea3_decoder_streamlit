import struct
import pandas as pd
import io

def parse_ea3(file_bytes):
    """
    ea3ファイルのバイナリデータを受け取り、
    (DataFrame, メタ情報dict) のタプルを返す
    """
    DATA_START_OFFSET = 256
    SCALE_FACTOR = 3276.8
    
    # バイト列をファイルライクオブジェクトとして扱う
    f = io.BytesIO(file_bytes)
    
    # 1. ヘッダー解析
    header_bytes = f.read(256)
    # オフセット 0x08 (8バイト目)
    num_points_raw = struct.unpack_from('<I', header_bytes, 8)[0]
    num_points = num_points_raw - 1  # 補正
    
    # 2. データ読み込み
    f.seek(DATA_START_OFFSET)
    read_size = num_points * 4
    binary_data = f.read(read_size)
    
    fmt = '<' + 'h' * (num_points * 2)
    try:
        values = struct.unpack(fmt, binary_data)
    except struct.error:
        return None, {"error": "データの読み込みに失敗しました。ファイル形式が正しいか確認してください。"}

    # 3. スケーリング & DataFrame化
    raw_x = values[0::2]
    raw_y = values[1::2]
    
    final_x = [x / SCALE_FACTOR for x in raw_x]
    final_y = [y / SCALE_FACTOR for y in raw_y]
    
    df = pd.DataFrame({
        'データＹ': final_y,
        'データＸ': final_x
    })
    
    metadata = {
        "raw_points": num_points_raw,
        "valid_points": num_points,
        "scale_factor": SCALE_FACTOR
    }
    
    return df, metadata

def convert_df_to_csv(df, num_points):
    """
    DataFrameをACT001形式のCSVテキストに変換する
    """
    # メモリ上のテキストバッファ
    output = io.StringIO()
    
    # ヘッダー書き込み
    output.write("DV,\n")
    output.write(f"データ点数,{num_points}\n")
    
    # データ本体書き込み
    df.to_csv(output, index=False, float_format='%.3f')
    
    # 文字列として返す（Shift-JISエンコードはダウンロードボタン側で行う）
    return output.getvalue()