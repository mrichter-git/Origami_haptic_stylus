#include<stdint.h>

float LowPassFilter(float previousFilteredValue, float input, float dt, float cutoffFreq);
float ComputeNumDerivative(float prevValue, float currentValue, float dt);
float ComputeNumIntegral(float prevValue, float currentValue, float dt, float integral);
float computePID(float Kp, float Ki, float Kd, float error, float prevError,
                float dt, float arw_value, float &integral);



