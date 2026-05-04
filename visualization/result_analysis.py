import json
import sys
import os

def check_log_file(file_path, target_string):
    try:
        with open(file_path, 'r') as file:
            file_content = file.read()
            if target_string in file_content:
                return True
            else:
                return False
    except FileNotFoundError:
        print(f"file '{file_path}' not exist")

if __name__ == '__main__':
    args = sys.argv
    main_path = args[1]
    suppix = args[2] if len(args) > 2 else None
    route_id_bank_list = ["r1_town05_ins_c", "r2_town05_ins_c", "r3_town05_ins_c", "r4_town06_ins_c", "r5_town06_ins_c", "r6_town07_ins_c", "r7_town05_ins_ss", "r8_town05_ins_ss", "r9_town06_ins_ss", "r10_town07_ins_ss", "r11_town05_ins_sl", "r12_town06_ins_sl", "r13_town05_ins_sl", "r14_town07_ins_sl", "r15_town07_ins_sl", "r16_town05_ins_sl", "r17_town05_ins_sr", "r18_town05_ins_sr", "r19_town05_ins_sr", "r20_town06_ins_sr", "r21_town07_ins_sr", "r22_town07_ins_sr", "r23_town05_ins_oppo", "r24_town05_ins_rl", "r25_town05_ins_crosschange", "r26_town05_ins_chaos", "r27_town06_hw_merge", "r28_town06_hw_c", "r29_town06_hw_merge", "r30_town06_hw_merge", "r31_town05_ins_oppo", "r32_town05_ins_oppo", "r33_town05_ins_rl", "r34_town05_ins_rl", "r35_town05_ins_crosschange", "r36_town05_ins_crosschange", "r37_town05_ins_chaos", "r38_town05_ins_chaos", "r39_town06_hw_c", "r40_town06_hw_c", "r41_town05_ins_oppo", "r42_town05_ins_rl", "r43_town05_ins_crosschange", "r44_town05_ins_chaos", "r45_town06_hw_merge", "r46_town06_hw_c"]

    if suppix is not None: suppix_list = [suppix] 
    
    suppix_list = ['_1round_0306 ', '_2round_0305', '_npc_0304', '_wo_consensus_0305', '_wo_critic_0307']
    if suppix is not None:
        suppix_list = [suppix]
    # prefixes = ["Interdrive_no_npc_", "Interdrive_npc_"] 
    prefixes = ["Interdrive_no_npc_"] 
    # prefixes = ["Interdrive_npc_"]

    route_id_bank_list = [prefix + r for prefix in prefixes for r in route_id_bank_list]


    for suppix in suppix_list:
        root_path = f"{main_path}{suppix}/v2x_final/"
        title = root_path.split('/')[-3].split('_')[5:]
        title = '_'.join(title)
        if os.path.exists(root_path):
            print(title)
        else:
            print(f"{title} not exists\n\n")
            continue

        invalid_str_list = []
        save_as_excel = []
        analysis = {'score_composed':[0] * 4, 'score_route':[0] * 4, 'score_penalty':[0] * 4, 'success_rate':[0] * 4, 'game_time':[0] * 4}
        cnt = [0,0,0] # ins, hw

        for route in route_id_bank_list:
            reported_route_id = []
            file_path = []
            # route = 'Interdrive_no_npc_' + route
            route_dir = os.path.join(root_path, route)
            ego_num = 0

            try :
                for folder_name in os.listdir(route_dir):
                    folder_path = os.path.join(route_dir, folder_name)
                    if os.path.isdir(folder_path) and folder_name.startswith('ego_vehicle'):
                        ego_num += 1

                for i in range(ego_num):
                    file_path.append(f"{root_path}/{route}/ego_vehicle_{i}/results.json")
            
                valid_flag = True
                fcc_data = []
                original_record = []

                for i in range(ego_num):
                    with open(file_path[i], 'r') as fcc_file:
                        fcc_data.append(json.load(fcc_file))
                    original_record.append(fcc_data[i]["_checkpoint"]["records"])

                records = []
                # records = original_record[0]
                import copy
                record = copy.deepcopy(original_record[0][0])

                record['scores']['score_route'] = sum(original_record[j][0]['scores']['score_route'] for j in range(ego_num)) / ego_num
                record['scores']['score_penalty'] = 1
                for j in range(ego_num):
                    record['scores']['score_penalty'] *= original_record[j][0]['scores']['score_penalty']
                record['scores']['score_composed'] = record['scores']['score_route'] * record['scores']['score_penalty']

                if len(args)>1:
                    print('{}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}'.format(route, record['scores']['score_route'], record['scores']['score_penalty'], record['scores']['score_composed'], record['meta']['duration_game'], record['meta']['duration_system']))
                reported_route_id.append(route)

                save_as_excel.append([
                    route, record['scores']['score_route'], record['scores']['score_penalty'], record['scores']['score_composed'],
                    record['meta']['duration_game'], record['meta']['duration_system']
                    ])
                analysis['score_route'][0] += record['scores']['score_route']
                analysis['score_penalty'][0] += record['scores']['score_penalty']
                analysis['score_composed'][0] += record['scores']['score_composed']
                analysis['game_time'][0] += record['meta']['duration_game']
                if record['scores']['score_composed'] > 99.95:
                    analysis['success_rate'][0] += 1
                if 'ins_ss' in route or 'ins_sl' in route or 'ins_oppo' in route or 'ins_chaos' in route:
                    analysis['score_route'][1] += record['scores']['score_route']
                    analysis['score_penalty'][1] += record['scores']['score_penalty']
                    analysis['score_composed'][1] += record['scores']['score_composed']
                    analysis['game_time'][1] += record['meta']['duration_game']
                    if record['scores']['score_composed'] > 99.95:
                        analysis['success_rate'][1] += 1
                    cnt[0] += 1
                elif 'crosschange' in route or 'hw_c' in route:
                    analysis['score_route'][3] += record['scores']['score_route']
                    analysis['score_penalty'][3] += record['scores']['score_penalty']
                    analysis['score_composed'][3] += record['scores']['score_composed']
                    analysis['game_time'][3] += record['meta']['duration_game']
                    if record['scores']['score_composed'] > 99.95:
                        analysis['success_rate'][3] += 1
                    cnt[2] += 1
                elif 'ins_sr' in route or 'ins_c' in route or 'ins_rl' in route or 'hw_merge' in route:
                    analysis['score_route'][2] += record['scores']['score_route']
                    analysis['score_penalty'][2] += record['scores']['score_penalty']
                    analysis['score_composed'][2] += record['scores']['score_composed']
                    analysis['game_time'][2] += record['meta']['duration_game']
                    if record['scores']['score_composed'] > 99.95:
                        analysis['success_rate'][2] += 1
                    cnt[1] += 1
                else:
                    print('error')
                        
            except Exception as e:
                print(e)
                pass

        val = list(analysis.values())
        
        val = [[x[0] / max(cnt[0]+cnt[1]+cnt[2],1), x[1] / max(cnt[0],1), x[2] / max(cnt[1],1), x[3] / max(cnt[2],1)] for x in val]
        val = list(map(list, zip(*val)))

        print(cnt[0]+cnt[1]+cnt[2],cnt[0],cnt[1],cnt[2])

        categories = ['Total', 'IC', 'LM', 'LC']
        for i in range(4):
            print(categories[i])
            for num in val[i]:
                if num>1:
                    print(format(num, '.2f'), end='\t')
                else:
                    print(format(num, '.3f'), end='\t')
            print('')
        print('')

    # from pandas import DataFrame
    # df = DataFrame({'name': [a[0] for a in save_as_excel], 'score_route': [a[1] for a in save_as_excel], 
    #                 'score_penalty': [a[2] for a in save_as_excel], 'score_composed': [a[3] for a in save_as_excel],
    #                 'duration_game': [a[4] for a in save_as_excel], 'duration_system': [a[5] for a in save_as_excel],
    #                 'valid_flag': [a[6] for a in save_as_excel], 'invalid_type': [a[7] for a in save_as_excel]})
    # df.to_excel(os.path.join(root_path, excel_file), sheet_name='sheet1', index=False)
