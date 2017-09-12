# importing libraries
import os
import csv
import sys
import xml.etree.ElementTree as ET
import pandas as pd
from collections import defaultdict


#INPUT FILE PATH DEFINITION
Input_file_Path = "I0809_SI_WMS_Input_File.csv"
Gist_XML_Path = []
Gist_XML_Path.append('BB_9_BB1004796681.xml')
Gist_XML_Path.append('BD_9_BD1004979297.xml')
Gist_XML_Path.append('BK_9_BK1004147372.xml')
Gist_XML_Path.append('BN_9_BN1003833094.xml')
Gist_XML_Path.append('BQ_9_BQ1002854978.xml')
Gist_XML_Path.append('BR_9_BR1003971741.xml')
Gist_XML_Path.append('BT_9_BT1008090503.xml')
Gist_XML_Path.append('BZ_9_BD1004979296.xml')
Gist_XML_Path.append('DJ_9_BR1003971742.xml')
Gist_XML_Path.append('DL_9_DL1003692583.xml')
Gist_XML_Path.append('DV_9_BR1003971895.xml')
Gist_XML_Path.append('DW_9_BR1003971743.xml')

SAP_Input_Path = []
SAP_Input_Path.append('Q1_9_5908.csv')
SAP_Input_Path.append('Q1_10_5966.csv')
SAP_Input_Path.append('Q1_11_6567.csv')
SAP_Input_Path.append('Q1_5_5380.csv')
SAP_Input_Path.append('Q1_7_5652.csv')
SAP_Input_Path.append('Q1_8_5898.csv')
SAP_Input_Path.append('Q1_1_1137.csv')
SAP_Input_Path.append('Q1_3_5212.csv')
SAP_Input_Path.append('Q1_4_5281.csv')
SAP_Input_Path.append('Q1_13_3942.csv')
SAP_Input_Path.append('Q1_12_9010.csv')
SAP_Input_Path.append('Q1_2_5173.csv')

ArticleUPCFilePath = 'Bradford_Article_UPC_master.csv'

MergedSAPDepotUPCStockDetails = 'MergedSAPDepotUPCStockDetails.csv'

# LEGACY - SAP DEPOT CODE
Depot = {}
Depot['BB'] = 5173
Depot['BN'] = 5908
Depot['BD'] = 5212
Depot['BK'] = 6567
Depot['BR'] = 5652
Depot['BT'] = 5966
Depot['BZ'] = 5898
Depot['BQ'] = 5380
Depot['DV'] = 5281
Depot['DW'] = 1137
Depot['DL'] = 3942
Depot['DJ'] = 9010


#OUT PUT FILE PATH DEFINITION
Output_file_Path = 'I0809_SI_Issues_SAP_Upload.CSV'
Error_file_Path = 'I0809_SI_Issues_SAP_Upload_Error_Records.CSV'

def ReadGISTXML(Gist_XML_Path_D1, Depot):
   
   #GIST_Depot_Stock_XML = open(GistF1).read() # OPEN GIST XML
   GIST_XML_Tree = ET.parse(Gist_XML_Path_D1) # element tree
   GIST_XML_Root = GIST_XML_Tree.getroot()
   DepotCode = Depot[Gist_XML_Path_D1[:2]]
   #print DepotCode
   
   
   namespace = {'ns2': 'marksspencer.com/is/2009/schemas/envelope/'}
   
   #Dic_DepotUPCStockDetails = defaultdict(list)
   Dic_DepotUPCStockDetails = {}
  
   for EachUPC in GIST_XML_Root.findall('ns2:Payload/ns2:EODStockCounts/ns2:StockCount',namespace):
      
      UPC = EachUPC.find('ns2:BarCode',namespace).text
      #print UPC

      
      for UPCStockDetails in EachUPC.findall('ns2:StockDetails',namespace):
         ls_DepotUPCStockDetails = []
         StockType = UPCStockDetails.find('ns2:StockType',namespace).text
         BaseQty = UPCStockDetails.find('ns2:BaseQty',namespace).text
         BaseUOM = UPCStockDetails.find('ns2:BaseUOM',namespace).text

         ls_DepotUPCStockDetails.append(UPC)
         ls_DepotUPCStockDetails.append(DepotCode)
         ls_DepotUPCStockDetails.append(StockType)
         ls_DepotUPCStockDetails.append(BaseQty)
         ls_DepotUPCStockDetails.append(BaseUOM)

         #print StockType
         #print BaseQty
         #print BaseUOM

      str_UPC = str(UPC)
      str_Depot = str(DepotCode)
      #ADD THE UPC LEVEL STOCK DETALS
      Dic_DepotUPCStockDetails[str_UPC + str_Depot] = ls_DepotUPCStockDetails
      #Dic_DepotUPCStockDetails[UPC].append(BaseQty)
      #Dic_DepotUPCStockDetails[UPC].append(BaseUOM)

   df_DepotUPCStockDetails = pd.DataFrame(Dic_DepotUPCStockDetails).transpose()
   df_DepotUPCStockDetails.columns = ['UPC','Site','StockType','BaseQty', 'BaseUOM']
   
   return df_DepotUPCStockDetails

