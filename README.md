# mc-mod-compatibility

Minecraft modpacks can only be upgraded to a newer game version if every mod in
the pack supports that version. Checking this manually is tedious - this script
automates it.

For each mod in the modpack, the script checks whether a version of the mod
exists that is compatible with the given game versions, and reports which mods
are not compatible:

```shell
./compatibility.py --version 1.20 --version 1.20.1 mods.mrpack
```

## Limitations

* Only supports Modrinth modpacks (mrpack), and only checks mods from Modrinth.
  CurseForge mods in the 'overrides' section of the modpack will have to be
  checked manually.
* Doesn't actually update the modpack to the newer game version, only reports
  whether the update would be possible. Mod loaders can do the update.
