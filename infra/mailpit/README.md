# Mailpit

[Mailpit][mailpit] is an email testing tool for development.

## Setup

You only need to setup ssl certificates to get this mailpit instance working. This can be done with this command:

```shell
openssl req -x509 -newkey rsa:4096 -nodes -keyout key.pem -out cert.pem -sha256 -days 3650
```

Source: [MailPit Documentation][create-cert]

This will create self signed certificates valid for 365 days.

[mailpit]: https://mailpit.axllent.org/docs/
[create-cert]: https://mailpit.axllent.org/docs/configuration/certificates/
