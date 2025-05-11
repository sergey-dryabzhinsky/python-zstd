# pyzstd version 1.5.7.0

benchmark over multiple versions of python with different build options.

## system
CPU: i7-6850K CPU @ 3.60GHz
MEM:4x116Gb DDR4 2400
SYS:
- host: proxmox3 (debian7)
- guest: vm container openvz6 (ubuntu16):g gcc-5

## tests
mainly results from internal `pythonX.Y setup.py test`

### options:
- `--small`: compilation with `-Os`
- `--speed`: compilation with `-O3`
- `--speed-max`: compilation with `-march=native`
- `--libzstd-no-threads`: compilation without threads support

### results

asm:yes
threads:yes
**optimization: -O2**
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

asm: yes
threads:yes
**optimization: -Os**
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

asm:yes
threads:yes
**optimization: -O3 -march=native**
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

**asm:no**
threads:yes
optimization: -O2
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
