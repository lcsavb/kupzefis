## kupzefis - Gentoo Linux's kernel installation script for a EFISTUB boot

A simple CLI program to automate kernel and initramfs creation and instalation.
I've coded it to use it in my gentoo's box running on a zfs root and booting by efistub.

### Options
  --mountpoint TEXT  Selects efi boot partition mount directory, e.g. /efi
  
  --efidir TEXT      Selects efi directory, e.g. /efi/efi/gentoo
  
  --bootdir TEXT     Selects boot directory, e.g. /boot
  
  --bootdisk TEXT    Selects boot disk, e.g. /dev/sda
  
  --kver TEXT        Selects kernel version, e.g. 5.4.72
  
  --quiet INTEGER    Quiet startup. 1 or 0.
  
  --splash INTEGER   Yes if you would like to use plymouth. 1 or 0.
  
  --rootpool TEXT    Selects root pool, e.g. zpool/ROOT/gentoo

### Requirements
Dracut
pip packages - tqdm, click
