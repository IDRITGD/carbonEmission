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
