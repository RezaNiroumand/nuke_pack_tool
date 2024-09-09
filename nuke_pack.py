import nuke
import os
import fnmatch
import sys
from PySide2 import QtCore, QtUiTools, QtWidgets, QtGui
import time

import threading



# self.nuke_file_address_root_address = [

# ['T:/dwtv/mmo/00Prod/02_Episodes/S_01/101/99_CG/03_Comp/001_001/MMO_101_001_001_Comp_v001_LS.nk','T:/dwtv/mmo/00Prod/02_Episodes/S_01/'],
# ['L:/ODDBOT/WTP/LEMONCORE/WTP_PROJ/animation/season_01/100/01/001/COMP/WTP_100_01_001_COMP_002_LS.nk','L:/ODDBOT/WTP/LEMONCORE/WTP_PROJ/animation/season_01/'],
# ['M:/CAPT/LEMONCORE/CAPT_PROJ/animation/season_02/061/01/005/COMP/CAPT_061_01_005_COMP_001_LS.nk','M:/CAPT/LEMONCORE/CAPT_PROJ/animation/season_02/'], 
# ['D:/reza_niroumand/Script/nuke_pack/samples/sample_project/Prod/ep002/Seq001/shot030/comp/wip/ep002_Seq001_shot030_Comp_Lemonsky_v007.nk','D:/reza_niroumand/Script/nuke_pack/samples/sample_project/Prod/ep002/'],   
# ['P:/Pokemon_TCG/Prod/ep002/Seq001/shot030/comp/wip/ep002_Seq001_shot030_Comp_Lemonsky_v001.nk','P:/Pokemon_TCG/Prod/']

# ]






SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')+'/'



WRAP_IT_UP_PATH = SCRIPT_PATH+'WrapItUp_Edited.py'
WRAP_IT_UP_SIZE_PATH = SCRIPT_PATH+'WrapItUp_NoCopy.py'
CHECK_EXISTING_NUKE_FILE_LIST_ON_DISK = False
NUKE_EXE_PATH = nuke.env['ExecutablePath']




