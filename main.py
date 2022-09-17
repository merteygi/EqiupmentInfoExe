# -*- coding: utf-8 -*-
"""
Created on Sun Dec  6 18:43:53 2020

@author: MERT EYGI
"""

##
#--------- KÜTÜPHANELER -------#
import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import * # QtWidgets.QApplication gibi kullanımlardansa doğrudan QApplication kullanımı sağlıyor.
from LTE_EkipmanUI import *
from HakkindaUI import *
from FreqBandsUI import * 
import pandas as pd
from shutil import copyfile

import os
#from os import path

#--------- UYGULAMA OLUŞTUR -------#
Uygulama = QApplication(sys.argv)
penAna =QMainWindow()
ui = Ui_MainWindow() # Oluşturmuş olduğum form tanımlamlarına erişirken artık ui.btnARA diyeceğiz mesela.
ui.setupUi(penAna)
penAna.show()

penHakkinda = QDialog()
ui2 = Ui_Dialog()
ui2.setupUi(penHakkinda)

penFreqBand = QDialog()
ui3 = Ui_FrekansBandlari()
ui3.setupUi(penFreqBand)

local_directory = 'D:\\LTE_Bb_Rru\\'

def ARA():
    ui.btnIndir1.setEnabled(True) #Ozet BB & RRU Table Download Button
    ui.btnIndir2.setEnabled(True) #Detaylı BB & RRU Table Download Button
    ui.btnIndir3.setEnabled(True) #CELLs Download Button
    ui.btnIndir4.setEnabled(True) #RET Table Download Button
    ui.teOzet.clear()
    #print("ARA Fonksiyonuna girdi")
    sites=ui.lneSiteList.text()
    #print("Girilen Sahalar(txt): {}".format(sites))
    sites = sites.replace(" ", "").upper()
    site =[]
    site = sites.split(",")
    ui.teMesaj.setText("Girilen Sahalar:\n" + str(site))
    #print("Girilen Sahalar(list): {}".format(site))
    #ui.teOzet.setText("BUTONA TIKLANDI")
    if not (os.path.isfile(local_directory+'ipdatabase_all.txt') and os.path.isfile(local_directory+'CellBriefTable.txt')):
        ui.teMesaj.setText("D:\LTE_Bb_Rru altında gerekli text dosyaları bulunmuyor..\n" +
                           "Lütfen Veri Güncelle Butonuna tıklayıp Tekrar Aratınız..")
        return
    
    df_ip,df_cbt,df_nb,df_bb,df_rru,df_ret = dosyaOku()
    #print(df_ret[df_ret['NodeId']=='KOPGIL'])
    #ui.teSonuc.setText(df_cbt['enb'][100])
    #ui.teOzet.setText("INFO & OZET TEXT")
    #ui.teMesaj.setText("Mesaj TEXT")
    ######   MY CODE ####
    df_site=df_ip.loc[df_ip['Cabinet'].str.contains(site[0], regex=True)]
    i=1
    while i<len(site):
        df_site=df_site.append(df_ip.loc[df_ip['Cabinet'].str.startswith(site[i],na=True)])
        i += 1
    df_site = df_site.reset_index(drop=True)
    
    if df_site.empty:
        ui.teMesaj.setText("Girilen saha koduna ait LTE kabinet bulunamadı..\n" +
                           "Yazım hatası kontrolü yapınız veya Veri Güncellemeyi Deneyiniz..")
        return
    #print(df_site)
    
    df_lte=df_site.loc[(df_site['NodeType2']=='enodeB') & (df_site['RNC']!='RAN')]
    df_lte = df_lte.reset_index(drop=True)
    
    #df_cbt = pd.read_csv('\\\Fsr3403\\nt-rn\\ORTAK\\OPT\\PSC_PCI_FINDER\\ROMA\\CellBriefTable.txt',sep=";",names=['enb','Cell','Freq','admState','Tac','cid','pss','sss','fBand','barred','fdl','ful','lat','long','enbId','oprState','reserved','rrs','CC'])
    
    #
    #print("----------------------------------------------LTE CELL Info-------------------------------------------\n")
    df_cell = pd.DataFrame()
    i=0
