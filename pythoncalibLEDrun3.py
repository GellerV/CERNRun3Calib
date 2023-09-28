
from rundbapi import rundbapi
import os
import re
import glob
import ROOT
 

from datetime import datetime
# https://gitlab.cern.ch/lhcb-online/rundbapi/-/blob/master/rundbapi/rundbapi.py
class RUNINFO:
    def __init__(self, runid, endtime, inittime, timerange):
        self.runid =runid
        self.endtime =endtime 
        self.inittime = inittime
        self.timerange = timerange
        
def duration_of_stable_beams(history):
    # what about using "start_date" and "timestamp"?
    # the first seems to correspond to the PHYSICS timestamp
    # but the second is earlier than DUMP? compare:
    # https://lbrundb.cern.ch/api/fill/9153/
    # https://lbrundb.cern.ch/run/fill/9153/
    history_list = list(history.items())
    for i,(ts_dump,state_dump) in enumerate(history_list):
        if state_dump == "DUMP":
            for ts_physics,state_physics in history_list[i+1:]:
                if state_physics == "PHYSICS":
                    return ts_dump - ts_physics
    return 0
    

def findRunJustBeforeLastDump():
    # iterate fills in reverse chronological order
    fills = sorted(rundbapi.get_physics_fills()["fills"], key=lambda f: f["fill_id"], reverse=True)
    runbeflastdump= 0
    timeruninit = 0
    runid = 0
    for fill in fills:
        fill_id = fill.get('fill_id')
        runs_info = rundbapi.get_runs_in_fill(fill_id)
        if isinstance(runs_info, list) and len(runs_info) > 0:
            run_ids = []
            State_ids = []
            for run in runs_info:
                if 'runid' in run:
                    run_ids.append(run['runid'])
                    if 'LHCState' in run:
                        State_ids.append(run['LHCState'])
                    else:
                        print(f'Aucune information dans {fill_id}.')
        # Trouver le numéro de run correspondant à "NO_BEAM" précédé de "PHYSICS dans le fill en cours (avec d'autres conditions)"
        for i in range(1, len(State_ids)):
            if State_ids[i] == "PHYSICS" and State_ids[i - 1] == "ADJUST"or State_ids[i - 1] == "RAMP" or State_ids[i - 1] == "PHYS_ADJUST":
                runinit = run_ids[0] + i
                if runinit>timeruninit: 
                    timeruninit  = runinit
            if State_ids[i] == "NO_BEAM" and State_ids[i - 1] == "PHYSICS":
                run_id = run_ids[0] + i-1  # 
                # Condition pour obtenir le dernier run (le plus grand)
                if run_id>runid: 
                    runid  = run_id
                    break
   
    
    Timerunendinfo = rundbapi.get_run_info(timeruninit)
    inittime =Timerunendinfo['starttime'] 
   
    Timerunendinfo = rundbapi.get_run_info(runid)
    endtime =Timerunendinfo['endtime']
   
    timerange =(endtime-inittime).seconds
    
    runinfo = RUNINFO(runid, endtime, inittime,timerange )
  
    return runinfo
                
    raise RuntimeError()





def saveset_name(run):
    TASK_NAME = "CaloRelativeCalib"
    return f"/hist/Savesets/ByRun/{TASK_NAME}/{run // 10000}0000/{run // 1000}000/{TASK_NAME}-run{run}.root"

def updateWasAlreadyMadeFor(run):
    return checkIfSavesetExists(run)

def find_input_savesets(run, duration_s=75*60):
    """Find savesets ending at run `run` and having the given total duration"""
    
    return filenames
def list_savesets(run):
  
    # Spécifiez le chemin complet du répertoire
    repertoire = "/hist/Savesets/"+str(run.endtime.year)+"/LHCb/CaloMon/"+str(run.endtime.month).zfill(2)+"/"+str(run.endtime.day).zfill(2)+"/"
    
    # Spécifiez le modèle de numéro à rechercher
    numero_recherche = str(run.runid)
    listsavesets = []
    startlist = ((run.endtime).timestamp()-900-4500)#-900-4500
    endlist =((run.endtime).timestamp()-900)#-900
   
    
    # Liste tous les fichiers dans le répertoire
    fichiers_dans_repertoire = os.listdir(repertoire)

    pattern =r'-(\d{8})T(\d{6})'
    
    # Parcourez la liste des fichiers
    for fichier in fichiers_dans_repertoire:
         match = re.search(pattern, fichier)
         if match:
             date_part = match.group(1)
             heure_part = match.group(2)
        
             # Vérifier si le fichier contient "-EOR"
             if not "-EOR" in fichier:
                 # Convertir les parties date et heure en objets datetime
                 date_obj = datetime.strptime(date_part, "%Y%m%d")
                 heure_obj = datetime.strptime(heure_part, "%H%M%S").time()
                
                 # Créer un objet datetime complet
                 datetime_obj = datetime.combine(date_obj, heure_obj)
                 if startlist < datetime_obj.timestamp() < endlist:
                    listsavesets.append(fichier)
                 
         else:
             print("Aucun match trouvé dans le fichier", fichier)
       
    


    
    return listsavesets
     

