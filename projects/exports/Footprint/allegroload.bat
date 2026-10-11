allegro -s CMPLX-0020-2_4-3_3.PSX
if exist rr205_63r10.pad del rr205_63r10.pad
padstack_editor -s RR205_63R10.SCR
if exist u240_330r88_133cul20.pad del u240_330r88_133cul20.pad
padstack_editor -s U240_330R88_133CUL20.SCR
if exist SOIC9P127_490X600X170L83X42T-1.dra del SOIC9P127_490X600X170L83X42T-1.dra
allegro -s SOIC9P127_490X600X170L83X42T-1.SCR
