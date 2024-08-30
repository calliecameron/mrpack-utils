# mrpack-utils

Utilities for managing Modrinth-format (mrpack) Minecraft modpacks.

All commands are read only.

## List modpack contents

```shell
./mrpack list mods.mrpack
```

## Check for compatibility with newer game versions

Modpacks can only be upgraded to a newer game version if every mod in the pack
supports that version. For each mod in the modpack, the script checks whether a
version of the mod exists that is compatible with the given game versions, and
reports which mods are not compatible:

```shell
./mrpack list --check-version 1.20 --check-version 1.20.1 mods.mrpack
```

Limitations:

* Only supports Modrinth modpacks (mrpack), and only checks mods from Modrinth.
  CurseForge mods in the 'overrides' section of the modpack will have to be
  checked manually.
* Doesn't actually update the modpack to the newer game version, only reports
  whether the update would be possible. Mod loaders can do the update.

## Diff modpack versions

```shell
./mrpack diff v1.mrpack v2.mrpack
```
