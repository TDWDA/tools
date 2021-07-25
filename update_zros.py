#!/usr/bin/python
# -*- coding: utf-8 -*- 

import os
import sys
import time
import datetime
import subprocess
import shutil
import platform
from xml.dom.minidom import parse

mode = ''
project = '202'
update_pull_log = 'true'
tmp_dir = './zros_update_tmp/'

def usage():
  # print('请注意：')
  # print('> 此脚本只是自动升级zros，如果升级bsp请先备份控制器内的标定数据')
  # print('> 请确保安装python')
  # print('> 请使用usb-type C连接PC和控制器')
  # print('> 请将zros tar包和此脚本放在同一个目录下')
  # print('> zros tar可以有多个，支持用户选择')
  # print('> Windows系统终端工具推荐使用ConEmu')
  # print('')
  # print('=======================================')
  # print('usage：')
  # print('  python  upadte_zros.py  [log] [calib] [zm] [zm2] [zm_uss] [zm_fusion] [ca] [ca2] [ca_cfg]')
  # print('')
  # print('')
  print('python upadte_zros.py log')
  print('  1.导出版本信息、标定数据、core文件、zlog、logs、dmesg')
  print('')
  # print('\033[33mpython upadte_zros.py \033[31mcalib 202\033[0m')
  # print('\033[33mpython upadte_zros.py \033[31mcalib 569\033[0m')
  # print('  1.更新当前目录下的标定数据')
  # print('')
  # print('\033[33mpython upadte_zros.py \033[31mzm\033[0m')
  # print('  1.导出版本信息、标定数据、core文件、zlog、logs、dmesg')
  # print('  2.升级zros')
  # print('  3.自动更新控制器已有的标定数据')
  # print('')
  # print('\033[33mpython upadte_zros.py \033[31mzm2\033[0m')
  # print('  1.升级zros')
  # print('  2.自动更新控制器已有的标定数据')
  # print('')
  # print('\033[33mpython upadte_zros.py \033[31mzm_uss\033[0m')
  # print('  1.超声车位Rviz可视化显示')
  # print('  2.生成CSV文件')
  # print('  3.视觉、超声车位车机屏可视化显示')
  # print('  4.自启动节点remote_ros')
  # print('  5.自启动节点topic_bag，并配置按键录制')
  # print('')
  # print('\033[33mpython upadte_zros.py \033[31mzm_fusion\033[0m')
  # print('  1.配置ca_apa_agent节点log_param和enable_slot_log')
  # print('  2.配置log打印等级为1和node默认等级为1')
  # print('  3.自启动节点topic_bag，并配置按键录制')
  # print('  4.配置dvr data recorder按键自动分包录制')
  # print('')
  # print('\033[33mpython upadte_zros.py \033[31mca\033[0m')
  # print('  1.导出版本信息、标定数据、core文件、zlog、logs、dmesg')
  # print('  2.升级zros')
  # print('  3.自动更新控制器已有的标定数据')
  # print('  4.自启动节点topic_bag，并配置自动分包录制')
  # print('  5.配置USB以太网IP地址：192.168.1.30')
  # print('  6.配置dvr data recorder按键自动分包录制')
  # print('')
  # print('\033[33mpython upadte_zros.py \033[31mca2\033[0m')
  # print('  1.升级zros')
  # print('  2.自动更新控制器已有的标定数据')
  # print('  3.自启动节点topic_bag，并配置自动分包录制')
  # print('  4.配置USB以太网IP地址：192.168.1.30')
  # print('  5.配置dvr data recorder按键自动分包录制')
  # print('')
  print('python upadte_zros.py dt')
  # print('  1.自启动节点topic_bag，并配置自动分包录制')
  print('  2.配置USB以太网IP地址：192.168.1.30')
  print('  3.配置dvr data recorder按键自动分包录制')
  print('')
#  print(sys.argv)
  exit()

def list_dir(dir, depth = 1):
  paths = []
  depth -= 1
  if depth < 0:
    return paths
  for f in os.listdir(dir):
    path = os.path.join(dir, f)
    if os.path.isfile(path):
      paths.append(path)
    else:
      continue
  return paths

