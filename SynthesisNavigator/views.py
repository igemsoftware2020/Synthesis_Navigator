from django.http import HttpResponse,StreamingHttpResponse
from django.contrib import messages
from django.shortcuts import render,redirect
from SynthesisNavigator.DM import get_data,get_Enzyme,matrix2json
from SynthesisNavigator.functions import RandomWalkMetaSim,PathwaySearch,Score
from SynthesisNavigator import SqLiteConnect
from AppModel import models
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer,Image,Table,TableStyle,Frame,ListFlowable, ListItem
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib import colors
from reportlab.lib.colors import CMYKColor
import time,datetime
import json

def Home(request):
    '''
    '''
    return render(request, 'index.html')

def DataBase(request):
    '''
    '''
    return render(request, 'aboutdatabase.html')

def DBS(request):
    '''
    '''
    
    info = SqLiteConnect.select('COMPOUND')
    with open('statics/data_download/Compound.csv','w') as write_object:
        write_object.write('cid,name,formula,smile,toxicity,weight,sdf\n')
        for value in info:
            write_object.write('{},{},{},{},{},{},{}\n'.format(value[0],value[1],value[2],value[3],value[4],value[5],value[6]))
    info = SqLiteConnect.select('REACTION')
    with open('statics/data_download/Reaction.csv','w') as write_object:
        write_object.write('rid,ecnum,equation,reactionclass,energy,frequency\n')
        for value in info:
            write_object.write('{},{},{},{},{},{}\n'.format(value[0],value[2],value[1],value[3],value[4],value[5]))
    info = SqLiteConnect.select('ENZYME')
    with open('statics/data_download/Enzyme.csv','w') as write_object:
        write_object.write('pid,name,ecnum,organism,localization,ph,phr,t,tr,km,kkm,sequence\n')
        for value in info:
            write_object.write('{},{},{},{},{},{},{},{},{},{},{},{}\n'.format(value[0],value[2],value[1],value[3],value[4],value[5],value[6],value[7],value[8],value[9],value[10],value[13]))
    
    return render(request,'download.html',{'file1':'Compound.csv','file2':'Reaction.csv','file3':'Enzyme.csv','file4':'SyntheticBay.db'})

