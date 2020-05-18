import pickle
import json


def writeMod(fname,sp,m):
    f = open(fname,'w')

    for i in range(len(reac_num_list)):
        f.write('var r{} >={} <={} ;\n'.format(reac_num_list[i][0],reac_lb[i][1],reac_ub[i][1]))

    s='{} z: {} ;\n'.format(m,sp)
    f.write(s)

    f.write('s.t. con: rBIOMASS_Ec_iAF1260_core_59p81M >= {};\n'.format(yita*sol))
    for name in metabolites_list:
        n = []
        k = []
        tmp = ''
        for item in reac_num_list:
            if name in item[1]:
                k.append(item[1][name])
                n.append(item[0])
        tmp = ' + '.join(['('+str(k[i])+')*r'+n[i] for i in range(len(k))])
#     print(tmp)
        f.write('s.t. {}: {} = 0;\n'.format('v'+name,tmp))
    f.close()
    return 0;

# writeMod('../MOD/LP.mod','rATPM')

if __name__=="__main__":
    with open("../DATA/iAF1260.json",'r') as load_f:
    net_dict = json.load(load_f)
    metabolites_list = [net_dict['metabolites'][i]['id'] for i in range(len(net_dict['metabolites']))]
    reac_num_list = [(net_dict['reactions'][i]['id'],net_dict['reactions'][i]['metabolites']) for i in range(len(net_dict['reactions']))]
    reac_lb = [(net_dict['reactions'][i]['id'],net_dict['reactions'][i]['lower_bound']) for i in range(len(net_dict['reactions']))]
    reac_ub = [(net_dict['reactions'][i]['id'],net_dict['reactions'][i]['upper_bound']) for i in range(len(net_dict['reactions']))]
    yita = 0.9
    sol = 0.7367
    pool = Pool(processes = 56)

    for i in range(len(reac_num_list)):
        pool.apply_async(writeMod, args=('../MOD/LP_{}_maximize.mod'.format(n),'r'+n,'maximize', ))
        pool.apply_async(writeMod, args=('../MOD/LP_{}_minimize.mod'.format(n),'r'+n,'minimize', ))   
    print('======  apply_async  ======')
    pool.close()
    pool.join()
    print("Done!")