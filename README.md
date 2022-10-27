# theWaveShooter_AssistiveDevice
Code that makes my assistive device for the blind work!

My team created a device for the blind that acts as a proximity sensor and helps them spatially map out their surroundings, whether they are walking or sitting down. 

To design the device, we went through rigorous concept designs and evaluations in order to come up with a solid idea that we wanted to implement and feasibly create. 

We ultimately decided on *The Wave Shooter*, a device for the blind that vibrates the user’s wrist when they are approaching some sort of obstacle, **whether that is an obstacle as they walk or while they are sitting down and when there is an obstacle near their hand**.

Some specifications of the design included:

- **Raspberry Pi microcontroller**, A distance sensor (Time of Flight) sensor, a Vibration Motor, and a Buzzer
- **Two Switches** that can be used to operate the device and power it on/off, as well as alternate between modes
- **Two modes** that can be switched depending on user preference: Walk mode and Reach mode
- **Walk Mode**: The vibration motor activates when an object is a further distance away from the sensor (1800mm) and vibrates at a faster rate proportional to the average distance recorded
- **Reach Mode:** The vibration motor activates when an object is a closer distance away from the sensor (350mm) and vibrates faster as the recorded average decreases in the distance.
