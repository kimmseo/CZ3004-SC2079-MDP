# STM32 Robot Control Spec.

Updated 3 Feb 24.

Summary of the robot's movement tolerances when commanded using the Python code. Ideally, the information below should be set in code such that they can be changed easily if needed.

## Forward/Rev

Typical forward/rev movement speed is governed by the PID controllers to ensure both motors are moving the same speed, another to control its speed along the path and the linear mapping of distance left to motor speed near the end which overrides the PID.

Assuming the robot moves along the x axis, for any requested movement $x$ cm, <br>
```
           ^ +x
           |
           |
-----------█----------> +y
           |
           |

      ^ observer ^
```
the final position is $x \pm 1.5$. The value-dependent inaccuracy should be negligible (unless the dimensions of the wheels in the datasheet are inaccurate).<br>
Its y-axis deviation is upper bounded by $x \cdot tan(\phi) + (c-1) \cdot k x$ where $\phi$ is the servo motor's signed angle offset from the actual center, and $c$ is the ratio of distance covered by each motor for all $x$.<br>
($sgn(\phi)=1$ is the clockwise direction, and the numerator of $c$ is the left motor distance)<br>
The main improvement needed here is to make them both close to zero. It is hard to measure these values as they are so small.
<br>
Based on measurements (below), the deviation could just be assumed to be a scalar of $x$, i.e. 0.01:
| x   | abs(y)   |
|-----|-----|
| 400(F) + 400(R) | ~8 |
| 600 | 6.5 |
| 300 | 3.1 |
| 100 | 1.2 |
<br>

* $sgn(y)$ cannot be assumed to always be +ve.
<br>



## Rotation
 _Currently, the calibration scheme still needs some work, so these values will change (besides the turning radius)._<br>
Rotation is measured by using the quaternion vector $q \in \mathbb{H}^4$ derived from IMU (accel, gyro), with inbuilt filters enabled (see code for details).
get_quaternion returns $norm(q)$,<br>
get_yaw returns $\arctan\left(2 \cdot \left(q_0q_3 + q_1q_2\right), 1 - 2 \cdot \left(q_2^2 + q_3^2\right)\right)$ which is ideally its actual yaw relative to starting orientation.<br>

Magnetometer can't be used because of the motors. These values drift by minimally $0.02 deg/s$ and is not suitable for integration over time, and should be used for only short periods.<br>


The pseudocode describes a possible usecase:
```
cur_angle = robot.get_yaw()
robot.turn(some_angle)
thread.sleep(time_to_move + TOLERANCE_MS)
if abs ((cur_angle + some_angle) - robot.get_yaw()) > THRESHOLD_VALUE
   something went wrong!
```
This way the algorithm could verify that the robot's orientation has changed as required.

The accuracy of any turn is $\phi \pm \epsilon$ as well as an insignificant drift over short periods of time. Inaccuracy could be reduced by making larger turns instead of more smaller ones.
Currently, $\epsilon = 2$.

The turning arc is specified below. This holds for all $abs(\phi) \leq 180$. These values can be modified in STM32 code if necessary.
The values can vary by as much as $\pm 10$ % if the tires slip. The slipping tires can be reduced at the cost of higher $\epsilon$

|                  | Turn Radius (cm) | dx | dy |
|------------------|------------------|----|----|
| Forward (Right)  | 19.5             |    |    |
| Forward (Left)   | 19.75            |    |    |
| Backward (Right) | 19.5             |    |    |
| Backward (Left)  | 19.75            |    |    |

<br>