def xml_set(f, ks, v):
  if len(ks) != 2:
    print('ks error. ', f , ks, v)
    exit()
  domTree = parse(f)
  if domTree.documentElement.nodeName == ks[0]:
    nodes = domTree.documentElement.getElementsByTagName(ks[1])
    nodes[0].firstChild.nodeValue = v
  else:
    nodes = domTree.documentElement.getElementsByTagName(ks[0])
    if len(nodes) == 0:
      print('no nodes. ', f , ks, v)
      exit()
    for node in nodes[0].childNodes:
      if node.nodeName == ks[1]:
        node.firstChild.nodeValue = v
  with open(f, 'w') as fp:
    domTree.writexml(fp, addindent='  ', encoding='utf-8')

def xml_update(p, f, ks, v):
  if not os.path.isdir(tmp_dir):
    os.makedirs(tmp_dir)

  subprocess.call('adb pull ' + p + ' ' + tmp_dir + f, shell=True)
  if not os.path.isfile(tmp_dir + f):
    print(tmp_dir + f + ' no existed')
    exit()

  xml_set(tmp_dir + f, ks, v)
  subprocess.call('adb push ' + tmp_dir + f + ' ' + p, shell=True)

def auto_launch_topic_bag(enable,type):
  subprocess.call('adb shell "sed -i s/\<key_type\>[0-9]*/\<key_type\>' +str(type)+ '/ /zros/res/topic_bag/bag_default_config.xml"', shell=True)
  xml_update('/zros/res/product_config/launcher/launcher_others.xml', 'launcher_others.xml', ['topic_bag', 'enable'], enable)
  print('auto launch topic_bag: done!')

def auto_enable_dvr_data_recorder():
  subprocess.call('adb shell "sed -i s/\<data_recorder_effective\>false/\<data_recorder_effective\>true/ /zros/res/DVR_cam_recoder/config_mode.xml"', shell=True)
  subprocess.call('adb shell "sed -i s/\<key_recorder_mode\>1/\<key_recorder_mode\>2/ /zros/res/DVR_cam_recoder/config_mode.xml"', shell=True)
  print('auto enable dvr data_recorder: done!')

def config_ethernet():
  res = subprocess.check_output('adb shell "cat /usr/bin/zros.sh | grep ifconfig | wc -l"', shell=True)
  if int(res) == 0:
    subprocess.call("adb shell \"echo 'sleep 15' >> /usr/bin/zros.sh\"", shell=True)
    subprocess.call("adb shell \"echo 'ifup eth1' >> /usr/bin/zros.sh\"", shell=True)
    subprocess.call("adb shell \"echo 'sleep 15' >> /usr/bin/zros.sh\"", shell=True)
    subprocess.call("adb shell \"echo 'ifconfig eth1 192.168.1.30 netmask 255.255.255.0' >> /usr/bin/zros.sh\"", shell=True)
    subprocess.call("adb shell \"echo 'sleep 1' >> /usr/bin/zros.sh\"", shell=True)
    subprocess.call("adb shell \"echo 'date' >> /usr/bin/zros.sh\"", shell=True)
    subprocess.call("adb shell \"echo '' >> /usr/bin/zros.sh\"", shell=True)
    print('config ethernet: done!')
  else:
    print('config ethernet: done!')

def zm_uss_fusion_original_file_backup():
  subprocess.call('adb shell "mkdir -p /data/zros/zm_uss_fusion_original_cfg"', shell=True)
  subprocess.call('adb shell "rm -rf /data/zros/zm_uss_fusion_original_cfg/*"', shell=True)
  subprocess.call('adb shell "cp /zros/res/car_instance/ca_s202_960p/app/slot_search_fusion/config.xml /data/zros/zm_uss_fusion_original_cfg"', shell=True)
  subprocess.call('adb shell "cp /zros/res/ca_apa_agent/fusion_agent_cfg.xml /data/zros/zm_uss_fusion_original_cfg"', shell=True)