#    print("------")
#    print(df_lte)
#    print("------")
    while i<len(df_lte):
#        print(i)
#        print(df_lte.Cabinet[i])
        if not df_cbt[df_cbt['enb']==df_lte['Cabinet'][i]].empty:
            df7=df_cbt[df_cbt['enb']==df_lte['Cabinet'][i]]
            if i==0:
                df_cell=df7
                df_lte['TanımlıCell']=df_cell[df_cell['enb']==df_lte['Cabinet'][i]]['Cell'].nunique()
                df_lte['AktifCell']=df_cell[(df_cell['enb']==df_lte['Cabinet'][i]) & (df_cell['admState']=='UNLOCKED')]['Cell'].nunique()
            else:
                df_cell=df_cell.append(df7)
                df_lte.iloc[i,6]=df_cell[df_cell['enb']==df_lte['Cabinet'][i]]['Cell'].nunique() #'TanımlıCellCount' kolon no=6
                df_lte.iloc[i,7]=df_cell[(df_cell['enb']==df_lte['Cabinet'][i]) & (df_cell['admState']=='UNLOCKED')]['Cell'].nunique() #'AktifCellCount' kolon no=7
             
        i += 1
    
    
    if df_cell.empty:
        ui.teMesaj.setText("Girilen bilgilere ait LTE CELL Bulunamadı..\n" +
                           "CellBriefTable.txt dosyasında hata olabilir..")
        return
        
    cell_list=list(df_cell['Cell'])
    k=0
    df_cell = df_cell.reindex(columns = df_cell.columns.tolist() + ["Sector_Info","Carrier_Info"])
    while k<len(cell_list):
        carrier_no=cell_list[k][-2]
        sector_no=cell_list[k][-3]
        df_cell.iloc[k,14]='s'+sector_no
        df_cell.iloc[k,15]='c'+carrier_no
        #print(sektor_no)
        k += 1
    df_cell[['A','EutranCellFDD']]=df_cell.Cell.str.split("=",expand=True)
    df_cell['pci']=0
    df_cell['pci']=df_cell['sss'].astype(int)*3+df_cell['pss'].astype(int)
    df_cell2=df_cell[['enb','EutranCellFDD','admState','Sector_Info', 'Carrier_Info',
                      'fdl','pss','sss','pci','Tac','CellCount']]
    #df_cell2['pci']=df_cell2['sss'].astype(int)*3+df_cell2['pss'].astype(int)
    #print(df_cell2)
    #df_ret[df_ret['NodeId']=='KOPGIL']['maxTilt'].astype(int)*2
     ##################### TABLE tblwCell ########################    
    ui.tblwCell.clear()
    ui.tblwCell.setRowCount(len(df_cell2))
    ui.tblwCell.setColumnCount(len(df_cell2.columns))
    ui.tblwCell.setHorizontalHeaderLabels(list(df_cell2.columns))
    ui.tblwCell.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    #print("cell sayısı: {}".format(len(df_cell)))
    for x in range(0,len(df_cell2)):
        for y in range(0,len(df_cell2.columns)):
            ui.tblwCell.setItem(x,y,QTableWidgetItem(str(df_cell2.iloc[x,y])))
            
    ui.btnIndir3.clicked.connect(lambda: Download_Cells(df_cell2) )
    ###############################################################
    #print("----------------------------------------------NbIOT Cell Info-------------------------------------------\n")
    # create an Empty DataFrame object 
    df_nbcell = pd.DataFrame()
    df_lte['NBCell']=0 
    i=0
    while i<len(df_lte):
        nb_cell=0
        if not df_nb[df_nb['IP']==df_lte['IP'][i]].empty:
            df8=df_nb[df_nb['IP']==df_lte['IP'][i]].reset_index(drop=True)
            df8['Cabinet']=df_lte['Cabinet'][i]
            nb_cell=df8[df8['IP']==df_lte['IP'][i]]['nbCell'].nunique()
            df_lte.iloc[i,8]=nb_cell #'NBCellCount' kolon no=8
            if i==0:
                #print("if'de {}".format(i))
                df_nbcell=df8
            else:
                #print("else'de {}".format(i))
                df_nbcell=df_nbcell.append(df8)
                
        #del df8
        i += 1
    if not df_nbcell.empty:
        df_nbcell=df_nbcell.reset_index(drop=True)
