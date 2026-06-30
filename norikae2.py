import streamlit as st
import networkx as nx
import graphviz

# ==========================================
# 1. 路線データの定義（駅順リストとエッジ）
# ==========================================
LINES_STATIONS = {
    "中央線": ["一ノ瀬", "境港", "谷上町", "第1拠点", "晴海坂", "滝沢", "終宮", "新蒼海宮", "蒼海宮"],
    "桜町線(各停)": ["荒山村", "桜町一丁目", "谷上三丁目", "白浜崎", "砂炭江", "霧ヶ峰", "霧ヶ峰湖", "風見野", "北茜ヶ原", "茜ヶ原"],
    "桜町線(快速)": ["白浜崎", "霧ヶ峰", "茜ヶ原"],
    "東西線": ["一ノ瀬", "桜坂", "緑山", "旭ヶ丘", "霧ヶ峰", "亀浜"],
    "南北線": ["西霧ヶ峰", "新都町", "前哨基地"],
    "霧ヶ峰線": ["蒼海宮", "亀浜", "西霧ヶ峰", "霧ヶ峰湖"],
    "新都心線": ["終宮", "亀浜", "新都町", "朝凪"],
    "中央都市線": ["速見", "霧ヶ峰", "西霧ヶ峰", "南新都町", "朝凪南", "朝凪"],
    "南辺線": ["風見野", "前哨基地"],
    "中央新幹線": ["白浜崎", "新蒼海宮"],
    "晴海坂線": ["砂炭江", "晴海坂", "東晴海坂"]
}

def get_lines_data():
    return {
        "中央線": [("一ノ瀬", "境港", 120), ("境港", "谷上町", 60), ("谷上町", "第1拠点", 30), ("第1拠点", "晴海坂", 30), ("晴海坂", "滝沢", 90), ("滝沢", "終宮", 120), ("終宮", "新蒼海宮", 120), ("新蒼海宮", "蒼海宮", 60)],
        "桜町線(各停)": [("荒山村", "桜町一丁目", 60), ("桜町一丁目", "谷上三丁目", 30), ("谷上三丁目", "白浜崎", 60), ("白浜崎", "砂炭江", 90), ("砂炭江", "霧ヶ峰", 90), ("霧ヶ峰", "霧ヶ峰湖", 60), ("霧ヶ峰湖", "風見野", 120), ("風見野", "北茜ヶ原", 120), ("北茜ヶ原", "茜ヶ原", 60)],
        "桜町線(快速)": [("白浜崎", "霧ヶ峰", 180), ("霧ヶ峰", "茜ヶ原", 360)],
        "東西線": [("一ノ瀬", "桜坂", 180), ("桜坂", "緑山", 180), ("緑山", "旭ヶ丘", 60), ("旭ヶ丘", "霧ヶ峰", 90), ("霧ヶ峰", "亀浜", 60)],
        "南北線": [("西霧ヶ峰", "新都町", 30), ("新都町", "前哨基地", 180)],
        "霧ヶ峰線": [("蒼海宮", "亀浜", 150), ("亀浜", "西霧ヶ峰", 30), ("西霧ヶ峰", "霧ヶ峰湖", 60)],
        "新都心線": [("終宮", "亀浜", 130), ("亀浜", "新都町", 60), ("新都町", "朝凪", 60)],
        "中央都市線": [("速見", "霧ヶ峰", 60), ("霧ヶ峰", "西霧ヶ峰", 30), ("西霧ヶ峰", "南新都町", 60), ("南新都町", "朝凪南", 60), ("朝凪南", "朝凪", 60)],
        "南辺線": [("風見野", "前哨基地", 150)],
        "中央新幹線": [("白浜崎", "新蒼海宮", 50)],
        "晴海坂線": [("砂炭江", "晴海坂", 120), ("晴海坂", "東晴海坂", 60)]
    }

def get_direction(line_name, from_station, to_station):
    if line_name in LINES_STATIONS:
        stations = LINES_STATIONS[line_name]
        if from_station in stations and to_station in stations:
            idx_from = stations.index(from_station)
            idx_to = stations.index(to_station)
            if idx_to > idx_from:
                return f"{stations[-1]}方面"
            else:
                return f"{stations[0]}方面"
    if "直通" in line_name:
        return f"{to_station}方面"
    return ""

