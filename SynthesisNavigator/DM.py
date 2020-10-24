
# -*- coding: utf-8 -*-
 
from django.http import HttpResponse
from AppModel import models
from SynthesisNavigator import SqLiteConnect
#import SqLiteConnect
import json
import numpy as np

# 数据库操作
def get_data(databasename):
    '''
    获取数据库的数据
    '''
    info = SqLiteConnect.select(DatabaseName=databasename)
    return info


def matrix2json(reaction_deficient,compound_deficient):
    '''
    将对应的数据库内数据进行预加载
    '''
    energy_mean_mean,energy_mean_max,energy_mean_min,mass_mean,mass_max,mass_min,metabolic_nums,reaction_nums = 0,-999,999,0,0,999,0,0
    metabolic_frequency = {}
    jsontext = {'metabolites':[],'reactions':[],'STAT':{}}
    compound_info = SqLiteConnect.select('COMPOUND')
    #print(compound_info[-1])
    #compound data的录入
    for EC in compound_info:
        if EC[0] in compound_deficient:
            continue 
        jsontext['metabolites'].append({'id':EC[0],'name':EC[1],'formula':EC[2],'mass':EC[5],'smile':EC[3]})
        metabolic_nums+=1
        if EC[5]:
            mass_mean+=EC[5]
            if EC[5]>mass_max:mass_max=EC[5]
            if EC[5]<mass_min:
                mass_min=EC[5]
                #print(mass_min)
        metabolic_frequency[EC[0]]=0
    
    reaction_info = SqLiteConnect.select('REACTION')
    #print(reaction_info[1])
    #reaction data的录入
    for ER in reaction_info:
        flag = 0
        if ER[0] in reaction_deficient:flag = 1
        metabolites = {}
        if 'G' in ER[1] or 'm' in ER[1] or 'n' in ER[1]:
            flag = 1
        reactant = ER[1].split('<=>')[0].split('+')
        product = ER[1].split('<=>')[1].split('+')
        for nc in reactant:
            if len(nc.strip().split(' '))==1:
                if nc.strip()[:6]=='C22133':c = 'C21097'
                else:c = nc.strip()[:6]
                if c not in compound_deficient:metabolites[c]=1
            else:
                if nc.strip().split(' ')[1][:6]=='C22133':c = 'C21097'
                else:c = nc.strip().split(' ')[1][:6]
                try:
                    if c not in compound_deficient: metabolites[c]=int(nc.strip().split(' ')[0])
                except:flag = 1
        for nc in product:
            if len(nc.strip().split(' '))==1:
                if nc.strip()[:6]=='C22133':c = 'C21097'
                else:c = nc.strip()[:6]
                if c not in compound_deficient:metabolites[c]=-1
            else:
                if nc.strip().split(' ')[1][:6]=='C22133':c = 'C21097'
                else:c = nc.strip().split(' ')[1][:6]
                try:
                    if c not in compound_deficient:metabolites[c]=-int(nc.strip().split(' ')[0])
                except:flag = 1
        
        reaction_class = ER[3].split('\t')
        ecnum = ER[2].split('\t')
        if ER[4]:
            if ER[4].split('\t')[0] != 'nan':
                mean = float(ER[4].split('\t')[0])
            else:
                mean = -59.4797
            if ER[4].split('\t')[1] != 'nan':
                sd = float(ER[4].split('\t')[1])
            else:
                sd = 8.0264
            energy = {'mean':mean,'sd':sd}
        else:energy = {'mean':-59.4797,'sd': 8.0264}
        if flag:continue
        else:
            jsontext['reactions'].append({'id':ER[0],'metabolites':metabolites,'lower_bound':0.0,'upper_bound':999999.0,'ecnum':ecnum,'reaction_class':reaction_class,'energy':energy})
            reaction_nums+=1
            energy_mean_mean+=energy['mean']
            if energy['mean']>energy_mean_max:energy_mean_max=energy['mean']
            if energy['mean']<energy_mean_min:energy_mean_min=energy['mean']
            for key in metabolites.keys():
                metabolic_frequency[key]+=1

            
    #STAT data的录入
    jsontext['STAT']['energy_mean_mean'] = energy_mean_mean/reaction_nums
    jsontext['STAT']['energy_mean_min'] = energy_mean_min
    jsontext['STAT']['energy_mean_max'] = energy_mean_max
    jsontext['STAT']['metabolic_nums'] = metabolic_nums
    jsontext['STAT']['reaction_nums'] = reaction_nums
    jsontext['STAT']['mass_mean'] = mass_mean/metabolic_nums
    jsontext['STAT']['mass_max'] = mass_max
    jsontext['STAT']['mass_min'] = mass_min
    jsontext['STAT']['metabolic_frequency'] = metabolic_frequency

    jsondata = json.dumps(jsontext,indent=4,separators=(',', ': '))
    write_object = open('statics/complex_data.json','w')
    write_object.write(jsondata)
    write_object.close()
    return True
    
