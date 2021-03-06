#include "Controller.hpp"

#define _USE_MATH_DEFINES
#include <cmath>

#define PI 3.14159265358979323846


/**
* @brief Filters a signal with a first-order low-pass filter.
* @param previousFilteredValue the previous filtered value.
* @param input the filter input (the current sample of the signal to filter).
* @param dt the time elapsed since the last call of this function [s].
* @param cutoffFreq the cutoff frequency of the filter [Hz].
* @return the new output of the filter.
*/
float LowPassFilter(float previousFilteredValue, float input, float dt, float cutoffFreq)
{
	float tau = 1.0f / (2.0f * PI * cutoffFreq); // Rise time (time to reach 63% of the steady-state value).
	float alpha = dt / (tau+dt); // Smoothing factor.
	return alpha * input + (1.0f - alpha) * previousFilteredValue;
}

/**
* @brief Computes the numerical derivative.
* @param prevValue:the previous input value.
* @param currentValue:the current input value.
* @param dt the time elapsed since the last call of this function [s].
* @return the derivative.
*/
float ComputeNumDerivative(float prevValue, float currentValue, float dt)
{
	return (currentValue-prevValue)/dt ;
}

/**
* @brief Computes the numerical Integral.
* @param prevValue: the previous input value, used when doing the trapezoidal approximation.
* @param currentValue: the current input value.
* @param dt the time elapsed since the last call of this function [s].
* @return the integral.
*/
float ComputeNumIntegral(float prevValue, float currentValue, float dt, float integral)
{
	//Trapezoidal approx
	//Integral += dt*(currentValue + prevValue)/2;
	//Linear approx
	integral += dt*currentValue;
	return integral;
}

/**
* @brief Computes a PID control value
* @param Kp: proportional gain
* @param Ki: integral gain
* @param Kp: derivative gain
* @param error: the input to the controller
* @param prevError: error at the previous time step, used for derivation
* @param prevPrevError: error at the before previous time step, used for derivation over 2 time steps
* @param dt the time elapsed since the last call of this function [s].
* @return the control value
*/
float computePID(float Kp, float Ki, float Kd, float error, float prevError,
				 float dt, float arw_value, float &integral)
{
	//Proportional term
	float P_term = Kp*error;

	//Integral term I
	integral += dt*error;
	float I_term = Ki*integral;

	//Anti-reset windup
	if (I_term > arw_value) I_term = arw_value;
	else if (I_term < -arw_value) I_term = -arw_value;

	//Derivative term
	float D_term = 0;
	D_term = Kd*ComputeNumDerivative(prevError, error, dt);

	//Total
	//return P_term + I_term + D_term;
	return P_term + I_term + D_term;
}

float ViscousFricComp(float speed)
{
	if(speed > DEADZONE_VISCOUS || speed < -DEADZONE_VISCOUS) return speed*FRIC_VISCOUS_COEFF;
	else return 0;
}

float StaticFricComp(float speed)
{
	if(speed > DEADZONE_DRY) return FRIC_STATIC_NEG;
	else if(speed < -DEADZONE_DRY) return -FRIC_STATIC_NEG;
	else return 0;
}

/**
* @brief Computes a Virtual wall at a given angle WALL_ANGLE
* @param stiff: wall stiffness
* @param damp: wall damping
* @param angle: current paddle angle, used to calculate stiffness effect
* @param speed: current paddle speed, used to calculate damping effect
* @return the desired force that needs to be applied to the system at the end of the paddle
*/
float hapt_ComputeWall(float stiff, float damp, float pos, float speed, float wall_pos)
{
	float damping;
	if(speed > DEADZONE_VISCOUS || speed < -DEADZONE_VISCOUS) damping = damp*speed;
	else damping = 0;

	if(pos > wall_pos) return stiff*(wall_pos-pos) - damping;
	else if(pos < -wall_pos) return stiff*(wall_pos-pos) - damping;
	else return 0;
}
