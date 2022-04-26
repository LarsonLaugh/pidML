# pidML


In "pidML", "pid" stands for a PID temperature controller. This temperature controller is to help me repurpose my old electric kettle into a "mini" Sous vide cooker. This kettle has a small volume of 1 liter, easy to reach stable and uniform temperature even without external water cycle, which is necessary in a much larger, commercial cooker. On the other hand, "ML" stands for machine learning, which I tried to implement genetic algorithm to help training PID parameters.

## List of components

Microprocessor -> Raspberry Pi Pico

Temperature sensor -> MAX6675

220V control -> Relay

User interface -> ICD 1602
 
## Develop upon the simplest idea
Idea0: 
```
if measured temperature is lower than the set temperature:
	turn on the heater (relay) 
else:
	turn off the heater (relay)
```
Straightforward, but won't work...

Idea1:
```
Kp, Ki, Kd = x, x, x
error = measured temperature - set temperature
integral = error + integral
derivative = (lasterror-error)/dt
output = Kp*error+Ki*integral+Kd*derivative
if output > 0:
	turn on the heater (relay)
else:
	turn off the heater (relay)

```
The PID system instead of temperature will indicate the ON/OFF status of the heater. However, we need to manually set the PID parameters Kp, Ki, Kd. Not cool. 

Idea2:
```
Genetic Algorithm to find the best Kp, Ki, Kd -> PID system

```
The genetic algorithm needs data to train itself. One way is to use practical data, meaning trying out as many as possible PID parameters then feed the experimental data to the algorithm. However, this is tedious and time-consuming. Here we can first build a physical model to predict what will happen according to the law of physics.

Idea3:
```
Physical model to virtually realize the scene 

-> genetic algorithm to find the best Kp, Ki, Kd 

-> PID system
```
## Physical model

Heat transfer can happen in four different ways: Advection, thermal conduction, convection and radiation. Here we only consider thermal conduction and ignore the rest. We also ignore the metal piece between hot water and air around, and ideally think the hot water directly interface the cold air.

According to Fourier's law: heater transfer/meter square/second = - thermal conductivity * gradient of temperature ~ 450 W/meter square. The surface of the kettle is about 700 cm square. Then the heater dissipation 
power ~ 30 W. The power of the heater according to manufacturer is 1000 W. 

Let's see how the temperature changes when the heater is on and off.  The heat capacity of water is 4.184 Joule/gram/degree, and assume 0.8L (800 gram) of water inside.  That means the temperature goes up by a rate of **0.32 deg/sec** when the heater is on, and decreases by a rate of **0.008 deg/se** when the heater is off. So far, we have finished the physcial modelling part.


## PID controller and genetic algorithm
In PID controller, the temperature changes according to the results of physical modelling: goes up 0.32 deg/cycle and decrease 0.008 deg/cycle. We can set a cycle to be 1 sec. But 1 sec is meaningless here, since we can set the cycle time to much shorter to run more cycles in a certain time. But remember to correct this in the calculation of Kd. 

To evaluate each PID, we need to define a cost function = sum(abs(set temp - measured temp)) or sum((set temp - measured temp)^2). At each generation, we choose the PID with the smallest cost function to be passed onto the next generation (Elitism) and the one the largest cost function to mutate (mutation, randomize three numbers Kp, Ki, Kd), the rest hybridize with its neighboring to produce the next genertation (hybrid).


 