# Install EnaSolar Integration

This topic describes how to install and use the EnaSolar integration in Home Assistant.

## Prerequisites

* You need to have an EnaSolar Solar inverter and it mst be accessible on port 80 over your network.

* You have installed Python 3.8 or a later version on your system.


## Set up

After you have installed Home Assistant Core, you will need to download the EnaSolar files from GitHub and copy them to your Home Assistant deployment. You can find the files on [GitHub](https://github.com/geustace/home-assistant-enasolar). Either clone the repo or download the ZIP file by selecting the Code button.

Copy the **enasolar** folder to the **config/custom_components** folder in your Home Assistant deployment.

> **Note**:
Only Home Assistant 2021.10.4 and later versions support this integration.

1. Enter `<your HASS server>:8123` into the address bar in your browser and hit Enter to connect to Home Assistant.
2. Log in.
3. Select **Configuration** > **Integrations**.

   <img src="https://github.com/geustace/home-assistant-enasolar/docs/EnaSolar-1.jpg" width="70%" alt="Integrations">

4. On the **Integrations** page in the configurations panel, select the **+ ADD INTEGRATION** button in the lower right and search for **enasolar**.
   <img src="https://github.com/geustace/home-assistant-enasolar/docs/EnaSolar-2.jpg" width="70%" alt="Add integration">

5. Select **EnaSolar Solar Inverter** and set up the integration.

   <img src="https://github.com/geustace/home-assistant-enasolar/docs/EnaSolar-3.jpg" width="65%">
<a id="Config 1"></a>
6. Replace **my.inverter.fqdn** with the Fully Qualified Domain Name or the IP Address of your inverter.  You can enter a name but this is only useful if you have more than one inverter and need to differentiate the sensors. Select **NEXT**

   <img src="https://github.com/geustace/home-assistant-enasolar/docs/EnaSolar-4.jpg" width="65%" alt="Config 2">
7. The next panel has the capabilities andf attributes of your inverter.  If you know that they are incorrect, you can override them by selecting appropriate values.

   <img src="https://github.com/geustace/home-assistant-enasolar/docs/EnaSolar-5.jpg" width="65%" alt="Config 3">

7. Select **Submit**.