def analyze_savesets(input_savesets, output_saveset):
    # open output root file
    # merge only relevant histograms, write
    # analyze and write "diagnostic" histograms/tgraphs?
    #     some knowledge is needed to translate CellID to spatial position to make nice plots.
    # close root file
    # write new Cell-HV maps (something easy to use from cpp)
    return path_to_hv_maps





def mergelist(listruncalib,run):

    runidname= (run.runid)

    fm = ROOT.TFileMerger(ROOT.kFALSE)

    # Définissez le chemin du répertoire racine
    root_directory = "/home/vgeller/Desktop/stack/stack/Savesets/ByRun/CaloMon/"

    # Obtenez les deux premiers chiffres de runid
    runid_prefix1 = str(runidname)[:2]
    
    runid_prefix = str(runid_prefix1)+"0000"
    
    # Créez le répertoire des deux premiers chiffres si nécessaire
    runid_prefix_directory = os.path.join(root_directory, runid_prefix)
    if not os.path.exists(runid_prefix_directory):
        os.makedirs(runid_prefix_directory)

    # Obtenez les trois premiers chiffres de runid
    runid_sub_prefix1 = str(runidname)[:3]
    
    runid_sub_prefix = str(runid_sub_prefix1)+"000"
    
    # Créez le répertoire des trois premiers chiffres dans le répertoire des deux premiers chiffres
    output_directory = os.path.join(runid_prefix_directory, runid_sub_prefix)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

        # Utilisez os.path.join pour créer le chemin complet du fichier de sortie
    output_file_name = os.path.join(output_directory, "CaloMon-" + str(runidname) + ".root")

    
    fm.OutputFile(output_file_name, "RECREATE")
   
    pattern = r'(\d{4})(\d{2})(\d{2})T\d+\.root'

    for file_name in listruncalib:
        match = re.search(pattern, file_name)
        if match:
            annee, mois, jour = match.groups()
            fm.AddFile("/hist/Savesets/"+annee+"/LHCb/CaloMon/"+mois+"/"+jour+"/"+str(file_name))
        else:
            print(f'Fichier invalide: {fichier}')

    fm.Merge()
    fm.Reset()
   
    return 0

    
def current_LHC_state():
    svc = pydim
    return svc

while True:
    
   

    
    run = findRunJustBeforeLastDump()
   
   
    runidname= (run.runid)
    runid_prefix1 = str(runidname)[:2]
    runid_prefix = str(runid_prefix1)+"0000"
    runid_sub_prefix1 = str(runidname)[:3]
    runid_sub_prefix = str(runid_sub_prefix1)+"000"
    directory = "/home/vgeller/Desktop/stack/stack/Savesets/ByRun/CaloMon/"+runid_prefix+"/"+runid_sub_prefix+"/"

    
    if (run.timerange/3600)>2:
       listruncalib = list_savesets(run)
      
       if not os.path.isfile(directory +"CaloMon-" + str(runidname) + ".root"):
          
           mergefile = mergelist(listruncalib,run)
           print(" nouveau fichier : ", mergefile)

    print("boucle terminée")

        
   # if updateWasAlreadyMadeFor(run):
    #    continue
   # input_savesets = find_input_savesets(run)
    
   # output_saveset = saveset_name(run)
   # hv_maps = analyze_savesets(input_savesets, output_saveset)
        
   # if current_LHC_state() == "DUMP":
        # should we (also) check that the HV is off?
       # subprocess.run(["Moore/run", "gaudirun.py", "update_hvs.py"], env={"HVMAPSFILE": hv_maps})
        
    # what if we crash in between saving the saveset and updating the HVs?
        
    
