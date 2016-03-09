import os
import csv
import xml.etree.ElementTree as ET
import numpy as np
import pdb

def turn_analysis(log_path):
    total_dialogue = 0
    correct_turn = onlist_turn = offlist_turn = ogg_turn_asr = ogg_turn_slu = ogg_turn_sys = 0
    turn_counts_user = []
    turn_counts_sys = []

    for d in os.listdir(log_path):
        log = os.path.join(log_path, d, 'session.xml')
        turn_number_user = 0
        turn_number_sys = 0
        if os.path.isfile(log):
            print '===============dialogue xml:', log
            total_dialogue+=1
            tree = ET.parse(log)
            for turn in tree.iter('turn'):
                if turn.attrib['speaker']=='user':
                    turn_number_user = turn.attrib['turn_number']
                    print 'user_turn', turn_number_user, log
                    asr = turn.find('asr')
                    if asr != None:
                        first_asr = asr.find('hypothesis').text
                        if first_asr == '_other_':
                            ogg_turn_asr +=1
                        
                    slu = turn.find('slu')
                    if slu != None:
                        first_slu = slu.find('interpretation').text
                        if first_slu == 'null()' or first_slu =='other()':
                            ogg_turn_slu +=1
                            #pdb.set_trace()
                else:#system turn:
                    turn_number_sys = turn.attrib['turn_number']
                    print 'sys_turn', turn_number_sys, log
                    sys_da = turn.find('dialogue_act')
                    if sys_da!=None and sys_da.text == 'notunderstood()':
                        ogg_turn_sys +=1

        turn_counts_user.append(int(turn_number_user))
        turn_counts_sys.append(int(turn_number_sys))
        #if total_dialogue>=10:
            #break
    
    print '============SUMARY================='
    print 'Total dialogue:', total_dialogue 
    print 'Total user turn:', sum(turn_counts_user) 
    print 'Total sys turn:', sum(turn_counts_sys) 
    print 'Average turn dialogue (user): %f (%f)'%(np.mean(turn_counts_user),np.std(turn_counts_user))
    print 'Average turn dialogue (sys): %f (%f)'%(np.mean(turn_counts_sys),np.std(turn_counts_sys))
    print 'OGG turn (sys_da): %d'%(ogg_turn_sys)
    print 'OGG turn (asr): %d'%(ogg_turn_asr)
    print 'OGG turn (slu): %d'%(ogg_turn_slu)
    #pdb.set_trace()

def success_rate(csv_path, log_path):
    total_dialogue = success_dialogue = 0

    print 'csv_file: %s\nlog_path: %s'%(csv_path, log_path)
    for f in os.listdir(csv_path):
        csv_file = os.path.join(csv_path, f)

        print '==================csv file:', csv_file
        with open(csv_file, 'rb') as job:
            job_details = csv.DictReader(job)
            for row in job_details:
                total_dialogue +=1
                if row['have_you_found_what_you_were_looking_for'].strip().lower()=='yes':
                    success_dialogue +=1
                #pdb.set_trace()
        
    print '---Success rate: %f(%d/%d)'%(success_dialogue*100.0/total_dialogue, success_dialogue,total_dialogue)

if __name__ == '__main__':
    csv_path = '/scratch/thanh/study/alex/analysis/call_data_ondrej/cf_results/csv'
    log_path = '/scratch/thanh/study/alex/analysis/call_data_ondrej/'
    success_rate(csv_path, log_path)
    #turn_analysis(log_path) 
