#include<stdint.h>

float LowPassFilter(float previousFilteredValue, float input, float dt, float cutoffFreq);
float ComputeNumDerivative(float prevValue, float currentValue, float dt);
float ComputeNumIntegral(float prevValue, float currentValue, float dt, float integral);
float computePID(float Kp, float Ki, float Kd, float error, float prevError,
                float dt, float arw_value, float &integral);
float ViscousFricComp(float speed);
float StaticFricComp(float speed);

#define DEADZONE_DRY 3
#define FRIC_STATIC_POS 50
#define FRIC_STATIC_NEG 50

#define DEADZONE_VISCOUS 1
#define FRIC_VISCOUS_COEFF 10




