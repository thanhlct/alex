#!/bin/bash
# This encodes the train data.

cd $WORK_DIR

# Create a file with the filename with wav and mfc extensions on it.
# Only get the files in the training directory.
find -L $TRAIN_DATA_SOURCE -iname '*.wav' > $WORK_DIR/train_wav_files.txt

# Create the list file we need to send to HCopy to convert .wav files to .mfc
perl $TRAIN_SCRIPTS/CreateMFCList.pl $WORK_DIR/train_wav_files.txt wav mfc >$TEMP_DIR/train_wav_mfc.scp
python $TRAIN_SCRIPTS/SubstituteInMFCList.py $TEMP_DIR/train_wav_mfc.scp $TRAIN_DATA > $WORK_DIR/train_wav_mfc.scp

HCopy -T 1 -C $TRAIN_COMMON/configwav -C $TRAIN_COMMON/config -S $WORK_DIR/train_wav_mfc.scp > $LOG_DIR/hcopy_train.log
