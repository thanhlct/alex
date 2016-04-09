import os
import csv
import xml.etree.ElementTree as ET
import numpy as np
import argparse
import pdb

split_statistics = 50

def analysis_gp_run_log(run_log_file):
    split_summary = split_statistics
    flag_in_dialogue= False
    flag_in_user_turn= False
    flag_count_user_turn= False
    flag_start_dialogue = ''
    flag_start_user_turn = '-ASR input-debug-'
    flag_start_gp_turn = '-Extract features form'
    flag_end_dialogue = '-END EPISODE-'
    flag_success_dialogue = 'final_reward= 20'
    flag_unsuccess_dialogue = 'final_reward= 0'
    flag_user_silence = 'silence'

    total_user_turn = 0
    total_sys_turn = 0
    total_gp_turn = 0
    total_dialogue = 0
    total_batch_dialogue = 0
    total_success_dialogue = 0
    total_unsuccess_dialogue =0
    user_turns = []
    gp_turns = []
    rewards = []
    
    print '#dia, success, unsuccess, mean gpturn, std gpturn, mean userturn, std userturn, mena reward, std reward'

    with open(run_log_file, 'rt') as f:
        for line in f:
            line = line.strip()
            #print line
            if line.find(flag_start_user_turn)>=0:#not detect correctly this is the user turn or time out  turn
                if flag_in_user_turn==False:
                    flag_in_user_turn= True
                    flag_count_user_turn= True
                    #total_sys_turn += 1
                    continue
                else:
                    flag_in_user_turn = False
                    flag_count_user_turn= False
                    continue

            if flag_in_user_turn and flag_count_user_turn:
                if line.find(flag_user_silence)<0 and line != '':
                    total_user_turn +=1
                    flag_count_user_turn = False
                    
            if line.find(flag_start_gp_turn)>=0:
                total_gp_turn += 1
                continue
            if line.find(flag_end_dialogue)>=0:
                total_dialogue += 1
                total_batch_dialogue += 1
                user_turns.append(total_user_turn)
                gp_turns.append(total_gp_turn)
                turn_reward = total_gp_turn
                total_user_turn = 0
                total_gp_turn = 0
                
            if line.find(flag_success_dialogue)>=0:
                total_success_dialogue += 1 
                rewards.append(-1.0*turn_reward+20)
                #pdb.set_trace()
            if line.find(flag_unsuccess_dialogue)>=0:
                total_unsuccess_dialogue += 1    
                rewards.append(-1.0*turn_reward+0)
                #pdb.set_trace()

            if total_unsuccess_dialogue + total_success_dialogue == split_summary:
                print '%d, %.3f, %3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %s'%(total_dialogue, total_success_dialogue*1.0/split_summary, total_unsuccess_dialogue*1.0/split_summary, np.mean(gp_turns), np.std(gp_turns), np.mean(user_turns), np.std(user_turns), np.mean(rewards), np.std(rewards), 'size:%dsuc:%dun:%d'%(total_batch_dialogue, total_success_dialogue, total_unsuccess_dialogue)) 
                #pdb.set_trace()
                total_batch_dialogue =0
                total_unsuccess_dialogue = 0
                total_success_dialogue = 0
                gp_turns = []
                user_turns = []
                rewards = []

    if total_batch_dialogue >0:
        print '%d, %.3f, %3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %s'%(total_dialogue, total_success_dialogue*1.0/total_batch_dialogue, total_unsuccess_dialogue*1.0/total_batch_dialogue, np.mean(gp_turns), np.std(gp_turns), np.mean(user_turns), np.std(user_turns), np.mean(rewards), np.std(rewards), 'size:%d,suc:%d,un:%d'%(total_batch_dialogue, total_success_dialogue, total_unsuccess_dialogue)) 

if __name__ == '__main__':
    #gp_log_file = '/scratch/root_data/alex/ptien/gp_cf_learn/cf_learn/full_run_log.txt'
    gp_log_file = '/scratch/root_data/alex/ptien/gp_cf_learn/cf_learn/full_run_log2.txt'
    parser = argparse.ArgumentParser(description='Runing the analysis of the GP-Sarsa log.')
    parser.add_argument('-s', metavar='split', dest='split', help='Number of dialogues for each batch of summary', type=int, default=30)
    parser.add_argument('-f', metavar='log_file', dest='log_file', help='File log', type=str, default=gp_log_file)
    
    args = parser.parse_args()
    split_statistics = args.split
    gp_log_file = args.log_file

    analysis_gp_run_log(gp_log_file) 
