# Software security

Security fixes target the main branch. Minhao Liu is the sole maintainer; there
is no guaranteed response deadline.

Report software vulnerabilities privately through
[GitHub vulnerability reporting](https://github.com/chineseschrodingercat/elvia/security/advisories/new)
when available, or contact contact@elvia-atlas.org. Include the affected commit,
environment, impact and a minimal synthetic reproduction. Do not post credentials
or exploitable details in public Issues.

Scientific concerns belong in the website's contribution workflow. The security
channel is not a confidential scientific intake service.

Site building and record export never execute evidence code. Report compilation
is an offline maintainer operation on reviewed sources with shell execution
disabled. Uploaded files are not executable jobs. See the
[record format](docs/record-format.md) and [website operations](website/README.md)
for filesystem, authentication and deployment boundaries.
