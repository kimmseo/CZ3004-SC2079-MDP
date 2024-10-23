/*
 * PID.h
 *
 */

#ifndef INC_PID_H_
#define INC_PID_H_

typedef struct PIDController{
	//Controller gains
	float Kp;
	float Ki;
	float Kd;

	//Derivative low-pass filter time constant
	float tau;

	//Output limits
	float limMin;
	float limMax;

	//Sample time (seconds)
	float T;

	//Controller variables
	float integrator;
	float prevError;
	float differentiator;
	float prevMeasurement;

	//Controller output
	float out;
} PIDController;

void PIDController_Init(PIDController *pid);
void MotorPIDController_Init(PIDController *pid);
int MotorPIDController_Update(PIDController *pid, float measurement, float setpoint, int currentpwm);
int PIDController_Update(PIDController *pid, float measurement, float setpoint, int currentPWM);

#endif /* INC_PID_H_ */
