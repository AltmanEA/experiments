# Configuration, Services, Logging and Power Management

## Configuration Files

### The sysctl utility

The `sysctl(8)` utility is used to make changes to a running FreeBSD system.

The `sysctl(8)` utility retrieves kernel state and allows processes with appropriate privilege to set kernel state. The state to be retrieved or set is described using a "Management Information Base" ("MIB") style name, described as a dotted set of components.

Management Information Base

| MIB | Description |
| --- | --- |
| sysctl | "Magic" numbers |
| kern | Kernel functions and features |
| vm | Virtual memory |
| vfs | Filesystem |
| net | Network |
| debug | Debugging parameters |
| hw | Hardware |
| machdep | Machine dependent |
| user | Userland |
| p1003_1b | POSIX 1003.1B |

At its core, `sysctl(8)` serves two functions: to read and to modify system settings.

To view all readable variables:

```shell
% sysctl -a
```

The output should be similar to the following:

```
kern.ostype: FreeBSD
...
vm.swap_enabled: 1
vm.overcommit: 0
vm.domain.0.pidctrl.kdd: 8
vm.domain.0.pidctrl.kid: 4
vm.domain.0.pidctrl.kpd: 3
...
vfs.zfs.sync_pass_rewrite: 2
vfs.zfs.sync_pass_dont_compress: 8
vfs.zfs.sync_pass_deferred_free: 2
```

To read a particular variable, specify its name:

```shell
% sysctl kern.maxproc
```

The output should be similar to the following:

```
kern.maxproc: 1044
```
