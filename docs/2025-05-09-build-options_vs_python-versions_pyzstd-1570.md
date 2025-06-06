# pyzstd version 1.5.7.0

benchmark over multiple versions of python with different build options.

## system
- CPU: i7-6850K CPU @ 3.60GHz
- MEM:4x116Gb DDR4 2400
- SYS:
 - host: proxmox3 (debian7)
 - guest: vm container openvz6 (ubuntu16):g gcc-5

## tests
mainly results from internal `pythonX.Y setup.py test`

### options:
- `--small`: compilation with `-Os`
- `--speed`: compilation with `-O3`
- `--speed0`: compilation with `-O0`
- `--speed1`: compilation with `-O1`
- `--speed2`: compilation with `-O2`
- `--speed3`: compilation with `-O3`
- `--speed-max`: compilation with `-march=native` and `-O3`
- `--libzstd-no-threads`: compilation without threads support
- `--libzstd-no-use-asm`: compilation without use assembler (if any...)

### results

- asm:yes
- threads:yes
- **optimization: -O2**
```
python version	size,kb	check Mb/Sec	compress Mb/Sec	decompress blk Mb/Sec
.2.7.18.	588	611,37	31,27	44,56
.3.4.10.	412	407,86	20,16	27,95
.3.5.10.	588	402,76	24,42	27,02
.3.6.15.	588	533,86	31,12	43,93
.3.7.17.	588	417,99	25,84	36,66
.3.8.20.	580	473,98	29,82	42,77
.3.9.22.	580	523,07	28,61	44,22
.3.10.17.	588	530,97	29,83	44,07
.3.11.12.	588	502,44	30,52	42,62
.3.12.10.	588	509,94	22,6	33,87
.3.13.3-gil	588	596,89	30,78	44,71
.3.13.3-nogil		488,69	30,73	42,43
.3.14.0-gil	588	600,26	30,96	44,16
.3.14.0-nogil		581,69	30,91	43,71
```

- asm: yes
- threads:yes
- **optimization: -Os**
```
python version	size,kb	check Mb/Sec	compress Mb/Sec	decompress blk Mb/Sec
.2.7.18.	412	620,03	25,56	38,46
.3.4.10.	412	515,7	24,6	37,29
.3.5.10.	412	503,68	24,07	37,81
.3.6.15.	412	531,94	24,56	37,6
.3.7.17.	412	510,33	24,08	37,63
.3.8.20.	404	516,43	24,25	36,47
.3.9.22.	404	518,18	24,09	35,97
.3.10.17.	412	534,63	24,32	36,28
.3.11.12.	412	498,29	24,35	36,12
.3.12.10.	412	579,05	24,56	37,52
.3.13.3-gil	412	607,58	23,28	37,19
.3.13.3-nogil
.3.14.0-gil	412	562,64	24,29	36,98
```

- asm:yes
- threads:yes
- **optimization: -O3 -march=native**
```
python version	size,kb	check Mb/Sec	compress Mb/Sec	decompress blk Mb/Sec
.2.7.18.	688	617,92	33,53	49,05
.3.4.10.	684	510,15	32,62	48,06
.3.5.10.	684	507,18	32,79	46,61
.3.6.15.	684	533,64	32,29	47,73
.3.7.17.	684	517,14	32,72	47,56
.3.8.20.	628	518,16	32	48,37
.3.9.22.	628	527,06	31,9	47,15
.3.10.17.	684	541,39	33,49	47,92
.3.11.12.	684	506,61	33,18	45,45
.3.12.10.	684	594,67	33,49	48,03
.3.13.3-gil	684	616,04	33,22	48,7
.3.14.0b1-gil	684	588,15	33,66	49,11
.3.14.0b1-nogil	684	573,43	33,56	47,71
```

