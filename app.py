import streamlit as st
import plotly.express as px
from src.decoder import parse_ea3, convert_df_to_csv

# ページ設定
st.set_page_config(page_title="EA3 Decoder", layout="wide")

st.title("EA3 File Decoder")
st.markdown("計測器の生データ(.ea3)をアップロードして、波形確認とCSV変換を行います")

# サイドバーにファイルアップロード
with st.sidebar:
    uploaded_file = st.file_uploader("ファイルをここにドラッグ&ドロップ", type=["ea3"])

if uploaded_file is not None:
    # ファイル読み込み
    file_bytes = uploaded_file.getvalue()
    
    # 解析実行
    with st.spinner('解析中...'):
        df, meta = parse_ea3(file_bytes)
    
    if df is not None:
        # --- メタデータ表示 ---
        st.subheader("ファイル情報")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("データ点数", f"{meta['valid_points']} 点")
        col2.metric("サンプリング", f"{meta['sampling_rate']} Hz")
        col3.metric("CH数", f"{meta['num_channels']} ch")
        col4.metric("スケーリング", f"1/{meta['scale_factor']}")
        
        # if meta['title']:
            # st.info(f"📁 タイトル: {meta['title']}")
        st.info(f"ファイル解析完了")
        
        if meta['comment']:
            st.caption(f"📝 コメント: {meta['comment']}")

        # --- グラフ描画 (Plotly) ---
        st.subheader("波形プレビュー")
        
        # 散布図でリサージュ波形を描画
        fig = px.scatter(
            df, 
            x="データＸ", 
            y="データＹ", 
            title="XYリサージュ波形",
            width=600,
            height=600
        )
        # 点をつなぐ線も追加したい場合は px.line を使うか update_traces で調整
        fig.update_traces(mode='markers', marker=dict(size=4))
        st.plotly_chart(fig, use_container_width=True)

        # --- データ表示 & ダウンロード ---
        st.subheader("データ変換")
        
        # 画面上で表を確認
        with st.expander("データテーブルを表示"):
            st.dataframe(df)

        # CSV生成
        # 辞書「meta」をまるごと渡すように変更
        csv_str = convert_df_to_csv(df, meta)
        
        # ダウンロードボタン
        st.download_button(
            label="CSVをダウンロード (Shift-JIS)",
            data=csv_str.encode('shift_jis'), # ここでエンコード
            file_name=f"{uploaded_file.name.split('.')[0]}.csv",
            mime='text/csv',
        )
        
    else:
        st.error(meta["error"])
else:
    st.info("👈 左のサイドバーから .ea3 ファイルをアップロードしてください。")