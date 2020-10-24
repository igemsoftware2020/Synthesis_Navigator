from multiprocessing import Pool
from itertools import islice
import networkx as nx
import json
import random
import numpy as np
import math
import time,datetime


class RandomWalkMetaSim:
    """
    Using random walk to simulate metabolism.
    """
    
    def __init__(self,init_json):
        """init_json should be formatted in a special style. An example is provided. e_coli_core.json"""
        assert (type(init_json)==str)
        self.net_dict=json.loads(init_json)
        self.reac_num_dict = {self.net_dict['reactions'][i]['id'] : self.net_dict['reactions'][i]['metabolites'] for i in range(len(self.net_dict['reactions']))}
        #self.reac_num_dict_neg = {self.net_dict['reactions'][i]['id'] : {k:-v for k,v in self.net_dict['reactions'][i]['metabolites'].items()} for i in range(len(self.net_dict['reactions']))}
        #del self.reac_num_dict['BIOMASS_Ecoli_core_w_GAM']
        self.metabolites = [self.net_dict['metabolites'][i]['id'] for i in range(len(self.net_dict['metabolites']))]
        self.metabolite_count=len(self.metabolites)
        self.reaction_count=len(self.reac_num_dict.items())
        self.reac_nparr=np.zeros((self.reaction_count,self.metabolite_count),dtype=np.int)
        self.energy_min=self.net_dict['STAT']['energy_mean_min']
        self.energy_max=self.net_dict['STAT']['energy_mean_max']
        self.energy_mean=self.net_dict['STAT']['energy_mean_mean']
        d=self.energy_max-self.energy_min
        self.reac_energy_dict = {self.net_dict['reactions'][i]['id'] : (self.net_dict['reactions'][i]['energy']['mean']-self.energy_mean)/d for i in range(len(self.net_dict['reactions']))}
        i=0
        for item in self.reac_num_dict.items():
            for k,v in item[1].items():
                self.reac_nparr[i][self.metabolites.index(k)]=int(v)
            i+=1
                
    
    def runSim(self,config_json):
        """config_json has three parameters: default_value (int), specified_value (dict: str:int), epoches (int)
        eg. 
        {'default_value': 100, 'specified_value': {'glc__D_e': 100000, 'gln__L_c': 100000, 'gln__L_e': 100000, 'glu__L_c': 100000, 'glu__L_e': 100000, 'glx_c': 100000}, 'epoches': 5000}
        """
        assert (type(config_json)==str)
        conf=json.loads(config_json)
        #print(conf)
        metabolites_dict = {self.net_dict['metabolites'][i]['id'] : conf['default_value'] for i in range(len(self.net_dict['metabolites']))}
        epoch = conf['epoches']
        for k,v in conf['specified_value'].items():
            metabolites_dict[k]=v
        for i in range(epoch):
            this_reac = self.reac_num_dict[random.choice(list(self.reac_num_dict))]
            flag = True
            for item in this_reac.items():
                if metabolites_dict[item[0]]-item[1]<0:
                    flag = False
            if flag:
                for item in this_reac.items():
                    metabolites_dict[item[0]]-=item[1]
        return metabolites_dict

    
    def runSim_neg(self,config_json):
        """config_json has three parameters: default_value (int), specified_value (dict: str:int), epoches (int)
        eg. 
        {'default_value': 100, 'specified_value': {'glc__D_e': 100000, 'gln__L_c': 100000, 'gln__L_e': 100000, 'glu__L_c': 100000, 'glu__L_e': 100000, 'glx_c': 100000}, 'epoches': 5000}
        """
        assert (type(config_json)==str)
        conf=json.loads(config_json)
        #print(conf)
        metabolites_dict = {self.net_dict['metabolites'][i]['id'] : conf['default_value'] for i in range(len(self.net_dict['metabolites']))}
        epoch = conf['epoches']
        for k,v in conf['specified_value'].items():
            metabolites_dict[k]=v
        for i in range(epoch):
            this_reac_id=random.choice(list(self.reac_num_dict))
            this_reac = self.reac_num_dict[this_reac_id]
            #print(list(this_reac)[:3])
            flag = True
            for item in this_reac.items():
                if metabolites_dict[item[0]]+item[1]<0:
                    flag = False
            for item in this_reac.items():
                if metabolites_dict[item[0]]-item[1]<0:
                    flag = False
            dg=self.reac_energy_dict[this_reac_id]
            if flag:
                if 0.001*sum([-m[1]*np.log(metabolites_dict[m[0]]) for m in this_reac.items()])>=dg:
                    for item in this_reac.items():
                        metabolites_dict[item[0]]+=item[1]
                    #print("S")
                else:
                    for item in this_reac.items():
                        metabolites_dict[item[0]]-=item[1]
                    #print("R")
            else:
                #print("N")
                pass
                #print(0.001*sum([np.log(metabolites_dict[m[0]]) for m in this_reac.items()]),dg)
                #for item in this_reac.items():
                    #metabolites_dict[item[0]]+=item[1]
        return metabolites_dict

    
    
    def runSimNpy(self,config_json):
        """config_json has three parameters: default_value (int), specified_value (dict: str:int), epoches (int)
        eg. 
        {'default_value': 100, 'specified_value': {'glc__D_e': 100000, 'gln__L_c': 100000, 'gln__L_e': 100000, 'glu__L_c': 100000, 'glu__L_e': 100000, 'glx_c': 100000}, 'epoches': 5000}
        """
        assert (type(config_json)==str)
        conf=json.loads(config_json)
        metabolites_nparr = np.zeros((self.metabolite_count),dtype=np.int)
        epoch = conf['epoches']
        for i in range(self.metabolite_count):
            if self.metabolites[i] in conf['specified_value']:
                metabolites_nparr[i]=conf['specified_value'][self.metabolites[i]]
            else:
                metabolites_nparr[i]=conf['default_value']
        choices=np.random.randint(0,self.reaction_count,size=(epoch))
        for i in choices:
            this_reac = self.reac_nparr[i]
            if True in ((metabolites_nparr+this_reac)<0):
                continue
            else:
                metabolites_nparr=metabolites_nparr+this_reac
        metabolites_dict = {self.metabolites[i] : int(metabolites_nparr[i]) for i in range(self.metabolite_count)}
        return json.dumps(metabolites_dict)
        
    
    
    def runSimMultiThread(self,config_json,threads):
        """
        config_json has three parameters: default_value (int), specified_value (dict: str:int), epoches (int)
        """
        result = []
        pool = Pool(processes = threads)
        for i in range(threads):
            # 维持执行的进程总数为processes，当一个进程执行完毕后会添加新的进程进去
            result.append(pool.apply_async(self.runSim, args=(config_json, )))       
        #print('======  apply_async  ======')
        pool.close()
        #调用join之前，先调用close函数，否则会出错。执行完close后不会有新的进程加入到pool,join函数等待所有子进程结束
        pool.join()
        raw_results=[]
        for res in result:
            raw_results.append(res.get())
        result_list=[]
        for item in raw_results:
            result_list.append(json.loads(item))
        result_dict = {self.net_dict['metabolites'][i]['id'] : sum([result_list[j][self.net_dict['metabolites'][i]['id']] for j in range(len(result_list))])/threads for i in range(len(self.net_dict['metabolites']))}
        return result_dict
    

    def runSimMultiThreadNpy(self,config_json,threads):
        """
        config_json has three parameters: default_value (int), specified_value (dict: str:int), epoches (int)
        """
        result = []
        pool = Pool(processes = threads)
        for i in range(threads):
            # 维持执行的进程总数为processes，当一个进程执行完毕后会添加新的进程进去
            result.append(pool.apply_async(self.runSimNpy, args=(config_json, )))       
        #print('======  apply_async  ======')
        pool.close()
        #调用join之前，先调用close函数，否则会出错。执行完close后不会有新的进程加入到pool,join函数等待所有子进程结束
        pool.join()
        raw_results=[]
        for res in result:
            raw_results.append(res.get())
        result_list=[]
        for item in raw_results:
            result_list.append(json.loads(item))
        result_dict = {self.net_dict['metabolites'][i]['id'] : sum([result_list[j][self.net_dict['metabolites'][i]['id']] for j in range(len(result_list))])/threads for i in range(len(self.net_dict['metabolites']))}
        return result_dict

