import streamlit as st
import pandas as pd
import plotly.express as px

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="Dashboard Interaktif Tujuan, Sasaran & Program K3LH 2026",
    page_icon="🛡️",
    layout="wide"
)

# Styling Tema Gelap (Dark Mode CSS persis seperti tampilan HTML)
st.markdown("""
    <style>
    .main { background-color: #0b0f19; color: #f8fafc; }
    .stApp { background-color: #0b0f19; }
    .kpi-card {
        background-color: #111827;
        border: 1px solid #1f2937;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Header Utama
st.markdown("""
    <div style="background-color: #111827; border: 1px solid #1f2937; padding: 20px; border-radius: 16px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        <div style="display: flex; align-items: center; gap: 12px;">
            <div style="background-color: rgba(20, 184, 166, 0.1); border: 1px solid rgba(20, 184, 166, 0.3); padding: 10px; border-radius: 12px; color: #2dd4bf;">
                🛡️
            </div>
            <div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <h1 style="color: white; margin: 0; font-size: 16px; font-weight: bold;">PT. TRISATRIA PERSADA BORNEO</h1>
                    <span style="background-color: rgba(20, 184, 166, 0.2); color: #2dd4bf; font-size: 10px; font-weight: bold; padding: 2px 8px; border-radius: 9999px; border: 1px solid rgba(20, 184, 166, 0.3);">2026</span>
                </div>
                <p style="color: #94a3b8; margin: 2px 0 0 0; font-size: 12px;">Dashboard Interaktif Tujuan, Sasaran & Program K3LH Periode 2026</p>
            </div>
        </div>
        <div style="background-color: #0f172a; border: 1px solid #1e293b; padding: 8px 16px; border-radius: 12px; font-size: 12px; color: #2dd4bf; font-weight: bold;">
            📅 Tahun Evaluasi: 2026
        </div>
    </div>
""", unsafe_allow_html=True)

# 🔗 LINK GOOGLE SHEETS ANDA
GOOGLE_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1MxWz6wuBynEdhRlrGlH-z3-hCjCTk8DA/edit?gid=880433697#gid=880433697"

# Konversi link edit otomatis ke format export csv
if "/edit" in GOOGLE_SHEET_CSV_URL:
    base_url = GOOGLE_SHEET_CSV_URL.split("/edit")[0]
    gid = "880433697"
    if "gid=" in GOOGLE_SHEET_CSV_URL:
        gid = GOOGLE_SHEET_CSV_URL.split("gid=")[1].split("#")[0]
    GOOGLE_SHEET_CSV_URL = f"{base_url}/export?format=csv&gid={gid}"

@st.cache_data(ttl=60)
def load_data(url):
    return pd.read_csv(url, header=None, dtype=str)

def safe_float(val):
    if pd.isna(val) or val is None:
        return 0.0
    val_str = str(val).strip()
    if val_str in ['', 'nan', 'NaN', '#DIV/0!', '#N/A', '#VALUE!', '#REF!', '-']:
        return 0.0
    try:
        return float(val_str)
    except ValueError:
        digits = ''.join(filter(lambda c: c.isdigit() or c == '.', val_str))
        try:
            return float(digits) if digits != '' else 0.0
        except ValueError:
            return 0.0

months_names = ['JAN', 'FEB', 'MAR', 'APR', 'MEI', 'JUN', 'JUL', 'AGU', 'SEP', 'OKT', 'NOV', 'DES']

try:
    df_raw = load_data(GOOGLE_SHEET_CSV_URL)
    
    programs_data = []
    monthly_plan_sum = [0.0] * 12
    monthly_act_sum = [0.0] * 12
    count_terpenuhi = 0
    count_sebagian = 0
    count_belum = 0
    total_budget_sum = 0.0
    total_sum_pct = 0.0

    # Parsing 26 Program dari baris ke-5 s.d ke-30 (index 4 s.d 29)
    for i in range(4, 30):
        if i < len(df_raw):
            r = df_raw.iloc[i]
            if pd.notna(r.iloc[1]):
                no = safe_float(r.iloc[0]) if pd.notna(r.iloc[0]) else (i - 3)
                prog = str(r.iloc[1])
                
                monthly_pairs = []
                tot_plan = 0.0
                tot_act = 0.0
                col_idx = 2
                for m in range(12):
                    p_val = safe_float(r.iloc[col_idx] if col_idx < len(r) else 0)
                    a_val = safe_float(r.iloc[col_idx+1] if (col_idx+1) < len(r) else 0)
                    monthly_pairs.append({'plan': p_val, 'act': a_val})
                    tot_plan += p_val
                    tot_act += a_val
                    monthly_plan_sum[m] += p_val
                    monthly_act_sum[m] += a_val
                    col_idx += 2
                
                pct = int(round((tot_act / tot_plan) * 100)) if tot_plan > 0 else 0
                total_sum_pct += pct

                if pct >= 100:
                    status = 'TERPENUHI'
                    count_terpenuhi += 1
                elif pct > 0:
                    status = 'SEBAGIAN'
                    count_sebagian += 1
                else:
                    status = 'BELUM'
                    count_belum += 1

                # Kolom AC (index 28) untuk Biaya dan Kolom AD (index 29) untuk PIC
                biaya = safe_float(r.iloc[28] if len(r) > 28 else 0)
                total_budget_sum += biaya
                pic = str(r.iloc[29]) if len(r) > 29 and pd.notna(r.iloc[29]) else '-'

                programs_data.append({
                    'no': int(no) if no > 0 else (i-3),
                    'prog': prog,
                    'monthly_pairs': monthly_pairs,
                    'tot_plan': int(tot_plan),
                    'tot_act': int(tot_act),
                    'pct': pct,
                    'status': status,
                    'biaya': biaya,
                    'pic': pic
                })

    total_prog = len(programs_data)
    avg_cap = int(round(total_sum_pct / total_prog)) if total_prog > 0 else 0
    trend_arr = [int(round((monthly_act_sum[idx] / monthly_plan_sum[idx]) * 100)) if monthly_plan_sum[idx] > 0 else 0 for idx in range(12)]

    # --- KPI SUMMARY CARDS ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
            <div class="kpi-card">
                <p style="font-size: 11px; font-weight: 600; color: #94a3b8; text-transform: uppercase; margin: 0;">Total Program Kerja</p>
                <div style="display: flex; align-items: baseline; gap: 8px; margin-top: 4px;">
                    <h3 style="font-size: 28px; font-weight: 800; color: white; margin: 0;">{total_prog}</h3>
                    <span style="font-size: 12px; color: #94a3b8;">Item Program</span>
                </div>
                <p style="font-size: 11px; color: #2dd4bf; margin: 8px 0 0 0; font-weight: 500;">👤 PIC: Leo & Nisa</p>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class="kpi-card">
                <p style="font-size: 11px; font-weight: 600; color: #94a3b8; text-transform: uppercase; margin: 0;">Rata-Rata Ketercapaian</p>
                <div style="display: flex; align-items: baseline; gap: 8px; margin-top: 4px;">
                    <h3 style="font-size: 28px; font-weight: 800; color: #2dd4bf; margin: 0;">{avg_cap}%</h3>
                    <span style="font-size: 12px; color: #94a3b8;">Akumulasi Tahunan</span>
                </div>
                <div style="background-color: #1e293b; height: 6px; border-radius: 9999px; margin-top: 12px; overflow: hidden;">
                    <div style="background-color: #14b8a6; width: {min(avg_cap, 100)}%; height: 100%;"></div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
            <div class="kpi-card">
                <p style="font-size: 11px; font-weight: 600; color: #94a3b8; text-transform: uppercase; margin: 0;">Program Terpenuhi (≥100%)</p>
                <div style="display: flex; align-items: baseline; gap: 8px; margin-top: 4px;">
                    <h3 style="font-size: 28px; font-weight: 800; color: #34d399; margin: 0;">{count_terpenuhi}</h3>
                    <span style="font-size: 12px; color: #94a3b8;">dari {total_prog} Program</span>
                </div>
                <p style="font-size: 11px; color: #94a3b8; margin: 8px 0 0 0;">{count_sebagian} Sebagian • {count_belum} Belum</p>
            </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
            <div class="kpi-card">
                <p style="font-size: 11px; font-weight: 600; color: #94a3b8; text-transform: uppercase; margin: 0;">Total Anggaran K3LH</p>
                <div style="margin-top: 6px;">
                    <h3 style="font-size: 20px; font-weight: 800; color: #38bdf8; margin: 0;">Rp {total_budget_sum:,.0f}</h3>
                </div>
                <p style="font-size: 11px; color: #94a3b8; margin: 8px 0 0 0;">Pengadaan & Support RKAB</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- CHARTS ROW ---
    c_chart1, c_chart2 = st.columns([2, 1])
    with c_chart1:
        st.markdown("### Perbandingan Target (Plan) vs Realisasi (Actual)")
        st.markdown("<p style='font-size:11px; color:#94a3b8; margin-top:-10px;'>Jumlah frekuensi kegiatan K3LH per bulan selama tahun 2026</p>", unsafe_allow_html=True)
        df_bar = pd.DataFrame({
            "Bulan": months_names * 2,
            "Jumlah": [int(x) for x in monthly_plan_sum] + [int(x) for x in monthly_act_sum],
            "Tipe": ["Target (Plan)"] * 12 + ["Realisasi (Actual)"] * 12
        })
        fig_bar = px.bar(df_bar, x="Bulan", y="Jumlah", color="Tipe", barmode="group",
                         color_discrete_map={"Target (Plan)": "#3b82f6", "Realisasi (Actual)": "#10b981"})
        fig_bar.update_layout(paper_bgcolor="#111827", plot_bgcolor="#111827", font_color="#f8fafc",
                              legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                              margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_bar, use_container_width=True)

    with c_chart2:
        st.markdown("### Distribusi Status Program")
        st.markdown("<p style='font-size:11px; color:#94a3b8; margin-top:-10px;'>Persentase tingkat ketercapaian 26 program K3LH</p>", unsafe_allow_html=True)
        fig_donut = px.pie(names=['Terpenuhi', 'Sebagian', 'Belum'], values=[count_terpenuhi, count_sebagian, count_belum],
                           hole=0.75, color_discrete_sequence=['#10b981', '#f59e0b', '#f43f5e'])
        fig_donut.update_layout(paper_bgcolor="#111827", plot_bgcolor="#111827", font_color="#f8fafc",
                                showlegend=False, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_donut, use_container_width=True)
        
        # Donut Legend Grid
        st.markdown(f"""
            <div style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); text-align: center; border-top: 1px solid #1f2937; padding-top: 10px; font-size: 12px;">
                <div>
                    <p style="font-weight: 800; color: #34d399; margin: 0; font-size: 14px;">{count_terpenuhi}</p>
                    <span style="font-size: 10px; color: #94a3b8;">Terpenuhi</span>
                </div>
                <div>
                    <p style="font-weight: 800; color: #fbbf24; margin: 0; font-size: 14px;">{count_sebagian}</p>
                    <span style="font-size: 10px; color: #94a3b8;">Sebagian</span>
                </div>
                <div>
                    <p style="font-weight: 800; color: #f43f5e; margin: 0; font-size: 14px;">{count_belum}</p>
                    <span style="font-size: 10px; color: #94a3b8;">Belum</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Line Chart Tren
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Tren Persentase Ketercapaian Bulanan (%)")
    st.markdown("<p style='font-size:11px; color:#94a3b8; margin-top:-10px;'>Formulasi: Total Realisasi (Actual) / Total Rencana (Plan) × 100%</p>", unsafe_allow_html=True)
    df_line = pd.DataFrame({"Bulan": months_names, "Persentase": trend_arr})
    fig_line = px.line(df_line, x="Bulan", y="Persentase", markers=True, color_discrete_sequence=['#10b981'])
    fig_line.update_layout(paper_bgcolor="#111827", plot_bgcolor="#111827", font_color="#f8fafc",
                           margin=dict(t=10, b=10, l=10, r=10))
    st.plotly_chart(fig_line, use_container_width=True)

    # --- TABEL 1: SUMMARY ---
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Rincian Program & Status Ketercapaian (Summary)")
    search_query = st.text_input("🔍 Cari program atau PIC (Summary):", "")
    
    filtered_data = [item for item in programs_data if search_query.lower() in item['prog'].lower() or search_query.lower() in item['pic'].lower()]
    
    summary_rows = []
    for item in filtered_data:
        summary_rows.append({
            "NO": item['no'],
            "PROGRAM KERJA K3LH": item['prog'],
            "TOTAL PLAN": item['tot_plan'],
            "TOTAL ACTUAL": item['tot_act'],
            "KETERCAPAIAN": f"{item['pct']}%",
            "RINCIAN BIAYA": f"Rp {item['biaya']:,.0f}" if item['biaya'] > 0 else "Rp 0",
            "PIC": item['pic']
        })
    st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)

    # --- TABEL 2: MATRIKS DETAIL ---
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Matrikulasi Program Kerja K3LH 2026 (Detail Matriks)")
    status_filter = st.selectbox("Filter Status Program:", ["Semua Status", "Terpenuhi (≥100%)", "Sebagian (1-99%)", "Belum Terpenuhi (0%)"])
    
    matrix_filtered = filtered_data
    if status_filter == "Terpenuhi (≥100%)":
        matrix_filtered = [i for i in matrix_filtered if i['status'] == 'TERPENUHI']
    elif status_filter == "Sebagian (1-99%)":
        matrix_filtered = [i for i in matrix_filtered if i['status'] == 'SEBAGIAN']
    elif status_filter == "Belum Terpenuhi (0%)":
        matrix_filtered = [i for i in matrix_filtered if i['status'] == 'BELUM']

    matrix_rows = []
    for item in matrix_filtered:
        row_dict = {"NO": item['no'], "PROGRAM KERJA K3LH": item['prog']}
        for idx, m_name in enumerate(months_names):
            p_val = item['monthly_pairs'][idx]['plan']
            a_val = item['monthly_pairs'][idx]['act']
            row_dict[f"{m_name}"] = f"{int(p_val) if p_val > 0 else '-'} / {int(a_val)}"
        row_dict["TOT PLAN"] = item['tot_plan']
        row_dict["TOT ACT"] = item['tot_act']
        row_dict["KETERCAPAIAN"] = f"{item['pct']}%"
        row_dict["RINCIAN BIAYA"] = f"Rp {item['biaya']:,.0f}" if item['biaya'] > 0 else "-"
        row_dict["PIC"] = item['pic']
        matrix_rows.append(row_dict)

    st.dataframe(pd.DataFrame(matrix_rows), use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Gagal memuat data dari Google Sheets. Detail error: {e}")
