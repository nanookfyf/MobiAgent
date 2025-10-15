## 静态BenchMark构建
构建分层状态机来模拟设备App，提高测试效率，标准化评估流程。

### **设计思路**

将用户操作后得到的界面视为一个状态，从数据中收集出N个状态-动作序列。将动作信息合并的状态跳转信息中。根据具体规则对不同的状态进行归类。同类状态共享跳转空间。根据已有状态，随机初始化第一个状态，构建FSM。

### **设计过程记录**
- 正常的trace： [ img --> action --> img --> action .... ] x N
- 但我希望做一个有限状态机，应该将N条trace链规约为 一个状态转移图（FSM）
- 难点就是如何 **规约** 【如何把几条独立的link规约成一个状态机】

- 思考1：给所有状态划分簇类（得根据具体的APP） 有一种思路是根据哈希感知来聚类的
- 思考2：同簇类状态在也特定情况下可以随机转入

###  **核心组件**

- **State** : 状态信息。包含 名称，截图,交互映射表,跳转接口。
- **交互映射表** : <区域，动作> --> next State。
- **跳转接口** :  根据传入动作，以及当前状态的交互映射表来确定下一状态。
- **状态表** 维护该状态机的所有可能状态
- **FSM** ：根据 app 和 task 初始化状态表，并维护当前状态。

#### **跳转接口设计**
根据操作的种类可以发现如下对应关系
``` python
@dataclass
class State:
    '''
        app_state 
    '''
    img_path : str = None# 界面截图路径
    
    map_info : Dict[str, Dict] = field(default_factory=lambda: {
        "click": {
            (x1,y1,x2,y2）: state
        },
        "swipe": {
            (direction,distance):state
        },
        "input": {
            string : state
        },
        "wait": {
            time : state
        }
    })
    
    cluster_class : str = None # 状态簇类别
   
@dataclass
class Action:
    '''
        app action
    '''
    act_type : str
    parameters : dict
```



#### **跳转接口设计**
根据操作的种类可以发现如下对应关系
``` python
    map_info = {
        "click":{
            #(x1,y1,x2,y2) -> target_state
        },
        "swipe":{
            #(dir,dis)  -> target_state
        },
        "input":{
            # text -> target_state
        },
        "wait":{
            # duration -> target_state
        }
    }
```
-归约所有的TraceLink为一体状态机
            
    -状态分簇
        - 分析UI树 X
        - 图像特征聚类 X
        - 基于对称操作的自聚类 yes
    -转移归约

FSM维护动作次数和无响应动作次数，超过一定数量将refresh

#### **优化**



