# Intel-i9-10900-Gigabyte-Z490-Vision-G-Hackintosh  

## USB Port Configuration  

I created my own SSDT-UIAC.aml using Hackintool v3.4.0. Previously I used [corpnewt/USBMap](https://github.com/corpnewt/USBMap) but I discovered it has some bugs.  

Below is the usb map of Vision G. Please notice that HS12 is the onboard RGB fusion controller. I spend some hours figuring out what this port is doing. Also, I don't have a USB-C port on my case, so I don't know the F-U32C internal USB header's port. It's welcome to tell me by pull requests or issues so I can update the map.  

![](USB-Map/USB-Map.png)

In my SSDT-UIAC.aml, I disabled HS03, SS03, HS01 and HS12 so other USB ports all works at their original specs(except F-U32C). Besides, I set HS02 to internal port because it's the port where my Fenvi T919's bluetooth header is connected to.