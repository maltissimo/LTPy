## Objective
Have the scanner averaging over multiple scans. 
**Facilities in place**
1) Measurementcontrols2.py  is ready, has spaces variables and methods implemented:
    ''
    self.gui.nrofscans_input # LineEdit
    self.gui.nrofscans_display # LineEdit
    self.gui.avg_scan #Radio Button
    self.gui.nr_of_measurements_for_avg # Set to 1 to avoid issues.
    ''
2) Variables and methods are connected to the GUI. 
    ''
    get_nr_of_averages(self) #implemented. 
    ''

xStartPos is set by user
nr of scan for avg is set by user
cycle is: 
for i in range (nrofscans):
    meas forward, store fwd_data[i] <- raw_slopes

average fwd_data
display avg_fwd_data
save ALL DATA? Or only avg_fwd_data??
Does this go in a single class?? 
It starts to look like I need a File_handling_utils module... 

