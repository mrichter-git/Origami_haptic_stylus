
#include "Arduino.h"
#include <Wire.h>
#include <SparkFun_VL6180X.h>
#include <Encoder.h>
#include <Controller.hpp>

// Hardware ------------------------------------------------
#define MOTOR_IN1       22
#define MOTOR_IN2       23
#define MOTOR_ENC_C1    2
#define MOTOR_ENC_C2    3
#define TOF_SDA         18
#define TOF_SCL         19

#define VL6180X_ADDRESS 0x29

//Software ----------------------------------------------
#define DT			50 //[ns]
#define ARW_VAL 	0.1 

#define DIST_INCR       255/3000
#define MAX_DIST        255

#define TOF_MAX_DIST	20

#define CUT_OFF_FREQ 	20 //[Hz]


Encoder motor_enc(MOTOR_ENC_C1, MOTOR_ENC_C2);
VL6180x sensor(VL6180X_ADDRESS);
// IntervalTimer Timer1;

void measure_loop();
volatile bool stop = 0;
volatile float filtDistance;
volatile float prev_filtDistance;
volatile long encoderPos = 0;
volatile long prev_encoderPos = 0;
volatile float Integral = 0;

void setup() {
	Serial.begin(19200); // Start Serial at 57600bps
	Wire.begin();         // Start I2C library
	delay(100);           // delay .1s

	//sensor.getIdentification(&identification); // Retrieve manufacture info from device memory
	//printIdentification(&identification);      // Helper function to print all the Module information

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

	Serial.println("Staring test");
	measure_loop();
	delay(100);

	// Timer1.priority(3);
	// Timer1.begin(measure_loop, DT);

}


void loop() {

	float control_value = 0;
	int cont_IN1 = 0;
	int cont_IN2 = 0;
	control_value = computePID(2.0f, 0, 0.2f, -float(encoderPos), -float(prev_encoderPos), DT/1000.0f, ARW_VAL, Integral);


	if (control_value < 0) cont_IN1 = -int(control_value);
	else cont_IN2 = int(control_value);

	if (!stop){
		// ramp up forward
 		analogWrite(MOTOR_IN1, cont_IN1);
		analogWrite(MOTOR_IN2, cont_IN2);
	}
	else {
		digitalWrite(MOTOR_IN1, LOW);
		digitalWrite(MOTOR_IN2, LOW);
	}
	measure_loop();
	Serial.print(",");
	Serial.print("test_val");
	Serial.print(":");
	Serial.print("1_");
	Serial.print(control_value);
	Serial.print(" 2_");
	Serial.print(cont_IN2);
	


	// end transmission line
	Serial.println();
	delay(DT);

}

void measure_loop(){

	if (Serial.available()) {
		Serial.read();
		Serial.print("Turning motor off,");
		stop = 1;
	}
	if (stop) Serial.print("Stopped,");
	else {

		// Encoder --------
		encoderPos= motor_enc.read();
		Serial.print("Motor encoder (counts):");
		Serial.print(encoderPos);

		// ToF ------------
		filtDistance = LowPassFilter(prev_filtDistance, sensor.getDistance(), DT, CUT_OFF_FREQ);
		Serial.print(",");
		Serial.print("Filtered distance measured (mm):");
		Serial.print(filtDistance);

		Serial.print(",");
		Serial.print("Ambient light:");
		Serial.print(sensor.getAmbientLight(GAIN_20));

		//Setting previous values
		prev_filtDistance = filtDistance; 
		prev_encoderPos = encoderPos;
	}
}
