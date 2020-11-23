import subprocess
import os
import click
from tqdm import tqdm

def get_selected_kernel():
    ''' Retrieves the selected kernel from eselect kernel list
     and return the substring with its version '''

    eselect_command = subprocess.run(['eselect', 'kernel', 'list'],
                                 capture_output=True, text=True)
    
    kernel_list = eselect_command.stdout.splitlines()  
  
    for k in kernel_list:
        if k.endswith('*'):
            selected_kernel = k

    kernel_string = selected_kernel.split()[1]
    
    kver = kernel_string.split('-')[1] + '-' + kernel_string.split('-')[2]

    return kver

def boot_entries():
    efibootmgr = subprocess.run('efibootmgr',shell=True,capture_output=True,text=True)
    entries_list = efibootmgr.stdout.splitlines()
    versions_list = []
    for e in entries_list:
        versions_list.append(e.split()[1])
    return versions_list
        
        
def install_kernel(kver,bootdir,efidir):
    os.chdir(bootdir)
    kernel_install_commands = [f'cp initramfs-{kver}.img {efidir}',
                               f'cp vmlinuz-{kver} {efidir}/vmlinuz-{kver}.efi'
                               ]

    for c in tqdm(kernel_install_commands):
        subprocess.run(c, shell=True)


def create_fallback(kver,efidir):
    os.chdir(efidir)

    fallback_creation_commands = [f'mv initramfs-{kver}.img initramfs-{kver}-fallback.img', 
                                    f'mv vmlinuz-{kver}.efi vmlinuz-{kver}-fallback.efi'
                                ]

    for c in tqdm(fallback_creation_commands):
        subprocess.run(c, shell=True)

def update_firmware(kver,bootdisk,rootpool,quiet,splash,efidir,boot_entries):
    if splash:
        splash = 'splash'
    else:
        splash = ''
    if quiet:
        quiet = 'quiet'
    else:
        quiet = ''

    kver_fallback = kver + '-fallback'

    if kver_fallback not in boot_entries:
        efi_command = f'efibootmgr --disk {bootdisk} --part 1 --create --label "{kver_fallback}" --loader "efi\gentoo\\vmlinuz-{kver_fallback}.efi" --unicode "root=ZFS={rootpool} ro {quiet} {splash} initrd=\efi\gentoo\initramfs-{kver_fallback}.img"'
        subprocess.run(efi_command,shell=True)

    if kver not in boot_entries:
        efi_command = f'efibootmgr --disk {bootdisk} --part 1 --create --label "{kver}" --loader "efi\gentoo\\vmlinuz-{kver}.efi" --unicode "root=ZFS={rootpool} ro {quiet} {splash} initrd=\efi\gentoo\initramfs-{kver}.img"'
        subprocess.run(efi_command,shell=True)


@click.command()
@click.option('--mountpoint', default='/efi',
                help='Selects efi boot partition mount directory, e.g. /efi')
@click.option('--efidir', default='/efi/efi/gentoo',
                help='Selects efi directory, e.g. /efi/efi/gentoo')
@click.option('--bootdir', default='/boot',
                help='Selects boot directory, e.g. /boot')
@click.option('--bootdisk', default='/dev/nvme2n1p1',
                help='Selects boot disk, e.g. /dev/sda')
@click.option('--kver', default=get_selected_kernel(),
                help='Selects kernel version, e.g. 5.4.72')
@click.option('--quiet', default=1,
                help='Quiet startup. 1 or 0.')
@click.option('--splash', default=1,
                help='Yes if you would like to use plymouth. 1 or 0.')
@click.option('--rootpool', default='gpool/ROOT/gentoo',
                help='Selects root pool, e.g. zpool/ROOT/gentoo')
def install(efidir,mountpoint,bootdir,bootdisk,kver,rootpool,quiet,splash):
    '''Installs or upgrade the kernel and initramfs'''

    subprocess.run(f'mount {bootdisk} {mountpoint}',shell=True,stdout=subprocess.DEVNULL)
    kernel = 'linux-' + kver
    os.chdir(f'/usr/src/{kernel}')

    #Compiling and installing kernel and modules
    make_kernel_commands = ['modules prepare', '-j17', 'modules_install',
                            'install']

    for command in tqdm(make_kernel_commands, desc=f'Compiling and installing kernel {kver}'):
        subprocess.run('make ' + command,shell=True,stdout=subprocess.DEVNULL)

    pk_commands = ['emerge -q @module-rebuild',
                    f'dracut -f --kver {kver}'
                    ]

    for command in tqdm(pk_commands,desc='Rebuilding modules and generating initramfs'):
        subprocess.run(command, shell=True, stdout=subprocess.DEVNULL)

    os.chdir(efidir)
    if os.path.isfile('vmlinuz-' + kver + '.efi'):
        create_fallback(kver,efidir)

    install_kernel(kver,bootdir,efidir)
    update_firmware(kver,bootdisk,rootpool,quiet,splash,efidir,boot_entries())







        

        





