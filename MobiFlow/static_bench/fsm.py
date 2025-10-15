import os
from type_spaces import *
from parsedata2link import *
import random

def union_maps(map1, map2):
    '''
        合并两个状态的map_info字典 map1 -合并给> map2【不覆盖】
    '''
    for act_type in map1.keys():
        if act_type in map2.keys():
            for k,v in map1[act_type].items():
                if k not in map2[act_type].keys():
                    map2[act_type][k] = v
                
    return map2
def random_choice_from_list(lst):
    """
    从列表中随机选择一个元素
    
    Args:
        lst: 输入列表
        
    Returns:
        随机选择的元素
        
    Raises:
        ValueError: 如果列表为空
    """
    if not lst:
        raise ValueError("列表不能为空")
    
    return random.choice(lst)

def loadactions(file_path: str) -> List[Action]:
    '''
        从actions.json中加载动作序列
    '''
    Actions = []
    with open(file_path, 'r', encoding='utf-8') as f:
        jsonf = json.load(f)
        
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

def point_in_rectangle(x: float, y: float, 
                      x1,y1,x2,y2) -> bool:
    return x1 <= x <= x2 and y1 <= y <= y2

class AppFSM:
    
    def __init__(self,app,task,data_path) -> None:
        self.app = app #app name
        self.task = task #task name
        self.data_path = data_path #构建此FSM的数据路径
        self.filename = os.path.join(data_path,"fsm",app,task,"fsm_traces.json") #保存trace的文件路径
        self.traces = [] #所有的traceLink
        self.hash_map = {}# img_path -> State
        self.app_states: Dict[str, List] = {} # app所有的状态簇
        
        self.cur_state: State = None
        self.parser = TraceParser()
        
        self._init_states()
        self._cluster()
        self._reduce_transitions()
        
          
        
        self.max_op_times = 100
        self.max_undefine_op_times = 5
        
        self.undefine_op_times = 0
        self.op_times = 0
        
        
    def save_traces(self):
        directory = os.path.dirname(self.filename)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        
        traces = self.traces
            
        """保存多条轨迹链到文件"""
        data = {
            "version": "1.0",
            "total_traces": len(traces),
            "traces": [trace.to_dict() for trace in traces]
        }
        
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    
    def load_traces(self):
        """从文件加载多条轨迹链"""
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                traces = [TraceLink.from_dict(trace) for trace in data["traces"]]
                self.traces = traces
            return 
        except FileNotFoundError:
            return
        
    def _init_states(self):
        # 解析数据路径下的所有trace数据
        task_path = os.path.join(self.data_path,self.app,self.task)
        trace_links = []
        i = 0
        walker = os.walk(task_path)
        next(walker) #跳过根目录
        for root,_,_ in walker:
            #print(root)
            try:
                trace_link = self.parser.parse_trace_directory(root)
                merge_info(trace_link)
                trace_links.append(trace_link)
                self.hash_map.update(self.parser.states_map)
                
            except Exception as e:
                print(f"Error parsing trace in {root}: {e}")
                continue
        self.traces = trace_links
        
            

            
    def _cluster(self):
        '''
            归约所有的TraceLink为一体状态机
            
                -状态分簇
                    - 分析UI树 X
                    - 图像特征聚类 X
                    - 基于对称操作的自聚类 yes
                -转移归约
        '''
        print("all cluster ...") 
        for t in self.traces:
            for i,s in enumerate(t.states):
                if i ==0 :
                    #初始状态归为HomeFeed
                    s.cluster_class = "HomeFeed"
                    if s.cluster_class not in self.app_states.keys():
                        self.app_states[s.cluster_class] = [s]
                    else:
                        self.app_states[s.cluster_class].append(s) 
                if 0<i:
                    act = t.actions[i]
                    if act.act_type == "input":
                        # 输入操作的状态归为inputpage
                        s.cluster_class = "inputpage"
                        if s.cluster_class not in self.app_states.keys():
                            self.app_states[s.cluster_class] = [s]
                        else:
                            self.app_states[s.cluster_class].append(s)
                            
                    if act.act_type == "done":
                        s.cluster_class = "Done"
                        
               
    def _reduce_transitions(self):
        '''
            归约求并状态转移
        '''
        print("reduce transitions ...")
        for k,v in self.app_states.items():
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
    
    def _transition(self,act) -> State:
        self.op_times += 1
        
        
        if action.act_type == "click":
            #遍历当前状态mapinfo的所有bound 如果在区域中跳转
            #否则 返回原状态
            
            for k,v in self.cur_state.map_info["click"].items():
                if k == "unknown":
                    
                    continue
                if point_in_rectangle(act.parameters['position_x'],act.parameters['position_y'],
                                      k[0],k[1],k[2],k[3]):
                    return self.hash_map[v]
            
            self.undefine_op_times += 1   
            return self.cur_state  
        
        elif action.act_type == "swipe":
            for k,v in self.cur_state.map_info["swipe"].items():
                dir_ = action.parameters["direction"]
                dis = 0
                if dir_ == "up" or dir_ == "down":
                    dis = math.fabs(action.parameters["press_position_y"] - action.parameters["release_position_y"])
                    
                elif dir_ == "left" or dir_ == "right":
                    dis = math.fabs(action.parameters["press_position_x"] - action.parameters["release_position_x"])
                if k[0] == dir_ and k[1]-2 <= dis <= k[1]+2:
                    return self.hash_map[v]
            self.undefine_op_times += 1
            return self.cur_state
        
        elif action.act_type == "input":
            for k,v in self.cur_state.map_info["input"].items():
                if k == act.parameters["text"]:
                    return self.hash_map[v]
                
            self.undefine_op_times += 1
            return self.cur_state
        else:
            self.undefine_op_times += 1
            return self.cur_state
                               
    def _reset(self):
        self.cur_state = None
        self.undefine_op_times = 0
        self.op_times = 0
                                              
    def action(self, act) -> State:
        
        if self.cur_state is None:
            self.cur_state = random_choice_from_list(self.app_states["HomeFeed"])
            print(f"random init state {self.cur_state.img_path} {self.cur_state.cluster_class}...")
        self.cur_state = self._transition(act)
        
        return self.cur_state
    
    
if __name__ == "__main__":
    #path C:/Users/32089/Desktop/AIinfra/MobiAgent/collect/manual/data/
    # C:/Users/32089/Desktop/AIinfra/MobiAgent/MobiFlow/static_bench/test_data
    fsm = AppFSM("bilibili","type1","C:/Users/32089/Desktop/AIinfra/MobiAgent/MobiFlow/static_bench/test_data")
    actions = loadactions("C:/Users/32089/Desktop/AIinfra/MobiAgent/MobiFlow/static_bench/test_data/bilibili/type1/5/actions.json")
    fsm.save_traces()
    #print(fsm.hash_map)
    for action in actions:
        state = fsm.action(action)
        print(f"action: {action}, state: {state.img_path} {state.cluster_class}")
        if state.cluster_class == "Done":
            print("task done!")
            break