def ReadSAPStockFile(SAPCSVFilePath):
   df_SAPDepotUPCStockDetails = pd.read_csv(SAPCSVFilePath,
      names = ['Site','StorageLocation','Article','UPC','Department','Stroke','ArticleStatus','DeletedSL','UnrestrictedStockQty','QIStockQty','BlockedStockQty','MvngAvgPrice','BaseUOM'],
      dtype={'Site': object,'StorageLocation': object,'Article': object,'UPC': object,'Department':object,'Stroke':object,'ArticleStatus':object,'DeletedSL':object,'UnrestrictedStockQty':object,'QIStockQty':object,'BlockedStockQty':object,'MvngAvgPrice':object,'BaseUOM':object},
      header=0)
   
   df_SAPDepotUPCStockDetails['UPC'] = df_SAPDepotUPCStockDetails['UPC'].apply(lambda x: '{0:0>8}'.format(x))
   df_SAPDepotUPCStockDetails['Article'] = df_SAPDepotUPCStockDetails['Article'].str.lstrip('0')
   return df_SAPDepotUPCStockDetails

def ReadArticleUPCMaster(ArticleUPCFilePath):
   df_ArticleUPCMaster = pd.read_csv(ArticleUPCFilePath, names=['Article','UPC'],dtype={'Article': object,'UPC': object}, header=0)
   df_ArticleUPCMaster['Article'] = df_ArticleUPCMaster['Article'].str.lstrip('0')
   return df_ArticleUPCMaster


def MergeGISTSAPStock(df_ALL_DepotUPCStockDetails,df_ALL_SAPDepotUPCStockDetails,df_ArticleUPCMaster):

   #df_ALL_MergedSAPDepotUPCStockDetails = pd.merge(df_ALL_DepotUPCStockDetails,df_ALL_SAPDepotUPCStockDetails [['StorageLocation','Department']], on=['UPC', 'Site'] ,how='inner')
   df_ALL_BradfordSAPDepotUPCStockDetails = pd.merge(df_ArticleUPCMaster ,df_ALL_SAPDepotUPCStockDetails, on='Article', how='left')
   df_ALL_BradfordGISTDepotUPCStockDetails = pd.merge(df_ArticleUPCMaster ,df_ALL_DepotUPCStockDetails, on='UPC', how='inner')
   
   df_ALL_BradfordDepotUPCStockDetails = pd.merge(df_ALL_BradfordSAPDepotUPCStockDetails ,df_ALL_BradfordGISTDepotUPCStockDetails, on=['Article','Site'], how='outer')
   print '-------- OUTER -----------'
   print df_ALL_BradfordDepotUPCStockDetails.head(10)
   print df_ALL_BradfordDepotUPCStockDetails.shape

   #df_ALL_BradfordUPCStockDetails   = pd.merge(df_ALL_BradfordSAPDepotUPCStockDetails ,df_ALL_SAPDepotUPCStockDetails, on=['Article','Site'], how='left')
   return df_ALL_BradfordGISTDepotUPCStockDetails
     

# READ AND BUILD DEPOT/GIST STOCK
df_ALL_DepotUPCStockDetails = pd.DataFrame()
for depotXML in Gist_XML_Path: 
   
   df_Each_DepotUPCStockDetails = ReadGISTXML(depotXML,Depot)
   #print df_Each_DepotUPCStockDetails.shape
   df_ALL_DepotUPCStockDetails = df_ALL_DepotUPCStockDetails.append(df_Each_DepotUPCStockDetails)

print df_ALL_DepotUPCStockDetails.head(10)
print df_ALL_DepotUPCStockDetails.shape

df_ALL_DepotUPCStockDetails.to_csv('GIST_Stock.csv')

# READ AND BUILD DEPOT/SAP STOCK
df_ALL_SAPDepotUPCStockDetails = pd.DataFrame()
for SAPCSVFP in SAP_Input_Path: 
   
   df_SAP_Each_DepotUPCStockDetails = ReadSAPStockFile(SAPCSVFP)
   #print df_SAP_Each_DepotUPCStockDetails.head(5)
   #print df_SAP_Each_DepotUPCStockDetails.shape
   
   df_ALL_SAPDepotUPCStockDetails = df_ALL_SAPDepotUPCStockDetails.append(df_SAP_Each_DepotUPCStockDetails)

print df_ALL_SAPDepotUPCStockDetails.shape

# READ AND BUILD ARTICLE UPC MASTER

df_ArticleUPCMaster = ReadArticleUPCMaster(ArticleUPCFilePath)
print df_ArticleUPCMaster.head(10)
print df_ArticleUPCMaster.shape

# MERGE GIST AND SAP STOCK TO FIND THE DIFF
#print df_ALL_SAPDepotUPCStockDetails.dtypes
#print "-------------------"
#print df_ArticleUPCMaster.dtypes

df_ALL_MergedSAPDepotUPCStockDetails = MergeGISTSAPStock(df_ALL_DepotUPCStockDetails,df_ALL_SAPDepotUPCStockDetails,df_ArticleUPCMaster)
print df_ALL_MergedSAPDepotUPCStockDetails.head(10)
print df_ALL_MergedSAPDepotUPCStockDetails.shape

df_ALL_MergedSAPDepotUPCStockDetails.to_csv(MergedSAPDepotUPCStockDetails)

print "Script Completed Successfully "