#        print(df_nbcell.to_string(index=False))
#    else:
#        print("NbIOT hücre bulunmuyor..")
    #print(df_lte)
    
    #    if df_lte.empty:
    #        print("Girilen saha koduna ait LTE kabinet bulunamadı")
    #        return
    
    
    #print("----------------------------------------------LTE Ekipman Info-------------------------------------------\n")
    #print("--------LTE BB & RRU----------\n")
    df_lte['Baseband']=0
    bb=0
    i=0
    
    df_lte_rru = pd.DataFrame()
    while i<len(df_lte):
        #print("while içine girdi, i = {}".format(i))
        if not df_rru[df_rru['IP']==df_lte['IP'][i]].empty:
            df6 = df_rru[df_rru['IP']==df_lte['IP'][i]][['IP','SxCx','rru','rruSeriNo','rruDate']]
        if not df_bb[df_bb['IP']==df_lte['IP'][i]].empty:
            bb=df_bb[df_bb['IP']==df_lte['IP'][i]].reset_index(drop=True)['Baseband'][0]
            df6['Baseband'] = bb
            df_lte.iloc[i,9] = bb
            df6['BbSeriNo'] = df_bb[df_bb['IP']==df_lte['IP'][i]].reset_index(drop=True)['BbSeriNo'][0]
            df6['BbDate'] = df_bb[df_bb['IP']==df_lte['IP'][i]].reset_index(drop=True)['BbDate'][0]
            df6['Cabinet']=df_lte['Cabinet'][i]
            df6['ENM']=df_lte['ENM'][i]
            
                    
            cols = list(df6.columns)
            df6 = df6[[cols[-2]] + [cols[-1]] + [cols[0]] + cols[5:8] + cols[1:5] ]
            if i==0:
                df_lte_rru=df6
            else:
                #print(i)
                df_lte_rru=df_lte_rru.append(df6)
        #print(df3.to_string(index=False))
        i += 1
    
    if df_lte_rru.empty:
        ui.teMesaj.setText("Girilen kabinet için BB & RRU bilgisi bulunmuyor..\n")
        return
    
    df_lte_rru = df_lte_rru.reset_index(drop=True)
    #print(df_lte_rru)
    #print(df_lte_rru.to_string(index=False))
    
    ##################### TABLE tblwBbRru #######################3
    ui.tblwBbRru.clear()
    ui.tblwBbRru.setRowCount(len(df_lte_rru))
    ui.tblwBbRru.setColumnCount(len(df_lte_rru.columns))
    ui.tblwBbRru.setHorizontalHeaderLabels(list(df_lte_rru.columns))
    ui.tblwBbRru.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    for x in range(0,len(df_lte_rru)):
        for y in range(0,len(df_lte_rru.columns)):
            ui.tblwBbRru.setItem(x,y,QTableWidgetItem(str(df_lte_rru.iloc[x,y])))
    ##################################################################
    
    j=0
    rru_list2=list(df_lte_rru['rru'].drop_duplicates())
    rru_list2 = [x for x in rru_list2 if str(x) != 'nan'] #Remove NaN if there is
    while j<len(rru_list2):
        df_lte[rru_list2[j]]=0
        j += 1
    
    #print("\n-----------------------------------LTE Ekipman Özet-1-------------------------------\n")
    
    bb=0
    i=0
    while i<len(df_lte):
        if not df_bb[df_bb['IP']==df_lte['IP'][i]].empty:
            cab = df_lte['Cabinet'][i]
            bb = df_lte_rru[df_lte_rru['IP']==df_lte['IP'][i]]['Baseband'].drop_duplicates().reset_index(drop=True)[0]
            uniq_bb = df_lte_rru[df_lte_rru['IP']==df_lte['IP'][i]]['BbSeriNo'].nunique()
            bb_date = df_lte_rru[df_lte_rru['IP']==df_lte['IP'][i]]['BbDate'].drop_duplicates().reset_index(drop=True)[0]
            #print("{}\tBBU: {}\tAdet(tekil): {}\ttarih:{}".format(cab,bb,uniq_bb,bb_date))
        
        if not df_rru[df_rru['IP']==df_lte['IP'][i]].empty:
            rru_list=list(df_lte_rru[df_lte_rru['IP']==df_lte['IP'][i]]['rru'].drop_duplicates())
            rru_list = [x for x in rru_list if str(x) != 'nan'] #Remove NaN if there is
            rru_date=df_lte_rru[df_lte_rru['IP']==df_lte['IP'][i]]['rruDate'].drop_duplicates().reset_index(drop=True)[0]
            j=0
            while j<len(rru_list):
                rru = rru_list[j]
                rru_count = df_lte_rru[(df_lte_rru.rru==rru_list[j]) & (df_lte_rru.IP==df_lte['IP'][i])]['rru'].count()
                col_index=df_lte.columns.get_loc(rru)
                df_lte.iloc[i,col_index]=rru_count
                #df_lte[rru]=rru_count
                uniq_rru = df_lte_rru[(df_lte_rru['IP']==df_lte['IP'][i]) &(df_lte_rru.rru==rru_list[j])]['rruSeriNo'].nunique()
    #            if 10>len(rru):
    #                print("{}\tRRU: {}\t\tAdet(tekil): {}\ttarih:{}".format(cab,rru,uniq_rru,rru_date))
    #            else:
    #                print("{}\tRRU: {}\tAdet(tekil): {}\ttarih:{}".format(cab,rru,uniq_rru,rru_date))
                j += 1
            
        i += 1
    #print("\n")
    i=0
    df_lte['Sector_Info']=""
    cols = list(df_lte.columns)
    col_no=len(df_lte.columns)-1
    while i<len(df_lte):
        sector_list=list(df_cell[df_lte['Cabinet'][i]==df_cell['enb']]['Sector_Info'].drop_duplicates())
        sector_str = '-'.join([str(elem) for elem in sector_list])
        df_lte.iloc[i,col_no]=sector_str
        i += 1
    #print("\n---------------------------------------------LTE Ekipman Özet------------------------------------------\n")
    
    cols = list(df_lte.columns)
    df_lte2 = df_lte[ [cols[0]] + [cols[-1]] +  cols[5:(len(cols)-1)] ]
    #print(df_lte2.to_string(index=False))
    
    ##################### TABLE tblwOzet ########################
    ui.tblwOzet.clear()
    ui.tblwOzet.setRowCount(len(df_lte2))
    ui.tblwOzet.setColumnCount(len(df_lte2.columns))
    ui.tblwOzet.setHorizontalHeaderLabels(list(df_lte2.columns))
    ui.tblwOzet.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    for x in range(0,len(df_lte2)):
        for y in range(0,len(df_lte2.columns)):
            ui.tblwOzet.setItem(x,y,QTableWidgetItem(str(df_lte2.iloc[x,y])))
    
    #ui.tblwOzet.selectionModel.sele
    #ui.tblwOzet.AdjustToContentsOnFirstShow()
    ui.btnIndir1.clicked.connect(lambda: Download_OzetTablo(df_lte2) )
    ##################################################################
    
    #print("\nToplam LTE Baseband\tSayısı: {}".format(df_lte_rru['BbSeriNo'].nunique()))
    #print("Toplam Rru sayısı: {}".format(df_lte_rru['rru'].count()))
    #print("Toplam LTE Radiounit\tSayısı: {}\n".format(df_lte_rru['rruSeriNo'].nunique()))
    
    ui.teOzet.setText("Toplam LTE Baseband Sayısı: " + str(df_lte_rru['BbSeriNo'].nunique()) +"\n"
                      + "Toplam LTE Radiounit Sayısı: " + str(df_lte_rru['rruSeriNo'].nunique()) )
    #Download(df_lte2)
    
    ui.btnIndir2.clicked.connect(lambda: Download_Rru(df_lte_rru) )

    #print("----------------------------------------------LTE RET Info-------------------------------------------\n")
    #print("--------LTE BB & RRU----------\n")  
    i=0
    df_lte_ret = pd.DataFrame()
    while i<len(df_lte):
        #print("while içine girdi, i = {}".format(i))
        #print(df_ret[df_ret['NodeId']==df_lte['Cabinet'][i]])
        if not df_ret[df_ret['NodeId']==df_lte['Cabinet'][i]].empty:
            df_lte_ret = df_lte_ret.append(df_ret[df_ret['NodeId']==df_lte['Cabinet'][i]])
        i = i+1
    #print(df_lte_ret)
    if df_lte_ret.empty:
        ui.teMesaj.setText("Girilen kabinet(ler) için RET bilgisi bulunamadı..\n")
        return
    
    ##################### TABLE tblwRet ########################
    ui.tblwRet.clear()
    ui.tblwRet.setRowCount(len(df_lte_ret))
    ui.tblwRet.setColumnCount(len(df_lte_ret.columns))
    ui.tblwRet.setHorizontalHeaderLabels(list(df_lte_ret.columns))
    ui.tblwRet.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    ui.tblwRet.horizontalHeader().setSectionResizeMode(4,QHeaderView.ResizeToContents) #Antenna Model Column
    ui.tblwRet.horizontalHeader().setSectionResizeMode(8,QHeaderView.ResizeToContents) #UserLabel Column

    for x in range(0,len(df_lte_ret)):
        for y in range(0,len(df_lte_ret.columns)):
            ui.tblwRet.setItem(x,y,QTableWidgetItem(str(df_lte_ret.iloc[x,y])))
    
    #ui.tblwRet.selectionModel.sele
    #ui.tblwRet.AdjustToContentsOnFirstShow()
            
    ui.btnIndir4.clicked.connect(lambda: Download_RETs(df_lte_ret) )
    ##################################################################

    
    