def get_Enzyme(reaction_list):
    '''
    '''
    Reac_Indi_list = []
    Reac_enzyme_list = []
    for reaction in reaction_list:
        try:enzyme_info = models.Reaction.objects.get(rid=reaction).ecnum.strip().split('\t')
        except:enzyme_info = []
        T,PH,KM,KKM = np.nan,np.nan,np.nan,np.nan
        try:
            Toxicity = float(models.Reaction.objects.get(rid=reaction).frequency)
        except:Toxicity = -999
        Indi_res = [KM,KKM,Toxicity,PH,T]
        en_res = ''
        for enzyme in enzyme_info:
            try:
                EvaIndi = models.Enzyme.objects.filter(ecnum=enzyme)
                en_res = enzyme
            except:
                #spec_ecnum.append(enzyme)
                EvaIndi = []
                en_res = ''
            for e in EvaIndi:

                T_list = e.t.strip().split('#')
                for t in T_list:
                    try:T = float(t.strip().split('{')[0].strip().split('-')[0])
                    except:continue
                    if T != -999 or T != 999 or KKM != np.nan:break
                
                PH_list = e.ph.strip().split('#')
                for p in PH_list:
                    try:PH = float(p.strip().split('{')[0].strip().split('-')[0])
                    except:continue
                    if PH != -999 or PH != 999 or KKM != np.nan:break
                
                KM_list = e.km.strip().split('#')
                for k in KM_list:
                    try:KM = float(k.strip().split('{')[0].strip().split('-')[0])
                    except:continue
                    if KM != -999 or KM != 999 or KKM != np.nan:break
                
                KKM_list = e.kkm.strip().split('#')
                for k in KKM_list:
                    try:KKM = float(k.strip().split('{')[0].strip().split('-')[0])
                    except:continue
                    if KKM != -999 or KKM != 999 or KKM != np.nan:break
                Indi = [KM,KKM,Toxicity,PH,T]
                if Indi.count(np.nan)<Indi_res.count(np.nan):
                    Indi_res = Indi.copy()
                    en_res = enzyme
                    #print(Indi_res)
                
        Reac_Indi_list.append(Indi_res)
        Reac_enzyme_list.append(en_res)
    for i,value_list in enumerate(zip(*Reac_Indi_list)):
        if value_list.count(np.nan)==len(value_list):
            if i == 0:Reac_Indi_list[0][i]=9.5
            elif i == 1:Reac_Indi_list[0][i]=1660599
            elif i == 2:Reac_Indi_list[0][i]=-999
            elif i == 3:Reac_Indi_list[0][i]=7.0
            else:Reac_Indi_list[0][i]=37.0
        else:
            pass
    return Reac_Indi_list,Reac_enzyme_list
            




def insert_all_data(request):
    '''
    数据输入
    '''
    info = SqLiteConnect.select('REACTION')
    for value in info:
        test1 = models.Reaction(rid=value[0],ecnum=value[2],equation=value[1],reactionclass=value[3],energy=value[4],frequency=value[5])
        test1.save()
    info = SqLiteConnect.select('COMPOUND')
    for value in info:
        test1 = models.Compound(cid=value[0],name=value[1],formula=value[2],smile=value[3],toxicity=value[4],weight=value[5],sdf=value[6])
        test1.save()
    info = SqLiteConnect.select('ENZYME')
    for value in info:
        test1 = models.Enzyme(pid=value[0],name=value[2],ecnum=value[1],organism=value[3],localization=value[4],ph=value[5],phr=value[6],t=value[7],tr=value[8],km=value[9],kkm=value[10],fromprediction=value[11],plabel=value[12],sequence=value[12])
        test1.save()
    
    return HttpResponse("<p>数据添加成功！</p>")


def update_data():
    '''
    '''
    return 0

def delete_data():
    '''
    '''
    return 0


if __name__ == '__main__':
    print('RUN!')
    matrix2json([],[])
    print('END!')