def HMS(request):
    '''
    '''
    #参数默认值
    """
    test1 = models.Compound(cid='C18847',name='Mycinamicin V',formula='C37H61NO12',smile='',toxicity='',weight='711.4194',sdf='')
    test1.save()
    test1 = models.Compound(cid='C21462',name='Kdo2-lipid A 4-(2-aminoethyl diphosphate)',formula='C112H208N3O42P3',smile='',toxicity='',weight='2360.3445',sdf='')
    test1.save()
    """
    observation_list = []
    reaction_deficient = []
    default_value,epoches,thread = 100,100,8
    specified_value = {}
    '''
    设定初始状态
    '''
    with open('statics/initial_state.txt') as read_objects:
        for line in read_objects:
            specified_value[line.strip().split(',')[0]] = int(line.strip().split(',')[1])
    #读取网页表单
    request.encoding = 'utf-8'
    if request.method == 'GET' and request.GET:
        if 'observation_list' in request.GET and request.GET['observation_list']:
            observation_list = request.GET['observation_list'].strip().split(';')
            #print(observation_list)
            while '' in observation_list:
                observation_list.remove('')
        else:observation_list = []
        if 'reaction_deficient' in request.GET and request.GET['reaction_deficient']:
            reaction_deficient = request.GET['reaction_deficient'].strip().split(';')
            while '' in reaction_deficient:
                reaction_deficient.remove('')
        else:reaction_deficient = []
        if 'default_value' in request.GET and request.GET['default_value']:
            try:
                default_value = int(request.GET['default_value'].strip())
                if default_value<0: 
                    messages.warning(request,'please input the number >= 0!')
                    specified_value_text = ''
                    for key,value in specified_value.items():
                        specified_value_text+='{}:{},'.format(key,value)
                    info = {'observation_list':';'.join(observation_list),'reaction_deficient':';'.join(reaction_deficient),'default_value':default_value,'default_epoches':epoches,'specified_value':specified_value_text,}
                    return  render(request,'abouthms.html',info)
            except:
                default_value = 100
                messages.warning(request,'please input use number with type int!')
                specified_value_text = ''
                for key,value in specified_value.items():
                    specified_value_text+='{}:{},'.format(key,value)
                info = {'observation_list':';'.join(observation_list),'reaction_deficient':';'.join(reaction_deficient),'default_value':default_value,'default_epoches':epoches,'specified_value':specified_value_text,}
                return  render(request,'abouthms.html',info)
        else:default_value = 100
        if 'default_epoches' in request.GET and request.GET['default_epoches']:
            try:
                epoches = int(request.GET['default_epoches'].strip())
                if epoches>500000:
                    epoches = 50000
                elif epoches<=0:
                    epoches = 5000
            except:
                epoches = 500
                messages.warning(request,'please input use number with type int!')
                specified_value_text = ''
                for key,value in specified_value.items():
                    specified_value_text+='{}:{},'.format(key,value)
                info = {'observation_list':';'.join(observation_list),'reaction_deficient':';'.join(reaction_deficient),'default_value':default_value,'default_epoches':epoches,'specified_value':specified_value_text,}
                return  render(request,'abouthms.html',info)
        else:epoches = 500
        if 'specified_value' in request.GET and request.GET['specified_value']:
            specified_value_info = request.GET['specified_value'].strip().split(',')
            for C_V in specified_value_info:
                if C_V == '':continue
                comp = C_V.strip().split(':')[0].strip()
                try:
                    comp_num = int(C_V.strip().split(':')[1].strip())
                    if comp_num<0: 
                        messages.warning(request,'please input the number >= 0!')
                        specified_value_text = ''
                        for key,value in specified_value.items():
                            specified_value_text+='{}:{},'.format(key,value)
                        info = {'observation_list':';'.join(observation_list),'reaction_deficient':';'.join(reaction_deficient),'default_value':default_value,'default_epoches':epoches,'specified_value':specified_value_text,}
                        return  render(request,'abouthms.html',info)
                    specified_value[comp] = comp_num
                except:
                    specified_value[comp] = 100
                    messages.warning(request,'please input use number with type int!')
                    specified_value_text = ''
                    for key,value in specified_value.items():
                        specified_value_text+='{}:{},'.format(key,value)
                    info = {'observation_list':';'.join(observation_list),'reaction_deficient':';'.join(reaction_deficient),'default_value':default_value,'default_epoches':epoches,'specified_value':specified_value_text,}
                    return  render(request,'abouthms.html',info)
        else:specified_value_value = {}
    #debug
    
    #print(observation_list)
    for compound in observation_list:
        try:a = models.Compound.objects.get(cid=compound)
        except:
            messages.error(request,'Sorry but Not Found the compound '+compound+' ! please input like C00051!')
            specified_value_text = ''
            for key,value in specified_value.items():
                specified_value_text+='{}:{},'.format(key,value)
            info = {'observation_list':';'.join(observation_list),'reaction_deficient':';'.join(reaction_deficient),'default_value':default_value,'default_epoches':epoches,'specified_value':specified_value_text,}
            return  render(request,'abouthms.html',info)
    #print(reaction_deficient)
    for reaction in reaction_deficient:
        try:a = models.Reaction.objects.get(rid=reaction)
        except:
            messages.error(request,'Sorry but Not Found the reaction '+reaction+' ! please input like R00112!')
            specified_value_text = ''
            for key,value in specified_value.items():
                specified_value_text+='{}:{},'.format(key,value)
            info = {'observation_list':';'.join(observation_list),'reaction_deficient':';'.join(reaction_deficient),'default_value':default_value,'default_epoches':epoches,'specified_value':specified_value_text,}
            return  render(request,'abouthms.html',info)
    #print(specified_value)


    for key,value in specified_value.items():
        try:a = models.Compound.objects.get(cid=key)
        except:
            messages.error(request,'Sorry but Not Found the compound '+key+' ! please input like C00051!')
            specified_value_text = ''
            for key,value in specified_value.items():
                specified_value_text+='{}:{},'.format(key,value)
            info = {'observation_list':';'.join(observation_list),'reaction_deficient':';'.join(reaction_deficient),'default_value':default_value,'default_epoches':epoches,'specified_value':specified_value_text,}
            return  render(request,'abouthms.html',info)
    
    #格式预加载
    matrix2json(reaction_deficient,[])
    json_txt=''
    with open("statics/complex_data.json",'r') as load_f:
        json_txt=load_f.read()
    
    #PDF格式设置
    story=[]
    pdfmetrics.registerFont(TTFont('msyh', 'statics/msyh.ttf'))### 设置中文字体名称为msyh
    styles = getSampleStyleSheet()#获得reportlab预先设定的文本模板
    styles.add(ParagraphStyle(name='mytitle', leftIndent=-50,rightIndent=-50,alignment=TA_JUSTIFY,fontName="msyh",fontSize=24,textColor='#003153',bulletFontSize=12,
            bulletIndent=-50,bulletAnchor ='start',bulletFontName = 'Symbol' ))
    styles.add(ParagraphStyle(name='txt', leftIndent=-50,rightIndent=-50,alignment=TA_JUSTIFY,fontName="msyh",fontSize=12,textColor='#003153',bulletFontSize=12,
            bulletIndent=-50,bulletAnchor ='start',bulletFontName = 'Symbol' ))   
    styles.add(ParagraphStyle(name='importan_txt', leftIndent=-50,rightIndent=-50,alignment=TA_JUSTIFY,fontName="msyh",fontSize=14,textColor='#FF0000 ',bulletFontSize=12,
            bulletIndent=-50,bulletAnchor ='start',bulletFontName = 'Symbol' )) 
    styles.add(ParagraphStyle(name='annotation_txt', leftIndent=-50,rightIndent=-50,alignment=TA_JUSTIFY,fontName="msyh",fontSize=8,textColor='#003153',bulletFontSize=12,
            bulletIndent=-50,bulletAnchor ='start',bulletFontName = 'Symbol' ))     
            
    text = '''<para><br/>RandomWalking</para>'''
    story.append(Paragraph(text,styles["title"]))
    story.append(Spacer(240, 10))
    text = 'Summary:'
    story.append(Paragraph(text,styles["mytitle"]))
    story.append(Spacer(240, 20))
    text = 'observation compound(the compound you want to observe, which is label with color red!): \n' + ','.join(observation_list)
    story.append(Paragraph(text,styles["txt"]))
    story.append(Spacer(240, 2))
    text = 'reaction deficient: ' + ','.join(reaction_deficient)
    story.append(Paragraph(text,styles["txt"]))
    story.append(Spacer(240, 2))
    text = 'default_value: {},\tepoches: {},\tthread: {}'.format(default_value,epoches,thread)
    story.append(Paragraph(text,styles["txt"]))
    story.append(Spacer(240, 2))
    text = 'specified_value(the compound you altered, which is label with color red!):'
    story.append(Paragraph(text,styles["txt"]))
    story.append(Spacer(240, 2))
    text = ''
    for key,value in specified_value.items():
        #print(key)
        text += '\t{}: {},\t'.format(key,value)
    story.append(Paragraph(text,styles["txt"]))


    story.append(Spacer(240, 10))
    text = 'Results(TOP100):'
    story.append(Paragraph(text,styles["mytitle"]))
    story.append(Spacer(240, 20))
    #随机游走代谢模拟测试
    
    Walk=RandomWalkMetaSim(json_txt)
    #print(Walk.metabolites)
    confg={'default_value':default_value,'specified_value':specified_value,'epoches':epoches}
    conf_json_txt=json.dumps(confg)
    #print(Walk.runSim(conf_json_txt))
    #RunSim_res = Walk.runSimMultiThread(conf_json_txt,thread)
    #RunSim_res = Walk.runSim_neg(conf_json_txt)
    RunSim_res = Walk.runSim(conf_json_txt)
    for key in observation_list:
        if key in specified_value.keys():
            delta = RunSim_res[key]-specified_value[key]
            nor_delta = round(delta/(specified_value[key]+0.0000001),5)
        else:
            delta = RunSim_res[key]-default_value
            nor_delta = round(delta/(default_value+0.0000001),5)
        if key=='C22133':key='C21097'
        text = key+':\t'+models.Compound.objects.get(cid=key).name+',\t'+str(RunSim_res[key])+',\tdelta:'+str(delta)+',\tnormalize_delta:'+str(nor_delta)
        story.append(Paragraph(text,styles["importan_txt"]))
        story.append(Spacer(240, 4))
    
    story.append(Spacer(240, 8))

    for key,value in RunSim_res.items():
        if key=='C22133':key='C21097'
        if key in specified_value.keys():
            delta = value-specified_value[key]
            nor_delta = abs(round(delta/(specified_value[key]+0.0000001),5))
            RunSim_res[key]=(value,delta,nor_delta)
        else:
            delta = value-default_value
            nor_delta = abs(round(delta/(default_value+0.0000001),5))
            RunSim_res[key]=(value,delta,nor_delta)
    time_text = str(datetime.date.today()).replace('-','_') +'_'+ str(time.time()).replace('.','')[8:-1]
    with open('statics/data_download/randomwalk_res_'+time_text+'.csv','w') as write_object:
        write_object.write('compound,start_value,end_value,delta,normalize_delta\n')
        for key,value in RunSim_res.items():
            if key in specified_value.keys():
                write_object.write('{},{},{},{},{}\n'.format(key,specified_value[key],value[0],value[1],value[2]))
            else:
                write_object.write('{},{},{},{},{}\n'.format(key,default_value,value[0],value[1],value[2]))
    RunSim_res_list = []
    for key,value in RunSim_res.items():
        if value[1]!=0:RunSim_res_list.append([key,value])
    #print(RunSim_res_list[0:2])
    RunSim_res_list = sorted(RunSim_res_list, key = lambda x:x[1][2], reverse=True)
    #print(RunSim_res_list[0:2])
    i = 0
    for value in RunSim_res_list:
        if i>=100:break
        i +=1
        key,end,delta,nor_delta = value[0],value[1][0],value[1][1],value[1][2]
        try:text = key+':\t'+models.Compound.objects.get(cid=key).name+',\t'+str(end)+',\tdelta:'+str(delta)+',\tnormalize_delta:'+str(nor_delta)
        except:print(key)
        if key in specified_value.keys():
            story.append(Paragraph(text,styles["importan_txt"]))
        else:
            story.append(Paragraph(text,styles["txt"]))
        story.append(Spacer(240, 6))
    story.append(Spacer(240, 20))
    text = 'Annotation:'
    story.append(Paragraph(text,styles["mytitle"]))
    story.append(Spacer(240, 20))
    text = '''  we output the compound you want to observe, and the top100 compound which altered and ordered by alter number(delta).
        the output features are compound id, compound name, the Final state value, altered value and normalized altered value from left to right.
        if you want to get all results, please download the .csv file!'''
    story.append(Paragraph(text,styles["annotation_txt"]))
    doc = SimpleDocTemplate('statics/data_download/randomwalk_res_'+time_text+'.pdf',topMargin = 15,bottomMargin = 15)
    doc.build(story)
    return render(request,'download.html',{'file1':'randomwalk_res_'+time_text+'.pdf','file2':'randomwalk_res_'+time_text+'.csv','file3':'','file4':''})


