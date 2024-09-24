# FloodMonitor

Flood status at local station and weather status display with Lego stand

Original inspiration
  - https://ukdepartureboards.co.uk/store/product/desktop-departures/?desktop=true
  - https://github.com/chrisys/train-departure-display/tree/main

Credit for the Lego design in the pictures below must be attributed to my dear old friend Gregory Bullock. Not only is he a Lego aficionado but also a softwaare engineer par excellence!!! Much love my brother xx

![image](https://github.com/AgentK88/FloodMonitor/assets/8092108/8a924553-7ce9-4103-8626-942335b9cb91)
![image](https://github.com/AgentK88/FloodMonitor/assets/8092108/596b60bb-663c-47b2-974e-11015d392282)

### Flood Montoring API

[API Reference](https://environment.data.gov.uk/flood-monitoring/doc/reference#5dfx)

[Example for Buildwas](https://check-for-flooding.service.gov.uk/station/2058)

![image](https://github.com/AgentK88/FloodMonitor/assets/8092108/0fd09931-74ba-49fa-9f05-2e038ec900ec)

[What does river level mean?](https://check-for-flooding.service.gov.uk/how-we-measure-river-sea-groundwater-levels)

### Weather

[Met Office DataPoint API](https://www.metoffice.gov.uk/services/data/datapoint/getting-started)

### Credit where it's due!

In addition to those listed above, I've had to find and use multiple other repositories to complete this project. Below I list the repositories that have either been an inspiration or used in the final solution

[raspi-pico-epaper](https://github.com/CoenTempelaars/raspi-pico-epaper)
Original display driver used for testing Waveshare 3.7 Inch E-paper

[Pico_ePaper](https://github.com/phoreglad/pico-epaper)
Updated display driver used in final solution, which also led me to...

writer and freesans20 from [MicroPython nano-gui](https://github.com/peterhinch/micropython-nano-gui)
and eventually to other useful things such as...

date and ntptime from [micropython-samples](https://github.com/peterhinch/micropython-samples)

Later into the project, I realised that there was a need to freeze modules. However, there seems to be very little advice online on how to do this.

[This post on Reddit made the process of freezing modules on Raspberry Pico W simple!](https://www.reddit.com/r/raspberrypipico/comments/1endjfd/quick_tutorialinstructions_on_how_to_freeze/)
