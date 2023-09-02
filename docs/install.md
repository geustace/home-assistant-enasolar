# Install EnaSolar Integration

This topic describes how to install and use the EnaSolar integration in Home Assistant.

## Prerequisites

* You need to have an EnaSolar Solar inverter and it must be accessible on port 80 over your network.

* You have installed Python 3.8 or a later version on your system.


## Set up

After you have installed Home Assistant Core, you will need to download the EnaSolar files from GitHub and copy them to your Home Assistant deployment. You can find the files on [GitHub](https://github.com/geustace/home-assistant-enasolar). Either clone the repo or download the ZIP file by selecting the Code button.

Copy the **custom_components/enasolar** folder to the **config/custom_components** folder in your Home Assistant deployment.

> **Note**: Only Home Assistant 2021.10.4 and later versions support this integration.

1. Enter `<your HASS server>:8123` into the address bar in your browser and hit Enter to connect to Home Assistant.
2. Log in.
3. Select **Configuration** > **Devices & Services**.

   <img src="https://github.com/geustace/home-assistant-enasolar/blob/main/docs/EnaSolar-1.jpg" width="70%" alt="Integrations">

4. On the **Integrations** page in the configuration panel, select the **+ ADD INTEGRATION** button in the lower right and search for **enasolar**.

   <img src="https://github.com/geustace/home-assistant-enasolar/blob/main/docs/EnaSolar-2.jpg" width="70%" alt="Add integration">

5. Select **EnaSolar Solar Inverter** and set up the integration.

   <img src="https://github.com/geustace/home-assistant-enasolar/blob/main/docs/EnaSolar-3.jpg" width="65%">
<a id="Config 1"></a>

6. Replace **my.inverter.fqdn** with the Fully Qualified Domain Name or the IP Address of your inverter.  You can enter a name but this is only useful if you have more than one inverter and need to differentiate the sensors. Select **NEXT**

   <img src="https://github.com/geustace/home-assistant-enasolar/blob/main/docs/EnaSolar-4.jpg" width="65%" alt="Config 2">

7. The next panel has the capabilities and attributes of your inverter.  If you know that they are incorrect, you can override them by selecting appropriate values.

   <img src="https://github.com/geustace/home-assistant-enasolar/blob/main/docs/EnaSolar-5.jpg" width="65%" alt="Config 3">

7. Select **Submit**.

## Polling the Inverter

There is an issue with the internal web server in the inverter.  If it is polled too aggressively it locks up and will no longer respond.  The only solution to getting it back online is to turn the inverter off by turning the main AC switch OFF, waiting about 10 secs and then turning it ON again.

To prevent the lock up, the integration polls for meters every minute.

There is also little point in polling at night. The code has been updated to only poll when the Sun
is deemed to be UP by Home Assistant.

