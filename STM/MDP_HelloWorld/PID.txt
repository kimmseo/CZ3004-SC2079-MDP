/*
 * PID.c
 *
 *  Created on:
 *      Author:
 */

#include "PID.h"
#include "math.h"

void PIDController_Init(PIDController *pid) {

  /* Clear controller variables */
  pid->integrator = 0;
  pid->prevError  = 0.0f;
  pid->prevMeasurement = 0.0f;
  pid->out = 0;

}

void MotorPIDController_Init(PIDController *pid) {
  pid->T = 0.2;
//  pid->Kp = 0.11;
//  pid->Ki = 0.15;
//  pid->Kd = 0.03;
  pid->Kp = 0.25;
  pid->Ki = 0;
  pid->limMax = 6000; pid->limMin = 0;
  PIDController_Init(pid);
}

int MotorPIDController_Update(PIDController *pid, float measurement, float setpoint, int currentpwm) {

	//Proportional Component
	float error = setpoint - measurement;
	if (isnan(error) == 1) error = 0;

	//Integral Component
	pid->integrator = pid->integrator + error;

	// Anti-wind-up via dynamic integrator clamping
	int limMinInt, limMaxInt;

	// Compute integrator limits
	if (pid->limMax > error) {

	limMaxInt = pid->limMax - error;

	} else {

	limMaxInt = 0;

	}

	if (pid->limMin < error) {

	limMinInt = pid->limMin - error;

	} else {

	limMinInt = 0;

	}
	if (pid->integrator > limMaxInt) {

		pid->integrator = limMaxInt;

	} else if (pid->integrator < limMinInt) {

		pid->integrator = limMinInt;

	}

	//Derivative Component
	pid->differentiator = error - pid->prevError;

	//Output
	pid->out = currentpwm + (pid->Kp * error) + (pid->Ki * pid->integrator) + (pid->Kd * pid->differentiator);

	//Keep output within limits
	if (pid->out > pid->limMax) {

		pid->out = pid->limMax;

	} else if (pid->out < pid->limMin) {

		pid->out = pid->limMin;

	}

	pid->prevError = error;

	return (int)pid->out;
}

int PIDController_Update(PIDController *pid, float measurement, float setpoint, int currentpwm) {

  /*
  * Error signal
  */
    float error = setpoint - measurement;
    if (isnan(error) == 1) error = 0;

  // Proportional
    int proportional;

    // velocity implementation (instead of distance)
    if (error >= 0) // positive error, need to increase pwm
    {
    	proportional = (int)((1 + pid->Kp * (error / setpoint)) * currentpwm); // kP * (1 + percentage of error based on setpoint) * currentpwm
    }
    else // negative error, need to decrease pwm
    {
    	proportional = (int)((1 + pid->Kp * (error / measurement)) * currentpwm); // kP * (1 + percentage of error based on measurement) * currentpwm
    }

  // Integral
    pid->integrator = pid->integrator + 0.5f * pid->Ki * pid->T * (error + pid->prevError) * currentpwm;

  // Anti-wind-up via dynamic integrator clamping
  int limMinInt, limMaxInt;

  // Compute integrator limits
  if (pid->limMax > proportional) {

    limMaxInt = pid->limMax - proportional;

  } else {

    limMaxInt = 0;

  }

  if (pid->limMin < proportional) {

    limMinInt = pid->limMin - proportional;

  } else {

    limMinInt = 0;

  }

  // Clamp integrator
	if (pid->integrator > limMaxInt) {

		pid->integrator = limMaxInt;

	} else if (pid->integrator < limMinInt) {

		pid->integrator = limMinInt;

	}

  // Derivative

  /*
  * Compute output and apply limits
  */

    pid->out = proportional + pid->integrator;

    if (pid->out > pid->limMax) {

        pid->out = pid->limMax;

    } else if (pid->out < pid->limMin) {

        pid->out = pid->limMin;

    }

  /* Store error and measurement for later use */
    pid->prevError       = error;
    pid->prevMeasurement = measurement;

  /* Return controller output */
    return pid->out;

}
