# PhenoMaster Predefined Variables

## Calorimetry

| **Abbreviation** | **Unit**         | **Description**                                                                                                                                |
|------------------|------------------|------------------------------------------------------------------------------------------------------------------------------------------------|
| Flow             | l/min            | Flow per box                                                                                                                                   |
| S.Flow           | l/min            | Sample flow per box                                                                                                                            |
| Temp             | °C               | Temperature in box                                                                                                                             |
| O2               | %                | O2 concentration in box                                                                                                                        |
| CO2              | %                | CO2 concentration in box                                                                                                                       |
| Press            | hPa              | Air pressure in box                                                                                                                            |
| Hum              | %                | Relative humidity in box                                                                                                                       |
| dO2              | %                | Difference in O2 concentration between reference box and test box; dO2 = Ref.O2 – O2                                                           |
| dCO2             | %                | Difference in CO2 concentration between reference box and test box; dCO2 = CO2 – Ref.CO2                                                       |
| VO2(1)           | ml/h/kg          | O2 consumption (V = volume), normalized to total body weight                                                                                   |
| VO2(2)           | ml/h/kg          | O2 consumption (V = volume), normalized to approximate lean body mass (75 % of bodyweight) for allometric scaling                              |
| VO2(3)           | ml/h             | O2 consumption (V = volume), uncorrected values                                                                                                |
| VCO2(2)          | ml/h/kg          | CO2 production (V = volume), normalized to approximate lean body mass (75 % of bodyweight) for allometric scaling                              |
| VCO2(3)          | ml/h             | CO2 production (V = volume), uncorrected values                                                                                                |
| RER              | a.u.             | Respiratory exchange rate; RER = VCO2 / VO2                                                                                                    |
| H(1)             | kcal/h/kg / W/kg | Heat production, normalized to total body weight (heat in W/kg if set prior in Setup tab)                                                      |
| H(2)             | kcal/h/kg / W/kg | Heat production, normalized to approximate lean body mass (75 % of bodyweight) for allometric scaling (heat in W/kg if set prior in Setup tab) |
| H(3)             | kcal/h           | Heat production, uncorrected values                                                                                                            |
| Ref.O2           | %                | O2 concentration in reference box                                                                                                              |
| Ref.CO2          | %                | CO2 concentration in reference box                                                                                                             |
| TD               | °C / °F          | Reference value dew point (climate chamber only)                                                                                               |

## Telemetry

| **Abbreviation** | **Unit** | **Description**                             |
|------------------|----------|---------------------------------------------|
| TempT            | °C       | Body temperature                            |
| ActiT            | cnt      | Activity counts (counts per antenna change) |
| HeartRate        | bpm      | Heart beats per minute                      |

## Weight Sensors

| **Abbreviation** | **Unit** | **Description**                  |
|------------------|----------|----------------------------------|
| Drink            | ml       | Drink consumption (differential) |
| DrinkC           | ml       | Drink consumption (cumulative)   |
| Feed             | g        | Food consumption (differential)  |
| FeedC            | g        | Food consumption (cumulative)    |
| Weight           | g        | Body weight (absolute data)      |

## Activity

| **Abbreviation** | **Unit** | **Description**                                                                                      |
|------------------|----------|------------------------------------------------------------------------------------------------------|
| XT + YT          | cnt      | Sum of total X beam interruptions and total Y beam interruptions                                     |
| XT               | cnt      | Total X beam interruptions (XT = XA + XF)                                                            |
| YT               | cnt      | Total Y beam interruptions (YT = YA + YF)                                                            |
| XA               | cnt      | X beam interruptions for ambulatory movement                                                         |
| YA               | cnt      | Y beam interruptions for ambulatory movement                                                         |
| XF               | cnt      | X beam interruptions for fine movement                                                               |
| YF               | cnt      | Y beam interruptions for fine movement                                                               |
| Z                | cnt      | Total Z beam interruptions                                                                           |
| CenT             | cnt      | Sum of total X beam interruptions and total Y beam interruptions in center zone (CenT = CenA + CenF) |
| PerT             | cnt      | Sum of total X beam interruptions and total Y beam interruptions in periphery (PerT = PerA + PerF)   |
| CenA             | cnt      | Total X and Y beam interruptions for central ambulatory movement                                     |
| CenF             | cnt      | Total X and Y beam interruptions for central fine movement                                           |
| PerA             | cnt      | Total X and Y beam interruptions for peripheral ambulatory movement                                  |
| PerF             | cnt      | Total X and Y beam interruptions for peripheral fine movement                                        |
| DistK            | cm       | Distance traveled in the horizontal plane (XY) (cumulative)                                          |
| DistD            | cm       | Distance traveled in the horizontal plane (XY) (differential)                                        |
| Speed            | cm/s     | Average speed                                                                                        |

