# 📜 Changelog
Tous les changements notables de ce projet seront documentés ici.




# [0.0.2-alpha] - 2025-10-23
### Information
 - Many translation issues have been identified. They will be fixed in upcoming versions once the translation engine is stabilized.




# [0.0.2-alpha] - 2025-11-07
### Information
 - Winion is completely open source: the GitHub repository is public, with the full source code accessible via git clone, under the CC BY-NC-ND 4.0 license. I must clarify this, as it is due to the fact that the documentation is outdated and may have caused some confusion.




# [0.0.2-alpha] - 2025-11-08
### Added
- Linux support is finally available!
Winion can now run on distributions based on the Linux kernel (successfully tested on Ubuntu).
This version is still undergoing optimization and stabilization before being ready for production use.
⚠️ The package system remains partially incompatible, as it was originally designed for Windows.
Only packages written entirely in pure Python are currently supported.

### Changed
- Réécriture du gestionnaire de paquets (préparation compatibilité Linux)

### Fixed

### Removed

### Information

# [0.0.2-alpha] - 2025-11-11
### Fixed
- Implementation of an open-source alternative aimed at improving translation quality and correcting inconsistencies found in the previous translation engine.

# [0.0.2-alpha] - 2025-11-13
### Added
- Added a remote security check at Winion startup via the community repository winion-status, displaying an alert message and blocking startup if a potential issue is detected, while providing the --no-remote-check option for experienced users wishing to bypass this check, with a warning about the associated risks.
- Tribute to the victims of the Islamic attacks on November 13.

# [0.0.2-alpha] - 2025-11-14
### Added
- The Winion translation system now allows changing the language on the fly, without requiring an application restart.