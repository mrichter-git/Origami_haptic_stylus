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

#define MOTOR_OFFSET 	0
#define PWM_RESOLUTION_BITS 10
#define PWM_MAX 		(pow(2.0, double(PWM_RESOLUTION_BITS)))

#define VL6180X_ADDRESS 0x29

#define ENCODER_OPTIMIZE_INTERRUPTS

#define COUNTS2MM(x) 22.0*(x)/244.0


//Software ----------------------------------------------
#define DT			350 //[us] 
#define COMM_DT		20000 //[us] --> 50Hz
#define ARW_VAL 	200 

#define CUT_OFF_FREQ 	1000 //[Hz]


Encoder motor_enc(MOTOR_ENC_C1, MOTOR_ENC_C2);
VL6180x sensor(VL6180X_ADDRESS);

void control();
void comm();

float Integral = 0.0f;

volatile bool stop = 0;

volatile float filtDistance;
volatile float prev_filtDistance;

volatile float ambientLight = 0.0f;

volatile float error = 0.0f;
volatile float prev_error = 0.0f;
volatile float Test_val = 0.0f;
volatile double input;
volatile unsigned long time = 0;
volatile unsigned long prev_time = 0;
volatile bool measure_dist = 0;

volatile long encoderPos = 0;
volatile long prev_encoderPos = 0;
volatile float speed = 0.0f;
volatile float prev_speed = 0.0f;

volatile float Kp = 0.0f;
volatile float Ki = 0.0f;
volatile float Kd = 0.0f;

volatile int target = 0;

void setup() {
	Serial.begin(9600); // Start Serial at 9600bps
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

	analogWriteResolution(PWM_RESOLUTION_BITS);


	Serial.println("Starting test");
	delay(100);



	// other interrupts prio of 128
	// ControlTimer.priority(220);
	// ControlTimer.begin(controlLoop, DT);
	// CommTimer.priority(219);
	// CommTimer.begin(commLoop, COMM_DT);

}

void loop(){
	
	encoderPos = motor_enc.read();

	time = micros();
	control();
	prev_time = time;

	comm();


	prev_filtDistance = filtDistance; 
	prev_error = error;
	prev_speed = speed;
	prev_encoderPos = encoderPos;

	delayMicroseconds(DT);
}

void control(){

	float control_value = 0;
	float dt = float(time-prev_time)/1000.0f;
	error = float(target - encoderPos);

	control_value = computePID(Kp, Ki, Kd, error, prev_error, dt, ARW_VAL, Integral);
	if (control_value >= PWM_MAX) control_value = PWM_MAX-2;
	if (-control_value >= PWM_MAX) control_value = -PWM_MAX+2;
	// speed = ComputeNumDerivative(float(prev_encoderPos), float(encoderPos), DT);
	// speed = LowPassFilter(prev_speed, speed, dt, CUT_OFF_FREQ);
	// Test_val = speed;

	// control_value += StaticFricComp(speed);
	// control_value += ViscousFricComp(speed);

	if (Ki == 0) Integral = 0.0f; //stops from keeping previous accumulation


	Test_val = (int(control_value));
	// Test_val += (error-prev_error)/1.0f;

	if (!stop){
		if (control_value < 0) {
			analogWrite(MOTOR_IN1, -int(control_value)+MOTOR_OFFSET);
			digitalWrite(MOTOR_IN2, LOW);
		}
		else{
			digitalWrite(MOTOR_IN1, LOW);
			analogWrite(MOTOR_IN2, int(control_value)+MOTOR_OFFSET);
		}
	}
	else {
		digitalWrite(MOTOR_IN1, LOW);
		digitalWrite(MOTOR_IN2, LOW);
	}

}

void comm(){
	if (measure_dist){
		filtDistance = sensor.getDistance();
		ambientLight = sensor.getAmbientLight(GAIN_20);
	}

	// Reading from serial port
	if (Serial.available()) {
		String serial_in = Serial.readStringUntil('\n');
		if (serial_in == "stop"){
			Serial.print("Turning motor off,");
			stop = 1;
		}
		else if (serial_in == "clear"){
			Serial.print("Clearing encoder values,");
			motor_enc.write(0);
			Kp = 0.0f;
			Ki = 0.0f;
			Kd = 0.0f;

		}
		else if (serial_in == "measure") measure_dist = 1;
		else if (serial_in == "no_measure") measure_dist = 0;
		else if (serial_in[0] == 'Z'){

			int idx = serial_in.indexOf(":");
			int idx_2 = serial_in.indexOf(",", ++idx);
			String sub_str = serial_in.substring(idx, idx_2);
			target = sub_str.toFloat();

		}
		else{
			int idx_2 = 0;
			int idx = serial_in.indexOf(",");
			String sub_str = serial_in.substring(0, idx);
			Kp = sub_str.toFloat();

			idx_2 = serial_in.indexOf(",", ++idx);
			sub_str = serial_in.substring(idx, idx_2);
			Ki = sub_str.toFloat();
			idx = idx_2;
			
			idx_2 = serial_in.indexOf(",", ++idx);
			sub_str = serial_in.substring(idx, idx_2);
			Kd = sub_str.toFloat();
			idx = idx_2;

			idx_2 = serial_in.indexOf(",", ++idx);
			sub_str = serial_in.substring(idx, idx_2);
			target = sub_str.toFloat();

			input = serial_in.toFloat();
		} 
	}
	if (stop) Serial.print("Stopped,");
	// Writing to serial port
	else {

		// Encoder --------
		Serial.print("Motor encoder (counts):");
		Serial.print(encoderPos);

		// ToF ------------
		if (measure_dist){
			Serial.print(",");
			Serial.print("ToF distance measured (mm):");
			Serial.print(filtDistance, 4);
			
			Serial.print(",");
			Serial.print("Ambient light:");
			Serial.print(ambientLight, 3);
		}

		Serial.print(",");
		Serial.print("delta time (us):");
		Serial.print(time - prev_time, 1);

		Serial.print(",");
		Serial.print("Encoder distance linearized (mm):");
		Serial.print(COUNTS2MM(float(encoderPos)), 4);

		Serial.print(",");
		Serial.print("test_val");
		Serial.print(":");
		Serial.print(Test_val, 5);

	}

	// end transmission line
	Serial.println();
}