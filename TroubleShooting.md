## In case of no Homing ##

- Check:

``
QsysStatus
``
    
if the result is:

``
P8254=19
``
    
then check with 

``
QsysError
``
if this gives:

``
P8256=256
``

then there is ( or has been) an air supply issue.  Try:

    selectAxes=selectAll 
    requestHost=requestRelease #this opens all the valves in the system 
    requestHost=requestIdle


at this point, the outputs should be: 

    QsysStatus
    P8254=18
    QsysError
    P8256=0


in which case the system will home:

``
requestHost=requestHome
``