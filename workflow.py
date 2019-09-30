# ======================================================================================================================
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# This file calculates the total greenhouse gas emissions and global warming potential.

# This method could be used for carbon emission calculation during wastewater treatment process (WTP). In this method,
# we mainly consider Greenhouse Gas (GHG) such as carbon dioxide, methane, and nitrous oxide. The total GHG emissions
# from WTP including direct emissions, indirect emissions and avoided carbon dioxide (due to biogas reuse). We assume
# that there is a complete WTP (including sludge disposal facility), A2/O process for wastewater treatment and anaerobic
# digestion process for sludge disposal.

# ----------------------------------------------------------------------------------------------------------------------
# References
# **********************************************************************************************************************
# Ren, Y., Wang, J., Xu, L., Liu, C., Zong, R., Yu, J., and Liang, S. (2015) Direct emissions of N2O, CO2, and CH4 from
# A/A/O bioreactor systems: impact of influent C/N ratio. Environ Sci Pollut R 22: 8163-8173.
# Xu, Y.L.L.J. (2014) Characteristics of greenhouse gas emission in three full-scale wastewater treatment processes. J
# Environ Sci-China 26: 256-263.
# Liu, H.T., Kong, X.J., Zheng, G.D., and Chen, C.C. (2016) Determination of greenhouse gas emission reductions from
# sewage sludge anaerobic digestion in China. Water Sci Technol 73: 137-143.
# Niu, D., Huang, H., Dai, X., and Zhao, Y. (2013) Greenhouse gases emissions accounting for typical sewage sludge
# digestion with energy utilization and residue land application in China. Waste Manage 33: 123-128.
# ----------------------------------------------------------------------------------------------------------------------

# Author  : Yuansheng Huang (Ethan Huang)
# Contact : Huangyuansheng@hotmail.com
# Date    : 2019/08/21
# Version : 0.1
# ======================================================================================================================

from functions import *
# ======================================================================================================================
# 获取基础参数
# ----------------------------------------------------------------------------------------------------------------------
# 读取用户输入值
# **********************************************************************************************************************
path = r'E:\results\carbonEmission'
fileName = input("请输入输出文件名称：\n").replace(" ", "")

Q = (float(input("请输入污水厂规模（立方米/天）:\n").replace(" ", ""))) * 365                    # 污水厂处理能力， m³/yr
conInStr = input("请输入进水污染物浓度（mg/L）并用“，”隔开！如：COD,TN,TP\n").replace(" ", "")     # 污染物年处理量，吨/年
conOutStr = input("请输入出水污染物浓度（mg/L）并用“，”隔开！如：COD,TN,TP\n").replace(" ", "")    # 《城镇污水处理厂污染物排放标准》一级A标准

_, conIn = strToList(conInStr, Q)              # 获取进水污染物质量列表，kg/yr
_, conOut = strToList(conOutStr, Q)            # 获取出水污染物质量列表，kg/yr

# 计算污水处理阶段温室气体
# ----------------------------------------------------------------------------------------------------------------------
# 计算污泥产量
# **********************************************************************************************************************
R = 0.5
weit1, sludge = sludgeOutput(conIn, conOut, R)     # weit kg
weit = weit1*1000/365/100000                       # g/m³

# 计算气体产量
# **********************************************************************************************************************
coeffWT = [458.40, 2.31, 2.08]                                   # 温室气体排放系数（单位污染物），g/kg
EmCO2, EmCH4, EmN2O = gasEmission(conIn, conOut, coeffWT)        # 去除单位污染物排放的温室气体（直接排放）, kg

coeffPlant = [0.087, 0.21208, 0.09106]                           # 构筑物能耗系数，kWh/m³
coeffElec = 0.8075                                               # 电能二氧化碳排放系数，kg CO2/kWh
coeffChem = [1.54, 2.50, 2.50]                                   # 药剂二氧化碳排放系数，kg CO2/kg 试剂
# mass0 = [weit, 0.125, 7.5]                                     # 药耗，g/m³
mass = [x / 1000 for x in [weit, 0.125, 7.5]]                    # 药耗，kg/m³
_, elecCO2 = energyConsumptionW(Q, coeffPlant, coeffElec)        # kg
chemCO2 = chemicalConsumption(Q, mass, coeffChem)                # kg

# 汇总1
# **********************************************************************************************************************
waterCO2 = EmCO2 + elecCO2 + chemCO2
waterCO2I = elecCO2 + chemCO2
waterCH4 = EmCH4
waterN2O = EmN2O
waterList = [waterCO2, waterCH4, waterN2O]
strCO2IW = str(waterCO2I)
strCO2DW = str(EmCO2)

# 计算污泥处置阶段温室气体
# ----------------------------------------------------------------------------------------------------------------------
VS = 0.55                                   # 挥发性固体百分含量
ratio = 0.1                                 # 甲烷泄漏比例
percent = [0.35, 0.75]                      # 气态产物组分体积百分比
coeffSD = [315.7, 3.18, 17.2]               # 污泥处置阶段各过程二氧化碳排放系数，kg/t
emissionCO2, emissionCH4, residue = biogenicGas(sludge, VS, ratio, percent, coeffSD)      # kg
volumeCH4 = (emissionCH4 * 1000 / 16) * (22.4 / 1000)      # pV=nRT     22.4   m³