def k_shortest_paths(G, source, target, k, weight=None):
    return list(
        islice(nx.shortest_simple_paths(G, source, target, weight=weight), k)
    )

class PathwaySearch:
    """
    Using graph algorithms to search pathway.
    """
    
    def __init__(self,init_json):
        """init_json should be formatted in a special style. An example is provided. e_coli_core.json"""
        assert (type(init_json)==str)
        self.net_dict=json.loads(init_json)
        self.reac_num_dict = {self.net_dict['reactions'][i]['id'] : self.net_dict['reactions'][i]['metabolites'] for i in range(len(self.net_dict['reactions']))}
        self.metabolites = [self.net_dict['metabolites'][i]['id'] for i in range(len(self.net_dict['metabolites']))]
        self.metabolite_count=len(self.metabolites)
        self.reaction_count=len(self.reac_num_dict.items())
        self.id2name_dict={}
        metalist=[i['id'] for i in self.net_dict['metabolites']]
        for meta in self.net_dict['metabolites']:
            self.id2name_dict[meta['id']]=meta['name']
        for reac in self.net_dict['reactions']:
            self.id2name_dict[reac['id']]=reac['id']
        self.G=nx.DiGraph()
        for meta in self.net_dict['metabolites']:
            self.G.add_node(meta['id'])
        for reac in self.net_dict['reactions']:
            self.G.add_node(reac['id'])
            for k,v in reac['metabolites'].items():
                if v<0:
                    try:
                        self.G.add_edge(reac['id'],k,weight = float(reac['energy']['mean'])/2+1336)
                        self.G.add_edge(k,reac['id'],weight = 1336*1336/(float(reac['energy']['mean'])/2+1336))
                    except:
                        pass
                else:
                    try:
                        self.G.add_edge(k,reac['id'],weight = float(reac['energy']['mean'])/2+1336)
                        self.G.add_edge(reac['id'],k,weight = 1336*1336/(float(reac['energy']['mean'])/2+1336))
                    except:
                        pass
    
    
    def SimpleSaerch(self,start,end,pathway_nums=10):
        """
        Given start compound and end compound to search pathways.
        start and end must be cid string
        pathway_nums must be an int and >0 (default is 5)
        """
        assert (type(start)==str)
        assert (type(end)==str)
        assert (type(pathway_nums)==int and pathway_nums>0 and pathway_nums<2000)
        ret=[]
        for path in k_shortest_paths(self.G,start,end,pathway_nums):
            res=[self.id2name_dict[i] for i in path]
            #if 'water' in res:continue
            length = sum([self.G.edges[path[i],path[i+1]]['weight'] for i in range(len(path)-1)])
            ret.append((res,length))
        
        return ret
        #return json.dumps(ret)
        
    def ReverseSaerch(self,target,nums=5):
        """
        Given target compound to reverse search the starting ones.
        tartget must be cid string
        num must be integer and >0
        """
        ret=[]
        for k,v in nx.single_target_shortest_path(self.G, target, cutoff=nums).items():
            if 'C' in k:
                pth=[self.id2name_dict[i] for i in v]
                ret.append((self.id2name_dict[k],pth))
        if len(ret)>=20:l = 20
        else:l = len(ret)
        return ret[0:l]
        #return json.dumps(ret)