def HybridMetabolicSimulation(request):
    '''
    '''
    return render(request, 'abouthms.html')
    
def PF(request):
    '''
    通路搜索
    '''
    Controllable_Indi = [0.2,0.2,0.2,0.2,0.2]
    start_C,end_C = '',''
    request.encoding = 'utf-8'
    if request.method == 'GET' and request.GET:
        if 'start' in request.GET and request.GET['start']:
            start_C = request.GET['start'].strip()
        else:pass
        if 'end' in request.GET and request.GET['end']:
            end_C = request.GET['end'].strip()
        else:pass
        if 'km' in request.GET and request.GET['km']:
            try:Controllable_Indi[0]=abs(float(request.GET['km'].strip()))
            except:
                Controllable_Indi[0] = 0.2
                messages.error(request,'please input use number with type float!')
                info = {'start':start_C,'end':end_C,'km':Controllable_Indi[0],'kkm':Controllable_Indi[1],'toxi':Controllable_Indi[2],'PH':Controllable_Indi[3],'tem':Controllable_Indi[4],}
                return render(request,'aboutpf.html',info)
        else:pass
        if 'kkm' in request.GET and request.GET['kkm']:
            try:Controllable_Indi[1]=abs(float(request.GET['kkm'].strip()))
            except:
                Controllable_Indi[1] = 0.2
                messages.error(request,'please input use number with type float!')
                info = {'start':start_C,'end':end_C,'km':Controllable_Indi[0],'kkm':Controllable_Indi[1],'toxi':Controllable_Indi[2],'PH':Controllable_Indi[3],'tem':Controllable_Indi[4],}
                return render(request,'aboutpf.html',info)
        else:pass
        if 'toxi' in request.GET and request.GET['toxi']:
            try:Controllable_Indi[2]=abs(float(request.GET['toxi'].strip()))
            except:
                Controllable_Indi[2] = 0.2
                messages.error(request,'please input use number with type float!')
                info = {'start':start_C,'end':end_C,'km':Controllable_Indi[0],'kkm':Controllable_Indi[1],'toxi':Controllable_Indi[2],'PH':Controllable_Indi[3],'tem':Controllable_Indi[4],}
                return render(request,'aboutpf.html',info)
        else:pass
        if 'PH' in request.GET and request.GET['PH']:
            try:Controllable_Indi[3]=abs(float(request.GET['PH'].strip()))
            except:
                Controllable_Indi[3] = 0.2
                messages.error(request,'please input use number with type float!')
                info = {'start':start_C,'end':end_C,'km':Controllable_Indi[0],'kkm':Controllable_Indi[1],'toxi':Controllable_Indi[2],'PH':Controllable_Indi[3],'tem':Controllable_Indi[4],}
                return render(request,'aboutpf.html',info)
        else:pass
        if 'tem' in request.GET and request.GET['tem']:
            try:Controllable_Indi[4]=abs(float(request.GET['tem'].strip()))
            except:
                Controllable_Indi[4] = 0.2
                messages.error(request,'please input use number with type float!')
                info = {'start':start_C,'end':end_C,'km':Controllable_Indi[0],'kkm':Controllable_Indi[1],'toxi':Controllable_Indi[2],'PH':Controllable_Indi[3],'tem':Controllable_Indi[4],}
                return render(request,'aboutpf.html',info)
        else:pass
        

     #格式预加载
    compound_deficient = ['C00001','C00007','C00011','C00009','C00014','C00009','C00013','C00023','C00027','C00030','C00038','C00087'\
        ,'C00080','C00132','C00003','C00004','C00005','C00006','C00002','C00008']
    if start_C in compound_deficient:
        compound_deficient.remove(start_C)
    if end_C in compound_deficient:
        compound_deficient.remove(end_C)
    matrix2json([],compound_deficient=compound_deficient)
    json_txt=''
    with open("statics/complex_data.json",'r') as load_f:
        json_txt=load_f.read()

    reaction_list = []
    pathway_reaction = []
    story=[]
    pdfmetrics.registerFont(TTFont('msyh', 'statics/msyh.ttf'))### 设置中文字体名称为msyh
    styles = getSampleStyleSheet()#获得reportlab预先设定的文本模板
    styles.add(ParagraphStyle(name='mytitle', leftIndent=-50,rightIndent=-50,alignment=TA_JUSTIFY,fontName="msyh",fontSize=24,textColor='#003153',bulletFontSize=12,
            bulletIndent=-50,bulletAnchor ='start',bulletFontName = 'Symbol' ))
    styles.add(ParagraphStyle(name='txt', leftIndent=-50,rightIndent=-50,alignment=TA_JUSTIFY,fontName="msyh",fontSize=12,textColor='#003153',bulletFontSize=12,
            bulletIndent=-50,bulletAnchor ='start',bulletFontName = 'Symbol' ))           
        
    text = '''<para><br/>PythwayFinder</para>'''
    story.append(Paragraph(text,styles["title"])) #将text添加到list中，并且风格为txt
    story.append(Spacer(240, 10))
    text = 'Summary:'
    story.append(Paragraph(text,styles["mytitle"]))
    story.append(Spacer(240, 20))
    text = 'start_compound: '+start_C
    story.append(Paragraph(text,styles["txt"]))
    story.append(Spacer(240, 2))
    text = 'end_compound: '+end_C
    story.append(Paragraph(text,styles["txt"]))
    story.append(Spacer(240, 2))
    text = 'km = {}; kkm = {}; Toxi = {}; PH = {}; temp = {};'.format(Controllable_Indi[0],Controllable_Indi[1],Controllable_Indi[2],Controllable_Indi[3],Controllable_Indi[4])
    story.append(Paragraph(text,styles["txt"]))
    story.append(Spacer(240, 10))
    text = 'Results:'
    story.append(Paragraph(text,styles["mytitle"]))
    story.append(Spacer(240, 20))

    #通路搜索
    Sear=PathwaySearch(json_txt)
    try:
        a = models.Compound.objects.get(cid=start_C)
    except:
        messages.error(request,'Sorry but Not Found the start compound '+start_C+' ! please input like C00051.')
        info = {'start':start_C,'end':end_C,'km':Controllable_Indi[0],'kkm':Controllable_Indi[1],'toxi':Controllable_Indi[2],'PH':Controllable_Indi[3],'tem':Controllable_Indi[4],}
        return render(request,'aboutpf.html',info)
    try:
        a = models.Compound.objects.get(cid=end_C)
    except:
        messages.error(request,'Sorry but Not Found the end compound '+end_C+' ! please input like C00051.')
        info = {'start':start_C,'end':end_C,'km':Controllable_Indi[0],'kkm':Controllable_Indi[1],'toxi':Controllable_Indi[2],'PH':Controllable_Indi[3],'tem':Controllable_Indi[4],}
        return render(request,'aboutpf.html',info)
    try:Sear_res = Sear.SimpleSaerch(start_C,end_C,pathway_nums=10)
    except:
        Sear_res = []
    if Sear_res == []:
        text = 'No pathway between these two compounds!'
        story.append(Paragraph(text,styles["txt"]))
        story.append(Spacer(240, 10))
        time_text = str(datetime.date.today()).replace('-','_') +'_'+ str(time.time()).replace('.','')[8:-1]
        doc = SimpleDocTemplate('statics/data_download/pathway_res_'+time_text+'.pdf',topMargin = 15,bottomMargin = 15)
        doc.build(story)
        return render(request,'download.html',{'file1':'pathway_res_'+time_text+'.pdf','file2':'','file3':'','file4':''})
    Sear_res = sorted(Sear_res, key = lambda x:x[1],reverse=False)
    #print(Sear_res)
    for pathway in Sear_res:
        for i in range(1,len(pathway[0]),2):
            reaction_list.append(pathway[0][i])  
    #print(reaction_list)
    Reac_Indi_list,Reac_enzyme_list = get_Enzyme(reaction_list)
    #print(Reac_Indi_list)
    if len(Reac_Indi_list) == 1:
        score = [1]
    else:
        score = Score(Reac_Indi_list,Controllable_Indi)
    i,L = 0,0
    
    for pathway in Sear_res:
        l = int(len(pathway[0])/2)
        scroe_average = 0
        enzyme_res = []
        while i<l+L:
            scroe_average += score[i]
            enzyme_res.append(Reac_enzyme_list[i])
            i+=1
        pathway_reaction.append([pathway[0],enzyme_res.copy(),[round(pathway[1],4),round(scroe_average/l,4)]])
        L += l
        text = ''
        for t,COR in enumerate(pathway[0]):
            if t%2==1:
                text =text + COR+', '+enzyme_res[t//2]+ ' ]——> '
            elif t%2==0 and t==len(pathway[0])-1:
                text =text + COR 
            else:
                text =text + COR + ' ——[ '
        story.append(Paragraph(text,styles["txt"]))
        story.append(Spacer(240, 2))
        text = 'EnergyScore: '+str(round(pathway[1],4))+'\tIndiScore: '+str(round(scroe_average/l,4))
        story.append(Paragraph(text,styles["txt"]))
        story.append(Spacer(240, 10))
    time_text = str(datetime.date.today()).replace('-','_') +'_'+ str(time.time()).replace('.','')[8:-1]
    doc = SimpleDocTemplate('statics/data_download/pathway_res_'+time_text+'.pdf',topMargin = 15,bottomMargin = 15)
    doc.build(story)
    return render(request,'download.html',{'file1':'pathway_res_'+time_text+'.pdf','file2':'','file3':'','file4':''})

def PFR(request):
    '''
    逆通路搜索
    '''
    Controllable_Indi = [0.2,0.2,0.2,0.2,0.2]
    end_C = ''
    control_nums = 4
    request.encoding = 'utf-8'
    if request.method == 'GET' and request.GET:
        if 'reverse' in request.GET and request.GET['reverse']:
            end_C = request.GET['reverse'].strip()
            start_C = ''
        else:pass
        if 'km' in request.GET and request.GET['km']:
            try:Controllable_Indi[0]=abs(float(request.GET['km'].strip()))
            except:
                Controllable_Indi[0] = 0.2
                messages.error(request,'please input use number with type float!')
                info = {'km':Controllable_Indi[0],'kkm':Controllable_Indi[1],'toxi':Controllable_Indi[2],'PH':Controllable_Indi[3],'tem':Controllable_Indi[4],'reverse':end_C,'steps':control_nums,}
                return render(request,'aboutpf.html',info)
        else:pass
        if 'kkm' in request.GET and request.GET['kkm']:
            try:Controllable_Indi[1]=abs(float(request.GET['kkm'].strip()))
            except:
                Controllable_Indi[1] = 0.2
                messages.error(request,'please input use number with type float!')
                info = {'km':Controllable_Indi[0],'kkm':Controllable_Indi[1],'toxi':Controllable_Indi[2],'PH':Controllable_Indi[3],'tem':Controllable_Indi[4],'reverse':end_C,'steps':control_nums,}
                return render(request,'aboutpf.html',info)
        else:pass
        if 'toxi' in request.GET and request.GET['toxi']:
            try:Controllable_Indi[2]=abs(float(request.GET['toxi'].strip()))
            except:
                Controllable_Indi[2] = 0.2
                messages.error(request,'please input use number with type float!')
                info = {'km':Controllable_Indi[0],'kkm':Controllable_Indi[1],'toxi':Controllable_Indi[2],'PH':Controllable_Indi[3],'tem':Controllable_Indi[4],'reverse':end_C,'steps':control_nums,}
                return render(request,'aboutpf.html',info)
        else:pass
        if 'PH' in request.GET and request.GET['PH']:
            try:Controllable_Indi[3]=abs(float(request.GET['PH'].strip()))
            except:
                Controllable_Indi[3] = 0.2
                messages.error(request,'please input use number with type float!')
                info = {'km':Controllable_Indi[0],'kkm':Controllable_Indi[1],'toxi':Controllable_Indi[2],'PH':Controllable_Indi[3],'tem':Controllable_Indi[4],'reverse':end_C,'steps':control_nums,}
                return render(request,'aboutpf.html',info)
        else:pass
        if 'tem' in request.GET and request.GET['tem']:
            try:Controllable_Indi[4]=abs(float(request.GET['tem'].strip()))
            except:
                Controllable_Indi[4] = 0.2
                messages.error(request,'please input use number with type float!')
                info = {'km':Controllable_Indi[0],'kkm':Controllable_Indi[1],'toxi':Controllable_Indi[2],'PH':Controllable_Indi[3],'tem':Controllable_Indi[4],'reverse':end_C,'steps':control_nums,}
                return render(request,'aboutpf.html',info)
        else:pass
        if 'steps' in request.GET and request.GET['steps']:
            try:
                control_nums = abs(int(request.GET['steps'].strip()))
                if control_nums>4:
                    control_nums=4
            except:
                control_nums = 4
                messages.error(request,'please input use number with type int!')
                info = {'km':Controllable_Indi[0],'kkm':Controllable_Indi[1],'toxi':Controllable_Indi[2],'PH':Controllable_Indi[3],'tem':Controllable_Indi[4],'reverse':end_C,'steps':control_nums,}
                return render(request,'aboutpf.html',info)
        else:pass
     #格式预加载
    compound_deficient = ['C00001','C00007','C00011','C00009','C00014','C00009','C00013','C00023','C00027','C00030','C00038','C00087'\
        ,'C00080','C00132','C00003','C00004','C00005','C00006','C00002','C00008']
    if end_C in compound_deficient:
        compound_deficient.remove(end_C)
    matrix2json([],compound_deficient=compound_deficient)
    json_txt=''
    with open("statics/complex_data.json",'r') as load_f:
        json_txt=load_f.read()

    reaction_list = []
    pathway_reaction = []
    story=[]
    pdfmetrics.registerFont(TTFont('msyh', 'statics/msyh.ttf'))### 设置中文字体名称为msyh
    styles = getSampleStyleSheet()#获得reportlab预先设定的文本模板
    styles.add(ParagraphStyle(name='mytitle', leftIndent=-50,rightIndent=-50,alignment=TA_JUSTIFY,fontName="msyh",fontSize=24,textColor='#003153',bulletFontSize=12,
            bulletIndent=-50,bulletAnchor ='start',bulletFontName = 'Symbol' ))
    styles.add(ParagraphStyle(name='txt', leftIndent=-50,rightIndent=-50,alignment=TA_JUSTIFY,fontName="msyh",fontSize=12,textColor='#003153',bulletFontSize=12,
            bulletIndent=-50,bulletAnchor ='start',bulletFontName = 'Symbol' )) 
        
    text = '''<para><br/>PythwayFinder</para>'''
    story.append(Paragraph(text,styles["title"])) #将text添加到list中，并且风格为txt
    story.append(Spacer(240, 10))
    text = 'Summary:'
    story.append(Paragraph(text,styles["mytitle"]))
    story.append(Spacer(240, 20))
    text = 'end_compound: '+end_C
    story.append(Paragraph(text,styles["txt"]))
    story.append(Spacer(240, 2))
    text = 'km = {}; kkm = {}; Toxi = {}; PH = {}; temp = {};'.format(Controllable_Indi[0],Controllable_Indi[1],Controllable_Indi[2],Controllable_Indi[3],Controllable_Indi[4])
    story.append(Paragraph(text,styles["txt"]))
    story.append(Spacer(240, 2))
    text = 'steps = '+str(control_nums)
    story.append(Paragraph(text,styles["txt"]))
    story.append(Spacer(240, 10))
    text = 'Results:'
    story.append(Paragraph(text,styles["mytitle"]))
    story.append(Spacer(240, 20))

    #通路搜索
    Sear=PathwaySearch(json_txt)
    try:
        a = models.Compound.objects.get(cid=end_C)
    except:
        messages.error(request,'Sorry but Not Found the compound '+end_C+' ! please input like C00051.')
        info = {'km':Controllable_Indi[0],'kkm':Controllable_Indi[1],'toxi':Controllable_Indi[2],'PH':Controllable_Indi[3],'tem':Controllable_Indi[4],'reverse':end_C,'steps':control_nums,}
        return render(request,'aboutpf.html',info)
    try:Sear_res = Sear.ReverseSaerch(end_C,nums=control_nums)
    except:Sear_res = []
    if Sear_res == []:
        text = 'No pathway between these two compounds!'
        story.append(Paragraph(text,styles["txt"]))
        story.append(Spacer(240, 10))
        time_text = str(datetime.date.today()).replace('-','_') +'_'+ str(time.time()).replace('.','')[8:-1]
        doc = SimpleDocTemplate('statics/data_download/pathway_res_'+time_text+'.pdf',topMargin = 15,bottomMargin = 15)
        doc.build(story)
        return render(request,'download.html',{'file1':'pathway_res_'+time_text+'.pdf','file2':'','file3':'','file4':''})

    for s in Sear_res:
        if len(s[1])==1:Sear_res.remove(s)
    #print(Sear_res)
    for pathway in Sear_res:
        for i in range(1,len(pathway[1]),2):
            reaction_list.append(pathway[1][i])
    Reac_Indi_list,Reac_enzyme_list = get_Enzyme(reaction_list)
    #print(Reac_Indi_list)
    if len(Reac_Indi_list) == 1:
        score = [1]
    else:
        score = Score(Reac_Indi_list,Controllable_Indi)
    #print(score)
    i,L = 0,0
    
    for pathway in Sear_res:
        l = int(len(pathway[1])/2)
        scroe_average = 0
        enzyme_res = []
        while i<l+L:
            scroe_average += score[i]
            enzyme_res.append(Reac_enzyme_list[i])
            i+=1
        pathway_reaction.append([pathway[0],pathway[1],enzyme_res.copy(),round(scroe_average/l,4)])
        L += l
        text = 'start_Compound:'+pathway[0]+' || '
        story.append(Paragraph(text,styles["txt"]))
        story.append(Spacer(240, 2))
        text = ''
        for t,COR in enumerate(pathway[1]):
            if t%2==1:
                text =text + COR+', '+enzyme_res[t//2]+ ' ]——> '
            elif t%2==0 and t==len(pathway[1])-1:
                text =text + COR 
            else:
                text =text + COR + ' ——[ '
        story.append(Paragraph(text,styles["txt"]))
        story.append(Spacer(240, 2))
        text = 'EnergyScore: no!'+'\tIndiScore: '+str(round(scroe_average/l,4))
        story.append(Paragraph(text,styles["txt"]))
        story.append(Spacer(240, 10))
    time_text = str(datetime.date.today()).replace('-','_') +'_'+ str(time.time()).replace('.','')[8:-1]
    doc = SimpleDocTemplate('statics/data_download/pathway_res_'+time_text+'.pdf',topMargin = 15,bottomMargin = 15)
    doc.build(story)
    return render(request,'download.html',{'file1':'pathway_res_'+time_text+'.pdf','file2':'','file3':'','file4':''})


def PathwayFinding(request):
    '''
    '''
    return render(request, 'aboutpf.html')


def file_down(request,path):  #文本下载
    import os
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    request.encoding = 'utf-8'
    name = path
    filename = os.path.join(BASE_DIR,'statics/data_download/'+path) # 要下载的文件路径
    # do something
    the_file_name = name
    if not os.path.isfile(filename):  # 判断下载文件是否存在
        return HttpResponse("Sorry but Not Found the File!")
    response = StreamingHttpResponse(readFile(filename))
    response['Content-Type'] = 'application/octet-stream'  #表明他是一个字节流
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(the_file_name) #默认文件名 不过好像加不加都没什么关系
    return response
#return HttpResponse("Sorry but Not Found the File")

def readFile(filename, chunk_size=512):
    with open(filename, 'rb') as f:
        while True:
            c = f.read(chunk_size)
            if c:
                yield c
            else:
                break