- **asm:no**
- threads:yes
- optimization: -O2
```
python version	size,kb	check Mb/Sec	compress Mb/Sec	decompress blk Mb/Sec	decompress strm Mb/Sec
.2.7.18.	588	623,34	31,24	43,98	40,26
.3.4.10.	588	516,59	30,44	43,64	41,3
.3.5.10.	588	494,67	30,61	43,42	41,37
.3.6.15.	588	519,98	30,89	43,47	40,77
.3.7.17.	588	521,23	30,36	43,84	40,81
.3.8.20.	580	519,81	30,02	42,61	39,92
.3.9.22.	580	509,62	30,64	42,71	40,12
.3.10.17.	588	517,77	30,05	43,09	40,78
.3.11.12.	588	489,68	30,18	41,99	40,7
.3.12.10.	588	590,05	30,2	43,23	40,79
.3.13.3-gil	588	602,03	31,48	44,72	41,52
.3.14.0b1-gil	588	584,01	31,09	43,57	39,08
```

- gcc:5
- **asm:no**
- threads:yes,fixed
- optimization: -O2
```
python version	size,kb	check Mb/Sec	compress one thread Mb/Sec	compress Mb/Sec	decompress blk Mb/Sec	decompress strm Mb/Sec
.2.7.18.	592	598,95	29,75	29,8	44,67	41,06
.3.4.10.	588	516,78	30,62	30,8	43,95	41,37
.3.5.10.	588	500,65	30,8	31,02	41,84	38,86
.3.6.15.	588	532,63	30,98	30,42	44,18	41,54
.3.7.17.	588	520,29	30,54	30,4	43,85	41,35
.3.8.20.	580	522,47	29,02	29,44	42,76	40,18
.3.9.22.	580	522,08	30,5	30,54	43,69	41,2
.3.10.17.	588	484,36	27,03	29,54	42,67	40,45
.3.11.12.	588	499,28	30,02	30,18	40,12	39,52
.3.12.10.	592	592,67	31,1	30,93	43,76	41,56
.3.13.3-gil	588	607,58	30,53	30,23	44,22	41,11
.3.13.3-nogil	592	493,77	29,5	27,45	42	37,28
.3.14.0b1-gil	588	577,32	30,85	30,89	44,05	40,41
.3.14.0b1-nogil	592	562,94	29,66	30,42	42,61	37,79
```

gcc:5
asm:no
threads:yes,**fixed**
**optimization: -O0**
```
python version	size,kb	check Mb/Sec	compress one thread Mb/Sec	compress Mb/Sec	decompress blk Mb/Sec	decompress strm Mb/Sec
.2.7.18.	1400	562,41	4,5	4,5	9,21	6,88
.3.4.10.	1400	492,79	4,49	4,49	9,24	6,85
.3.5.10.	1400	477,61	4,39	4,43	9,21	6,9
.3.6.15.	1400	499,82	4,51	4,52	9,27	6,9
.3.7.17.	1400	479,66	4,43	4,45	8,95	6,92
.3.8.20.	1400	484,96	4,47	4,4	9,03	6,86
.3.9.22.	1400	490,29	4,44	4,41	9,12	6,9
.3.10.17.	1400	506,79	4,47	4,49	8,79	6,93
.3.11.12.	1400	477,96	4,44	4,49	9,19	6,86
.3.12.10.	1400	555,44	4,5	4,48	9,16	6,84
.3.13.3-gil	1400	563,19	4,48	4,41	9,2	7
.3.13.3-nogil	1400	470,12	4,38	4,33	8,94	6,72
.3.14.0b1-gil	1400	551,12	4,41	4,39	9,1	6,8
.3.14.0b1-nogil	1400	540,12	4,41	3,26	8,38	6,82
```