def fill_ndarray(t1):
    '''对数组中的nan,用该列的平均值代替'''
    for i in range(t1.shape[1]):  # 遍历每一列（每一列中的nan替换成该列的均值）
        temp_col = t1[:, i]  # 当前的一列
        nan_num = np.count_nonzero(temp_col != temp_col)
        if nan_num != 0:  # 不为0，说明当前这一列中有nan
            temp_not_nan_col = temp_col[temp_col == temp_col]  # 去掉nan的ndarray
        # 选中当前为nan的位置，把值赋值为不为nan的均值
            # mean()表示求均值。
            temp_col[np.isnan(temp_col)] = temp_not_nan_col.mean()
    return t1


def Score(reaction_matrix, weight_user):
    '''
    # tips:
    # 检测NAN值并赋为每列的平均值

    # input:
    # 列表,五个指标分别是km,kkm,毒性，PH，温度。
    # 数组（np.array），1*5，也就是用户输入的五个权重

    # output：
    # 字典，key是每个反应，value是分数
    '''

    N = len(reaction_matrix)  # 列数
    reaction_array = np.array(reaction_matrix)  # 一个n*5的数组，一行代表一个反应，一列代表一个指标
    reaction_array = fill_ndarray(reaction_array)
    # 归一化

    parameter_min = np.min(reaction_array,axis=0) # 每个指标的最小值
    parameter_max = np.max(reaction_array,axis=0)  # 每个指标的最大值
    # 下面五个列表分别储存五个指标归一化后的数据
    km = []
    kkm = []
    toxicity = []
    ph = []
    temp = []
    for i in range(N):
        km.append(
            (parameter_max[0]+1-reaction_array[i][0])/(parameter_max[0]-parameter_min[0]+0.01))#加0.01是因为防止所有反应的某个指标都是相同的，除数为0
        kkm.append(
            (reaction_array[i][1]-parameter_min[1]+1) /
             (parameter_max[1]-parameter_min[1]+0.01))
        toxicity.append(
            (parameter_max[2]+1-reaction_array[i][2])/(parameter_max[2]-parameter_min[2]+0.01))
    # 设立9个间隔，计算一个指标的样本值落在每个间隔上的个数
    interval_ph=np.linspace(parameter_min[3]-1, parameter_max[3]+1, 10)  # 设立9个间隔,上界最大值加1是因为下面比较时是开区间
    interval_temp=np.linspace(parameter_min[4]-1, parameter_max[4]+1, 10)
    count_ph=np.zeros(9)  # 计数落在9个间隔
    count_temp=np.zeros(9)
    for m in range(N):
        for n in range(9):
            if reaction_array[m][3] < interval_ph[n+1] and reaction_array[m][3] >= interval_ph[n]:
                count_ph[n] += 1
            if reaction_array[m][4] < interval_temp[n+1] and reaction_array[m][4] >= interval_temp[n]:
                count_temp[n] += 1
    interval_ph_sorted=np.argsort(count_ph)  # 根据落在区间的数量升序排序，返回区间的索引
    interval_temp_sorted=np.argsort(count_temp)
    for m in range(N):
        for n in range(9):
            if reaction_array[m][3] < interval_ph[n+1] and reaction_array[m][3] >= interval_ph[n]:
                ph.append((interval_ph_sorted[n]/N)+0.01)  # 防止后面计算熵取对数时为0
            if reaction_array[m][4] < interval_temp[n+1] and reaction_array[m][4] >= interval_temp[n]:
                temp.append((interval_temp_sorted[n]/N)+0.01)
    reaction_matrix_normalized=[]  # 五个指标归一化后的矩阵
    reaction_matrix_normalized.append(km)
    reaction_matrix_normalized.append(kkm)
    reaction_matrix_normalized.append(toxicity)
    reaction_matrix_normalized.append(ph)
    reaction_matrix_normalized.append(temp)
    reaction_matrix_normalized=list(zip(*reaction_matrix_normalized))
    reaction_matrix_normalized=[list(t) for t in reaction_matrix_normalized]  # 得到归一化后的N*5的矩阵
    reaction_array_normalized=np.array(reaction_matrix_normalized)
    #######################
    # 找权值
    col_sum=np.sum(reaction_array_normalized, axis=0)  # 返回一个储存每一列和的数组
    for i in range(N):
        for j in range(5):
            reaction_array_normalized[i][j]=reaction_array_normalized[i][j]/col_sum[j]
    entropy=np.zeros(5)  # 储存熵
    for i in range(5):
        for j in range(N):
            entropy[i] += -(1/math.log(N))*reaction_array_normalized[j][i] * \
                            math.log(reaction_array_normalized[j][i])
    # 确定权重
    weight_initial=np.zeros(5)
    for i in range(5):
        weight_initial[i]=(1-entropy[i]+0.000001)/(5-sum(entropy)+0.000001)
    
    weight=weight_initial*weight_user  # 最终权重
    # 计算每条路的分数：
    score=np.zeros(N)
    for i in range(N):
        score[i]=weight[0]*km[i]+weight[1]*kkm[i]+weight[2] * \
            toxicity[i]+weight[3]*ph[i]+weight[4]*temp[i]
    return score




