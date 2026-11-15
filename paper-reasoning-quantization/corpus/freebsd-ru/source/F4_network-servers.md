# Network Servers

## Domain Name System (DNS)

Domain Name System (DNS) is the protocol through which domain names are mapped to IP addresses, and vice versa. DNS is coordinated across the Internet through a somewhat complex system of authoritative root, Top Level Domain (TLD), and other smaller-scale name servers, which host and cache individual domain information. It is not necessary to run a name server to perform DNS lookups on a system.

The following table describes some of the terms associated with DNS:

| Term | Definition |
| --- | --- |
| Forward DNS | Mapping of hostnames to IP addresses. |
| Origin | Refers to the domain covered in a particular zone file. |
| Resolver | A system process through which a machine queries a name server for zone information. |
| Reverse DNS | Mapping of IP addresses to hostnames. |
| Root zone | The beginning of the Internet zone hierarchy. All zones fall under the root zone, similar to how all files in a file system fall under the root directory. |
| Zone | An individual domain, subdomain, or portion of the DNS administered by the same authority. |

Examples of zones:

* `.` is how the root zone is usually referred to in documentation.
* `org.` is a Top Level Domain (TLD) under the root zone.
* `example.org.` is a zone under the `org.` TLD.
* `1.168.192.in-addr.arpa` is a zone referencing all IP addresses which fall under the `192.168.1.*` IP address space.

As one can see, the more specific part of a hostname appears to its left. For example, `example.org.` is more specific than `org.`, as `org.` is more specific than the root zone. The layout of each part of a hostname is much like a file system: the /dev directory falls within the root, and so on.

### Reasons to Run a Name Server

Name servers generally come in two forms: authoritative name servers, and caching (also known as resolving) name servers.

An authoritative name server is needed when:

* One wants to serve DNS information to the world, replying authoritatively to queries.
* A domain, such as `example.org`, is registered and IP addresses need to be assigned to hostnames under it.
* An IP address block requires reverse DNS entries (IP to hostname).
* A backup or second name server, called a slave, will reply to queries.

A caching name server is needed when:

* A local DNS server may cache and respond more quickly than querying an outside name server.

### DNS Server Configuration

Unbound is provided in the FreeBSD base system. By default, it will provide DNS resolution to the local machine only. While the base system package can be configured to provide resolution services beyond the local machine, it is recommended that such requirements be addressed by installing Unbound from the FreeBSD Ports Collection.

To enable Unbound, add the following to /etc/rc.conf:

```
local_unbound_enable="YES"
```

Any existing nameservers in /etc/resolv.conf will be configured as forwarders in the new Unbound configuration.

> **NOTE**
>
> If any of the listed nameservers do not support DNSSEC, local DNS resolution will fail. Be sure to test each nameserver and remove any that fail the test, for example for a nameserver running on `192.168.1.1`.

Once each nameserver is confirmed to support DNSSEC, start Unbound:

```shell
# service local_unbound onestart
```
