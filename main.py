import streamlit as st
import pandas as pd
import numpy as np

st.markdown("""
<style>
    .reportview-container .main .block-container{
        max-width: 1600px;
        padding-top: 2rem;
        padding-right: 2rem;
        padding-left: 2rem;
        padding-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

def evaluate_performance(row):
    try:
        if (0.006 <= row.iloc[11] <= 0.02 and
            0.05 <= row.iloc[15] <= 0.25 and
            0.04 <= row.iloc[16] <= 0.20 and
            0.05 <= row.iloc[19] <= 0.20):
            return "高"
        elif (row.iloc[11] <= 0.003 and
              row.iloc[15] >= 0.41 and
              0.001 <= row.iloc[16] <= 0.025 and
              0.001 <= row.iloc[19] <= 0.03):
            return "低"
        return "その他"
    except:
        return "エラー"

def format_percentage(value):
    return f"{value:.1f}%" if pd.notnull(value) else "0.0%"

def format_float(value):
    return f"{value:.1f}" if pd.notnull(value) else "0.0"

def format_integer(value):
    return f"{int(value)}" if pd.notnull(value) else "0"

def format_integer_percentage(value):
    return f"{int(value)}%" if pd.notnull(value) else "0%"

def format_match_type(value):
    if pd.isnull(value):
        return ""
    match_types = {
        "EXACT": "完全一致",
        "PHRASE": "フレーズ一致",
        "BROAD": "部分一致"
    }
    return match_types.get(value.upper(), value)

def main():
    st.title("Amazon広告キーワード自動判定ツール")
    st.text("powered by Spesia")

    if 'df' not in st.session_state:
        st.session_state.df = None

    uploaded_file = st.file_uploader("Amazon広告レポートを選択してください(※Excelファイルのみ)", type=["xlsx", "xls"])

    if uploaded_file is not None:
        st.session_state.df = pd.read_excel(uploaded_file)
        st.success("ファイルが正常にアップロードされました。")

    if st.button("データをクリアする"):
        st.session_state.df = None
        st.success("データがクリアされました。")

    if st.session_state.df is not None:
        unique_values = st.session_state.df.iloc[1:, 5].unique()

        st.write("広告グループ名:")
        col1, col2 = st.columns(2)
        selected_values = []

        with col1:
            for value in unique_values[:len(unique_values)//2]:
                if st.checkbox(str(value), key=f"checkbox_{value}"):
                    selected_values.append(value)

        with col2:
            for value in unique_values[len(unique_values)//2:]:
                if st.checkbox(str(value), key=f"checkbox_{value}"):
                    selected_values.append(value)

        if st.button("分析を実行"):
            if selected_values:
                filtered_df = st.session_state.df[st.session_state.df.iloc[:, 5].isin(selected_values)]
                filtered_df['Performance'] = filtered_df.apply(evaluate_performance, axis=1)

                high_performance = filtered_df[filtered_df['Performance'] == "高"].iloc[:, 8].tolist()
                low_performance = filtered_df[filtered_df['Performance'] == "低"].iloc[:, 8].tolist()

                st.write("パフォーマンスが高いKW")
                st.write(", ".join(map(str, high_performance)) if high_performance else "なし")

                st.write("パフォーマンスが低いKW")
                st.write(", ".join(map(str, low_performance)) if low_performance else "なし")

                st.write("データ評価")

                # データ評価テーブルの作成
                columns = [8, 6, 7, 9, 10, 11, 13, 12, 17, 14, 15, 16, 19]
                column_names = [
                    "カスタマーの検索キーワード", "ターゲティング", "タイプ", "インプレッション", 
                    "クリック数", "クリック率(CTR)", "広告費", "平均クリック単価", "注文数", 
                    "売上", "ACOS", "ROAS", "コンバージョン率(CVR)"
                ]
                
                evaluation_df = filtered_df.iloc[:, columns].copy()
                evaluation_df.columns = column_names
                evaluation_df = evaluation_df.sort_values("インプレッション", ascending=False)

                # データフォーマットの適用
                evaluation_df["クリック率(CTR)"] = evaluation_df["クリック率(CTR)"].apply(format_percentage)
                evaluation_df["ACOS"] = evaluation_df["ACOS"].apply(lambda x: format_percentage(x*100) if pd.notnull(x) else "0.0%")
                evaluation_df["コンバージョン率(CVR)"] = evaluation_df["コンバージョン率(CVR)"].apply(format_percentage)
                
                evaluation_df["広告費"] = evaluation_df["広告費"].apply(format_float)
                evaluation_df["平均クリック単価"] = evaluation_df["平均クリック単価"].apply(format_float)
                evaluation_df["売上"] = evaluation_df["売上"].apply(format_float)
                
                evaluation_df["ROAS"] = evaluation_df["ROAS"].apply(lambda x: format_integer_percentage(x * 100) if pd.notnull(x) else "0%")
                
                evaluation_df["インプレッション"] = evaluation_df["インプレッション"].apply(format_integer)
                evaluation_df["クリック数"] = evaluation_df["クリック数"].apply(format_integer)
                evaluation_df["注文数"] = evaluation_df["注文数"].apply(format_integer)
                evaluation_df["タイプ"] = evaluation_df["タイプ"].apply(format_match_type)

                st.dataframe(evaluation_df.reset_index(drop=True), height=800)
            else:
                st.warning("少なくとも1つの広告グループを選択してください。")

if __name__ == "__main__":
    main()
