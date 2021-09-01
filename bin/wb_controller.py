import tkinter as tk
import numpy as np
import tkinter.ttk as ttk
import os
import datetime
import time
import random
import matplotlib.pyplot as plt 
import subprocess
import json
from tkinter.filedialog import asksaveasfilename
from tkinter.filedialog import askopenfilename
import subprocess
import threading
from paramiko import SSHClient
import paramiko
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, 
NavigationToolbar2Tk)

from config_ultra import *


date = datetime.datetime.now()

if date.month < 10:
    month = "0"+str(date.month)
else:
    month = str(date.month)

if date.day < 10:
    day = "0"+str(date.day)
else:
    day = str(date.day)

if date.hour < 10:
    hour = "0"+str(date.hour)
else:
    hour = str(date.hour)

if date.minute < 10:
    minute = "0"+str(date.minute)
else:
    minute = str(date.minute)
    
date_format = month+day+hour+minute+str(date.year-2000)

client = SSHClient()
client.load_system_host_keys()
client.connect(ip_address, username=username)


e_monitor=threading.Event()
e_timer=threading.Event()
e_log = threading.Event()
e_acquisition = threading.Event()

def abortable_sleep(secs, abort_event):
    abort_event.wait(timeout=secs)
    abort_event.clear()


def v_adc(v_bias, t_board,ch):
    m_slope=(m_hot-m_cold)/(temp_hot-temp_cold)
    m_inter=(m_cold*temp_hot- temp_cold*m_hot)/(temp_hot-temp_cold)
   
    q_slope = (q_hot-q_cold)/(temp_hot-temp_cold)
    q_inter = (q_cold*temp_hot - temp_cold*q_hot)/(temp_hot-temp_cold)
    
    v_adc=(v_bias-(t_board*q_slope+q_inter))/((t_board*m_slope)+m_inter)
    
    return v_adc[ch]

t_board = float(subprocess.check_output("""ssh """ + username + """@""" + ip_address + """ 'bash get_param.sh' """, shell=True)[16:21]) 

def t_daq_read_tcp():
    print("Starting DaqReadTcp...")
    nbytes = 4096
    hostname = '192.168.137.30'
    port = 22
    username = 'root' 
    password = 'root'
    command = './DaqReadTcp'

    client = paramiko.Transport((hostname, port))
    client.connect(username=username, password=password)

    stdout_data = []
    stderr_data = []
    session = client.open_channel(kind='session')
    session.exec_command(command)
    while True:
        if session.recv_ready():
            stdout_data.append(session.recv(nbytes))
        if session.recv_stderr_ready():
            stderr_data.append(session.recv_stderr(nbytes))
        if session.exit_status_ready():
            break

    session.recv_exit_status()

    session.close()
    client.close()

def convert_adc_to_v(element,ch):
    return ((adc_to_v[ch][1]+element*adc_to_v[ch][0])*1000)

def convert_v_to_adc(element,ch):
    return (v_to_adc[ch][1]+element*v_to_adc[ch][0])


