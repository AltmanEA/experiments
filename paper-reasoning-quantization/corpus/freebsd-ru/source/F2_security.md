# Security

## SSH Server Security Options

While sshd is the most widely used remote administration facility for FreeBSD, brute force and drive by attacks are common to any system exposed to public networks.

Several additional parameters are available to prevent the success of these attacks and will be described in this section. All configurations will be done in /etc/ssh/sshd_config

> **TIP**
>
> Do not confuse /etc/ssh/sshd_config with /etc/ssh/ssh_config (note the extra `d` in the first filename). The first file configures the server and the second file configures the client. Refer to `ssh_config(5)` for a listing of the available client settings.

By default, authentication can be done with both pubkey and password.
To allow *only* pubkey authentication, *which is strongly recommended*, change the variable:

```
PasswordAuthentication no
```

It is a good idea to limit which users can log into the SSH server and from where using the `AllowUsers` keyword in the OpenSSH server configuration file. For example, to only allow `user` to log in from `192.168.1.32`, add this line to /etc/ssh/sshd_config:

```
AllowUsers user@192.168.1.32
```

Multiple users should be listed on the same line, like so:

```
AllowUsers root@192.168.1.32 user
```

After making all the changes, and before restarting the service, it is recommended to verify that the configuration made is correct by executing the following command:

```shell
# sshd -t
```

After making the changes and checking that the configuration file is correct, tell sshd to reload its configuration file by running:

```shell
# service sshd reload
```

## OpenSSL

OpenSSL is a cryptography toolkit implementing the Secure Sockets Layer (SSL) and Transport Layer Security (TLS) network protocols and many cryptography routines.

The openssl program is a command line tool for using the various cryptography functions of OpenSSL's crypto library from the shell. It can be used for:

* Creation and management of private keys, public keys and parameters
* Public key cryptographic operations
* Creation of X.509 certificates, CSRs and CRLs
* Calculation of Message Digests
* Encryption and Decryption with Ciphers
* SSL/TLS Client and Server Tests
* Handling of S/MIME signed or encrypted mail
* Time Stamp requests, generation and verification
* Benchmarking the crypto routines
