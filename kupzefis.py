import subprocess
import os
from tqdm import tqdm

eselect_command = subprocess.run(['eselect', 'kernel', 'list'],
                            capture_output=True, text=True)

kernel_list = eselect_command.stdout.splitlines()

efi_dir = "/efi/efi/gentoo"

boot_dir = "/boot"


for k in kernel_list:
    if k.endswith('*'):
        selected_kernel = k
       
kernel = selected_kernel.split()[1]
kver = kernel[6:]

os.chdir('/usr/src/linux')

#Compiling and installing kernel and modules
make_kernel_commands = ['modules prepare', '-j17', 'modules_install',
                        'install']

for command in tqdm(make_kernel_commands, desc=f'Compiling and installing kernel {kver}'):
    subprocess.run('make ' + command,shell=True,stdout=subprocess.DEVNULL)

pk_commands = ['emerge -q @module-rebuild',
                f'dracut -f --kver {kver}',
                'mount /dev/nvme2n1p1 /efi',
                f'cp initramfs-{kver}.img {efi_dir}',
                f'cp vmlinuz-{kver} {efi_dir}/vmlinuz-{kver}.efi'
                ]

os.chdir('/boot')

for command in tqdm(pk_commands,desc='Rebuilding modules and generating initramfs'):
    subprocess.run(command, shell=True, stdout=subprocess.DEVNULL)



# Update firmware record
efi_command = f'efibootmgr --disk /dev/nvme2n1 --part 1 --create --label "Gentoo {kver}" --loader "efi\gentoo\\vmlinuz-{kver}.efi" --unicode "root=ZFS=gpool/ROOT/gentoo ro quiet splash initrd=\efi\gentoo\initramfs-{kver}.img"'

subprocess.run(efi_command,shell=True)

