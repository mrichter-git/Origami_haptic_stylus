#include "Arduino.h"
#include <Wire.h>
#include <SparkFun_VL6180X.h>
#include <Encoder.h>
#include <Controller.hpp>
#include <string>

// Hardware ------------------------------------------------
#define MOTOR_IN1       22
#define MOTOR_IN2       23
#define MOTOR_ENC_C1    2
#define MOTOR_ENC_C2    3
#define TOF_SDA         18
#define TOF_SCL         19

#define MOTOR_OFFSET 	100

#define VL6180X_ADDRESS 0x29

//Software ----------------------------------------------
#define DT			350 //[us] 
#define COMM_DT		20000 //[us] --> 50Hz
#define ARW_VAL 	100 

#define CUT_OFF_FREQ 	1000 //[Hz]


Encoder motor_enc(MOTOR_ENC_C1, MOTOR_ENC_C2);
VL6180x sensor(VL6180X_ADDRESS);
IntervalTimer ControlTimer;
IntervalTimer CommTimer;

void controlLoop();
void commLoop();

float Integral = 0.0f;

volatile bool stop = 0;
volatile float filtDistance;
volatile float prev_filtDistance;
volatile float ambientLight = 0.0f;
volatile long encoderPos = 12;
volatile float prev_error = 0.0f;
volatile float Test_val = 0.0f;
volatile double input;
volatile unsigned long prev_time = 0;

void setup() {
	Serial.begin(57600); // Start Serial at 57600bps
	Wire.begin();         // Start I2C library
	delay(100);           // delay .1s

	if (sensor.VL6180xInit() != 0)
	{
		Serial.println("Failed to initialize ToF sensor. Freezing..."); // Initialize device and check for errors
		while (1) {
		Serial.print("Init Error of ToF sensor \n");
		delay(1000);
		}
	}

	sensor.VL6180xDefautSettings(); // Load default settings to get started.
	
	pinMode(MOTOR_IN1, OUTPUT);
	pinMode(MOTOR_IN2, OUTPUT);

	Serial.println("Starting test");
	delay(100);

	// other interrupts prio of 128
	ControlTimer.priority(220);
	ControlTimer.begin(controlLoop, DT);
	CommTimer.priority(219);
	CommTimer.begin(commLoop, COMM_DT);

}

void loop(){
}

void controlLoop() {
	unsigned long time = micros();
	// encoderPos= motor_enc.read();
	float control_value = 0;
	float error = 0.0f - float(encoderPos);

	control_value = computePID(2.0f, 0.5f, input, error, prev_error, (time-prev_time)/1000.0f, ARW_VAL, Integral);
	Test_val += (1);


	if (!stop){
		if (control_value < 0) {
			analogWrite(MOTOR_IN1, -int(control_value)+MOTOR_OFFSET);
			digitalWrite(MOTOR_IN2, LOW);
		}
		else{
			digitalWrite(MOTOR_IN1, LOW);
			analogWrite(MOTOR_IN2, int(control_value) + MOTOR_OFFSET);
		}
		// if ((encoderPos >= -150) && (encoderPos <= 0)){
		// 	}
		// }
		// else {
		// 	digitalWrite(MOTOR_IN1, LOW);
		// 	digitalWrite(MOTOR_IN2, LOW);
		// }
	}
	else {
		digitalWrite(MOTOR_IN1, LOW);
		digitalWrite(MOTOR_IN2, LOW);
	}

	//Setting previous values
	prev_filtDistance = filtDistance; 
	prev_error = error;
	prev_time = time;
}

void commLoop(){

	encoderPos= motor_enc.read();
	delayMicroseconds(2000);
	// filtDistance = sensor.getDistance();
	// ambientLight = sensor.getAmbientLight(GAIN_20);
	if (Serial.available()) {
		String serial_in = Serial.readStringUntil('\n');
		if (serial_in == "stop"){
			Serial.print("Turning motor off,");
			stop = 1;
		}
		else input = serial_in.toFloat();
	}
	if (stop) Serial.print("Stopped,");
	else {

		// Encoder --------
		Serial.print("Motor encoder (counts):");
		Serial.print(encoderPos);

		// ToF ------------
		// Serial.print(",");
		// Serial.print("Filtered distance measured (mm):");
		// Serial.print(filtDistance, 4);

		// Serial.print(",");
		// Serial.print("Ambient light:");
		// Serial.print(ambientLight, 3);

		Serial.print(",");
		Serial.print("test_val");
		Serial.print(":");
		Serial.print(Test_val, 5);

	}

	// end transmission line
	Serial.println();
}