class WbControllerUltraApp():



    def __init__(self, master=None):

        #self.protocol("WM_DELETE_WINDOW", self.on_exit)

        # build ui
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True)
        self.frm_data_acquisition = ttk.Frame(self.notebook, height=500)
        self.frm_plot = ttk.Frame(self.notebook)
        self.frm_rate = ttk.Frame(self.notebook)
        

        self.frm_data_acquisition.pack(fill='both', expand=True)
        self.frm_plot.pack(fill='both', expand=True)
        self.frm_rate.pack(fill='both', expand=True)

        self.notebook.add(self.frm_data_acquisition, text='Data acquisition')
        self.notebook.add(self.frm_plot, text='Plot and analysis')
        self.notebook.add(self.frm_rate, text='Rate Monitor')
    
        self.btn_ch = {}
        self.ent_start = {}
        self.ent_stop = {}
        self.ent_vbias = {}
        self.ent_lead = {}
        self.ent_tail = {}

        self.ch_status = {}
        for ch in range(12):
            self.ch_status[ch] = tk.IntVar()

        self.frm_param = tk.Frame(self.frm_data_acquisition)

        self.lbl_start_th = tk.Label(self.frm_param)
        self.lbl_start_th.configure(text='Start Th')
        self.lbl_start_th.grid(column='0', row='1')
        self.lbl_stop_th = tk.Label(self.frm_param)
        self.lbl_stop_th.configure(text='Stop Th')
        self.lbl_stop_th.grid(column='0',row='2')
        self.lbl_tail = tk.Label(self.frm_param)
        self.lbl_tail.configure(text='Tail')
        self.lbl_tail.grid(column='0', row='3')
        self.lbl_lead = tk.Label(self.frm_param)
        self.lbl_lead.configure(anchor='e', text='Lead')
        self.lbl_lead.grid(column='0', padx='1', pady='1', row='4')
        self.lbl_vbias = tk.Label(self.frm_param)
        self.lbl_vbias.configure(text='V bias (V)')
        self.lbl_vbias.grid(column='0',row='5')

        for col in range(12):
            for row in range(6):
                if row == 0:  #check button
                    self.btn_ch[col]=tk.Checkbutton(self.frm_param, variable=self.ch_status[col])
                    #self.btn_ch[col]=tk.Checkbutton(self.frm_param)
                    self.btn_ch[col].configure(relief='raised', text='CH '+ str(col))
                    self.btn_ch[col].grid(column=str(col+1), row=row)
                if row == 1:
                    self.ent_start[col]=tk.Entry(self.frm_param)
                    self.ent_start[col].configure(width='6')
                    self.ent_start[col].grid(column=str(col+1), row=row)


                if row == 2:
                    self.ent_stop[col]=tk.Entry(self.frm_param)
                    self.ent_stop[col].configure(width='6')
                    self.ent_stop[col].grid(column=str(col+1), row=row)
                
                if row == 3:
                    self.ent_tail[col]=tk.Entry(self.frm_param)
                    self.ent_tail[col].configure(width='6')
                    self.ent_tail[col].grid(column=str(col+1), row=row)

                if row == 4:
                    self.ent_lead[col]=tk.Entry(self.frm_param)
                    self.ent_lead[col].configure(width='6')
                    self.ent_lead[col].grid(column=str(col+1), row=row)

                if row == 5:
                    self.ent_vbias[col]=tk.Entry(self.frm_param)
                    self.ent_vbias[col].configure(width='6')
                    self.ent_vbias[col].grid(column=str(col+1), row=row)


        
        #self.frm_param.configure(height='200', width='400')
        self.frm_param.grid(row='0', column='0', columnspan='3')

        #PARAMETER ACTION BUTTON
        self.frm_param_action = ttk.Labelframe(self.frm_data_acquisition)
        self.frm_param_action.configure(height='200', text='Parameters', width='200')
        self.frm_param_action.grid(row='1', column='0', rowspan="2")

        self.btn_load_param = ttk.Button(self.frm_param_action)
        self.btn_load_param.configure(text='Load')
        self.btn_load_param.grid(column='0', row='0',padx='10', pady='10')
        self.btn_load_param.bind('<Button-1>', self.load_parameter_clicked, add='')
        
        self.btn_set_param = ttk.Button(self.frm_param_action)
        self.btn_set_param.configure(text='Set')
        self.btn_set_param.grid(column='1', row='0',padx='10', pady='10')
        self.btn_set_param.bind('<Button-1>', self.set_parameter_clicked, add='')

        self.btn_save_param = ttk.Button(self.frm_param_action)
        self.btn_save_param.configure(text='Save')
        self.btn_save_param.grid(column='3', row='0',padx='10', pady='10')
        self.btn_save_param.bind('<Button-1>', self.save_parameter_clicked, add='')
        


        #MISC BUTTONS

        self.btn_initialize = ttk.Button(self.frm_param_action)
        self.btn_initialize.configure(text='Initialize\n  board')
        self.btn_initialize.grid(column='0', row='1',padx='10', pady='10')
        self.btn_initialize.bind('<Button-1>', self.initialize_clicked, add='')

        self.btn_vbias_off = ttk.Button(self.frm_param_action)
        self.btn_vbias_off.configure(text='V bias\n  OFF')
        self.btn_vbias_off.grid(column='1', row='1',padx='10', pady='10')
        self.btn_vbias_off.bind('<Button-1>', self.vbias_off_clicked, add='')



        #DAQ CONTROLS
        self.frm_daq_control = ttk.Labelframe(self.frm_data_acquisition)
        self.frm_daq_control.configure(height='200', text='Waveform acquisition', width='200')
        self.frm_daq_control.grid(row='1', column='1', pady='10')

        self.btn_start_daq = ttk.Button(self.frm_daq_control)
        self.btn_start_daq.configure(text='Start')
        self.btn_start_daq.pack(side='left',padx='5', pady='5')
        self.btn_start_daq.bind('<Button-1>', self.start_daq_clicked, add='')

        self.btn_stop_daq = ttk.Button(self.frm_daq_control)
        self.btn_stop_daq.configure(text='Stop')
        self.btn_stop_daq.pack(side='left',padx='5', pady='5')
        self.btn_stop_daq.bind('<Button-1>', self.stop_daq_clicked, add='')     


        self.frm_daq_binary = ttk.Labelframe(self.frm_daq_control)
        self.frm_daq_binary.configure(height='200', text='Binary file', width='200')
        self.frm_daq_binary.pack(side='left', padx='5', pady='5')

        self.btn_save_binary = ttk.Button(self.frm_daq_binary)
        self.btn_save_binary.configure(text='Save as')
        self.btn_save_binary.pack(padx='5', pady='5', side='left')
        self.btn_save_binary.bind('<Button-1>', self.save_binary_clicked, add='')

        self.ent_name_binary=tk.Entry(self.frm_daq_binary)
        self.ent_name_binary.configure(width='20')
        self.ent_name_binary.pack(side='right', padx='10')


        #MONITOR STUFF
        self.frm_daq_status = ttk.Labelframe(self.frm_data_acquisition)
        self.frm_daq_status.configure(text='Status')
        self.frm_daq_status.grid(row='2',pady="3",column='1', columnspan='2')


        self.lbl_temperature = tk.Label(self.frm_daq_status)
        self.lbl_temperature.configure(text='Temperature = 27 C')
        self.lbl_temperature.pack(side='left', padx='5', pady='5')

        self.lbl_daq_status = tk.Label(self.frm_daq_status, width=30)
        self.lbl_daq_status.configure(text='Board initialized!')
        self.lbl_daq_status.pack(side='left',padx='5', pady='5')


        #RATE monitor

        self.frm_rate_acquisition = ttk.Labelframe(self.frm_rate)
        self.frm_rate_acquisition.configure(text="Rate monitor")
        self.frm_rate_acquisition.grid(row='3', column='1', padx='10', pady='10', columnspan=3)        

        self.frm_rate_option = ttk.Labelframe(self.frm_rate_acquisition)
        self.frm_rate_option.configure(text="Monitor options")
        self.frm_rate_option.grid(row='0', column='0', padx='10', pady='10')

        self.lbl_delay = tk.Label(self.frm_rate_acquisition)
        self.lbl_delay.configure(text="Delay (s)")
        self.lbl_delay.grid(row='0', column='0', padx='5', pady='5')

        self.ent_delay = tk.Entry(self.frm_rate_acquisition)
        self.ent_delay.configure(width=3)
        self.ent_delay.grid(row='0', column='1', padx='5', pady='5')

        self.lbl_interval = tk.Label(self.frm_rate_acquisition)
        self.lbl_interval.configure(text="Interval (s)")
        self.lbl_interval.grid(row='1', column='0', padx='5', pady='5')

        self.ent_interval = tk.Entry(self.frm_rate_acquisition)
        self.ent_interval.configure(width=3)
        self.ent_interval.grid(row='1', column='1', padx='5', pady='5')

        self.print_screen_status = tk.IntVar()
        self.btn_print_screen = tk.Checkbutton(self.frm_rate_acquisition, variable=self.print_screen_status)
        self.btn_print_screen.configure(text = 'Print to screen')
        self.btn_print_screen.grid(row='2', column='0', padx='5', pady='5', columnspan='2')

        self.frm_rate_logfile = ttk.Labelframe(self.frm_rate_acquisition)
        self.frm_rate_logfile.configure(text="Logfile")
        self.frm_rate_logfile.grid(row='0', column='2', padx='10', pady='10', rowspan="2", columnspan='2')

        self.btn_open_logfile = tk.Button(self.frm_rate_logfile)
        self.btn_open_logfile.configure(text="Open Logfile")
        self.btn_open_logfile.pack(side='left', padx='5', pady='5')
        self.btn_open_logfile.bind('<Button-1>', self.open_logfile_clicked, add='')


        self.ent_logfile = tk.Entry(self.frm_rate_logfile)
        self.ent_logfile.configure(width=20)
        self.ent_logfile.pack(side='left', padx='5', pady='5')

        self.btn_start_monitor = tk.Button(self.frm_rate_acquisition)
        self.btn_start_monitor.configure(text="Start monitor")
        self.btn_start_monitor.grid(row='2', column='2', padx='5', pady='5')
        self.btn_start_monitor.bind('<Button-1>', self.start_monitor_clicked, add='')        
        
        self.btn_stop_monitor = tk.Button(self.frm_rate_acquisition)
        self.btn_stop_monitor.configure(text="Stop monitor")
        self.btn_stop_monitor.grid(row='2', column='3', padx='5', pady='5')
        self.btn_stop_monitor.bind('<Button-1>', self.stop_monitor_clicked, add='')



        #INPUT SETTING
        self.frm_analysis_setting = ttk.Labelframe(self.frm_plot)
        self.frm_analysis_setting.configure(text="Input setting")
        self.frm_analysis_setting.grid(row='0', column='0', padx='5', pady='5', rowspan="2")

        self.lbl_select_channel = tk.Label(self.frm_analysis_setting)
        self.lbl_select_channel.configure(text="Select channel to analyze")
        self.lbl_select_channel.grid(row='0', column='0', padx='5', pady='5', columnspan="2")

        self.channel_variable = tk.StringVar(root)
        self.channel_option = ["0","1","2","3","4","5","6","7","8","9","10","11","ALL"]
        self.channel_variable.set("ALL")

        self.btn_select_channel = tk.OptionMenu(self.frm_analysis_setting, self.channel_variable,*self.channel_option)
        self.btn_select_channel.grid(row='0', column='2', padx='5', pady='5')

        self.btn_open_analysis = ttk.Button(self.frm_analysis_setting)
        self.btn_open_analysis.configure(text='Open file')
        self.btn_open_analysis.grid(row='1', column='0', padx='5', pady='5')
        self.btn_open_analysis.bind('<Button-1>', self.open_analysis_clicked, add='')

        self.ent_analysis=tk.Entry(self.frm_analysis_setting)
        self.ent_analysis.configure(width="30")
        self.ent_analysis.grid(row='1', column='1', padx='5', pady='5', columnspan="3")

        self.ent_wf_skip=tk.Entry(self.frm_analysis_setting)
        self.ent_wf_skip.configure(width='4')
        self.ent_wf_skip.grid(row='2', column='1', padx='1', pady='5', columnspan="1")

        self.ent_wf_plot=tk.Entry(self.frm_analysis_setting)
        self.ent_wf_plot.configure(width='4')
        self.ent_wf_plot.grid(row='2', column='3', padx='1', pady='5', columnspan="1")

        self.lbl_wf_skip = tk.Label(self.frm_analysis_setting)
        self.lbl_wf_skip.configure(text="Waveform\n  to skip")
        self.lbl_wf_skip.grid(row='2', column='0', padx='5', pady='5', columnspan="1")

        self.lbl_wf_plot = tk.Label(self.frm_analysis_setting)
        self.lbl_wf_plot.configure(text="Waveform\n  to plot")
        self.lbl_wf_plot.grid(row='2', column='2', padx='5', pady='5', columnspan="1")

        self.trigger_variable=tk.IntVar()
        self.btn_trigger=tk.Checkbutton(self.frm_analysis_setting, variable=self.trigger_variable)
        self.btn_trigger.configure(relief='raised', text="Analyze waveform\n with maximum\n amplitude above (V)")
        self.btn_trigger.grid(row='3', column='0', padx='2', pady='5', columnspan="2")

        self.ent_trigger=tk.Entry(self.frm_analysis_setting)
        self.ent_trigger.configure(width='4')
        self.ent_trigger.grid(row='3', column='2', padx='2', pady='5', columnspan="1")



        #PLOT SETTING
        self.frm_plot_setting = ttk.Labelframe(self.frm_plot)
        self.frm_plot_setting.configure(text="Plot options")
        self.frm_plot_setting.grid(row='0', column='1', padx='5', pady='5')

        self.lbl_plot_type = tk.Label(self.frm_plot_setting)
        self.lbl_plot_type.configure(text="Plot waveform from")
        self.lbl_plot_type.grid(row='0', column='0', padx='5', pady='5', columnspan="1")

        self.plot_type_variable = tk.StringVar(root)
        self.plot_type = ["Random", "Beginning"]
        self.plot_type_variable.set("Beginning")

        self.btn_plot_type = tk.OptionMenu(self.frm_plot_setting, self.plot_type_variable,*self.plot_type)
        self.btn_plot_type.grid(row='0', column='1', padx='5', pady='5')


        self.overlap_variable=tk.IntVar()
        self.btn_overlap=tk.Checkbutton(self.frm_plot_setting, variable=self.overlap_variable)
        self.btn_overlap.configure(relief='raised', text="Overlap")
        self.btn_overlap.grid(row='0', column='2', padx='5', pady='5')


        self.btn_plot = tk.Button(self.frm_plot_setting)
        self.btn_plot.configure(text="Plot")
        self.btn_plot.grid(row='1', column='2', padx='5', pady='5')
        self.btn_plot.bind('<Button-1>', self.plot_clicked, add='')        

        #HISTO SETTING
        self.frm_histo_setting = ttk.Labelframe(self.frm_plot)
        self.frm_histo_setting.configure(text="Histogram options")
        self.frm_histo_setting.grid(row='1', column='1', padx='5', pady='5')

        self.lbl_lead = tk.Label(self.frm_histo_setting)
        self.lbl_lead.configure(text="Pedestal sample")
        self.lbl_lead.grid(row='0', column='0', padx='5', pady='5', columnspan="1")

        self.ent_pedestal=tk.Entry(self.frm_histo_setting)
        self.ent_pedestal.configure(width='4')
        self.ent_pedestal.grid(row='0', column='1', padx='5', pady='5', columnspan="1")


        self.histo_type_variable = tk.StringVar(root)
        self.histo_type = ["Charge", "Maximum", "Duration", "Time interval"]
        self.histo_type_variable.set("Maximum")

        self.btn_histo_type = tk.OptionMenu(self.frm_histo_setting, self.histo_type_variable,*self.histo_type)
        self.btn_histo_type.grid(row='1', column='0', padx='5', pady='5')


        self.pedestal_variable=tk.IntVar()
        self.btn_pedestal=tk.Checkbutton(self.frm_histo_setting, variable=self.pedestal_variable)
        self.btn_pedestal.configure(relief='raised', text="Pedestal\nsubtraction")
        self.btn_pedestal.grid(row='0', column='2', padx='5', pady='5')

        self.btn_histo = tk.Button(self.frm_histo_setting)
        self.btn_histo.configure(text="Histogram")
        self.btn_histo.grid(row='1', column='1', padx='5', pady='5')
        self.btn_histo.bind('<Button-1>', self.histo_clicked, add='')        


        # Main widget
        self.mainwindow = master


        #INITIALIZE STARTUP PARAMETERS

        self.initialize_board()


        def t_monitor():
            global t_board
        
            interval=30
            time.sleep(2)
            e_monitor.set()


            while(e_monitor.is_set()):
                e_timer.clear()
                stdin, stdout, stderr = client.exec_command("""bash get_param.sh -N 2 """)
                parameter=stdout.read()
                t_board=float(parameter[16:21])
            
                if e_log.is_set():
                    with open("logfile_tmp.txt", "a") as f:
                        f.write(str(parameter)+"\n")
                    print("Parameter saved to logfile")
                

                if e_acquisition.is_set():

                    channel_string, start_th_string, stop_th_string, lead_string, tail_string, v_bias_string = self.get_parameter_string()

                    os.system("""ssh """ + username + """@""" + ip_address + """ 'bash daq_set_hv.sh -N """+ channel_string+ """ -V """+v_bias_string+""" ' """)
                    print("V bias updated")

                self.lbl_temperature.configure(text="Temperature = "+ str(t_board) +" C")
                print("Temperature field updated")
                abortable_sleep(interval,e_timer)


        thread_monitor = threading.Thread(target=t_monitor)
        thread_monitor.deamon = True
        thread_monitor.start()    


    def open_logfile_clicked(self, event=None):
        name = tk.filedialog.askopenfilename(filetypes=(("Rate Logfile", "*.txt"),),title="Choose a file")
        self.ent_logfile.delete(0,'end')
        self.ent_logfile.insert(0,name)

    def initialize_board(self):


        with open("startup_parameter.json") as f:
            param=json.load(f)

        for ch in np.arange(0,12):
            self.ent_start[ch].insert(0,str(param["start_th"][ch]))
            self.ent_stop[ch].insert(0,str(param["stop_th"][ch]))
            self.ent_lead[ch].insert(0,str(param["lead"][ch]))
            self.ent_tail[ch].insert(0,str(param["tail"][ch]))
            self.ent_vbias[ch].insert(0,str(param["v_bias"][ch]))


        channel_string, start_th_string, stop_th_string, lead_string, tail_string, v_bias_string = self.get_parameter_string()

        if param["gain"]=="high":
            print("Setting gain to 20...")
            os.system("""ssh """ + username + """@""" + ip_address + """ './M4Comm -s "\$gsha#" ' &""")

        if param["gain"]=="low":
            print("Setting gain to 2...")
            os.system("""ssh """ + username + """@""" + ip_address + """ './M4Comm -s "\$gsla#" ' &""")

        print("Initializing board...")
        os.system("""ssh """ + username + """@""" + ip_address + """ 'date """ + date_format  + "'")
        os.system("""ssh """ + username + """@""" + ip_address + """ './SetTimeReg -t l'""")
        os.system("""ssh """ + username + """@""" + ip_address + """ 'bash daq_set_iob_delay.sh -N "{0..11}" -F """ + iob_delay+ """' """)
        
        print("Board initialized")
        
        print("Setting channels parametes...")
        os.system("""ssh """ + username + """@""" + ip_address + """ 'bash daq_run_launch.sh -j -N """+channel_string+""" -S """+start_th_string+""" -P """+stop_th_string+ """ -L """ + lead_string + """ -T """+ tail_string +""" ' """)
        

    def save_binary_clicked(self, event=None):
        bin_filename=asksaveasfilename(filetypes=(("Binary file", "*.bin"),),title="Open binary file")

        if bin_filename!=() and bin_filename != '':
            self.ent_name_binary.delete(0,'end')
            self.ent_name_binary.insert(0,str(bin_filename))
        os.system("touch "+bin_filename)

    def initialize_clicked(self, event=None):
        self.initialize_board()
    

    def load_parameter_clicked(self, event=None):
        name = tk.filedialog.askopenfilename(filetypes=(("Json File", "*.json"),),title="Choose a file")
        if name!=() and name != '':
            with open(name) as f:
                param = json.load(f)


            for ch in np.arange(0,12):
                self.ent_start[ch].delete(0,'end')
                self.ent_stop[ch].delete(0,'end')
                self.ent_lead[ch].delete(0,'end')
                self.ent_tail[ch].delete(0,'end')
                self.ent_vbias[ch].delete(0,'end')

                self.ent_start[ch].insert(0,str(param["start_th"][ch]))
                self.ent_stop[ch].insert(0,str(param["stop_th"][ch]))
                self.ent_lead[ch].insert(0,str(param["lead"][ch]))
                self.ent_tail[ch].insert(0,str(param["tail"][ch]))
                self.ent_vbias[ch].insert(0,str(param["v_bias"][ch]))

    def t_start_daq(self):  
        daq_read_tcp_thread = threading.Thread(target=t_daq_read_tcp)
        daq_read_tcp_thread.deamon = True
        daq_read_tcp_thread.start()

        channel_string, start_th_string, stop_th_string, lead_string, tail_string, v_bias_string = self.get_parameter_string()

        print(self.daq_type)
        time.sleep(1)

        if self.daq_type == "waveform" :


            os.system("nc 192.168.137.30 5000 > " + str(self.ent_name_binary.get()) + " &")


            time.sleep(1)

            stdin, stdout, stderr = client.exec_command("bash daq_run_launch.sh -N "+channel_string+" -S "+start_th_string+" -P "+stop_th_string+" -L " + lead_string + " -T "+ tail_string)
            print ("stderr: ", stderr.readlines())
            print ( stdout.readlines())


        if self.daq_type == "rate":

            name=self.ent_logfile.get()
            print(self.print_screen_status)

            if self.print_screen_status.get():
                os.system("nc 192.168.137.30 5000 | ./RateParser -a -t "+str(self.ent_interval.get())+" -d " +self.ent_delay.get()+ " -c 13 &")

            if not self.print_screen_status.get():
                os.system("nc 192.168.137.30 5000 | ./RateParser -a -t "+str(self.ent_interval.get())+" -d " +self.ent_delay.get()+ " >> "+name +"&")



            time.sleep(1)
            stdin, stdout, stderr = client.exec_command("bash daq_run_launch.sh -N "+channel_string+" -S "+start_th_string+" -P "+stop_th_string+" -L " + lead_string + " -T "+ tail_string)
            print ("stderr: ", stderr.readlines())
            print ( stdout.readlines())

    def start_daq_clicked(self, event=None):
        
        name = self.ent_name_binary.get()

        if name != "":
            self.lbl_daq_status.configure(text='Starting waveform acquisition')

            channel_string, start_th_string, stop_th_string, lead_string, tail_string, v_bias_string = self.get_parameter_string()


            self.daq_type="waveform"
            
            self.thread_start = threading.Thread(target=self.t_start_daq)
            self.thread_start.deamon = True
            self.thread_start.start()

            e_timer.set()
            e_acquisition.set()
            

            def t_size():

                while(e_acquisition.is_set()):
                    time.sleep(0.1) 
                    filesize = subprocess.check_output("du -h "+ str(name), shell=True)[:-len(name)+1]
                    self.lbl_daq_status.configure(text=str(filesize))
                
                self.lbl_daq_status.configure(text="Board ready!")


            self.thread_size = threading.Thread(target=t_size)
            self.thread_size.deamon = True
            self.thread_size.start()
        
        else: 
            print("Error: insert file name")
            self.lbl_daq_status.configure(text='Error: insert file name')

    def vbias_off_clicked(self, event=None):

        channel_string, start_th_string, stop_th_string, lead_string, tail_string, v_bias_string = self.get_parameter_string()
        #os.system("""ssh """ + username + """@""" + ip_address + """ 'bash daq_disable_hv.sh -N """+channel_string+""" ' &""")
        stdin, stdout, stderr = client.exec_command("""bash daq_disable_hv.sh -N """+channel_string)
        print(stdout.readlines())

    def stop_daq_clicked(self, event=None):

        e_acquisition.clear()

        name= self.ent_name_binary.get()
        
        channel_string, start_th_string, stop_th_string, lead_string, tail_string, v_bias_string = self.get_parameter_string()


        time.sleep(1)

        #os.system("""ssh """ + username + """@""" + ip_address + """ 'bash daq_run_stop.sh -N """+channel_string+" '")
        #os.system("""ssh """ + username + """@""" + ip_address + """ 'killall DaqReadTcp'""")
        stdin, stdout, stderr = client.exec_command("""bash daq_run_stop.sh -N """+channel_string)
        print(stdout.readlines())

        stdin, stdout, stderr = client.exec_command("""killall DaqReadTcp""")
        print(stdout.readlines())


        self.lbl_daq_status.configure(text="Board ready!")


    def set_parameter_clicked(self, event=None):

        channel_string, start_th_string, stop_th_string, lead_string, tail_string, v_bias_string = self.get_parameter_string()

        os.system("""ssh """ + username + """@""" + ip_address + """ 'bash daq_run_launch.sh -j -N """+channel_string+""" -S """+start_th_string+""" -P """+stop_th_string+ """ -L """ + lead_string + """ -T """+ tail_string +""" ' """)
        print("Setting HV values...")
        os.system("""ssh """ + username + """@""" + ip_address + """ 'bash daq_set_hv.sh -N """+channel_string+""" -V """+v_bias_string+""" ' """)


    def save_parameter_clicked(self, event=None):
        param={"start_th":[],"stop_th":[],"v_bias":[],"lead":[],"tail":[]}
        
        for ch in np.arange(0,12):
            param["start_th"].append(self.ent_start[ch].get())
            param["stop_th"].append(self.ent_stop[ch].get())
            param["lead"].append(self.ent_lead[ch].get())
            param["tail"].append(self.ent_tail[ch].get())
            param["v_bias"].append(self.ent_vbias[ch].get())

        name = tk.filedialog.asksaveasfilename(filetypes=(("Json File", "*.json"),),title="Choose a file")

        if name!=() and name != '' :
            with open(name, 'w') as f:
                json.dump(param, f)    


    def get_parameter_string(self):
        start_th_mv={}
        start_th={}
        v_bias = {} 

        stop_th_mv={}
        stop_th={}

        lead={}
        tail={}

        channel = {}

        v_bias_string = '"'
        channel_string = '"'
        lead_string = '"'
        tail_string = '"'
        start_th_string = '"'
        stop_th_string = '"'

        for ch in np.arange(0,12):

            if self.ch_status[ch].get():

                start_th_mv[ch] = self.ent_start[ch].get()
                if start_th_mv[ch] != '':
                    start_th[ch] = str(int(0x3fff) - int(v_to_adc[ch][0] * float(start_th_mv[ch])*0.001 + v_to_adc[ch][1]))
                else:
                    print("Insert value of starth th on ch "+str(ch)+". Value set to zero")
                    start_th[ch] = '0x3fff'

                stop_th_mv[ch] = self.ent_stop[ch].get()
                if stop_th_mv[ch] != '':
                    stop_th[ch] = str(int(0x3fff) - int(v_to_adc[ch][0] * float(stop_th_mv[ch])*0.001 + v_to_adc[ch][1]))
                else :
                    print("Insert value of stop th on ch "+str(ch)+". Value set to zero")
                    stop_th[ch] = '0x3fff'

                lead[ch] = self.ent_lead[ch].get()
                if lead[ch] == '':
                    print("Insert value of lead sample on ch "+str(ch)+". Value set to zero")
                    lead[ch]='0'

                tail[ch] = self.ent_tail[ch].get()
                if tail[ch] == '':
                    print("Insert value of tail sample on ch "+str(ch)+". Value set to zero")
                    tail[ch]='0'

                v_bias[ch] = self.ent_vbias[ch].get()
                if v_bias[ch] != '':
                    #v_bias[ch] = (float(v_bias[ch])-v_bias_conv[ch][1])/v_bias_conv[ch][0]
                    v_bias[ch]=v_adc(float(v_bias[ch]), t_board,ch)
                else:
                    print("Insert value of v bias on ch "+str(ch)+". Value set to zero")
                    v_bias[ch] = 0

                v_bias_string = v_bias_string + str(int(v_bias[ch])) + " "
                channel_string = channel_string + str(ch) + " "
                lead_string = lead_string + lead[ch] + " "
                tail_string = tail_string + tail[ch] + " "
                start_th_string = start_th_string + start_th[ch] + " "
                stop_th_string = stop_th_string + stop_th[ch] + " "

            if ch == 11:
                channel_string = channel_string  + '"'
                lead_string = lead_string  + '"'
                tail_string = tail_string  + '"'
                start_th_string = start_th_string + '"'
                stop_th_string = stop_th_string + '"'
                v_bias_string = v_bias_string  + '"'


            else:
                pass        

        option_string=[channel_string, start_th_string, stop_th_string, lead_string, tail_string, v_bias_string]
        return option_string 

    def start_monitor_clicked(self, event=None):
        

        self.daq_type="rate"
            
        self.thread_start = threading.Thread(target=self.t_start_daq)
        self.thread_start.deamon = True
        self.thread_start.start()

        e_timer.set()
        e_acquisition.set()

    def stop_monitor_clicked(self, event=None):
        channel_string, start_th_string, stop_th_string, lead_string, tail_string, v_bias_string = self.get_parameter_string()

        e_log.clear()
        e_acquisition.clear()

        if self.print_screen_status.get():
            print("Stopping acquisition...")
            os.system("""ssh """ + username + """@""" + ip_address + """ 'bash daq_run_stop.sh -N """+channel_string+"'")
            time.sleep(1)
            os.system("""ssh """ + username + """@""" + ip_address + """ 'killall DaqReadTcp'""")
            time.sleep(1)
            os.system("killall RateParser")         

        else:
            print("Stopping acquisition...")
            os.system("""ssh """ + username + """@""" + ip_address + """ 'bash daq_run_stop.sh -N """+channel_string+"'")
            #os.system("pkill -f loop_temp.py")
            time.sleep(1)
            os.system("""ssh """ + username + """@""" + ip_address + """ 'killall DaqReadTcp'""")
            time.sleep(1)
            os.system("killall RateParser")
            time.sleep(1)
            #os.system("python3 fusion.py "+name)


    def open_analysis_clicked(self, event=None):
        name = tk.filedialog.askopenfilename(filetypes=(("Binary file", "*.bin"),),title="Choose a file")
        if name!=() and name != '':
            self.ent_analysis.delete(0,'end')
            self.ent_analysis.insert(0, name)

    def t_plot(self):


        filename=self.ent_analysis.get()
        print(filename)

        filename_txt= filename.split(sep="/")[-1][:-4]+".txt"

        hit_to_plot = self.ent_wf_plot.get()
        hit_to_skip = self.ent_wf_skip.get()
        
        if hit_to_plot == '':
            hit_to_plot=0
        if hit_to_skip == '':
            hit_to_skip =0  
        

        if self.channel_variable.get() == "ALL":
            filename_txt= filename.split(sep="/")[-1][:-4]+"_chall"+".txt"
            print(filename_txt)
            
            os.system("./HitViewer -p -c -1 -z -r -f "+str(filename)+" -n "+str(hit_to_plot) +" -o "+str(hit_to_skip)+" > " + filename_txt)

            with open(filename_txt) as data:
                waveform=data.read().splitlines()

            waveform=np.array(waveform)

            waveform_sorted={}
            for ch in np.arange(0,12):
                waveform_sorted[ch]=[]

            for wave in waveform:
                wave_split=wave.split("\t")[:-1]
                waveform_sorted[int(wave_split[0].split(":")[-1])].append(np.array(wave_split[1:]).astype(int))

            self.count=0

            def onclick_beginning(event):

                index=[(0,0),(1,0),(2,0),(0,1),(1,1),(2,1),(0,2),(1,2),(2,2),(0,3),(1,3),(2,3)]

                if event.button == 1:
                    for ch in np.arange(0,12):
                        
                        if len(waveform_sorted[ch])!=0:

                            if self.plot_type_variable.get()!="Beginning":
                                self.count=random.randint(0, len(waveform_sorted[ch])-1)
                            
                            y=waveform_sorted[ch][self.count]
                            y= np.array([convert_adc_to_v(element,int(ch))  for element in y])
                            x=np.arange(0,y.size*4,4)

                            if not self.overlap_variable.get():
                                ax[index[ch]].clear()

                            ax[index[ch]].plot(x,y)
                            ax[index[ch]].grid(True)
                            ax[index[ch]].set_title("Wf # "+str(self.count)+" ch "+str(ch))
                            #ax[index[ch]].set_xlabel("Time (ns)")
                            #ax[index[ch]].set_ylabel("Amplitude (mV)")
                            
                plt.draw() #redraw
                
                if self.plot_type_variable.get()=="Beginning":
                    self.count = self.count + 1 

            

            fig,ax=plt.subplots(3,4)
            plt.tight_layout(pad=2, w_pad=1, h_pad=1)
            fig.canvas.mpl_connect('button_press_event',onclick_beginning)
            plt.show()



        else:
            ch=self.channel_variable.get()
            print(ch)
            filename_txt= filename.split(sep="/")[-1][:-4]+"_ch"+str(ch)+".txt"
            print(filename_txt)

            os.system("./HitViewer -p -c " + str(ch) + " -f "+str(filename)+" -n "+str(hit_to_plot) +" -o "+str(hit_to_skip)+" > " + filename_txt)

            with open(filename_txt) as data:
                waveform=data.read().splitlines()


            if self.trigger_variable.get():
                for wave in waveform[1:]:
                    if np.array(wave.split("\t")[:-1]).astype(int).max()<= convert_v_to_adc(float(self.ent_trigger.get()),int(ch)):
                        waveform.remove(wave)

            waveform=np.array(waveform)

            self.count=0

            def onclick_beginning(event):

                if event.button == 1:
                    y=np.array(waveform[self.count].split("\t")[:-1]).astype(int)
                    y= np.array([convert_adc_to_v(element,int(ch))  for element in y])
                    x=np.arange(0,y.size*4,4)
                #clear frame
                    if not self.overlap_variable.get():
                        plt.clf()

                ax1 = plt.gca()
                ax1.set_title("waveform # "+ str(self.count))
                ax1.set_ylabel("Amplitude (mV)")
                ax1.set_xlabel("Time (ns)")
                plt.grid(True)
                ax1.plot(x,y)
                plt.draw() #redraw
                if self.plot_type_variable.get()=="Beginning":
                    self.count = self.count + 1 
                else:
                    self.count= random.randint(0, len(waveform)-1)
            


            fig,ax1=plt.subplots()
            ax1.set_title("waveform # "+ str(self.count))
            ax1.set_ylabel("Amplitude (V)")
            ax1.set_xlabel("Time")
            fig.canvas.mpl_connect('button_press_event',onclick_beginning)
            plt.show()

    def plot_clicked(self, event=None):

        

        self.thread_plot = threading.Thread(target=self.t_plot)
        self.thread_plot.deamon = True
        self.thread_plot.start()


    def t_histo(self):

        filename=self.ent_analysis.get()
        print(filename)

        filename_txt= filename.split(sep="/")[-1][:-4]+".txt"

        hit_to_plot = self.ent_wf_plot.get()
        hit_to_skip = self.ent_wf_skip.get()
        
        if hit_to_plot == '':
            hit_to_plot=0
        if hit_to_skip == '':
            hit_to_skip =0  
        

        if self.channel_variable.get() == "ALL":
            filename_txt= filename.split(sep="/")[-1][:-4]+"_chall"+".txt"
            
            os.system("./HitViewer -p -c -1 -z -r -f "+str(filename)+" -n "+str(hit_to_plot) +" -o "+str(hit_to_skip)+" > " + filename_txt)

            with open(filename_txt) as data:
                waveform=data.read().splitlines()

            waveform=np.array(waveform)

            waveform_sorted={}
            for ch in np.arange(0,12):
                waveform_sorted[ch]=[]

            for wave in waveform:
                wave_split=wave.split("\t")[:-1]
                waveform_sorted[int(wave_split[0].split(":")[-1])].append(np.array(wave_split[1:]).astype(int))


            maximum={}
            charge={}
            duration={}

            n_ch=[]

            for ch in waveform_sorted.keys():
                if len(waveform_sorted[ch])!=0:
                    n_ch.append(ch)

            print(n_ch) 

            if len(n_ch)<=4:
                row=1
                column=len(n_ch)

            elif len(n_ch)>4 and len(n_ch) <=8:
                row=2
                column=4

            else:
                row=3
                column=4

            fig,ax = plt.subplots(row,column)
            plt.tight_layout()
            #plt.tight_layout(pad=2, w_pad=1, h_pad=1)


            count=0
            for ch in waveform_sorted.keys():

                if len(waveform_sorted[ch])!=0:
                    maximum[ch]=[]
                    duration[ch]=[]
                    charge[ch]=[]

                    for wave in waveform_sorted[ch]:
                        if len(wave) != 0:
                            if self.histo_type_variable.get()=="Maximum":
                                maximum[ch].append(wave.max())

                            if self.histo_type_variable.get()=="Duration":
                                duration[ch].append(wave.size*4)

                            if self.histo_type_variable.get()=="Charge":
                                if self.pedestal_variable.get():
                                    pedestal=int(self.ent_pedestal.get())
                                    wave=convert_adc_to_v(wave, int(ch))
                                    charge[ch].append((wave*(4/50)).sum()-(wave[:pedestal].mean()*wave.size))

                                else:
                                    wave=convert_adc_to_v(wave, int(ch))
                                    charge[ch].append((wave*(4/50)).sum())
                    
                    #ax[count].set_xlabel("Max amplitude (mV)")
                    #ax[count].set_ylabel("Counts")
                    ax[count].set_title("ch "+str(ch)) 
                    if self.histo_type_variable.get()=="Maximum":
                        ax[count].hist(convert_adc_to_v(np.array(maximum[ch]).astype(int), int(ch)))
                    
                    if self.histo_type_variable.get()=="Duration":
                        ax[count].hist(duration[ch])

                    if self.histo_type_variable.get()=="Charge":
                        ax[count].hist(charge[ch])

                    count=count+1

            plt.show()


        else:
            ch=self.channel_variable.get()
            filename_txt= filename.split(sep="/")[-1][:-4]+"_ch"+str(ch)+".txt"

            os.system("./HitViewer -p -c " + str(ch) + " -f "+str(filename)+" -n "+str(hit_to_plot) +" -o "+str(hit_to_skip)+" > " + filename_txt)

            with open(filename_txt) as data:
                waveform=data.read().splitlines()   

            waveform=np.array(waveform)


            if self.histo_type_variable.get()=="Maximum":
                maximum=[]
                for wave in waveform:
                    if wave != "":
                        wave=np.array(wave.split("\t")[:-1]).astype(int)
                        if self.trigger_variable.get():
                            if wave.max() >= convert_v_to_adc(float(self.ent_trigger.get()),int(ch)):

                                maximum.append(wave.max())

                        else:
                            maximum.append(wave.max())

                fig,ax = plt.subplots()
                ax.set_xlabel("Max amplitude (mV)")
                ax.set_ylabel("Counts")
                ax.set_title("Max amplitude histogram") 
                ax.set_xlim(0,convert_adc_to_v(np.array(maximum).astype(int), int(ch)).max())
                ax.hist(convert_adc_to_v(np.array(maximum).astype(int), int(ch)), bins=np.arange(0,np.array(convert_adc_to_v(np.array(maximum).astype(int), int(ch) )).max()))
                plt.show()

            if self.histo_type_variable.get()=="Charge":
                charge=[]
                for wave in waveform:
                    if wave != "":
                        wave=np.array(wave.split("\t")[:-1]).astype(int)
                        if self.trigger_variable.get():

                            if wave.max() >= convert_v_to_adc(float(self.ent_trigger.get()),int(ch)):

                                if self.pedestal_variable.get():
                                    pedestal=int(self.ent_pedestal.get())
                                    wave=convert_adc_to_v(wave, int(ch))
                                    charge.append((wave*(4/50)).sum()-(wave[:pedestal].mean()*wave.size))

                                else:
                                    wave=convert_adc_to_v(wave, int(ch))
                                    charge.append((wave*(4/50)).sum())
                        else:
                            if self.pedestal_variable.get():
                                pedestal=int(self.ent_pedestal.get())
                                wave=convert_adc_to_v(wave, int(ch))
                                charge.append((wave*(4/50)).sum()-(wave[:pedestal].mean()*wave.size))

                            else:
                                wave=convert_adc_to_v(wave, int(ch))
                                charge.append((wave*(4/50)).sum())


                fig,ax = plt.subplots()
                ax.set_xlabel("Charge (pC)")
                ax.set_ylabel("Counts")
                ax.set_title("Charge histogram") 
                ax.hist(charge)
                plt.show()

            if self.histo_type_variable.get()=="Duration":
                duration=[]
                for wave in waveform:
                    if wave != "":
                        wave=np.array(wave.split("\t")[:-1]).astype(int)

                        if self.trigger_variable.get():
                            if wave.max() >= convert_v_to_adc(float(self.ent_trigger.get()),int(ch)):
                                duration.append(wave.size*4)
                        else:  
                            duration.append(wave.size*4)


                fig,ax = plt.subplots()
                ax.set_xlabel("Duration (ns)")
                ax.set_ylabel("Counts")
                ax.set_title("Duration histogram") 
                ax.hist(duration)
                plt.show()



    def histo_clicked(self, event=None):


        self.thread_histo = threading.Thread(target=self.t_histo)
        self.thread_histo.deamon = True
        self.thread_histo.start()



    def run(self):
        self.mainwindow.mainloop()


def on_exit():
    e_monitor.clear()
    e_timer.set()
    root.destroy()

if __name__ == '__main__':
    import tkinter as tk
    root = tk.Tk()
    root.title("WaveBoard Controller Ultra")
    root.protocol("WM_DELETE_WINDOW", on_exit)
    app = WbControllerUltraApp(root)
    app.run()