if __name__=='__main__':
    '''
    '''
    json_txt=''
    with open("statics/complex_data.json",'r') as load_f:
        json_txt=load_f.read()
    #print(str(time.time()).replace('.',''))
    #print(str(datetime.date.today()).replace('-','_'))
    """
    #随机游走代谢模拟测试
    Walk=RandomWalkMetaSim(json_txt)
    print(Walk.metabolites)
    confg={'default_value':100,'specified_value':{'C00001': 100000, 'C00002': 100000, 'C00003': 100000, 'C00004': 100000, 'C00005': 100000, 'C00006': 100000},'epoches':5000}
    conf_json_txt=json.dumps(confg)
    print(Walk.runSim(conf_json_txt))
    print(Walk.runSimMultiThread(conf_json_txt,8))
    """
    #通路搜索测试
    Sear=PathwaySearch(json_txt)
    print(Sear.SimpleSaerch('C06033','C06034'))
    #print(Sear.ReverseSaerch('C00061'))
    
    """
    #熵权法测试
    #reaction_matrix=[[np.nan, 67, -8, 8, 24], [35, 46, -78, np.nan, 34],[34, 67, 34, 6, 24],[48, 18, 58, 9, np.nan]]
    reaction_matrix = [[np.nan, np.nan, -99, np.nan, np.nan], [0.0004, 4.3, -99, 7.8, 35.0], [np.nan, np.nan, -99, np.nan, np.nan], [0.0004, 4.3, -99, 7.8, 35.0], [0.018, np.nan, -99, 8.0, np.nan], [0.0004, 4.3, -99, 7.8, 35.0], [np.nan, np.nan, -99, np.nan, np.nan], [0.059, 31.8, -99, 4.5, 60.0], [np.nan, np.nan, -99, np.nan, np.nan], [0.0004, 4.3, -99, 7.8, 35.0]]
    weight_user=np.array([0.25, 0.1, 0.35, 0.05, 0.25])
    print(Score(reaction_matrix, weight_user))
    """
    

