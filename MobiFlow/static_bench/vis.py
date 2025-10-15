import matplotlib.pyplot as plt
import networkx as nx
from pathlib import Path
import numpy as np

def simple_visualize_tracev1(trace_link):
    """简单可视化TraceLink数据，相同类别的节点画在一起"""
    
    # 创建图
    G = nx.DiGraph()
    
    # 添加节点和边
    for state in trace_link.states:
        state_name = Path(state.img_path).stem
        G.add_node(state_name)
        
        # 添加转移边
        for action_type, actions in state.map_info.items():
            if actions:
                for key, target_path in actions.items():
                    if target_path:
                        target_name = Path(target_path).stem
                        G.add_edge(state_name, target_name, action=action_type)
    
    # 绘制图形
    plt.figure(figsize=(12, 8))
    
    # 按类别分组节点
    categories = {}
    for node in G.nodes():
        category = node.split('_')[0]  # 提取a部分
        if category not in categories:
            categories[category] = []
        categories[category].append(node)
    
    # 手动设置节点位置，相同类别的节点放在同一列
    sortcategories = sorted(categories.items(), key=lambda x: int(x[0]))
    pos = {}
    num_categories = len(categories)
    
    for i, (category, nodes) in enumerate(sortcategories):
        x = i  # 每个类别一列
        nodes_sorted = sorted(nodes, key=lambda x: int(x.split('_')[1]))  # 按b排序
        
        for j, node in enumerate(nodes_sorted):
            y = -j  # 每个节点一行
            pos[node] = (x, y)
    
    # 绘制节点（按类别着色）
    category_colors = plt.cm.Set3(np.linspace(0, 1, len(categories)))
    color_map = {}
    
    for i, category in enumerate(categories.keys()):
        color_map[category] = category_colors[i]
    
    node_colors = [color_map[node.split('_')[0]] for node in G.nodes()]
    
    nx.draw_networkx_nodes(G, pos, node_size=500, node_color=node_colors, alpha=0.9, edgecolors='black')
    
    # 绘制边（按动作类型着色）
    edge_colors = []
    for u, v, data in G.edges(data=True):
        color_map = {'click': 'red', 'swipe': 'green', 'input': 'orange', 'wait': 'gray'}
        edge_colors.append(color_map.get(data['action'], 'black'))
    
    nx.draw_networkx_edges(G, pos, edge_color=edge_colors, arrows=True, arrowsize=20, alpha=0.7)
    
    # 绘制标签
    nx.draw_networkx_labels(G, pos, font_size=8)

    plt.title(f"FSM-V1")
    plt.axis('off')
    plt.tight_layout()
    plt.show()
    
    # 打印简单统计
    print(f"状态数: {len(G.nodes())}")
    print(f"转移数: {len(G.edges())}")
    print(f"类别数: {len(categories)}")
    for category, nodes in categories.items():
        print(f"  类别 {category}: {len(nodes)} 个状态")


def simple_visualize_trace(trace_link):
    """简单可视化TraceLink数据"""
    
    # 创建图
    G = nx.DiGraph()
    
    # 添加节点和边
    for state in trace_link.states:
        state_name = Path(state.img_path).stem
        G.add_node(state_name)
        
        # 添加转移边
        for action_type, actions in state.map_info.items():
            if actions:
                for key, target_path in actions.items():
                    if target_path:
                        target_name = Path(target_path).stem
                        G.add_edge(state_name, target_name, action=action_type)
    
    # 绘制图形
    plt.figure(figsize=(12, 8))
    
    # 使用spring布局
    pos = nx.spring_layout(G, k=1, iterations=50)
    
    # 绘制节点
    nx.draw_networkx_nodes(G, pos, node_size=500, node_color='lightblue', alpha=0.9)
    
    # 绘制边（按动作类型着色）
    edge_colors = []
    for u, v, data in G.edges(data=True):
        color_map = {'click': 'red', 'swipe': 'green', 'input': 'orange', 'wait': 'gray'}
        edge_colors.append(color_map.get(data['action'], 'black'))
    
    nx.draw_networkx_edges(G, pos, edge_color=edge_colors, arrows=True, arrowsize=20)
    
    # 绘制标签
    nx.draw_networkx_labels(G, pos, font_size=8)
    
    plt.title(f"FSM")
    plt.axis('off')
    plt.tight_layout()
    plt.show()
    
    # 打印简单统计
    print(f"状态数: {len(G.nodes())}")
    print(f"转移数: {len(G.edges())}")