@st.cache_resource
def build_routing_graph():
    G = nx.Graph()
    lines = get_lines_data()
    station_lines = {}

    for line_name, edges in lines.items():
        for u, v, w in edges:
            u_node = f"{u}|{line_name}"
            v_node = f"{v}|{line_name}"
            opt_w = w - 0.1 if "快速" in line_name else w
            G.add_edge(u_node, v_node, time=w, weight_fast=opt_w, weight_trans=w, line=line_name, is_transfer=False)
            station_lines.setdefault(u, set()).add(line_name)
            station_lines.setdefault(v, set()).add(line_name)

    for station, slines in station_lines.items():
        slines = list(slines)
        for i in range(len(slines)):
            for j in range(i+1, len(slines)):
                u_node = f"{station}|{slines[i]}"
                v_node = f"{station}|{slines[j]}"
                G.add_edge(u_node, v_node, time=30, weight_fast=30, weight_trans=10000, line="🔄 乗換", is_transfer=True)

    walks = [
        ("谷上町", "中央線", "谷上三丁目", "桜町線(各停)", 30),
        ("新都町", "南北線", "南新都町", "中央都市線", 30),
        ("新都町", "新都心線", "南新都町", "中央都市線", 30)
    ]
    for u, ul, v, vl, w in walks:
        G.add_edge(f"{u}|{ul}", f"{v}|{vl}", time=w, weight_fast=w, weight_trans=10000, line="🚶 徒歩連絡", is_transfer=True)

    G.add_edge("砂炭江|桜町線(各停)", "亀浜|東西線", time=120, weight_fast=120, weight_trans=120, line="桜町線⇔東西線(直通)", is_transfer=False)
    G.add_edge("砂炭江|桜町線(各停)", "亀浜|新都心線", time=120, weight_fast=120, weight_trans=120, line="桜町線⇔新都心線(直通)", is_transfer=False)
    G.add_edge("砂炭江|桜町線(各停)", "西霧ヶ峰|南北線", time=120, weight_fast=120, weight_trans=120, line="桜町線⇔南北線(直通)", is_transfer=False)

    return G, station_lines

# ==========================================
# 4. 動的路線図の生成ロジック (スマホ対応 縦長版)
# ==========================================
def generate_visual_map(path_stations=None):
    dot = graphviz.Graph(engine='dot')
    
    # 【変更点】rankdirを'TB'(Top to Bottom)にすることで、スマホで縦スクロールで綺麗に見えるように修正
    dot.attr(rankdir='TB', nodesep='0.4', ranksep='0.6', dpi='150')
    dot.attr('node', shape='rect', style='rounded,filled', fillcolor='#FFFFFF', color='#555555', fontname='sans-serif', fontsize='12', height='0.3')
    dot.attr('edge', fontname='sans-serif', fontsize='10', penwidth='6.0')
    
    colors = {
        "中央線": "#FF8C00", "桜町線(各停)": "#FF69B4", "桜町線(快速)": "#FF1493",
        "東西線": "#00BFFF", "南北線": "#1E90FF", "霧ヶ峰線": "#FF0000",
        "新都心線": "#8B4513", "中央都市線": "#228B22", "南辺線": "#8A2BE2",
        "中央新幹線": "#FFD700", "晴海坂線": "#808080"
    }
    
    lines = get_lines_data()
    
    path_edges = set()
    path_nodes = set(path_stations) if path_stations else set()
    if path_stations:
        for i in range(len(path_stations)-1):
            path_edges.add((path_stations[i], path_stations[i+1]))
            path_edges.add((path_stations[i+1], path_stations[i]))

    all_stations = set()
    for edges in lines.values():
        for u, v, _ in edges:
            all_stations.add(u)
            all_stations.add(v)
            
    for station in sorted(all_stations):
        if station in path_nodes:
            dot.node(station, station, fillcolor='#FFFEE0', color='#FFD700', penwidth='3.0')
        else:
            dot.node(station, station, penwidth='1.5')

    added_edges = set()
    for line_name, edges in lines.items():
        base_color = colors.get(line_name, "#000000")
        for u, v, _ in edges:
            edge_key = tuple(sorted([u, v]))
            if (edge_key, line_name) not in added_edges:
                is_on_path = (u, v) in path_edges
                if path_stations:
                    if is_on_path:
                        dot.edge(u, v, color=base_color, penwidth='7.0', label=line_name)
                    else:
                        dot.edge(u, v, color=f"{base_color}30", penwidth='2.0', style='dashed' if "快速" in line_name else 'solid')
                else:
                    dot.edge(u, v, color=base_color, style='dashed' if "快速" in line_name else 'solid')
                added_edges.add((edge_key, line_name))

    walks = [("谷上町", "谷上三丁目"), ("新都町", "南新都町")]
    for u, v in walks:
        is_on_path = (u, v) in path_edges
        if path_stations:
            if is_on_path:
                dot.edge(u, v, color="#666666", penwidth='4.0', style='dotted', label="徒歩")
            else:
                dot.edge(u, v, color="#66666630", penwidth='1.5', style='dotted')
        else:
            dot.edge(u, v, color="#666666", penwidth='2.5', style='dotted')

    return dot

