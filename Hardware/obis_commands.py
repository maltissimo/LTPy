"""
The following is a list of commands for the OBIS LX laser and its OBIS Remote.
It is taken from the OBIS LX_LS Interface Commands Part 3 Manual, pp 29 - 31

The OBIS logic is simple: given a parameter (i.e. Analog Modulation Type), the parameter is set with

SYSTem:INFormation:AMODulation:TYPe

and queried by appending a question mark at the end:

SYSTem:INFormation:AMODulation:TYPe?

In the Python version, the command is made all capital,  shortened, and to underline the query, an "is" is prependend
to the command. In the case above:


SYSTem:INFormation:AMODulation:TYPe  -> ANALOGMODULATION
SYSTem:INFormation:AMODulation:TYPe?  -> isANALOGMODULATION


M. Altissimo
20210531

"""

isIDENT = "*IDN?"
isWARMBOOT = "*RST"
isSELFTEST = "*TST?"
HSHAKE = "SYSTem:COMMunicate:HANDshaking"
isHSHAKE = "SYSTem:COMMunicate:HANDshaking?"
COMMPROMPT = "SYSTem:COMMunicate:PROMpt"
isCOMMPROMPT = "SYSTem:COMMunicate:PROMpt?"
AUTOSTARTENABLE = "SYSTem:AUTostart"
isAUTOSTARTENABLE = "SYSTem:AUTostart?"
ANALOGMODULATION = "SYSTem:INFormation:AMODulation:TYPe"
isANALOGMODULATION = "SYSTem:INFormation:AMODulation:TYPe?"
isSYSTSTATUS = "SYSTem:STATus?"
isSYSTFAULT = "SYSTem:FAULt?"
LASINDONOFF = "SYSTem:INDicator:LASer"
isLASINDONOFF = "SYSTem:INDicator:LASer?"
isERRCOUNT = "SYSTem:ERRor:COUNt?"
isNEXTERR = "SYSTem:ERRor:NEXT?"
CLEARERR = "SYSTem:ERRor:CLEar"
isLASERMODEL = "SYSTem:INFormation:MODel?"
isMANUFDATE = "SYSTem:INFormation:MDATe?"
isCALIBDATE = "SYSTem:INFormation:CDATe?"
isLASSERNUMB = "SYSTem:INFormation:SNUMber?"
isLASPARTNUMB = "SYSTem:INFormation:PNUMber?"
isLASFWVER = "SYSTem:INFormation:FVERsion?"
isOBISPROTVER = "SYSTem:INFormation:PVERsion?"
isWLENGTH = "SYSTem:INFormation:WAVelength?"
isPOWER = "SYSTem:INFormation:POWer?"
isDEVTYPE = "SYSTem:INFormation:TYPe?"
isNOMPOWOUT = "SOURce:POWer:NOMinal?"
isPOWLOWLIM = "SOURce:POWer:LIMit:LOW?"
isPOWHIGHLIM = "SOURce:POWer:LIMit:HIGH?"
USDEFINFO = "SYSTem:INFormation:USER"
isUSDEFINFO = "SYSTem:INFormation:USER?"
FIELDCALIBDATE = "SYSTem:INFormation:FCDate"
isFIELDCALIBDATE = "SYSTem:INFormation:FCDate?"
isONOFFCYCLES = "SYSTem:CYCLes?"
isONTIME = "SYSTem:HOURs?"
isDIODEOPTIME = "SYSTem:DIODe:HOURs?"
isOUTPOWLEVEL = "SOURce:POWer:LEVel?"
isOUTCURLEVEL = "SOURce:POWer:CURRent?"
isBPTEMP = "SOURce:TEMPerature:BASeplate?"
isSYSTINTLOCK = "SYSTem:LOCK?"
LASOPMODEINTCW = "SOURce:AM:INTernal"
LASOPMODEEXTMOD = "SOURce:AM:EXTernal"
isLASOPMODE = "SOURce:AM:SOURce?"
LASPOWLEVEL = "SOURce:POWer:LEVel:IMMediate:AMPLitude"
isLASPOWLEVEL = "SOURce:POWer:LEVel:IMMediate:AMPLitude?"
LASON = "SOURce:AM:STATe"
isLASON = "SOURce:AM:STATe?"
CDRHEMDEL = "SYSTem:CDRH"
isCDRHEMDEL = "SYSTem:CDRH?"
TEMPPROBONOFF = "SOURce:TEMPerature:APRobe"
isTEMPPROBONOFF = "SOURce:TEMPerature:APRobe?"
SELFLASPOWCAL = "SOURce:POWer:CALibration"
UNDOSELFLASPOWCAL = "SOURce:POWer:UNCalibration"
BLANKONOFF = "SOURce:AModulation:BLANKing"
isBLANKONOFF ="SOUR:AM:BLAN?"
isHTLIMIT = "SOURce:TEMPerature:PROTection:INTernal:HIGH?"
isLTLIMIT = "SOURce:TEMPerature:PROTection:INTernal:LOW?"
isDTEMP = "SOURce:TEMPerature:DIODe?"
isDTEMPSETP = "SOURce:TEMPerature:DSETpoint?"
isINTLASTEMP = "SOURce:TEMPerature:INTernal?"

