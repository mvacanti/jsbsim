#JSBSim Brushless DC Motor (BLDC) Propulsion Modeling & Test
##Brushless DC propulsion modeling for use in sUAS modeling
Matt Vacanti
11/26/2020 

##Challenges with Existing Configuration
As of writing, the current JSBSim for an electric engine combined with the propeller thruster is appropriate in many 
cases but introduces undesirable characteristics when applied to small (<55 lbs) multi-copter UAS. 
This analysis explores contributing factors, makes recommendations for code changes, and provides the test 
configurations to replicate the results. This analysis will investigate the following areas: 

- Propeller Moment of Inertia
- Propeller Generated Thrust and Torque
- Propeller Torque Force Application
- Motor Torque Generation

##Baseline Configuration
**Engine:** electric_eqv.xml \
**Propeller:** APC_13x8E_6K.xml \
**Aircraft:** Hexacopter_X.xml

##Areas of Analysis
###Propeller Moment of Inertia (Ixx)
In previous versions of JSBSim the minimum allowable Ixx value was 
[0.001 SLUG*FT2](https://github.com/JSBSim-Team/jsbsim/blob/4fe1aa72cd4234824f686b9495194f2ef5556774/src/models/propulsion/FGPropeller.cpp#L77-L78). 
While this appears as a small number it can be orders of magnitude incorrect for small propellers. 
This issue has been resolved in the current rolling release to 
[1e-06 SLUG*FT2](https://github.com/JSBSim-Team/jsbsim/blob/49262a7215402da1638caf75f17103a842a234fa/src/models/propulsion/FGPropeller.cpp#L72-L73). 

####Calculating Propeller Moment of Inertia
Desirably, propeller manufacturers would publish moment of inertia data. The reality is that this information is not
widely available for small UAS props. Two relatively simple methods to estimate the propeller moment of inertia is to 
assume the mass distribution is equal (as a solid rod) or use a tool such as OpenVSP to approximate the mass 
distribution for a given propeller shape. 

#####Estimating propeller moment of inertia as a solid rod
[Ixx = 1/12 * ML^2](https://archive.org/details/physicsforscient02serw/page/202/mode/2up) \
Using the [APC 13x8E Propeller](https://www.apcprop.com/product/13x8e/) \
Where: \
M = [1.09 oz.](https://49u9ei2todm6vjegs45ceqp1-wpengine.netdna-ssl.com/wp-content/uploads/2020/10/PROP-DATA-FILE_202010.xlsx) \
L = [18 in.](https://49u9ei2todm6vjegs45ceqp1-wpengine.netdna-ssl.com/wp-content/uploads/2020/10/PROP-DATA-FILE_202010.xlsx) \
**Ixx** = 29.43 OZxIN2 or 0.000397 SLUGxFT2 (JSBSim units)

#####Estimating moment of inertia using OpenVSP
[OpenVSP](http://openvsp.org/) is a multi-faceted tool and that includes a simple interface to evaluating object
properties including built-in propeller models. The .vsp3 file used in the image below is 
[here](doc/suas_bldc/APC_18x8E_6K_Generic.vsp3).

![OpenVSP](doc/suas_bldc/OpenVSP.png)

**Ixx** = 21.634 OZxIN2 or 0.000292 SLUGxFT2

####Moment of inertia conclusions
Absent manufacturer data or a highly-accurate 3D model the options considered above are a method of estimating
the propeller moment of inertia. For the purposes of this analysis, the larger of the two calculations will be used
(0.000397 SLUGxFT2). 

###Propeller Performance Characteristics
JSBSim calculates propeller thrust and power using inputs from the propeller data xml file. The key inputs JSBSim is
expecting are J (advance ratio), Ct (Coefficient of Thrust), and Cp (Coefficient of Power). APC Propellers publishes
this data (and more) for their entire catalog of small propellers
[here](https://www.apcprop.com/technical-information/file-downloads/) under the PERFILES_WEB-XXXX.zipx. 

![OpenVSP](doc/suas_bldc/13x8E_J-Cp.png)

![OpenVSP](doc/suas_bldc/13x8E_J-Ct.png)

####Estimating Propeller Performance Characteristics for JSBSim
The plots above indicate that there can be significant differences in propeller performance by RPM range. As JSBSim
currently does not vary Ct and Cp by RPM we will need to select one maximum RPM value to evaluate.
Selecting an appropriate RPM data set can be accomplished by matching the expected propeller RPM at 100% throttle. 
In the case of a brushless DC motor this is accomplished by multiplying the maximum voltage by the KV rating of the
motor. Note that this assumes the motor can generate the required power at the KV RPM.

**Kv** = 380 \
**V** = 21 \
**Max RPM** = 7980 (KV x V) 

In this case we select the 8000 RPM data set for the propeller.

#####Comparing JSBSim Outputs vs. APC Data
Using the propeller data set selected above, a comparison between JSBSim calculated thrust and power vs APC data is 
completed with the following configuration:
 
Configuration | Setting
------        | :------:
JSBSim Script | bench_electric_ramp.xml    
Motor         | electric_eqv.xml  
Motor Config  | Baseline Throttle Ramp Configuration   
Propeller     | APC_13x8E_8K.xml    

![OpenVSP](doc/suas_bldc/bench_electric_rpm_ramp_thrust.png) 

![OpenVSP](doc/suas_bldc/bench_electric_rpm_ramp_power.png)

The difference between the JSBSim data and APC data is attributed to the fact that APC Ct and Cp vary by RPM and JSBSim
assumes these values remain constant over the RPM range. The potential error introduced by this method will vary 
depending on individual prop and RPM range characteristics. A plot of static operation (J = 0) for the 13x8E propeller
Ct and Cp by RPM is below. 

![OpenVSP](doc/suas_bldc/13x8E__STATIC-RPM-Ct.png)

![OpenVSP](doc/suas_bldc/13x8E__STATIC-RPM-Cp.png)


####Exporting/Processing APC Formatted Data
A tool to produce the APC report and JSBSim formatted data can be found HERE.

###Propeller and Engine Torque
Torque available to accelerate the propeller is currently calculated in JSBSim calculated by LINK.
This method, while appropriate for generic use, produces an RPM response has some unique characteristics particularly 
problematic for vertical lift.  RPM response characteristics are plotted using the with the following configuration:

Configuration | Setting
------        | :------:
JSBSim Script | bench_electric.xml    
Motor         | electric_eqv.xml  
Motor Config  | Baseline Hexacopter Flight Configuration  
Propeller     | APC_13x8E_8K.xml

![OpenVSP](doc/suas_bldc/bench_electric_rpm.png)

The issues highlighted by this data include aggressive start up acceleration followed by smoothed overly "soft" 
changes thereafter - indicated by the rounded edges near RPM changes.

#### Proposed BLDC Motor Model
There are a significant number of variables that effect the way that a BLDC motor produces mechanical power and torque
from electric energy. For the purposes of producing a generic BLDC motor model we will focus on a core relationship: 
a motor's velocity constant (Kv) is directly related to the torque constant (Kt). A detailed discourse going into far 
greater description of this approach and some limitations can be found
[here.](https://things-in-motion.blogspot.com/2018/12/how-to-estimate-torque-of-bldc-pmsm.html) 

Given this information, the following core assumptions for the motor model are made:
1. RPM = Motor Velocity Constant (Kv) x Input Voltage
2. Torque = Torque Constant (Kt) x ( 1 / Kv ) x Input Current
3. When decelerating, the braking force will be equal to the propeller torque required at the current RPM.
 - NOTE: Kt of 8.3 Newton Meters (given by Richard Parsons in the above link) is converted to 6.1217 pound feet 
 for JSBSim units of measure.

Applying the model concepts above results in a removal of the initial RPM spike and significant improvement in RPM 
response. RPM response characteristics are generated using the with the following configuration:

Configuration | Setting
------        | :------:
JSBSim Script | bench_bldc.xml    
Motor         | DJI-3510-380.xml  
Motor Config  | Baseline Hexacopter Flight Configuration  
Propeller     | APC_13x8E_8K.xml
Airframe Cfg. | BLDC Ramp Config

![OpenVSP](doc/suas_bldc/bench_bldc_rpm.png)

Comparing the existing electric engine model vs. the proposed BLDC model yields the following results:

![OpenVSP](doc/suas_bldc/bench_bldc_vs_electric_rpm.png)

The comparison has been configured such that the maximum power output between the two models is the same - as shown by
the alignment of the initial period at 100% throttle. Other observations include:
- "Rounding" of RPM response when accelerating to 100% throttle (expected)
- "Sharp" transitions of RPM at throttle inputs <100% throttle (expected)
- Significantly different RPM outcomes at throttle inputs <100%

#### External Validation of Proposed BLDC Motor Model
To validate the performance of the proposed BLDC model a comparison of real world bench testing (static) data publicly 
available at http://www.flybrushless.com/ and a widely used modeling tool at https://www.ecalc.ch/motorcalc.php 
Test configurations for each were randomly selected based upon the following criteria:

- Data must be available for actual measured Kv performance
- Propeller must be APC model

##### Flybrushless.com Validation 1

http://www.flybrushless.com/motor/view/99

Configuration | Setting
------        | :------:
JSBSim Script | bench_bldc_validation.xml    
Motor         | XMotor-3536CA-8T.xml 
Motor Config  | Validation Configuration 1
Propeller     | APC_11x55E_8K
Airframe Cfg. | Validation Config 1 & 2


Element       | Reference | JSBSim   
------        | :------:  | :------:
RPM           | 8100      | 7158
Thrust (Lbf)  | 2.833     | 2.455
Voltage       | 10.7      | 10.7
Current (A)   | 21.3      | 21.3

##### Flybrushless.com Comparison 2

http://www.flybrushless.com/motor/view/99

Configuration | Setting
------        | :------:
JSBSim Script | bench_bldc_validation.xml    
Motor         | XMotor-3536CA-8T.xml 
Motor Config  | Validation Configuration 2
Propeller     | APC_11x55E_8K
Airframe Cfg. | Validation Config 1 & 2


Element       | Reference | JSBSim
------        | :------:  | :------:
RPM           | 7560      | 6652
Thrust (Lbf)  | 2.425     | 2.121
Voltage       | 9.8       | 9.8
Current (A)   | 18.4      | 18.4

##### Flybrushless.com Comparison 3

http://www.flybrushless.com/motor/view/84

Configuration | Setting
------        | :------:
JSBSim Script | bench_bldc_validation.xml    
Motor         | EP-2814-900.xml 
Motor Config  | Validation Configuration 1
Propeller     | APC_13x8E_6
Airframe Cfg. | Validation Config 3 & 4


Element       | Reference | JSBSim
------        | :------:  | :------:
RPM           | 6420      | 5898
Thrust (Lbf)  | 3.506     | 3.170
Voltage       | 11.1      | 11.1
Current (A)   | 30.7      | 30.7

##### Flybrushless.com Comparison 4

http://www.flybrushless.com/motor/view/84

Configuration | Setting
------        | :------:
JSBSim Script | bench_bldc_validation.xml    
Motor         | EP-2814-900.xml 
Motor Config  | Validation Configuration 2
Propeller     | APC_13x8E_6
Airframe Cfg. | Validation Config 3 & 4


Element       | Reference | JSBSim
------        | :------:  | :------:
RPM           | 5040      | 4640
Thrust (Lbf)  | 2.139     | 1.961
Voltage       | 7.8       | 7.8
Current (A)   | 19        | 19

##### Flybrushless.com Comparison 5

http://www.flybrushless.com/motor/view/40

Configuration | Setting
------        | :------:
JSBSim Script | bench_bldc_validation.xml    
Motor         | E-max-BL2210.xml 
Motor Config  | Validation Configuration 1
Propeller     | APC_7x5E_11K
Airframe Cfg. | Validation Config 5 & 6


Element       | Reference | JSBSim
------        | :------:  | :------:
RPM           | 10830     | 10599
Thrust (Lbf)  | 1.234     | 1.135
Voltage       | 7.4       | 7.4
Current (A)   | 16.5      | 16.5

##### Flybrushless.com Comparison 6

http://www.flybrushless.com/motor/view/40

Configuration | Setting
------        | :------:
JSBSim Script | bench_bldc_validation.xml    
Motor         | E-max-BL2210.xml 
Motor Config  | Validation Configuration 2
Propeller     | APC_7x5E_11K
Airframe Cfg. | Validation Config 5 & 6


Element       | Reference | JSBSim
------        | :------:  | :------:
RPM           | 10320     | 10106
Thrust (Lbf)  | 1.108     | 1.032
Voltage       | 6.9       | 6.9
Current (A)   | 15        | 15
	
##### Flybrushless.com Comparison 7

http://www.flybrushless.com/motor/view/160

Configuration | Setting
------        | :------:
JSBSim Script | bench_bldc_validation.xml    
Motor         | E-max-BL2205.xml 
Motor Config  | Validation Configuration 1
Propeller     | APC_6x4E_14K
Airframe Cfg. | Validation Config 7 & 8


Element       | Reference | JSBSim
------        | :------:  | :------:
RPM           | 13710     | 13038
Thrust (Lbf)  | 0.86      | 0.831
Voltage       | 10.9      | 10.9
Current (A)   | 9.6       | 9.6

##### Flybrushless.com Comparison 8

http://www.flybrushless.com/motor/view/160

Configuration | Setting
------        | :------:
JSBSim Script | bench_bldc_validation.xml    
Motor         | E-max-BL2205.xml 
Motor Config  | Validation Configuration 2
Propeller     | APC_6x4E_14K
Airframe Cfg. | Validation Config 7 & 8


Element       | Reference | JSBSim
------        | :------:  | :------:
RPM           | 12870     | 12196
Thrust (Lbf)  | 0.756     | 0.727
Voltage       | 9.9       | 9.9
Current (A)   | 8.4       | 8.4

##### Flybrushless.com Comparison 9

https://www.ecalc.ch/motorcalc.php

Configuration | Setting
------        | :------:
JSBSim Script | bench_bldc_validation.xml    
Motor         | DJI-3510-380.xml 
Motor Config  | Validation Configuration 1
Propeller     | APC_13x8E_6K
Airframe Cfg. | Validation Config 9 & 10


Element       | Reference | JSBSim
------        | :------:  | :------:
RPM           | 5653      | 5632
Thrust (Lbf)  | 3.331     | 2.890
Voltage       | 18.3      | 18.3
Current (A)   | 11.98     | 11.98

##### Flybrushless.com Comparison 10

https://www.ecalc.ch/motorcalc.php

Configuration | Setting
------        | :------:
JSBSim Script | bench_bldc_validation.xml    
Motor         | DJI-3510-380.xml 
Motor Config  | Validation Configuration 2
Propeller     | APC_13x8E_6K
Airframe Cfg. | Validation Config 9 & 10


Element       | Reference | JSBSim
------        | :------:  | :------:
RPM           | 4664      | 4671
Thrust (Lbf)  | 2.269     | 1.988
Voltage       | 14.63     | 14.63
Current (A)   | 8.24      | 8.24

##### External Validation Conclusions
On average JSBSim RPM is 5.94% less than observed with a standard deviation of 4.99%
On average JSBSim Thrust is 10.24% less than observed with a standard deviation of 4.49%

###Propeller Torque Force Application
JSBSim application of the propeller torque on the airframe does not take into consideration the location of the prop 
(lever arm) given by XXXX. 

##Combined Solution Outcome
By combin

##Required Work & Decisions
- 