electricity = 80 / 1000                        # 电能, kWh
electrLand = 58.5 / 1000                       # 电能, kWh
diesel = 41.3 * 42552 / 1000                   # 化石能，kJ
renew = 14636 * (1 - ratio) * 0.6 * volumeCH4           # 再生能，kJ
calori = [electricity, electrLand, diesel, renew]
coeffEG = [0.8075, 3.0959 / 42552, 2.162 / (14636 * 0.6)]        # 排放系数列表，kg CO2/....
energyCO2 = energyConsumptionS(sludge, VS, calori, coeffEG)

a = sludge * calori[2]

Sa = 48.2                                               # 效益系数，kWh/t
avoidCO2 = avoidedCO2(sludge, VS, Sa, coeffEG[0])

# 汇总2
# **********************************************************************************************************************
sludgeCO2 = emissionCO2 + energyCO2 - avoidCO2
sludgeCH4 = emissionCH4
sludgeN2O = 0
sludgeList = [sludgeCO2, sludgeCH4, sludgeN2O]
strCO2IS = str(energyCO2)
strCO2DS = str(emissionCO2)
strCO2A = str(avoidCO2)

# ----------------------------------------------------------------------------------------------------------------------
# 汇总
# ----------------------------------------------------------------------------------------------------------------------
CO2 = waterCO2 + sludgeCO2
CH4 = waterCH4 + sludgeCH4
N2O = waterN2O + sludgeN2O
greenhouseList = [CO2, CH4, N2O]

# ----------------------------------------------------------------------------------------------------------------------
# 计算GWP
# ----------------------------------------------------------------------------------------------------------------------
list1 = [CO2, CH4, N2O]
list2 = [1, 21, 310]
GWP = globalWP(list1, list2)
strGWP = str(GWP)

# ======================================================================================================================
# 结果输出 txt文本
# ----------------------------------------------------------------------------------------------------------------------
outputFile = open(path + "//" + fileName + '.txt', 'w')
table = ["CO2产量(kg)", "CH4产量(kg)", "N2O产量(kg)"]
outputFile.write("============================================================================================" + "\n" +
                 "计算结果" + "\n" +
                 "============================================================================================" + "\n" +
                 "污水处理阶段温室气体产量" + "\n" +
                 "--------------------------------------------------------------------------------------------" + "\n")
listW = list(zip(table, waterList))
for i in range(len(listW)):
    line = str(listW[i]).replace("',", ": ").strip('(').strip(')').strip("'")
    outputFile.write(line + '\n')
outputFile.write("********************************************************************************************" + "\n" +
                 "其中直接排放CO2(kg): " + strCO2DW + "间接排放CO2(kg): " + strCO2IW + "\n" +
                 "********************************************************************************************" + "\n")
outputFile.write("--------------------------------------------------------------------------------------------" + "\n" +
                 "污泥处置阶段温室气体产量" + "\n" +
                 "--------------------------------------------------------------------------------------------" + "\n")
listS = list(zip(table, sludgeList))
for i in range(len(listS)):
    line = str(listS[i]).replace("',", ": ").strip('(').strip(')').strip("'")
    outputFile.write(line + '\n')
outputFile.write("********************************************************************************************" + "\n" +
                 "其中直接排放CO2(kg):" + strCO2DS + "间接排放CO2(kg):" + strCO2IS + "\n" + "资源回用CO2(kg):" + strCO2A + "\n"
                 "********************************************************************************************" + "\n")
outputFile.write("--------------------------------------------------------------------------------------------" + "\n" +
                 "温室气体总产量" + "\n" +
                 "--------------------------------------------------------------------------------------------" + "\n")
listR = list(zip(table, greenhouseList))
for i in range(len(listR)):
    line = str(listR[i]).replace("',", ": ").strip('(').strip(')').strip("'")
    outputFile.write(line + '\n')
outputFile.write("============================================================================================" + "\n" +
                 "温室效应潜力（kg CO2 eq): " + strGWP + "\n" +
                 "============================================================================================" + "\n")

outputFile.close()

# 窗口打印
print("能耗kJ")


"""
outputFile = open(path + "//" + fileName + '.txt', 'r')
output = outputFile.readlines()
for x in output:
    print(x, end='')
print("污水处理单元CO2排放（kg): 直接排放, 电耗排放, 药耗排放")
print(EmCO2, elecCO2, chemCO2)
print("污泥处置单元CO2排放（kg): 直接排放, 能耗排放, 资源回用消减")
print(emissionCO2, energyCO2, avoidCO2)
print("污泥处置单元能耗: 电能(kWh/t sludge），化石能(kJ/t sludge），总能源再生(kJ）")
print(electricity, diesel, renew)
print("污泥产量（kg）：", end="")
print(sludge)
"""
print("DONE!!!")