def veriGuncelle():
    ui.teMesaj.setText("Veri Güncelleniyor, Lütfen Bekleyiniz..")
    
    source_dir='\\\Fsr3403\\nt-rn\\ORTAK\\OPT\\PSC_PCI_FINDER\\ROMA\\'
    source_pic_dir='\\\Fsr3403\\nt-rn\\ORTAK\\OPT\\mert\\LTE_Bb_Rru\\'
    
    if not (os.path.isdir(local_directory)):
        os.mkdir(local_directory)
    
    pics=['FrekansSpectrum.png', 'PyQt5.png']
    for resim in pics:
        copyfile(source_pic_dir + resim, local_directory +  resim)
        
    files=['ipdatabase_all.txt','CellBriefTable.txt','NbIotCell.txt','LTE_BaseBand.txt','LTE_RRU.txt','allenm_LTE_ret_list.txt']
    for dosya in files:
        copyfile(source_dir + dosya, local_directory + dosya)
        
    ui.teMesaj.setText("Veriler Güncellendi !!\nGerekli dosyalar D:\LTE_Bb_Rru altına Kopyalandı..")
def dosyaOku():
    
    df_ip = pd.read_csv(local_directory+'ipdatabase_all.txt',header=None,sep='\t',names=["Cabinet", "IP", "NodeType1", "RNC","NodeType2","ENM"])
    df_cbt = pd.read_csv(local_directory+'CellBriefTable.txt',sep=";",names=['enb','Cell','Freq','admState','Tac','sss','pss','band','barred','fdl','enbId','oprState','reserved','CellCount'],
        usecols=[0,1,2,3,4,6,7,8,9,10,14,15,16,18],dtype={4:'str',5:'str',6:'str',7:'str',8:'str',10:'str',14:'str',16:'str',18:'str'})
    df_nb = pd.read_csv(local_directory+'NbIotCell.txt',sep=";",usecols=[1,2,3,4,10],
                        names=['IP','nbCell','administrativeState','cellBarred','operationalState'])
    df_bb = pd.read_csv(local_directory+'LTE_BaseBand.txt',sep=";",names=['BbDate','IP','A','Baseband','productNumber','productRevision','B','productionDate','BbSeriNo'])

    df_rru = pd.read_csv(local_directory+'LTE_RRU.txt',sep=";",names=[\
      'rruDate','IP','SxCx','rru','productNumber','productRevision','B','productionDate','rruSeriNo'])
    
    df_ret = pd.read_csv(local_directory+'allenm_LTE_ret_list.txt',header=None,sep='\t',names=[
        'NodeId','AntUnitGrId','AntNearUnitId','ETilt','AntennaModel',
        'maxTilt','minTilt','operationalState','UserLabel'],usecols=[0,2,3,5,6,7,8,9,10],
        dtype={5:'str',7:'str',8:'str'})
    return(df_ip,df_cbt,df_nb,df_bb,df_rru,df_ret)
      
