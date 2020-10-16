import sqlite3
import sys
import os
import getopt


def main():
    DatabaseName = 'ENZYME'
    data = select(DatabaseName)
    km_sum,kkm_sum,i,j = 0,0,0,0 
    for info in data:
        for km in info[9].strip().split('#'):
            try:
                km_sum += float(km.strip().split('{')[0].strip().split('-')[0])
                i+=1
            except:pass
        for kkm in info[10].strip().split('#'):
            try:
                kkm_sum += float(kkm.strip().split('{')[0].strip().split('-')[0])
                j+=1
            except:pass
    print(km_sum/i,kkm_sum/j)
    print(i,j)

    

def select(DatabaseName):
    conn = sqlite3.connect('statics/data_download/SyntheticBay.db')
    cur = conn.cursor()
    select_string = '''SELECT * FROM '''+DatabaseName+''';'''
    try:
        cur.execute(select_string)
        data  = cur.fetchall() 
    except:
        data = ()
        print("select is failed")

    conn.commit()
    conn.close()
    return data


# 记录新的中药信息
def InsertEnzyme(PID, ECnum, name, Organism, localization, pH, PHR, T, TR, KM, KKM, Sequence):
    fromprediction = '0'
    plabel = '1.0'
    conn = sqlite3.connect('SyntheticBay.db')
    cur = conn.cursor()
    insert_string = "INSERT INTO ENZYME (PID, ECnum, name, Organism, Localization, pH, PHR, T, TR, KM, KKM, FromPrediction , PLabel, Sequence) VALUES ('" + \
        PID + "','"+ ECnum + "','" + name + "','" + Organism + "','" + localization + "','" + \
        pH + "','" + PHR + "','" + T + "','" + TR + "','" + KM + "','" + KKM + "'," + fromprediction + "," + plabel + ",'" + Sequence +"');"
    try:
        cur.execute(insert_string) # 执行sql语句
        conn.commit()  # 提交到数据库执行
    except:
        conn.rollback()
    conn.close()
    
def InsertCompounts(CID,Name,Formula,Smile,Toxicity,Weight,SDF):
    '''
    '''
    conn = sqlite3.connect('SyntheticBay.db')
    cur = conn.cursor()
    insert_string = "INSERT INTO igem.enzyme(CID,Name,Formula,Smile,Toxicity,Weight,SDF)VALUES ('" + \
        CID + "','"+ Name + "','" + Formula + "','" + Smile + "'," + \
        Toxicity + "," + Weight + ",'" + SDF  +"');"
    try:
        cur.execute(insert_string) # 执行sql语句
        conn.commit()  # 提交到数据库执行
    except:
        conn.rollback()
    conn.close()

def InsertReaction(RID,Equation,ECnum,ReactionClass,Energy,Frequency):
    '''
    '''
    conn = sqlite3.connect('SyntheticBay.db')
    cur = conn.cursor()
    insert_string = "RID,Equation,ECnum,ReactionClass,Energy,Frequency)VALUES ('" + \
        RID + "','"+ Equation + "','" + ECnum + "','" + ReactionClass + "','" + \
        Energy + "'," + Frequency +");"
    try:
        cur.execute(insert_string) # 执行sql语句
        conn.commit()  # 提交到数据库执行
    except:
        conn.rollback()
    conn.close()

if __name__=='__main__':
    print('run!')
    main()












