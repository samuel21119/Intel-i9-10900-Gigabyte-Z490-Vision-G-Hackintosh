#!/bin/bash
"""
Scripts to change CPU name in System Information (About This Mac)
"""

locale=`defaults read -g AppleLocale | cut -c 1-2`
cpu_name=`sysctl -n machdep.cpu.brand_string | sed -e 's/ *$//'`
target="/System/Library/PrivateFrameworks/AppleSystemInfo.framework/Versions/A/Resources/${locale}.lproj/AppleSystemInfo.strings"

if [ $# -ge 1 ]; then
  cpu_name=$1
fi

echo "Locale: $locale"
echo "New Name: $cpu_name"
read -p "ok? (y/n): " yn

case $yn in
  [yY])
    sudo mount -uw / &&
    sudo cp $target $target.`date +%Y%m%d%H%M` &&
    sudo plutil -replace IntelSpeedAndTypeFormat -string "%1\$@ $cpu_name" $target
    echo "Finished."
    ;;
  *) echo "Aborted."
esac