- **gcc:5**
- **asm:no
- threads:yes	fixed
- **optimization: -O1**
```
python version	size,kb	check Mb/Sec	compress one thread Mb/Sec	compress Mb/Sec	decompress blk Mb/Sec	decompress strm Mb/Sec
.2.7.18.	552	581,83	24,63	24,55	41,8	39,02
.3.4.10.	552	463,01	17,15	18,93	27,66	39,72
.3.5.10.	552	501,21	24,64	24,87	41,63	39
.3.6.15.	552	537,62	24,06	24,78	42,79	40,28
.3.7.17.	552	506,45	19,8	18,27	27,6	29,5
.3.8.20.	540	525,62	25,28	25,14	43,49	41,47
.3.9.22.	540	519,2	25,76	25,59	42,1	40,55
.3.10.17.	552	536,28	24,96	24,56	42,26	39,28
.3.11.12.	552	506,16	24,49	24,4	42,62	40,1
.3.12.10.	552	591,91	24,96	24,9	43,01	40,18
.3.13.3-gil	552	600,96	25,41	25,49	42,93	40,04
.3.13.3-nogil	552	489,43	24,81	24,8	42,16	36,78
.3.14.0b1-gil	552	556,4	24,07	24,12	42,36	39,75
.3.14.0b1-nogil	552	577,9	25,07	25,13	42,55	36,83
```

- **gcc:5**
- **asm:no**
- threads:yes	**fixed**
- **optimization: -O3**
```
python version	size,kb	check Mb/Sec	compress one thread Mb/Sec	compress Mb/Sec	decompress blk Mb/Sec	decompress strm Mb/Sec
.2.7.18.	716	594,3	30,03	30,09	46,87	42,23
.3.4.10.	712	510,43	28,05	27,99	45,89	42,45
.3.5.10.	712	503,13	29,38	29,3	45,76	42,51
.3.6.15.	712	532,59	29,53	29,82	45,05	42,43
.3.7.17.	712	524,2	26,86	26,62	45,66	42,33
.3.8.20.	636	529,65	29,46	29,26	44,37	41,96
.3.9.22.	636	529,77	29,13	29,27	43,33	41,17
.3.10.17.	712	534	29,51	29,48	44,92	41,94
.3.11.12.	712	509,35	29,29	29,2	44,7	42,87
.3.12.10.	712	579,03	29,49	29,51	45,77	42,53
.3.13.3-gil	712	556,89	29,48	29,43	44,42	42,5
.3.13.3-nogil	712	481,68	28,06	28,8	41,78	37,29
.3.14.0b1-gil	712	587,73	29,71	29,78	45,43	42,96
.3.14.0b1-nogil	712	577,96	28,13	28,27	45,52	38,93
```

- gcc:15
- **asm:no**
- threads:yes	**fixed**
- **optimization: -Os**
```
python version	size,kb	check Mb/Sec	compress one thread Mb/Sec	compress Mb/Sec	decompress blk Mb/Sec	decompress strm Mb/Sec
.2.7.18.	392	611,68	24,73	24,76	40,33	37,36
.3.4.10.	392	516,48	24,59	24,51	38,66	37,29
.3.5.10.	400	487,25	24,02	23,7	38,74	35,45
.3.6.15.	392	523,53	24,62	24,71	38,67	36,38
.3.7.17.	392	473,32	21,4	21,53	34,95	36,08
.3.8.20. gcc-5 	404	522,34	24,39	24,45	36,02	33,41
.3.9.22. gcc-5 	494	525,31	23,83	23,78	36,77	33,18
.3.10.17.	393	539,01	24,39	24,38	39,13	36,47
.3.11.12.	392	508,15	24,37	24,43	38,01	36,6
.3.12.10.	392	595,45	23,89	23,93	39,43	37,23
.3.13.3-gil	392	604,85	24,02	24,33	40,09	36,66
.3.13.3-nogil	392	496,43	24,45	24,38	38,53	33,49
.3.14.0b1-gil	392	579,54	24,78	24,69	39,59	36,14
.3.14.0b1-nogil	392	584,39	24,07	24,24	38,98	33,23
```