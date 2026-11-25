#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check effective Make load lists against the built kernel's thermal providers.

Run after m kernel: python3 kernel/check_thermal_modules.py --kernel-out /path/to/KERNEL_OBJ
This checks packaging inputs and compiled objects, not final images or device probe.
"""
import argparse
from pathlib import Path
import subprocess

PROVIDERS = {
    'qcom-spmi-temp-alarm': 'QCOM_SPMI_TEMP_ALARM',
    'qti_cpufreq_cdev': 'QTI_CPUFREQ_CDEV',
    'qti_devfreq_cdev': 'QTI_DEVFREQ_CDEV',
    'qti_userspace_cdev': 'QTI_USERSPACE_CDEV',
    'qti_dynamic_hw_trip': 'QTI_DYNAMIC_HW_THERMAL_TRIP',
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kernel-out', type=Path, required=True)
    args = parser.parse_args()
    names = ['MYRON_VENDOR_MODULES', 'MYRON_VENDOR_LOAD_MODULES',
             'MYRON_BOOT_LOAD_MODULES', 'MYRON_ALL_MODULES']
    text = 'include modules.mk\n' + ''.join(
        '$(info ' + name + '=$(' + name + '))\n' for name in names)
    text += '.PHONY: check\ncheck:\n\t@:\n'
    result = subprocess.run(['make', '--no-print-directory', '-f', '-', 'check'],
                            cwd=Path(__file__).resolve().parent, input=text,
                            capture_output=True, text=True, check=True)
    groups = dict(line.split('=', 1) for line in result.stdout.splitlines() if '=' in line)
    groups = {key: value.split() for key, value in groups.items()}
    config = (args.kernel_out / '.config').read_text().splitlines()
    for name, symbol in PROVIDERS.items():
        module = name + '.ko'
        if 'CONFIG_' + symbol + '=m' not in config:
            raise SystemExit('FAIL: provider not selected as a module: ' + symbol)
        for group in ('MYRON_VENDOR_MODULES', 'MYRON_VENDOR_LOAD_MODULES', 'MYRON_ALL_MODULES'):
            if groups[group].count(module) != 1:
                raise SystemExit('FAIL: expected exactly one ' + module + ' in ' + group)
        obj = args.kernel_out / 'drivers/thermal/qcom' / (name + '.o')
        data = obj.read_bytes()
        # ELF64, little-endian, AArch64; full .ko/modpost and image checks are separate.
        if data[:6] != b'\x7fELF\x02\x01' or int.from_bytes(data[18:20], 'little') != 183:
            raise SystemExit('FAIL: not an AArch64 ELF object: ' + str(obj))
        print('PASS: ' + module + ' selected, built and in vendor load lists')
    # These dependencies precede the added consumers in the first-stage load list.
    for dependency in ('qcom_scmi_client.ko', 'qcom_scmi_vendor.ko',
                       'qcom_ipc_logging.ko', 'qcom-spmi-pmic.ko'):
        if dependency not in groups['MYRON_BOOT_LOAD_MODULES']:
            raise SystemExit('FAIL: missing first-stage provider: ' + dependency)
    print('PASS: SCMI, IPC logging and PMIC providers selected for first-stage loading')
    print('Final image contents, module loading, thermal HAL and hardware remain unverified.')


if __name__ == '__main__':
    main()