# ==========================================
# 5. メインアプリケーション
# ==========================================
def main():
    st.set_page_config(page_title="Minecraft鉄道 乗り換え案内", layout="centered")
    st.title("Minecraft鉄道 乗り換え案内 🛤️")
    
    G_base, station_lines = build_routing_graph()
    unique_stations = sorted(list(station_lines.keys()))

    st.markdown("### 出発・到着駅と条件を選択")
    col1, col2 = st.columns(2)
    with col1:
        start_station = st.selectbox("出発駅", unique_stations, index=unique_stations.index("荒山村") if "荒山村" in unique_stations else 0)
    with col2:
        end_station = st.selectbox("到着駅", unique_stations, index=unique_stations.index("霧ヶ峰") if "霧ヶ峰" in unique_stations else 0)

    search_mode = st.radio("優先する条件", ["最速（時間を優先／快速優先）", "乗り換え回数（乗換の少なさを優先）"], horizontal=True)

    if st.button("経路を検索", type="primary", use_container_width=True):
        if start_station == end_station:
            st.warning("出発駅と到着駅が同じです。")
            return

        G = G_base.copy()
        for node in G_base.nodes():
            if node.startswith(f"{start_station}|"):
                G.add_edge("START", node, time=0, weight_fast=0, weight_trans=0, line="乗車", is_transfer=False)
            if node.startswith(f"{end_station}|"):
                G.add_edge(node, "END", time=0, weight_fast=0, weight_trans=0, line="降車", is_transfer=False)
                
        weight_key = "weight_fast" if "最速" in search_mode else "weight_trans"
        
        try:
            path = nx.shortest_path(G, source="START", target="END", weight=weight_key)
            
            # STARTとENDを除外した実際の駅リスト
            actual_path = path[1:-1]
            steps = []
            real_time = 0
            transfer_count = 0
            path_stations = []
            
            # ハイライト図のための駅名抽出
            for node in actual_path:
                s_name = node.split('|')[0]
                if not path_stations or path_stations[-1] != s_name:
                    path_stations.append(s_name)

            # 【変更点】途中駅（intermediates）を記録するロジック
            for i in range(len(actual_path) - 1):
                u, v = actual_path[i], actual_path[i+1]
                edge = G[u][v]
                real_time += edge['time']
                if edge['is_transfer']: transfer_count += 1
                
                u_sta = u.split('|')[0]
                v_sta = v.split('|')[0]
                
                # 同じ路線が続く場合は、toを更新し、間の駅をintermediatesリストに放り込む
                if steps and not edge['is_transfer'] and steps[-1]['line'] == edge['line']:
                    steps[-1]['to'] = v_sta
                    steps[-1]['time'] += edge['time']
                    steps[-1]['intermediates'].append(u_sta)
                else:
                    steps.append({
                        "from": u_sta, "to": v_sta,
                        "line": edge['line'], "time": edge['time'], "is_transfer": edge['is_transfer'],
                        "intermediates": [] # 新しい路線の乗車時にリストを初期化
                    })
            
            st.success(f"⏱️ 所要時間: **{real_time // 60}分 {real_time % 60}秒** 🔄 乗換: **{transfer_count}回**")
            st.divider()
            
            st.markdown("### 🗺️ 経路案内")
            st.markdown(f"**🟢 {steps[0]['from']}**")
            
            for step in steps:
                if step['is_transfer']:
                    st.markdown(f" *({step['line']})*")
                else:
                    m, s = divmod(step['time'], 60)
                    time_str = f"{m}分{s}秒" if m > 0 else f"{s}秒"
                    direction = get_direction(step['line'], step['from'], step['to'])
                    dir_str = f" （{direction}行）" if direction else ""
                    st.info(f"⬇️ **{step['line']}**{dir_str} （{time_str}）")
                    
                    # 【変更点】途中駅がある場合のみ、アコーディオン（expander）を表示
                    if step['intermediates']:
                        num_stations = len(step['intermediates'])
                        with st.expander(f"🔽 途中駅（{num_stations}駅）"):
                            for intermediate_station in step['intermediates']:
                                st.write(f" ・ {intermediate_station}")
                
                st.markdown(f"**🔵 {step['to']}**")
                
            st.markdown("🏁 **到着**")
            
            st.divider()
            st.markdown("### 🗺️ 運行ルート路線図 (ハイライト)")
            route_map = generate_visual_map(path_stations)
            st.graphviz_chart(route_map, use_container_width=True)

        except nx.NetworkXNoPath:
            st.error("経路が見つかりませんでした。")

    st.divider()
    
    st.markdown("### 🚉 路線図ビューア")
    selected_line = st.selectbox("路線を選択して駅一覧を表示", list(LINES_STATIONS.keys()))
    line_stations = LINES_STATIONS[selected_line]
    st.markdown(f"**{selected_line} の駅一覧:**")
    st.write(" ➔ ".join(line_stations))
    
    st.markdown("#### 🌐 全体路線ネットワーク図")
    st.graphviz_chart(generate_visual_map(), use_container_width=True)

if __name__ == "__main__":
    main()