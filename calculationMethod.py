# ======================================================================================================================
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/> Everyone is permitted to copy and distribute
# verbatim copies of this license document, but changing it is not allowed.

# This file contains the whole functions which used to calculate carbon emissions during wastewater treatment process.

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

def strToList(char, Q):
    """
    将读取的键盘输入字符转化为数值列表

    输入参数
    char: 读取的键盘输入字符, 主要为进出水浓度，mg/L
    Q：用户输入的污水厂处理规模莫，m³/d

    输出参数
    listNum: 数值列表，污染物浓度, mg/L
    listW: 数值列表，污染物质量， kg
    """
    char = char.replace(" ", "")
    listStr = char.split(",")
#   listNum = list(map(float, listStr))      # 将字符列表转化为数值列表，mg/L
    listNum = [x / 1000 for x in list(map(float, listStr))]    # 将字符列表转化为数值列表，kg/m³
    listW = [x * Q for x in listNum]                           # 获取污染物质量列表,kg/yr
    return listNum, listW

def getConRed(conIn, conOut):
    """
    获取污染物消减列表

    输入参数
    conIn: 进水污染物质量列表[COD, TN,...]，kg/yr
    conOut：出水污染物质量列表[COD, TN,...]，kg/yr

    输出参数
    conReduction： 污染物消减列表, kg/yr
    """
    if len(conIn) != len(conOut):
        raise Exception("ERROR: THE LENGTH OF THESE TWO LISTS MUST BE EQUAL!!!")

    conReduction = [x-y for (x, y) in zip(conIn, conOut)]
#    for (x, y) in zip(conIn, conOut):
#        conReduction.append(x - y)     # 获取污染物消减量列表
    return conReduction

def gasEmission(conIn, conOut, coeff):
    """
    采用排放系数法计算污水处理过程中排放的二氧化碳、甲烷、氧化亚氮等温室气体

    输入参数
    conIn: 污染物输入量列表[COD, TN,...]，kg
    conOut：污染物输出量列表[COD, TN,...]，kg
    coeff: 温室气体排放系数列表[CO2, CH4, N2O,...], g/kg

    输出参数
    EmCO2, EmCH4, EmN2O: 消减污染物产生的二氧化碳、甲烷、氧化亚氮排放量，kg
    """
    conRed = getConRed(conIn, conOut)
    EmCO2 = conRed[0] / 1000 * coeff[0]       # kg
    EmCH4 = conRed[0] / 1000 * coeff[1]       # kg
    EmN2O = conRed[1] / 1000 * coeff[2]       # kg
    return EmCO2, EmCH4, EmN2O

def energyConsumptionW(Q, coeff, coeffElec):
    """
    计算污水处理过程中由于电能消耗产生的二氧化碳排放量

    输入参数
    Q: 污水厂处理能力，m³/yr
    coeff: 能耗系数列表，kWh/m³
    coeffElec: 电能的二氧化碳排放因子，kg CO2/ kWh

    输出参数
    energy: 消耗电能，kWh
    CO2: 电能消耗导致的二氧化碳排放量，kg
    """
    energy = Q * sum(coeff)
    CO2 = energy * coeffElec
    return energy, CO2

def chemicalConsumption(Q, mass, coeff):
    """
    计算药耗产生的二氧化碳排放量

    输入参数
    Q: 污水厂处理能力，m³/yr
    mass: 质量列表，kg/m³
    coeff: 二氧化碳排放因子列表，kg CO2/ kg 试剂

    CO2: 药耗导致的二氧化碳排放量，kg
    """
    if len(mass) != len(coeff):
        raise Exception("ERROR: THE LENGTH OF THESE TWO LISTS MUST BE EQUAL!!!")

    CO2List = [x * y * Q for (x, y) in zip(mass, coeff)]
#    for (x, y) in zip(mass, coeff):
#        CO2List.append((x * y)/1000)
    CO2 = sum(CO2List)
    return CO2

