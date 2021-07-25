#!usr/bin/python3
# _*_ coding:utf-8 _*_

import re
import os
import sys
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import numpy as np 
import matplotlib.ticker as ticker
from numpy.core.fromnumeric import mean



def usage():
  print('usage：')
  print('  python top.py  proc_name  top_file')
  exit()

def matchProcName(fp, proc):
  n1 = ''
  n2 = ''
  loop = 0
  lines = fp.readlines()
  for line in lines:
    items = line.decode('utf-8').strip(' \n').replace('   ', ' ').replace('  ', ' ').replace('  ', ' ').split(' ')
    
    print(len(items), items)
    
    if len(items) == 12:
      if items[0] != 'top' and items[11] != 'COMMAND':
        if proc in items[11]:
          #if re.fullmatch(proc, items[11]):
          if n1 == '':
            n1 = items[11]
          n2 = items[11]
          if n1 != n2:
            print('find more proc name!' + proc_name + ' ' + proc_name0)
            exit()
      elif items[11] == 'COMMAND':
        loop += 1
        if loop == 2:
          return n1

def DrawTop():
  proc = ''
  proc_name = ''
  proc_name0 = ''
  draw_type = '-l'
  top_file = 'top.log'
  
 
  
  # if len(sys.argv) == 2:
  #   if sys.argv[1] == '-l' or sys.argv[1] == '-d':
  #     usage()
  #   else:
  #     proc = sys.argv[1]
  # elif len(sys.argv) == 3:
  #   if sys.argv[1] == '-l' or sys.argv[1] == '-d':
  #     draw_type = sys.argv[1]
  #   else:
  #     usage()
  #   proc = sys.argv[2]
  # elif len(sys.argv) == 4:
  #   if sys.argv[2] == '-f':
  #     top_file = sys.argv[3]
      
  #     print(top_file)
      
  #   else:
  #     usage()
  # elif len(sys.argv) == 5:
  #   if sys.argv[3] == '-f':
  #     top_file = sys.argv[4]
  #   else:
  #     usage()
  # else:
  #   usage()
  if len(sys.argv)==3:
    proc = sys.argv[1]
    top_file = sys.argv[2]

  # print("argv[0]:%s \nargv[1]:%s \nargv[2]:%s \nargv[3]:%s"%(sys.argv[0],sys.argv[1],sys.argv[2],sys.argv[3]))
  # print(proc,draw_type,top_file)


  with open(top_file, 'rb') as fp:
    #proc_name = matchProcName(fp, proc)
    lines = fp.readlines()
    cpu = []
    cpu_total = []
    ctotal = 0
    mem = []
    mtotal =0
    memtotal= []
    time = []
    for line in lines:
      # print (line)
      #items = line.decode('utf-8').strip(' \n').replace('   ', ' ').replace('  ', ' ').replace('  ', ' ').split(' ')
      items = line.decode('utf-8').strip(' \n').replace('     ',' ').replace('    ',' ').replace('   ',' ').replace('  ',' ').split(' ')
      # print(len(items), items)

      if len(items) == 12:
        if items[0] != 'top' and items[11] != 'COMMAND':
          try:
            ctotal += float(items[8])
            mtotal+=float(items[9])
          except ValueError:
            pass
          if proc in items[11]:
          #if re.fullmatch(proc, items[11]):
            if proc_name == '':
              proc_name = items[11]
            proc_name0 = items[11]
            if proc_name != proc_name0:
              print('find more proc name!' + proc_name + ' ' + proc_name0)
              exit()
            cpu.append(float(items[8]))
            mem.append(float(items[9]))
            # time.append((items[10]))
        elif items[11] == 'COMMAND':
          if ctotal != 0:
            cpu_total.append(ctotal)
            memtotal.append(mtotal)
            ctotal = 0
            mtotal =0
      elif items[0] == 'top':
          time.append(items[2])

    x=np.array(time)
    y_cpu=np.array(cpu)
    y_cputotal=np.array(cpu_total)
    y_mem=np.array(mem)
    y_memtotal=np.array(memtotal)
    num_y=(len(y_cputotal))
    num_x=(len(x))
    # print(time)
    if(num_x!=num_y):
      if(num_x>num_y):
        # x = x[:, :-1]
        x=np.delete(x,-1,axis=0)
        y_cpu=np.delete(y_cpu,-1,axis=0)
        y_mem=np.delete(y_mem,-1,axis=0)  

    fig = plt.figure('CPU')
    ax1_1 = fig.add_subplot(8,2,1)
    ax1_2 = fig.add_subplot(8,2,2)
    ax2_1 = fig.add_subplot(8,2,3)
    ax2_2 = fig.add_subplot(8,2,4)
    # ax3_1 = fig.add_subplot(8,2,5)
    # ax3_2 = fig.add_subplot(8,2,6)
    # ax4_1 = fig.add_subplot(8,2,7)
    # ax4_2 = fig.add_subplot(8,2,8)
    # ax5_1 = fig.add_subplot(8,2,9)
    # ax5_2 = fig.add_subplot(8,2,10)
    # ax6_1 = fig.add_subplot(8,2,11)
    # ax6_2 = fig.add_subplot(8,2,12)
    # ax7_1 = fig.add_subplot(8,2,13)
    # ax7_2 = fig.add_subplot(8,2,14)
    # ax8_1 = fig.add_subplot(8,2,15)
    # ax8_2 = fig.add_subplot(8,2,16)
    if draw_type == '-l':
      #-----------------------#
      ax1_1.plot(x, y_cputotal, color = 'blue')
      ax1_2.plot(x, y_memtotal, color = 'blue')
      #-----------------------#
      ax2_1.plot(x, y_cpu, color = 'green')
      ax2_2.plot(x, y_mem, color = 'green')
      #-----------------------#
      # ax3_1.plot(x, y_cpu, color = 'green')
      # ax3_2.plot(x, y_mem, color = 'green')
      # #-----------------------#
      # ax4_1.plot(x, y_cpu, color = 'green')
      # ax4_2.plot(x, y_mem, color = 'green')
      # #-----------------------#
      # ax5_1.plot(x, y_cpu, color = 'green')
      # ax5_2.plot(x, y_mem, color = 'green')
      # #-----------------------#
      # ax6_1.plot(x, y_cpu, color = 'green')
      # ax6_2.plot(x, y_mem, color = 'green')
      # #-----------------------#
      # ax7_1.plot(x, y_cpu, color = 'green')
      # ax7_2.plot(x, y_mem, color = 'green')
      # #-----------------------#
      # ax8_1.plot(x, y_cpu, color = 'green')
      # ax8_2.plot(x, y_mem, color = 'green')
      #-----------------------#
  

    else:
      pass
      # ax1.scatter(range(len(cpu)), cpu, marker = 'o', color = 'green', s = 40, label = proc + ' cpu(%)')
      # ax2.scatter(range(len(cpu_total)), cpu_total, marker = 'o', color = 'blue', s = 40, label = 'total cpu(%)')
    
    # ax1.set_xticks(range(0,len(x),80)) 
    # ax2.set_xticks(range(0,len(x),80)) 
    # ax3.set_xticks(range(0,len(x),80)) 
    # ax4.set_xticks(range(0,len(x),80)) 
    # ax1.set_xticklabels(x,rotation=15)



  # ax1.legend(labels = ['Total cpu%'], loc = 'best')
  # ax2.legend(labels = ['Total mem%'], loc = 'best')
  # ax3.legend(labels = [proc_name+' cpu%'], loc = 'best')
  # ax4.legend(labels = [proc_name+' mem%'], loc = 'best')
  plt.show()


if __name__ == '__main__':
  DrawTop()