def zm_uss_fusion_original_file_check():
  subprocess.call('adb pull -p /data/zros/zm_uss_fusion_original_cfg/ ./', shell=True)
  if not os.path.isdir('zm_uss_fusion_original_cfg'):
    print('zm_uss_fusion_original_cfg directory not found !')
    exit()
  elif not os.path.isfile('zm_uss_fusion_original_cfg/config.xml'):
    print('slot_search_fusion/config.xml not found !')
    exit()
  elif not os.path.isfile('zm_uss_fusion_original_cfg/fusion_agent_cfg.xml'):
    print('fusion_agent_cfg.xml not found !')
    exit()
  subprocess.call('adb shell mount -o rw,remount /', shell=True)
  subprocess.call('adb shell "rm /zros/res/car_instance/ca_s202_960p/app/slot_search_fusion/config.xml"', shell=True)
  subprocess.call('adb shell "rm /zros/res/ca_apa_agent/fusion_agent_cfg.xml"', shell=True)
  subprocess.call('adb push -p ./zm_uss_fusion_original_cfg/config.xml /zros/res/car_instance/ca_s202_960p/app/slot_search_fusion', shell=True)
  subprocess.call('adb push -p ./zm_uss_fusion_original_cfg/fusion_agent_cfg.xml /zros/res/ca_apa_agent/', shell=True)
  subprocess.call('adb shell sync', shell=True)
  shutil.rmtree('zm_uss_fusion_original_cfg')

def zm_uss():
  #  Rviz车位可视化
  xml_update('/zros/res/car_instance/ca_s202_960p/app/slot_search_fusion/config.xml', 'slot_search_fusion.xml', ['slot_search_fusion', 'send_to_rviz'], 1)
  # 生产csv
  subprocess.call('adb shell "sed -i s/\<recorder_csv\>0/\<recorder_csv\>1/ /zros/res/car_instance/ca_s202_960p/app/apa_target_node/config.xml"', shell=True)
  # 视觉&超声车位可视化
  xml_update('/zros/res/ca_apa_agent/fusion_agent_cfg.xml', 'fusion_agent_cfg.xml', ['debug_param', 'enable'], 1)
  # DVR
  subprocess.call('adb shell "sed -i s/\<key_recorder_mode\>1/\<key_recorder_mode\>2/ /zros/res/DVR_cam_recoder/config_mode.xml"', shell=True)
  # remote_ros
  xml_update('/zros/res/product_config/launcher/ca_launcher_apa.xml', 'ca_launcher_apa.xml', ['remote_ros', 'enable'], 1)
  auto_launch_topic_bag(1, 1)
  print('config ethernet: done!')

def zm_fusion():
  # Topic_bag
  subprocess.call('adb shell "sed -i s/\<key_type\>[0-9]*/\<key_type\>1/ /zros/res/topic_bag/bag_default_config.xml"', shell=True)
  xml_update('/zros/res/product_config/launcher/launcher_others.xml', 'launcher_others.xml', ['topic_bag', 'enable'], 1)
  # fused log
  xml_update('/zros/res/ca_apa_agent/fusion_agent_cfg.xml', 'fusion_agent_cfg.xml', ['log_param', 'enable'], 1)
  xml_update('/zros/res/ca_apa_agent/fusion_agent_cfg.xml', 'fusion_agent_cfg.xml', ['log_param', 'enable_slot_log'], 1)
  # log
  subprocess.call('adb shell "sed -i s/log_level:.*/log_level:1/ /zros/res/log_center/config_console.pb.txt"', shell=True)
  subprocess.call('adb shell "sed -i 3s/level:.*/level:1/ /zros/res/log_center/node_log_level.pb.txt"', shell=True)
  subprocess.call('adb shell "sed -i s/\<key_recorder_mode\>1/\<key_recorder_mode\>2/ /zros/res/DVR_cam_recoder/config_mode.xml"', shell=True)
  print('config ethernet: done!')

def csv_backup():
  print('')
  print('pull slot csv file:')
  now = datetime.datetime.now()
  subprocess.call('adb shell "cd /data/zros/data && tar zcf apa_target.tar.gz ./apa_target_node"', shell=True)
  subprocess.call('adb pull /data/zros/data/apa_target.tar.gz ./csv/apa_target_' + now.strftime("%Y-%m-%d_%H-%M-%S") + '.tar.gz', shell=True)
  subprocess.call('adb shell "rm -rf /data/zros/data/apa_target.tar.gz"', shell=True)

