import os
import pandas as pd
import ollama
import streamlit as st
import plotly.express as px
from datetime import datetime

# ====================== 配置 ======================
ROOT_FOLDER = r"C:\Users\93478\Desktop\水质监测"
PREPROCESSED_FOLDER = os.path.join(ROOT_FOLDER, "preprocessing", "预处理后")
OLLAMA_MODEL = "qwen2.5:14b"

AVAILABLE_YEARS = ["2021年", "2022年", "2023年", "2024年", "2025年"]

REGIONS = ["全国", "浙江", "江苏", "上海", "安徽", "福建", "广东", "山东", "湖北", "湖南", "四川", "河南"]

ALL_INDICATORS = [
    "水温(℃)", "pH(无量纲)", "溶解氧(mg/L)", "电导率(μS/cm)", "浊度(NTU)",
    "高锰酸盐指数(mg/L)", "氨氮(mg/L)", "总磷(mg/L)", "总氮(mg/L)",
    "叶绿素α(mg/L)", "藻密度(cells/L)", "水质类别"
]

# ====================== 页面配置 ======================
st.set_page_config(
    page_title="水质监测智能分析系统",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== 自定义样式 ======================
st.markdown("""
<style>
    .main-header {font-size: 2.5rem; color: #1E88E5; text-align: center; margin-bottom: 0.5rem;}
    .sub-header {font-size: 1.3rem; color: #424242; text-align: center; margin-bottom: 2rem;}
    .stButton>button {width: 100%; border-radius: 10px; height: 3.2em; font-size: 1.1em; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-header'>🌊 水质监测智能分析系统</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>基于 Qwen2.5-14B 的多维度水质数据智能分析平台</p>", unsafe_allow_html=True)

# ====================== 数据加载 ======================
@st.cache_data
def load_and_clean_data(year_name):
    file_path = os.path.join(PREPROCESSED_FOLDER, f"{year_name}_预处理后.csv")
    if not os.path.exists(file_path):
        st.error(f"❌ 文件不存在: {file_path}")
        return None
    try:
        df = pd.read_csv(file_path, encoding='utf-8-sig', low_memory=False)
        
        numeric_cols = [col for col in ALL_INDICATORS if col != "水质类别"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].astype(str).str.extract(r'([-+]?\d*\.?\d+)')[0], errors='coerce')
        
        if "监测时间" in df.columns:
            df["监测时间"] = pd.to_datetime(df["监测时间"], errors='coerce')
        return df
    except Exception as e:
        st.error(f"读取 {year_name} 数据失败: {e}")
        return None

# ====================== 侧边栏 ======================
with st.sidebar:
    st.header("📋 全局参数")
    selected_years = st.multiselect("选择年份（支持多选）", AVAILABLE_YEARS, default=["2025年"])

# ====================== 主界面 Tabs ======================
tab1, tab2 = st.tabs(["🤖 智能分析", "📊 数据可视化"])

# ====================== Tab 1: 智能分析 ======================
with tab1:
    st.subheader("智能分析参数")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        selected_region = st.selectbox("📍 分析区域", REGIONS, index=0)
        selected_column = st.selectbox("📊 重点关注指标", ["综合分析"] + ALL_INDICATORS, index=0)
        custom_question = st.text_area("💬 自定义分析问题（可选）", 
                                      placeholder="例如：浙江地区氨氮超标的原因及治理建议...", 
                                      height=120)

        if st.button("🚀 开始智能分析", type="primary", use_container_width=True):
            if not selected_years:
                st.error("❌ 请至少选择一个年份！")
            else:
                with st.spinner("🔄 正在加载数据并调用大模型分析..."):
                    data_dict = {}
                    total_rows = 0
                    for year in selected_years:
                        df = load_and_clean_data(year)
                        if df is not None:
                            data_dict[year] = df
                            total_rows += len(df)
                    
                    if not data_dict:
                        st.error("❌ 数据加载失败，请检查路径")
                        st.stop()
                    
                    years_str = "、".join(selected_years)
                    prompt = f"""你是一位资深水质监测数据专家。
请对以下年份的水质数据进行专业分析：{years_str}。

总记录数：{total_rows:,}
涉及年份：{years_str}
"""
                    if selected_region and selected_region != "全国":
                        prompt += f"指定分析地区：{selected_region}\n"
                    if selected_column and selected_column != "综合分析":
                        prompt += f"重点关注指标：{selected_column}\n"
                    if custom_question.strip():
                        prompt += f"用户具体问题：{custom_question}\n"

                    prompt += "\n请从以下角度深入分析：\n1. 总体水质状况及年际变化趋势\n2. 重点指标达标情况及问题分析\n3. 区域特征（如果指定地区）\n4. 提出1-2条具体可操作的建议"

                    try:
                        response = ollama.chat(model=OLLAMA_MODEL, messages=[{'role': 'user', 'content': prompt}])
                        answer = response['message']['content']
                        
                        st.success("✅ 分析完成！")
                        st.markdown("### 🤖 Qwen2.5 分析报告")
                        st.markdown(answer)
                        
                        # 保存报告
                        report_dir = os.path.join(ROOT_FOLDER, "reports")
                        os.makedirs(report_dir, exist_ok=True)
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
                        report_path = os.path.join(report_dir, f"水质分析报告_{timestamp}.txt")
                        
                        with open(report_path, "w", encoding="utf-8") as f:
                            f.write(f"分析时间：{datetime.now()}\n")
                            f.write(f"模型：{OLLAMA_MODEL}\n")
                            f.write(f"年份：{years_str}\n")
                            f.write(f"地区：{selected_region}\n")
                            f.write(f"指标：{selected_column}\n\n")
                            f.write(answer)
                        
                        st.info(f"📄 报告已保存至：\n`{report_path}`")
                    except Exception as e:
                        st.error(f"❌ Ollama 调用失败: {e}")

    with col2:
        st.markdown("### 当前数据路径")
        st.code(PREPROCESSED_FOLDER)

# ====================== Tab 2: 数据可视化 ======================
with tab2:
    st.header("📊 双指标关系可视化（X轴 vs Y轴）")
    
    if not selected_years:
        st.warning("请在左侧选择至少一个年份")
    else:
        # 加载数据
        data_list = []
        for year in selected_years:
            df = load_and_clean_data(year)
            if df is not None:
                df['年份'] = year
                data_list.append(df)
        
        if data_list:
            df_all = pd.concat(data_list, ignore_index=True)
            
            # 地区选择
            st.subheader("🔍 选择地区 / 流域 / 断面")
            region_cols = [col for col in df_all.columns if any(k in col.lower() for k in ["流域", "断面", "地区", "站点", "位置", "水系"])]
            region_options = ["全部地区"]
            
            if region_cols:
                for col in region_cols:
                    unique_vals = sorted(df_all[col].dropna().astype(str).unique())
                    region_options.extend([v for v in unique_vals if str(v).strip() != ""])
            region_options = list(dict.fromkeys(region_options))
            
            selected_region_viz = st.selectbox("请选择地区", region_options, index=0)
            
            if selected_region_viz != "全部地区" and region_cols:
                mask = False
                for col in region_cols:
                    mask = mask | df_all[col].astype(str).str.contains(selected_region_viz, na=False, case=False)
                df_all = df_all[mask]
                st.success(f"已筛选：**{selected_region_viz}**  （共 {len(df_all):,} 条记录）")
            
            # X轴 和 Y轴 指标选择
            st.subheader("选择 X 轴 和 Y 轴 指标")
            col_x, col_y = st.columns(2)
            with col_x:
                x_axis = st.selectbox("X 轴 指标", ALL_INDICATORS, index=0, key="x_axis")
            with col_y:
                y_options = [col for col in ALL_INDICATORS if col != x_axis]
                y_axis = st.selectbox("Y 轴 指标", y_options, index=0, key="y_axis")
            
            chart_type = st.radio("图表类型", ["散点图 (推荐)", "折线图"], horizontal=True)
            
            if not df_all.empty:
                if chart_type == "散点图 (推荐)":
                    fig = px.scatter(df_all, x=x_axis, y=y_axis,
                                    color="年份" if len(selected_years) > 1 else None,
                                    title=f"{x_axis} vs {y_axis} 关系图",
                                    hover_data=["监测时间"] if "监测时间" in df_all.columns else None,
                                    height=650)
                else:
                    fig = px.line(df_all.sort_values("监测时间" if "监测时间" in df_all.columns else x_axis),
                                 x=x_axis, y=y_axis,
                                 color="年份" if len(selected_years) > 1 else None,
                                 title=f"{x_axis} vs {y_axis} 趋势图",
                                 markers=True, height=650)
                
                st.plotly_chart(fig, use_container_width=True)
                
                # 相关性分析
                if pd.api.types.is_numeric_dtype(df_all[x_axis]) and pd.api.types.is_numeric_dtype(df_all[y_axis]):
                    corr = df_all[[x_axis, y_axis]].corr().iloc[0, 1]
                    st.info(f"**相关系数**：{corr:.4f}（{x_axis} 与 {y_axis}）")
                
                if st.checkbox("显示原始数据表格"):
                    display_cols = [x_axis, y_axis, "年份"]
                    if "监测时间" in df_all.columns:
                        display_cols.insert(0, "监测时间")
                    st.dataframe(df_all[display_cols], use_container_width=True)
            else:
                st.error("筛选后没有数据，请调整筛选条件")
        else:
            st.error("未能加载任何年份数据，请检查文件路径和文件名")

st.caption("Powered by Qwen2.5-14B + Streamlit | 双指标可视化分析")