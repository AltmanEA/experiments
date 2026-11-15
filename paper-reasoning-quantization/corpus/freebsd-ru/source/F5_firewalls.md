# Firewalls

## IPFW

### Enabling IPFW

To configure the system to enable IPFW at boot time, add `firewall_enable="YES"` to `/etc/rc.conf`:

```shell
# sysrc firewall_enable="YES"
```

To use one of the default firewall types provided by FreeBSD, add another line which specifies the type:

```shell
# sysrc firewall_type="open"
```

The available types are:

* `open`: passes all traffic.
* `client`: protects only this machine.
* `simple`: protects the whole network.
* `closed`: entirely disables IP traffic except for the loopback interface.
* `workstation`: protects only this machine using stateful rules.
* `UNKNOWN`: disables the loading of firewall rules.
* `filename`: full path of the file containing the firewall ruleset.

If `firewall_type` is set to either `client` or `simple`, modify the default rules found in `/etc/rc.firewall` to fit the configuration of the system.

To enable logging through `syslogd(8)`, include this line:

```shell
# sysrc firewall_logging="YES"
```

To limit the number of times a rule is logged per connection attempt, specify the number using this line in `/etc/sysctl.conf`:

```shell
# echo "net.inet.ip.fw.verbose_limit=5" >> /etc/sysctl.conf
```

Then use tcpdump to see what is being logged:

```shell
# tcpdump -t -n -i ipfw0
```

After saving the needed edits, start the firewall. To enable logging limits now, also set the `sysctl` value specified above:

```shell
# service ipfw start
# sysctl net.inet.ip.fw.verbose_limit=5
```