def update_calib():
  '''if not os.path.isdir('calib'):
    print('calib folder no existed !')
    exit()
  elif not os.path.isfile('calib/'):
    print(tmp_dir + f + ' no existed')
    exit()
  elif not os.path.isfile(tmp_dir + f):
    print(tmp_dir + f + ' no existed')
    exit()
    '''
  if project == '202':
    subprocess.call('adb shell "rm -rf /data/zros/data/ca_s202_960p/calib"', shell=True)
    subprocess.call('adb push -p calib /data/zros/data/ca_s202_960p/', shell=True)
  elif project == '569':
    subprocess.call('adb shell "rm -rf /data/zros/data/ca_cd569/calib"', shell=True)
    subprocess.call('adb push -p calib /data/zros/data/ca_cd569/', shell=True)
  subprocess.call('adb shell "rm -rf /data/zros_datas_backup"', shell=True)
  subprocess.call('adb shell "rm -rf /data/zros/cache"', shell=True)
  subprocess.call('adb shell sync', shell=True)
  print('update calib done!')

def log_coredump_backup():
  print('')
  print('pull zlog、logs、dmesg and coredump:')
  now = datetime.datetime.now()
  subprocess.call('adb shell "mkdir -p /data/log_coredump"', shell=True)
  subprocess.call('adb shell "dmesg > /data/zlog/dmesg.txt && tar zcf /data/log.tar.gz /data/zlog/ /data/logs/"', shell=True)
  subprocess.call('adb shell "mv /data/log.tar.gz /data/log_coredump"', shell=True)
  if mode == 'ca2' or mode == 'zm2':
    subprocess.call('adb shell "rm -rf /data/core*"', shell=True)
  else:
    subprocess.call('adb shell "mv -f /data/core* /data/log_coredump"', shell=True)
  subprocess.call('adb shell "cp -rf /data/zros/data /data/log_coredump"', shell=True)
  subprocess.call('adb shell "cd /zros/bin && ./app_version > /data/log_coredump/app_version.txt"', shell=True)
  subprocess.call('adb pull /data/log_coredump ./log_coredump_' + now.strftime("%Y-%m-%d_%H-%M-%S"), shell=True)
  subprocess.call('adb shell "rm -rf /data/log_coredump /data/zlog/* /data/logs/*"', shell=True)

def update_zros():
# select zros version
  print('zros version list:')
  paths = list_dir('./')
  tars = []
  for path in paths:
    if path.find("zros_A_CA_S202") != -1 and path.find(".tar.gz") != -1:
      print(str(len(tars)) + '-' + os.path.basename(path))
      tars.append(path)

  idx = 0
  if len(tars) == 0:
    print('\033[33m没有找到zros升级包！\033[0m')
    exit()
  elif len(tars) == 1:
    print('\033[33m只有一个zros升级包，已自动选择: \033[0m')
  elif len(tars) > 1:
    idx = input('\033[33m找到多个zros升级包，请选择(0,1,2,...): \033[0m')

  zros_tar = tars[int(idx)]
  print('\033[33m ' + os.path.basename(zros_tar) + ' \033[0m')
  print('')
  res = input('are you sure update? (yes:y, no:n):')
  if res != 'y':
    exit()

# backup log
  subprocess.call('adb shell "mkdir -p /data/zlog/debug/ && mkdir -p /data/zros/data/ && mkdir -p /zros/bin && mkdir -p /zros/lib"', shell=True)
  log_coredump_backup()

# show version
  print('')
  print('pre-update zros version:')
  subprocess.call('adb shell mount -o rw,remount /', shell=True)
  subprocess.Popen("adb shell \"cd /zros/bin && ./mcu_debug_mode --foff > /dev/null \"", shell=True)
  subprocess.Popen("adb shell \"cd /zros/bin && ./app_version|grep -A 3 '\-\-ZROS\-\-\-'\"", shell=True)
  time.sleep(2)

# push zros
  print('push zros file:') 
  subprocess.call('adb shell "mkdir -p /data/zros_update"', shell=True)
  subprocess.call('adb shell "rm -rf /data/zros_update/*"', shell=True)
  subprocess.call('adb push -p ' + zros_tar + ' /data/zros_update/', shell=True)

