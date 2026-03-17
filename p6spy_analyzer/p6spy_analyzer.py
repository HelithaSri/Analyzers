import streamlit as st
import pandas as pd
import re
from datetime import datetime

st.set_page_config(page_title="p6spy Log Analyzer", layout="wide")
st.title("🛠 p6spy Log Analyzer Dashboard")
st.markdown("Upload your `today-queries.log` (or any p6spy log) → see slow queries + indexing recommendations")

# ====================== PARSER ======================
def parse_p6spy_log(log_text):
    queries = []
    current_query = ""
    current_took = 0
    current_ts = ""
    current_type = ""

    lines = log_text.splitlines()
    for line in lines:
        # New log entry
        if re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}', line):
            if current_query and current_took > 0:
                queries.append({
                    "timestamp": current_ts,
                    "took_ms": current_took,
                    "type": current_type,
                    "query": current_query.strip()
                })
            # Extract new header
            match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}) .*?took (\d+)ms .*? (\w+)', line)
            if match:
                current_ts = match.group(1)
                current_took = int(match.group(2))
                current_type = match.group(3)
                current_query = ""
        else:
            # Append query text (indented lines)
            if current_query is not None and line.strip():
                current_query += line + "\n"

    # Last query
    if current_query and current_took > 0:
        queries.append({
            "timestamp": current_ts,
            "took_ms": current_took,
            "type": current_type,
            "query": current_query.strip()
        })

    df = pd.DataFrame(queries)
    return df

# ====================== UPLOAD ======================
uploaded_file = st.file_uploader("Upload your p6spy log file", type=["log", "txt"])
if uploaded_file:
    log_text = uploaded_file.read().decode("utf-8")
    df = parse_p6spy_log(log_text)

    # Only keep real executing statements
    df = df[df['took_ms'] > 0].copy()
    df['query_short'] = df['query'].str[:150] + "..."

    st.success(f"✅ Parsed {len(df)} queries")

    # ====================== DASHBOARD TABS ======================
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "⏱️ Slowest Queries", "🔍 Indexing Recommendations", "📈 Charts"])

    with tab1:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Queries", len(df))
        col2.metric("Total Time (ms)", df['took_ms'].sum())
        col3.metric("Avg Time (ms)", round(df['took_ms'].mean(), 2))
        col4.metric("Slowest Query", f"{df['took_ms'].max()} ms")

    with tab2:
        st.subheader("Top 15 Slowest Queries")
        top_slow = df.nlargest(15, 'took_ms')[['timestamp', 'took_ms', 'query_short']]
        st.dataframe(top_slow, use_container_width=True)

        st.download_button("Download full slow queries CSV", df.to_csv(index=False), "slow_queries.csv")

    with tab3:
        st.subheader("🚨 Queries that probably need indexing")
        # Focus on SELECT statements that are slow
        selects = df[df['query'].str.contains('^select', case=False, regex=True)].copy()
        slow_selects = selects[selects['took_ms'] > 100].sort_values('took_ms', ascending=False)

        st.write(f"**{len(slow_selects)} slow SELECT queries** (took > 100 ms)")
        st.dataframe(slow_selects[['took_ms', 'query_short']], use_container_width=True)

        st.markdown("""
        **Quick indexing advice (copy-paste into MySQL):**
        - `WHERE code = ?` → `ALTER TABLE biller ADD INDEX idx_code (code);`
        - `WHERE category_id = ? AND status = ?` → `ALTER TABLE biller ADD INDEX idx_cat_status (category_id, status);`
        - `WHERE status = 'ACTIVE'` → `ALTER TABLE biller_category ADD INDEX idx_status (status);`
        - Any `WHERE nic = ?` or `login_name = ?` → add index on that column
        """)

    with tab4:
        st.subheader("Execution Time Distribution")
        fig = pd.DataFrame({
            'Time Range': ['0-100ms', '100-500ms', '500-1000ms', '>1000ms'],
            'Count': [
                len(df[df['took_ms'] <= 100]),
                len(df[(df['took_ms'] > 100) & (df['took_ms'] <= 500)]),
                len(df[(df['took_ms'] > 500) & (df['took_ms'] <= 1000)]),
                len(df[df['took_ms'] > 1000])
            ]
        })
        st.bar_chart(fig.set_index('Time Range'))

    # Optional: raw data
    with st.expander("See all parsed queries"):
        st.dataframe(df[['timestamp', 'took_ms', 'query_short']])

else:
    st.info("Upload your log file to start analyzing")