def on_SiteList_edited():
        ui.btnARA.setEnabled(bool(ui.lneSiteList.text()))

def Download_OzetTablo(df):
    #print("\n--------Download_OzetTablo...\n")
    #print(df)
    df.to_excel(local_directory+"LTE_BB_RRU_Ozet.xlsx",sheet_name='OzetTablo',index=False)
    ui.teMesaj.setText("D:\LTE_Bb_Rru altına LTE_BB_RRU_Ozet.xlsx dosyası İndirildi !!")
def Download_Rru(df):
    #print("\n--------Download_RRU_Liste...\n")
    #print(df)
    df.to_excel(local_directory+"LTE_BB_RRU_Detaylı.xlsx",sheet_name='RRU_Liste',index=False)
    ui.teMesaj.setText("D:\LTE_Bb_Rru altına LTE_BB_RRU_Detaylı.xlsx dosyası İndirildi !!")
    
def Download_Cells(df):
    #print("\n--------Download_LTE_CELLs...\n")
    #print(df)
    df.to_excel(local_directory+"LTE_CELLs.xlsx",sheet_name='CELLs',index=False)
    ui.teMesaj.setText("D:\LTE_Bb_Rru altına LTE_CELLs.xlsx dosyası İndirildi !!")

def Download_RETs(df):
    #print("\n--------Download_LTE_RETs...\n")
    #print(df)
    df.to_excel(local_directory+"LTE_RETs.xlsx",sheet_name='CELLs',index=False)
    ui.teMesaj.setText("D:\LTE_Bb_Rru altına LTE_RETs.xlsx dosyası İndirildi !!")


#------HAKKINDA
def HAKKINDA():
    penHakkinda.show()

def FREQBANDS():
    penFreqBand.show()


#------SINYAL SLOT
ui.btnARA.setEnabled(False)
ui.lneSiteList.textEdited.connect(on_SiteList_edited)

ui.btnIndir1.setDisabled(True) #Ozet BB & RRU Table Download Button
ui.btnIndir2.setDisabled(True) #Detaylı BB & RRU Table Download Button
ui.btnIndir3.setDisabled(True) #CELLs Download Button
ui.btnIndir4.setDisabled(True) #RET Table Download Button

ui.btnARA.clicked.connect(ARA)

#print(df_lte2)
#
#print("hello")
ui.btnGuncelle.clicked.connect(veriGuncelle)

ui.Hakkinda.triggered.connect(HAKKINDA)
ui.LTE_Bands.triggered.connect(FREQBANDS)

sys.exit(Uygulama.exec_())
