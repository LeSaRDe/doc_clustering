import math

def get_val(ele):
    return ele[0]

def weighted_overlap(v1, v2):
    v_idx = [x for x in range(1, 4)]
    v1_z = list(zip(v1, v_idx))
    v2_z = list(zip(v2, v_idx))
    print v1_z
    print v2_z
    v1_z.sort(key=get_val)
    v2_z.sort(key=get_val)
    print v_idx
    print v1_z
    print v2_z
    v1_r = []
    v2_r = []
    for dim_i in range(1, 4):
        v1_r_i = [id_v1_x for id_v1_x, v1_x in enumerate(v1_z) if v1_x[1] == dim_i]
        v1_r.append(v1_r_i[0]+1)
        v2_r_i = [id_v2_x for id_v2_x, v2_x in enumerate(v2_z) if v2_x[1] == dim_i]
        v2_r.append(v2_r_i[0]+1)
    print v1_r
    print v2_r
    wo_pairs = []
    for i in range(3):
        wo_pairs.append((v1_r[i], v2_r[i]))
    #print wo_pairs
    l_n = []
    for i in range(3):
        l_n.append(math.pow(wo_pairs[i][0] + wo_pairs[i][1], -1))
    n = sum(l_n)
    l_d = []
    for i in range(3):
        l_d.append(math.pow(2*(i+1), -1))
    d = sum(l_d)
    wo = math.sqrt(n / d)
    print wo
    

def main():
    v1 = [1, 2, 3]
    v2 = [3, 2, 1]
    weighted_overlap(v1, v2)

main()
