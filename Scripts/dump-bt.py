#!/usr/bin/env python
"""
Script for dumping Bluetooth pairings from OS X to a registry file, for Windows
import. This will allow you to have your Bluetooth devices paired with both
operating systems at the same time.

In case of problems with Windows registry entries: pair your device with Windows
first, then with OS X, and then do the dump and import.

Latest version can be found at:
https://gist.github.com/a7d842b0a118373ed13a.git

Tutorial: https://www.reddit.com/r/hackintosh/comments/hjwu43/howto_share_a_bluetooth_pairing_headphones_etc/
"""
__author__ = 'pawelszydlo@gmail.com'

import os
import plistlib
import sys
import subprocess

BLUED_PLIST = '/private/var/root/Library/Preferences/com.apple.Bluetoothd.plist'


def _choose_one(options, what='one'):
    """Force user to choose an option if more than one is available."""
    chosen = None
    if not options:
        return
    elif len(options) == 1:
        chosen = 0
    else:
        print 'Choose %s:' % what
        for number, line in enumerate(options):
            print '%d. %s' % (number + 1, line)
        while chosen is None or chosen < 0 or chosen >= len(options):
            chosen = raw_input('Choose (1 - %d): ' % len(options))
            try:
                chosen = int(chosen) - 1
            except ValueError:
                chosen = None
    return options[chosen]


def _run_command(command):
    """Run a shell command."""
    p = subprocess.Popen(
        command, shell=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = '\n'.join(p.stdout.readlines())
    retval = p.wait()
    return retval, output


def _get_pairs(xml_data):
    """Extract host device id and pairings from plist xml."""
    plist = plistlib.readPlistFromString(xml_data)
    keys_root = plist.get('LinkKeys')
    if not keys_root:
        print 'Key LinkKeys not found in blued.plist.'
        return None, []
    hosts = keys_root.keys()
    if not hosts:
        print 'No Bluetooth hosts found in blued.plist.'
        return None, []
    host = _choose_one(hosts, 'Bluetooth host device')
    print 'Using Bluetooth host device %s...' % host
    pairs = []
    for device_id, device_key in keys_root.get(host, {}).items():
        device_key = device_key.data.encode('hex_codec')
        pairs.append([device_id, device_key])
    return host, pairs


def _write_reg_file(host_id, pair):
    """Write the pairing into a Windows registry file."""
    host_id = host_id.replace('-', '')
    device_id = pair[0].replace('-', '')
    key = pair[1]
    # The key needs to be reversed and written as comma separated list of bytes
    key = ','.join(reversed([key[i:i + 2] for i in range(0, len(key), 2)]))

    reg_file = open('bt_pair_%s.reg' % device_id, 'w')
    reg_file.write('Windows Registry Editor Version 5.00\r\n\r\n')
    reg_file.write('[HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\services\\'
                   'BTHPORT\Parameters\Keys\%s]\r\n' % host_id)
    reg_file.write('"%s"=hex:%s\r\n' % (device_id, key))
    reg_file.close()


if __name__ == '__main__':
    # This script should be run as root
    if os.geteuid() != 0:
        print 'You must run this script as root. Try:\nsudo %s' \
              % os.path.basename(__file__)
        sys.exit(1)

    # Get the keys from blued.plist
    status, xml_data = _run_command(
        'plutil -convert xml1 -o - %s' % BLUED_PLIST)
    if status != 0:
        print 'Cannot convert binary blued plist into xml.\n"%s"' % xml_data
        sys.exit(2)
    host_id, pairs = _get_pairs(xml_data)
    if not pairs:
        print 'No pairings found for host device %s.' % host_id
        sys.exit(3)

    # Choose which pair to dump
    chosen = _choose_one(pairs, 'pairing')

    # Dump the selected pair to registry file
    print 'Dumping pairing (%s) to registry file...' % ' = '.join(chosen)
    _write_reg_file(host_id, chosen)

    print 'Done.'