class nuke_pack(QtWidgets.QWidget):

    def __init__(self, parent=None):

        super(nuke_pack, self).__init__()
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle('Nuke Pack')
        icon = QtGui.QIcon(SCRIPT_PATH+'icon.ico')
        self.setWindowIcon(icon)
        self.resize(600, 100)
        self.setAcceptDrops(True)
        self.ui = SCRIPT_PATH+'nuke_pack.ui'
        loader = QtUiTools.QUiLoader()
        ui_file = QtCore.QFile(self.ui)
        ui_file.open(QtCore.QFile.ReadOnly)
        self.theMainWidget = loader.load(ui_file)
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self.theMainWidget)
        self.setLayout(main_layout)
        self.help_path = SCRIPT_PATH + 'USER_MANUAL.pdf'
        self.EXTERNAL_PROJECT_ENV = ''
        self.nuke_file_address_root_address_pair = []
        self.nuke_file_address_root_address = []
        self.scan_files = True
        
        menu_bar = self.theMainWidget.menuBar()
        menu_help = menu_bar.findChild(QtWidgets.QMenu, "menuHelp")
        help_action = menu_help.actions()[0]
        help_action.triggered.connect(self.showHelp)

        self.lineEdit_nuke_file = self.findChild(QtWidgets.QLineEdit, "lineEdit_nuke_file")
        self.lineEdit_nuke_file.textChanged.connect(lambda text: self.text_change(self.lineEdit_nuke_file, text))
        
        self.lineEdit_root = self.findChild(QtWidgets.QLineEdit, "lineEdit_root")
        self.lineEdit_root.textChanged.connect(lambda text: self.text_change(self.lineEdit_root, text))
        
        self.lineEdit_destination = self.findChild(QtWidgets.QLineEdit, "lineEdit_destination")
        self.lineEdit_destination.textChanged.connect(lambda text: self.text_change(self.lineEdit_destination, text))
                
        
        self.pushButton_nuke_file = self.findChild(QtWidgets.QPushButton, "pushButton_nuke_file")
        self.pushButton_nuke_file.clicked.connect(self.browse_nuke_file)
        
        self.pushButton_root = self.findChild(QtWidgets.QPushButton, "pushButton_root")
        self.pushButton_root.clicked.connect(self.browse_root_folder)
        
        self.pushButton_destination = self.findChild(QtWidgets.QPushButton, "pushButton_destination")
        self.pushButton_destination.clicked.connect(self.browse_destination_folder)
        
        self.pushButton_generate_batch = self.findChild(QtWidgets.QPushButton, "pushButton_generate_batch")
        self.pushButton_generate_batch.clicked.connect(self.submit_addresses)
        
        self.label_generated = self.findChild(QtWidgets.QLabel, "label_generated")  
    
        
    def browse_nuke_file(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select File", "", "Nuke Files (*.nk)")
        if file_path:
            self.lineEdit_nuke_file.setText(file_path)


    def browse_root_folder(self):
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.lineEdit_root.setText(folder_path)


    def browse_destination_folder(self):
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.lineEdit_destination.setText(folder_path)

    
    def text_change(self,*argv):        
        a = argv[1].replace('\\', '/')
        argv[0].setText(a)
    


    def submit_addresses(self):

        nuke_file = self.lineEdit_nuke_file.text()
        root_folder = self.lineEdit_root.text()
        self.destination_path = self.lineEdit_destination.text()
        
        if (not nuke_file) or (not root_folder) or (not self.destination_path):
            QtWidgets.QMessageBox.critical(self, "Invalid Paths", "Please provide valid file and folder addresses.")
        else:
            
            if not root_folder.endswith('/'):
                root_folder = root_folder+'/' 
            if not self.destination_path.endswith('/'):
                self.destination_path = self.destination_path+'/'
            
            if os.path.isfile(nuke_file) and os.path.isdir(root_folder) and os.path.isdir(self.destination_path):
                self.nuke_file_address_root_address_pair.append(nuke_file)
                self.nuke_file_address_root_address_pair.append(root_folder)
                self.nuke_file_address_root_address.append(self.nuke_file_address_root_address_pair)
                
                

                self.run()
            else:
                QtWidgets.QMessageBox.critical(self, "Invalid Paths", "Please provide valid file and folder addresses.") 


    def showHelp(self):
        os.startfile(self.help_path)


    def run(self):
        self.t = threading.Thread(target=self.get_nuke_files)
        self.t.start()

    def blink(self):
        while self.scan_files == True:
            self.label_generated.setText('scanning all nuke files.')
            time.sleep(1)
            self.label_generated.setText('scanning all nuke files...')
            time.sleep(1)
            self.label_generated.setText('scanning all nuke files......')
            time.sleep(1)
        else:
            self.label_generated.setText('batch file saved here:'+ self.destination_path + 'nuke_pack.bat') 
        
    def get_nuke_files(self):
        self.t2 = threading.Thread(target=self.blink)
        self.t2.start()

        depth = self.nuke_file_address_root_address[0][0].count('/')
        root_dir = self.nuke_file_address_root_address[0][1]
        self.label_generated.setText('scanning all nuke files')
        self.nk_files = []
        if ('animation/season_') in self.nuke_file_address_root_address[0][1]:
            project = ('local') 
        elif ('00Prod/02_Episodes/S_') in self.nuke_file_address_root_address[0][1]:
            project = ('dreamworks')
        elif ('Pokemon_TCG/Prod') in self.nuke_file_address_root_address[0][1]:
            project = ('TCG')       
        for dirpath, dirnames, filenames in os.walk(root_dir):
            dirpath = dirpath.replace('\\', '/')
            if project == 'local':
                
                if 'COMP' in dirpath : # For local
                    for filename in fnmatch.filter(filenames, '*.nk'):
                        if (dirpath+'/'+filename).count('/') == depth:
                            self.nk_files.append(dirpath+'/'+filename)


            elif project == 'dreamworks':
                if '03_Comp' in dirpath: # for dreamworks
                    for filename in fnmatch.filter(filenames, '*.nk'):
                        if (dirpath+'/'+filename).count('/') == depth:
                            self.nk_files.append(dirpath+'/'+filename) 
 
            if project == 'TCG':
                if 'comp' in dirpath and 'wip' in dirpath: # for TCG
                    for filename in fnmatch.filter(filenames, '*.nk'):
                        if (dirpath+'/'+filename).count('/') == depth:
                            self.nk_files.append(dirpath+'/'+filename)
       
        
        self.main()


    def filter_nuke_files(self, all_nuke_paths, project, project_nuke_files_prefix, project_nuke_files_length):
        
        # local
        
        if project == 'local':

            all_wtp_nuke_valid_paths = []        
            for item in all_nuke_paths:
                if len(item.split('/')[-1])== project_nuke_files_length and project_nuke_files_prefix in item and '_COMP_' in item and '_LS.nk' in item:
                    all_wtp_nuke_valid_paths.append(item)
            
            last_versions = {}
            for file_path in all_wtp_nuke_valid_paths:
                unique_key = "_".join(file_path.split("_")[:-2])
                version_number = int(file_path.split("_")[-2])
                if unique_key in last_versions and version_number > last_versions[unique_key]:
                    last_versions[unique_key] = version_number
                elif unique_key not in last_versions:
                    last_versions[unique_key] = version_number
            result_list = ['{}_{}_LS.nk'.format(key, str(last_versions[key]).zfill(3)) for key in last_versions]
            return result_list
        # dreamworks

        if project == 'dreamworks':
            
            all_mmo_nuke_valid_paths = []       
            for item in all_nuke_paths:
                length = len(item.split('/')[-1])
                if (length == project_nuke_files_length or length == (project_nuke_files_length+5) or length == (project_nuke_files_length+1)) and project_nuke_files_prefix in item and '_Comp_v' in item and '_LS.nk' in item:
                    all_mmo_nuke_valid_paths.append(item)

            
            last_versions = {}
            for file_path in all_mmo_nuke_valid_paths: 
                unique_key = "_".join(file_path.split("_v")[0].split("_")[:-1])+'_Comp'
                version_number = int(file_path.split("_v")[1].split("_")[0])    
                if unique_key in last_versions and version_number > last_versions[unique_key]:
                    last_versions[unique_key] = version_number
                elif unique_key not in last_versions:
                    last_versions[unique_key] = version_number
            result_list = ['{}_v{}_LS.nk'.format(key, str(last_versions[key]).zfill(3)) for key in last_versions]       
            return result_list

        # TCG

        if project == 'TCG':
            
            all_tcg_nuke_valid_paths = []        
            for item in all_nuke_paths:
                if len(item.split('/')[-1])== project_nuke_files_length and '_Seq' in item and '_shot' in item and '_Comp_Lemonsky_v' in item:
                    all_tcg_nuke_valid_paths.append(item)

            last_versions = {}
            for file_path in all_tcg_nuke_valid_paths:
                unique_key = "_v".join(file_path.split("_v")[:-1])
                version_number = int(file_path.split("_v")[1].split(".")[0][1:])
                if unique_key in last_versions and version_number > last_versions[unique_key]:
                    last_versions[unique_key] = version_number
                elif unique_key not in last_versions:
                    last_versions[unique_key] = version_number
            result_list = ['{}_v{}.nk'.format(key, str(last_versions[key]).zfill(3)) for key in last_versions]   
            return result_list


    def main(self):
        for item in self.nuke_file_address_root_address:



            project_nuke_files_prefix = ''

            if ('animation/season_') in item[1]:

                project_nuke_files_prefix = item[0].split('/')[-1].split('_')[0]+'_'
                project_nuke_files_length = len(item[0].split('/')[-1])       
                nuke_files_list_file_name = project_nuke_files_prefix[:-1]


                result_list = self.filter_nuke_files(self.nk_files,'local', project_nuke_files_prefix, project_nuke_files_length)
            
            elif ('00Prod/02_Episodes/S_') in item[1]:
                self.EXTERNAL_PROJECT_ENV = 'set NUKE_PATH='+SCRIPT_PATH+'DW_ENV'+';%NUKE_PATH%'

                
                project_nuke_files_prefix = item[0].split('/')[-1].split('_')[0]+'_'
                project_nuke_files_length = len(item[0].split('/')[-1])        
                nuke_files_list_file_name = project_nuke_files_prefix[:-1]



                result_list = self.filter_nuke_files(self.nk_files,'dreamworks',project_nuke_files_prefix, project_nuke_files_length)
            
            elif ('Pokemon_TCG/Prod') in item[1]:
       
                project_nuke_files_length = len(item[0].split('/')[-1])
                nuke_files_list_file_name = item[0].split('/')[1]
                project_nuke_files_prefix = nuke_files_list_file_name


                result_list = self.filter_nuke_files(self.nk_files,'TCG', project_nuke_files_prefix, project_nuke_files_length)

        


        env_variables = os.environ

        env_variables_file_path = self.destination_path + 'env_variables.txt'      
        with open(env_variables_file_path, 'w') as file:
            for key, value in env_variables.items():
                file.write('{}={}\n'.format(key, value))

        batch_file_header = '''@echo on

        REM Read and set environment variables from the file
        for /f "usebackq tokens=1* delims==" %%A in ("'''+env_variables_file_path+'''") do (
            set "%%A=%%B"
        )
        '''
        result_list = sorted(result_list)
        bat_file_path = self.destination_path + 'nuke_pack.bat'
        with open(bat_file_path, 'w') as file:
            file.writelines(batch_file_header)
            file.write("\n")
            file.write(self.EXTERNAL_PROJECT_ENV+"\n")                    
            file.write(self.destination_path[0:2]+"\n")
            file.write('cd '+self.destination_path+"\n")
            for item in result_list:           
                folder_name = item.split('/')[-1].split('.')[0]            
                file.write('mkdir '+ folder_name +"\n")
                file.write(('"'+NUKE_EXE_PATH+'" -ti "'+WRAP_IT_UP_PATH+'" -nk "'+item+'" -o "'+self.destination_path+folder_name+'" -pd 3 -s\n').replace('/','\\'))
        self.scan_files = False


        #calculate_files_size_batch_file
        batch_file_header = '''@echo off

        REM Read and set environment variables from the file
        for /f "usebackq tokens=1* delims==" %%A in ("'''+env_variables_file_path+'''") do (
            set "%%A=%%B"
        )
        '''
        bat_file_path = self.destination_path + 'calculate_files_size.bat'
        with open(bat_file_path, 'w') as file:
            file.writelines(batch_file_header)
            file.write("\n")
            file.write(self.EXTERNAL_PROJECT_ENV+"\n")                    
            file.write(self.destination_path[0:2]+"\n")
            file.write('cd '+self.destination_path+"\n")
            for item in result_list:           
                folder_name = item.split('/')[-1].split('.')[0]            
                file.write('mkdir '+ folder_name +"\n")
                file.write(('"'+NUKE_EXE_PATH+'" -ti "'+WRAP_IT_UP_SIZE_PATH+'" -nk "'+item+'" -o "'+self.destination_path+folder_name+'" -pd 3 -s\n').replace('/','\\'))
        
     




try:
    UI.close()
except:
    pass
UI = nuke_pack()
UI.show()
