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

- pyzstd version: pre 1.5.7.1
- gcc:15
- **lto:no**
- **asm:no**
- **threads:yes**
- **optimization: -O3**
- **data:x10**
```
pypy version	glibc version needed 	size,kb	check Mb/Sec	compress one thread Mb/Sec	compress Mb/Sec	decompress blk Mb/Sec	decompress strm Mb/Sec
.2.7./7.3.19	.2.14.	756	212,86	14,29	28,83	32,65	65,44
.3.6./7.3.3	.2.14.	757	364,99	14,11	29,25	39,73	86,99
.3.7./7.3.9	.2.14.	757	347,29	14,25	29,51	38,94	86,18
.3.8./7.3.11	.2.14.	745	274,31	9,08	19,54	27,71	60,28
.3.9./7.3.16	.2.14.	745	325,69	13,86	27,73	38,41	77,9
.3.10./7.3.19	.2.14.	745	333,25	13,8	28,85	38,36	73,17
.3.11./7.3.19	.2.14.	745	331,61	13,8	28,68	38,2	77,39
```