## Treadmill

| Abbreviation | Unit | Description                                                                                                                                                                                                   |
|--------------|------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| SpeedM       | m/s  | Average running speed (distance covered per second)                                                                                                                                                           |
| Box          | No.  | Box number                                                                                                                                                                                                    |
| Elapsed      | s    | Time from start of timer up to interruption of light beam                                                                                                                                                     |
| Speed        | m/s  | Current speed at time of light beam interruption                                                                                                                                                              |
| Dist         | m    | Distance covered, depending on mode:Training mode (+ single mode deactivated): Sum of single paths of previous measurementsSingle mode (+ Training mode activated): Distance covered during the time interval |
| Power        | W    | Animal performance from the start of timer up to light beam interruption (if “Angle of Inclination” is &gt; 0)                                                                                                |
| Shock        | 0/1  | Manual administration of electrical stimulus (0 = no stimulus, 1 = stimulus administered)                                                                                                                     |
| Air puff     | 0/1  | Manual administration of air puff (0 = no air puff, 1 = air puff applied)                                                                                                                                     |
| Phase        | No.  | Phase number in which light beam interruption occurred                                                                                                                                                        |
| Phs          | s    | Time from start of phase (motor start) up to light beam interruption                                                                                                                                          |
| Tps          | s    | Time from start of timer to start of profile                                                                                                                                                                  |

## Running Wheel

| **Abbreviation** | **Unit** | **Description**                                                                                               |
|------------------|----------|---------------------------------------------------------------------------------------------------------------|
| Right            | cnt      | Number of wheel rotations to the right                                                                        |
| Right            | cm       | Distance covered by wheel rotations to the right                                                              |
| Left             | cnt      | Number of wheel rotations to the left                                                                         |
| Left             | cm       | Distance covered by wheel rotations to the left                                                               |
| SumR+L           | cnt      | Total number of rotations to right and left                                                                   |
| SumR+L           | cm       | Sum of distances covered by wheel rotations to right and left                                                 |
| SumTime          | min      | Wheel retention time (total duration the animal has spent in the wheel)                                       |
| SumRuns          | cn       | Total number of run episodes (movement threshold exceeded)                                                    |
| MaxSpeed         | m/s      | Maximum of the maximal speed and the current speed achieved in all running episodes within a cycle interval   |
| MaxSpeed         | rpm      | Maximum of the maximal speed and the current speed achieved in all running episodes within a cycle interval   |
| AVGSpeed         | m/s      | Mean value of the speeds achieved in all running episodes within a cycle interval                             |
| AVGSpeed         | rpm      | Mean value of the speeds achieved in all running episodes within a cycle interval                             |
| MaxLen           | s        | Longest individual duration of a run episode                                                                  |
| HB-Torque        | mNm      | Hysteresis Brake Torque                                                                                       |
| HB-Work          | mJ       | Hysteresis Brake Work                                                                                         |
| HB-Power         | mW       | Hysteresis Brake Power                                                                                        |
| SpeedR           | r/s      | Rotations per second (forced wheel)                                                                           |

## Laboratory

| **Abbreviation** | **Unit**         | **Description**                                                     |
|------------------|------------------|---------------------------------------------------------------------|
| PressL           | Pa               | Ambient air pressure (actual value)                                 |
| LightL           | lx               | Ambient brightness (actual value)                                   |
| HumL             | %                | Ambient humidity (actual value)                                     |
| TempL            | °C               | Temperature ambient humidity sensor (actual value)                  |
| CO2L             | ppm              | Ambient CO2 (actual value)                                          |
| NoiseL           | a.u. (ADC value) | Noise level (actual value)                                          |
| MotionL          | s                | Motion detector for monitoring staff presence (summed up over time) |

## Climate Chamber

| **Abbreviation** | **Unit** | **Description**                               |
|------------------|----------|-----------------------------------------------|
| TempC            | °C       | Temperature climate chamber (actual value)    |
| HumC             | %        | Humidity (actual value)                       |
| LightC           | %        | Illumination intensity (actual value)         |
| ColTemp          | K        | Illumination color temperature (actual value) |