import os
import re
import json
import os
from typing import List, Dict, Any
from pathlib import Path
from type_spaces  import *
import math
from fsm import union_maps
from vis import simple_visualize_trace, simple_visualize_tracev1
ActionTypeMAP = {
    
    "click":ClickAction,
    "swipe":SwipeAction,
    "input_text":InputAction,
    "wait":WaitAction,
    "done":DoneAction
            
}

class TraceLink:
    app_name: str
    task_type: str
    task_description: str
    num_states: int
    states: List[State]  # 状态列表
    actions: List[Action] # 动作列表
    class_data : Dict
    def to_dict(self):
        return {
            "app_name": self.app_name,
            "task_type": self.task_type,
            "task_description": self.task_description,
            "num_states": self.num_states,
            "states": [state.to_dict() for state in self.states],
            #"actions": [action.to_dict() for action in self.actions]
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            app_name=data["app_name"],
            task_type=data["task_type"],
            task_description=data["task_description"],
            num_states=data["num_states"],
            states=[State.from_dict(state) for state in data["states"]],
            actions=[Action.from_dict(action) for action in data["actions"]]
        )
        
def save_states(self, states: List[State]):
    """保存状态列表到JSON文件"""
    data = [state.to_dict() for state in states]
    with open(self.filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_states(self) -> List[State]:
    """从JSON文件加载状态列表"""
    try:
        with open(self.filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return [State.from_dict(item) for item in data]
    except FileNotFoundError:
        return []
    
class TraceParser:
    """Trace数据解析器"""
    
    def __init__(self):
        self.trace_link = None
        self.states_map = {}  # img_path -> State
        self.class_data = {}
    
    def parse_trace_directory(self, trace_dir: str) -> TraceLink:
        """
        解析trace目录，包含actions.json、react.json和截图文件
        
        Args:
            trace_dir: trace数据目录路径
            
        Returns:
            Trace对象
        """
        trace_dir = Path(trace_dir)
        
        # 解析actions.json
        actions_file = trace_dir / "actions.json"
        if not actions_file.exists():
            raise FileNotFoundError(f"actions.json not found in {trace_dir}")
        
        actions = self._load_parse_json_file(actions_file)
        
        # 解析截图文件
        screenshots = self._parse_screenshots(trace_dir)
        
        # 构建Trace对象
        trace = self._build_trace_link(states=screenshots, actions=actions)
        
        return trace
    
    def _load_parse_json_file(self, file_path: Path) -> Dict[str, Any]:
        """加载JSON文件"""
        Actions = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                jsonf = json.load(f)
                self.app_name = jsonf.get("app_name", "unknown")
                self.task_type = jsonf.get("task_type", "unknown")
                self.task_description = jsonf.get("task_description", [])
                self.num_states = jsonf.get("action_count", 0)
                actions = jsonf.get("actions", [])
                for action in actions:
                    act_type = action.get("type", "")
                    act_param = {}
                    for k, v in action.items():
                        if k != "type" and v is not None:
                            act_param[k] = v
                    action_obj = Action(act_type=act_type, parameters=act_param) 
                    Actions.append(action_obj)      
                return Actions
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in {file_path}: {e}")
    
    def _parse_screenshots(self, trace_dir: Path) -> List[State]:
        """解析截图文件"""
        
        def sort_images_by_order(folder_path):
        
            """按照收集顺序排序图片文件"""
            
            image_files = []
            
            # 收集所有图片文件
            for filename in os.listdir(folder_path):
                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                    # 解析文件名格式 a_b.jpg
                    match = re.match(r'^(\d+)_(\d+)\.', filename)
                    if match:
                        category = match.group(1)  # a
                        order = int(match.group(2))  # b
                        image_files.append((order, category, filename))
            
            # 按照 b（收集顺序）排序
            sorted_files = sorted(image_files, key=lambda x: x[0])
            files = []
            #class_data = {}
            for order, category, filename in sorted_files:
                files.append(os.path.join(folder_path,filename))
                
            
            return files,sorted_files
        
        States = []
        
        # 查找所有jpg文件（按数字序排序：1.jpg, 2.jpg, ... 10.jpg）
        jpg_files,sort_files = sort_images_by_order(trace_dir) 
        
        for i, jpg_file in enumerate(jpg_files):
            screenshot = State(img_path=str(jpg_file))
            self.states_map[str(jpg_file)] = screenshot
            States.append(screenshot)
        for order, category, filename in sort_files:
            if category not in self.class_data.keys():
                self.class_data[category] = [self.states_map[os.path.join(trace_dir,filename)]]
            else:
                self.class_data[category].append(self.states_map[os.path.join(trace_dir,filename)]) 
        return States

    def _build_trace_link(self,states,actions):
        self.trace_link = TraceLink()
        self.trace_link.app_name = self.app_name
        self.trace_link.task_type = self.task_type
        self.trace_link.task_description = self.task_description
        self.trace_link.num_states = self.num_states
        self.trace_link.states = states
        self.trace_link.actions = actions
        self.trace_link.class_data = self.class_data
        return self.trace_link

def add_transition(start_state:State, action:Action, target_state:State):
    if action.act_type == "click":
        
        if 'bounds' in action.parameters.keys():
            key = action.parameters['bounds']
            start_state.map_info["click"][tuple(key)] = target_state.img_path
        else:
            if "unknown" not in start_state.map_info["click"]:
                start_state.map_info["click"]["unknown"] = [target_state.img_path]
            else:
                start_state.map_info["click"]["unknown"].append(target_state.img_path)
                
                
    elif action.act_type == "swipe":
        dir_ = action.parameters["direction"]
        dis = 0
        
        if dir_ == "up" or dir_ == "down":
            dis = math.fabs(action.parameters["press_position_y"] - action.parameters["release_position_y"])
            
        elif dir_ == "left" or dir_ == "right":
            dis = math.fabs(action.parameters["press_position_x"] - action.parameters["release_position_x"])
            
        start_state.map_info["swipe"][(dir_,dis)] = target_state.img_path
    elif action.act_type == "input":
        start_state.map_info["input"][action.parameters["text"]] = target_state.img_path
    elif action.act_type == "wait":
        start_state.map_info["wait"][action.parameters["duration"]] = target_state.img_path
        
def merge_info(trace:TraceLink):
    '''
        将trace中的action信息合并至state中
    '''
    for i in range(trace.num_states-1):

        add_transition(trace.states[i], trace.actions[i],trace.states[i+1] )
def merge_class_info(traces:TraceLink):
    '''
        将多个trace的class_data信息合并
    '''
    
    print("reduce transitions ...")
    for k,v in traces.class_data.items():
        all_map = {
            "click":{
            },
            "swipe":{
            },
            "input":{
            },
            "wait":{
            }
        }
        for s in v:
            for act_type, map_ in s.map_info.items():
                #print(act_type,map_)
                if act_type in all_map.keys():
                    all_map[act_type].update(map_)
        #print(all_map)
        for s in v:
            union_maps(all_map, s.map_info)  
#test
if __name__ == "__main__":
    parser = TraceParser()
    #trace = parser.parse_trace_directory("C:/Users/32089/Desktop/AIinfra/MobiAgent/collect/manual/data/美团/type1/9")
    trace = parser.parse_trace_directory("C:/Users/32089/Desktop/AIinfra/MobiAgent/collect/manual/data/bilibili/type1/2")
    print(f"App Name: {trace.app_name}")
    print(f"Task Type: {trace.task_type}")
    print(f"Task Description: {trace.task_description}")
    print(f"Number of States: {trace.num_states}")
    
    for action in trace.actions:
        print(f"Action Type: {action.act_type}, Parameters: {action.parameters}")
    merge_info(trace)

    for state in trace.states:
        print(f"State Image Path: {state.img_path}, Map Info: {state.map_info}")
    print(f"class data : {parser.class_data}")
    merge_class_info(trace)
    for state in trace.states:
        print(f"State Image Path: {state.img_path}, Map Info: {state.map_info}")

    




    # 使用示例
    simple_visualize_trace(trace)
    #simple_visualize_tracev1(trace)