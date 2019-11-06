#!/usr/bin/env bash
python3.6 run_classifier.py \
  --task_name=fyp \
  --do_predict=true \
  --data_dir=  \
  --vocab_file=multi_cased_L-12_H-768_A-12/vocab.txt \
  --bert_config_file=multi_cased_L-12_H-768_A-12/bert_config.json \
  --init_checkpoint=model.ckpt-2827 \
  --max_seq_length=70 \
  --output_dir=output