def sludgeOutput(conIn, conOut, rate):
    """
    根据氮、碳、磷的物料平衡及微生物化学通式(C5H8O2N)计算是否需补充碳源，及剩余污泥的产量。

    输入参数
    conIn: 污染物输入量列表[COD, TN,...]，kg
    conOut：污染物输出量列表[COD, TN,...]，kg
    rate: 消减TN转化为生物质的比例（%)

    输出参数
    additionalSC: 外加碳源（methanol），kg
    sludge: 污泥产量，kg
    """
    conReduction = getConRed(conIn, conOut)
    C = conReduction[0] * 12 / 16  # kg
    N, P = conReduction[1], conReduction[2]  # kg
    n = (C / 12) / (N / 14)  # molar ratio
    if n <= 5:
        sludge = (N * rate * 114 / 14) + (P * 110 / 62)     # kg
        additionalSC = (N * 5 - C) * 35 / 12   # 甲醇使用量   kg
    else:  # a > 5
        sludge = (N * rate * 114 / 14) + P * 0.5 + (C / 12 - (N / 14) * 5) * 30     # kg
        additionalSC = 0
    return additionalSC, sludge

def biogenicGas(sludge, VS, ratio, percent, coeff):
    """
    计算厌氧消化过程由于生物异化产生的二氧化碳量，以及厌氧消化残渣。

    输入参数
    sludge: 污泥质量，kg
    VS: 挥发性固体的比例，%
    ratio:甲烷泄露比例， %
    percent：气态产物组分体积百分比列表，%
    coeff: 二氧化碳释放系数列表,kg/t

    输出参数
    emissionCO2: 二氧化碳释放量，kg
    emissionCH4: 甲烷释放量，kg
    residueWeight: 厌氧消化残渣，t
    """
    residueWeight = sludge * (1 - VS) / 1000
    emissionCH4 = sludge * VS * coeff[0] * ratio / 1000 + residueWeight * coeff[1]
    emissionCO2 = sludge * VS * coeff[0] * (44 / 16) * (percent[0] / percent[1]) / 1000 + residueWeight * coeff[2]
    return emissionCO2, emissionCH4, residueWeight

def energyConsumptionS(sludge, VS, energy, coeff):
    """
    计算厌氧消化过程中由于能耗产生的二氧化碳排放。次计算中扣除了能源回用部分。

    输入参数
    sludge: 污泥质量，kg
    VS: 挥发性固体的比例，%
    energy: 能耗列表，kJ
    ratio:甲烷泄露比例， %
    coeff: 排放系数列表

    输出参数
    energyS: 能耗产生二氧化碳排放量，kg
    """
    residueWeight = sludge / 1000 * (1 - VS)
    energyS = (sludge * energy[0] * coeff[0] + (sludge * energy[2] - energy[3]) *
               coeff[1]) + residueWeight * energy[1] * coeff[0] + energy[2] * coeff[2]
    return energyS

def avoidedCO2(sludge, VS, Sa, coeff):
    """
    残渣土地利用消减化肥用量

    输入参数
    sludge: 污泥质量，kg
    VS: 挥发性固体的比例，%
    Sa: 厌氧消化残渣土地利用带来的效益， kWh/t残渣
    coeff: 二氧化碳排放系数

    输出参数
    CO2: 资源再利用效益带来的二氧化碳消减量， kg
    """
    residueWeight = sludge * (1 - VS)
    CO2 = residueWeight * Sa * coeff / 1000
    return CO2

def globalWP(list1, list2):
    """
    温室效应潜力计算

    输入参数
    list1: 污染物列表，kg
    list2: 温室效应潜力列表，

    输出参数
    GWP: 温室效应潜力
    """
    if len(list2) != len(list1):
        raise Exception("ERROR: THE LENGTH OF THESE TWO LISTS MUST BE EQUAL!!!")

    lit = []
    for (x, y) in zip(list1, list2):
        lit.append(x * y)
        GWP = sum(lit)
    return GWP

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