# update zros
  zros_tar = os.path.basename(zros_tar)
  print('')
  print('update zros:')
  subprocess.call('adb shell "cd /data/zros_update/ && tar zxf ' + zros_tar + '"', shell=True)
  if project == '202':
    subprocess.call('adb shell "rm /data/zros_update/data/ca_s202_960p/calib/*"', shell=True)
    subprocess.call('adb shell "cp -rf /data/zros/data/ca_s202_960p/calib/* /data/zros_update/data/ca_s202_960p/calib/"', shell=True)
  elif project == '569':
    subprocess.call('adb shell "rm /data/zros_update/data/ca_cd569/calib/*"', shell=True)
    subprocess.call('adb shell "cp -rf /data/zros/data/ca_cd569/calib/* /data/zros_update/data/ca_cd569/calib/"', shell=True)
  subprocess.call('adb shell "rm -rf /data/zros/* /zros/*"', shell=True)
  subprocess.call('adb shell "mv /data/zros_update/bin /data/zros_update/lib /data/zros_update/res /zros/"', shell=True)
  subprocess.call('adb shell "mv /data/zros_update/data /data/zros/"', shell=True)

# clean up
  time.sleep(1)
  subprocess.call('adb shell "rm -rf /data/zros_datas_backup /data/zros_update"', shell=True)
  subprocess.call('adb shell sync', shell=True)

def main_process():
  if len(sys.argv) == 2 or len(sys.argv) == 3:
    if sys.argv[1] == 'log':
      mode = sys.argv[1]
    elif sys.argv[1] == 'calib':
      mode = sys.argv[1]
    elif sys.argv[1] == 'zm':
      mode = sys.argv[1]
    elif sys.argv[1] == 'zm2':
      mode = sys.argv[1]
    elif sys.argv[1] == 'zm_uss':
      mode = sys.argv[1]
    elif sys.argv[1] == 'zm_fusion':
      mode = sys.argv[1]
    elif sys.argv[1] == 'ca':
      mode = sys.argv[1]
    elif sys.argv[1] == 'ca2':
      mode = sys.argv[1]
    elif sys.argv[1] == 'dt':
      mode = sys.argv[1]
    else:
      usage()
  else:
    usage()
  if len(sys.argv) == 3:
    if sys.argv[2] == '202':
      project = sys.argv[2]
    elif sys.argv[2] == '569':
      project = sys.argv[2]
    else:
      usage()

  print('adb auth')
  subprocess.call('adb usb 820@zongmutech', shell=True)
  time.sleep(10)

  if mode == 'log':
    log_coredump_backup()
    exit()
  elif mode == 'calib':
    update_calib()
    exit()
  elif mode == 'dt':
 #   config_ethernet()
    auto_launch_topic_bag('enable',1)
    auto_enable_dvr_data_recorder()
    exit()
  elif mode == 'zm_uss':
    print('\033[33mconfig ZM USS mode!\033[0m')
    zm_uss_fusion_original_file_check()
    zm_uss()
    csv_backup()
    exit()
  elif mode == 'zm_fusion':
    print('\033[33mconfig ZM FUSION mode!\033[0m')
    zm_uss_fusion_original_file_check()
    zm_fusion()
    csv_backup()
    exit()

# update zros tar.gz
  update_zros()

  if mode == 'ca' or mode == 'ca2':
    print('\033[33mconfig CA mode!\033[0m')
    config_ethernet()
    auto_launch_topic_bag(1, 3)
    auto_enable_dvr_data_recorder()
  elif mode == 'zm':
    print('\033[33mconfig ZM mode!\033[0m')
    zm_uss_fusion_original_file_backup()

# clean up and reset
  print('')
  subprocess.call('adb shell sync', shell=True)
  subprocess.call('adb shell reboot -f', shell=True)

  print('reboot soc, please wait...')
  time.sleep(25)
  subprocess.call('adb usb 820@zongmutech', shell=True)
  time.sleep(10)
  print('')
  print('updated zros version:')
  subprocess.Popen("adb shell \"cd /zros/bin && ./app_version|grep -A 3 '\-\-ZROS\-\-\-'\"", shell=True)
  time.sleep(2)

  print('')
  print('\033[33mupdate finish \033[0m')


if __name__ == "__main__":
  if sys.version < '3':
    print('please use python3!')
    exit()
  main_process()
