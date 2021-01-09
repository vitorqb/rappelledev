# RappelleDev

This repository contains dev tools for Rappelle-BE and
Rappelle-Web. It's mostly a wrapper around docker-compose that allows
you to run all services that compose rappelle functionality.


## Installation and Configuration

1. Close this repository to some folder on your local machine:

```sh
git clone 'https://github.com/vitorqb/rappelledev.git' ~/rappelledev
```

2. Create a configuration folder

```sh
mkdir -p ~/.config/rappelledev
```

3. Create a json config file with your configurations. Example:

```json
# File: ~/.config/rappelledev/config.json
{
    "env": "dev",
    "directory": "~/rappelledev"
}
```

4. Create a docker-compose file that may override the default options for rappelledev. Example:

```yaml
# File: ~/.config/rappelledev/docker-compose.override.yaml
version: "3.5"
services:
  rappelle-be:
    image: rappelle-be:0.1.0-2-ge5a1e28
```

5. Run

```sh
~/rappelledev/rappelledev.py run-rappelle-be
```


## Configuration options

The following keys are recognized on `~/.config/rappelledev/config.json`. All other keys are ignored.

#### *env*

Defines the environment we are running, either `dev` or `prod`. Defaults to `prod`.

#### *docker-compose-cmd*

A json array with the command to use for running docker compose. For example, if you need to sudo, you can do this:

```json
    "docker-compose-cmd": ["sudo", "docker-compose"],
```

Defaults to ["docker-compose"]

#### *directory*

The directory where the git repo for rappelledev can be fount. Defaults to `~/rappelledev`.


## Usage tips

### Custom docker-compose configuration (e.g. image tag)

`rappelledev` will pass a docker-compose override file defined at
`~/.config/rappelledev/docker-compose.override.yaml` everytime it runs
any docker-compose command.

For example, in order to change the image tag of one of the services, you can:

```yaml
# file: ~/.config/rappelledev/docker-compose.override.yaml
version: "3.5"
services:
  rappelle-be:
    image: rappelle-be:0.1.0-2-ge5a1e28
  rappelle-web:
    image: rappelle-web:0.2.0
```

### Custom configuration for rappelle-be

Rappelle-BE docker image automatically uses any application file
mounted at `/apps/rappelle/application.conf`.

In order to set custom configuration for the command `rappelledev.py
run-rappelle-be`, you can do the following:

1. Create your `application.conf` in
   `~/.config/rappelle/application.conf`, extending the local
   application config and setting your options:
   
```conf
# File: ~/.config/rappelledev/application.conf
include "application.local.conf"

auth.tokenRepository.type=AuthTokenRepository
auth.userRepository.type=UserRepository
# ....
```

2. Create a docker-compose override file and mount the volume:

```yaml
version: "3.5"
services:
  rappelle-be:
    volumes:
      - ~/.config/rappelledev/application.conf:/apps/rappelle/application.conf
```
