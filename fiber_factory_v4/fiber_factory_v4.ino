
#include <AccelStepper.h>

#define PUL_4 13
#define DIR_4 12
#define ENA_4 11

#define PUL_3 10
#define DIR_3 9
#define ENA_3 8

#define PUL_2 7
#define DIR_2 6
#define ENA_2 5

#define PUL_1 4
#define DIR_1 3
#define ENA_1 2

#define TMP A0
#define INTERVAL 500

#define LINEAR_DISTANCE 1600*10

#define PING 0XABADBABE
#define PONG 0XB16B00B5

typedef void (*SensorFunction) (void* s);

struct motor {
    char symbol;
    char* name;
    AccelStepper motor;
    short dir;
    int ena_pin;
    int speed;
    bool linear;
    int max_dist;
    bool enabled;
    bool go;
};

struct sensor {
    char symbol;
    int value;
    char* unit;
    char* name;
    SensorFunction update;
};

struct cmd {
	char symbol;
	short op;
	int arg;
};

void com();
void incer(void* s);
void get_temp(void* s);
void rander(void* s);
void establish_comm();
void execute();
void new_execute();
void linear_motion(motor* lm);
void controller_cmds(cmd command);
cmd parse_cmd(String command);

unsigned long temp_timer = 0;
String input = "";
char in;
int ctrl;
unsigned long lock = 0x0;
String config = "";
bool wait = false;

// Add a new line for a new motor :)
#define NUM_MOTORS 4
motor motors[NUM_MOTORS] = {
    {'A', "Motor 1", AccelStepper(1, PUL_1, DIR_1) , 1, ENA_1, 0, false, 0, false, false},
    {'B', "Motor 2", AccelStepper(1, PUL_2, DIR_2) , 1, ENA_2, 0, false, 0, false, false},
    {'C', "Motor 3", AccelStepper(1, PUL_3, DIR_3) , 1, ENA_3, 0, false, 0, false, false},
    {'D', "Motor 4", AccelStepper(1, PUL_4, DIR_4) , 1, ENA_4, 0, false, 0, false, false},
};

#define NUM_SENSORS 3
sensor sensors[NUM_SENSORS] = {
    {'T', 0, "C", "Temperature", get_temp},
    {'I', 0, "...", "Incrementor", incer},
    {'R', 0, "?", "Random", rander},
};

// Establishes ocnnection to control program and sends config
void establish_comm() {
	while (true) {
		if (SerialUSB.available())
		{
			lock = SerialUSB.parseInt();
			SerialUSB.flush();
			if (lock == PING) {
				break;
			}
			delay(200);
			// SerialUSB.println("hello there");
		}
	}
	SerialUSB.print(PONG);
	for (int i = 0; i < NUM_MOTORS; ++i)
	{
		config += ';';
		config += motors[i].symbol;
		config += ',';
		config += motors[i].name;
	}
	config += '&';
	for (int i = 0; i < NUM_SENSORS; ++i)
	{
		config += ';';
		config += sensors[i].symbol;
		config += ',';
		config += sensors[i].unit;
		config += ',';
		config += sensors[i].name;

	}
	SerialUSB.println(config);
	temp_timer = millis();
}

void setup() {

	for (int i = 0; i < NUM_MOTORS; ++i) {
		motors[i].motor.setMaxSpeed(64000);
		motors[i].motor.setAcceleration(500.0);
		motors[i].motor.setSpeed(0);
		motors[i].motor.setEnablePin(motors[i].ena_pin);
		motors[i].motor.setPinsInverted(true, false, true);
		motors[i].motor.disableOutputs();
	}

	SerialUSB.begin(9600);

	establish_comm();
}

/*
	The next three functions are examples of functions to update sensor values
	The function must return void and take a void* as a parameter
	The void* parameter should point to an instance of a sensor struct
	The function should update the value in the sensor struct
	To assign the new value the void* must be cast to a sensor*
*/

void rander(void* s) {
	((sensor*)(s))->value = float(random(0, 1000));
}

void get_temp(void* s) {
	float sen = analogRead(TMP);
	float voltage = sen * (5.0 / 1023.0);
	float I = voltage / 100;
	float VRx = 5 - voltage;
	float Rx = (VRx / I) - 10.49;
	float r = float(random(0, 100))/10000;
	((sensor*)(s))->value = ((Rx - 100.0) * (50.0 - 0.0) / (119.73 - 100.00) + 0.0) + r;
}

void incer(void* s) {
	((sensor*)(s))->value++;
}

void update_values(sensor* sensors) {
	for (int i = 0; i < NUM_SENSORS; ++i)
	{
		sensors[i].update((void*)&sensors[i]);
	}
}

cmd parse_cmd(String command) {
	String p[3] = {"", "0", "-1"};
	cmd parsed = {'\0', 0, -1};
	int from = 1;
	int to = 0;
	for (int i = 0; i < 3; ++i)
	{
		to = command.indexOf(';', from);
		if (to == -1) {
			to = command.length();
		}
		p[i] = command.substring(from, to);
		from = to+1;
	}
	parsed.symbol = p[0][0];
	parsed.op = p[1].toInt();
	parsed.arg = p[2].toInt();
	return parsed;
}

void linear_motion(motor* lm) {

	if (!lm->go) {
		lm->motor.run();
		return;
	}

	if (lm->motor.distanceToGo() == 0) {
		if (lm->motor.currentPosition() == 0) {
			lm->motor.moveTo(lm->max_dist);
		} else {
			lm->motor.moveTo(0);
		}
	}
	lm->motor.run();
}

void controller_cmds(cmd command) {
	if (command.op == -69) {
		String out = "";
		for (int i = 0; i < NUM_MOTORS; ++i)
		{
			out += ';';
			out += motors[i].symbol;
			out += ',';
			out += motors[i].speed;
			out += ',';
			out += motors[i].dir;
			out += ',';
			out += motors[i].linear;
			out += ',';
			out += motors[i].enabled;
			out += ',';
			out += motors[i].go;
		}
		SerialUSB.println(out);
	}
	if (command.op == -42) {
		wait = true;
	}
}

/*
	 0: PARSE_ERROR
	-1: ON
	-2: OFF
	-3: speed *
	-4: forward
	-5: reverse
	-6: linear
	-7: zero
	-8: max
	-9: step *
	-10: maxspeed
	-11: acceleration
	-12: go/stop
*/
void new_execute() {
	if (input == String(PING)) {
		wait = false;
		SerialUSB.println(String(PONG) + config + "&REC");
		temp_timer = millis() + 1000;
		return;
	}
	cmd split = parse_cmd(input);
	if (split.symbol == '0') {
		controller_cmds(split);
	}

	int m_idx = -1;
	for (int i = 0; i < NUM_MOTORS; ++i) {
		if (motors[i].symbol == split.symbol) {
			m_idx = i;
		}
	}
	if (m_idx == -1)
		return;

	switch(split.op) {
		case -1:
			motors[m_idx].motor.enableOutputs();
			motors[m_idx].enabled = true;
			break;
		case -2:
			motors[m_idx].motor.disableOutputs();
			motors[m_idx].go = false;
			motors[m_idx].enabled = false;
			break;
		case -3:
			motors[m_idx].motor.setSpeed(split.arg * motors[m_idx].dir);
			motors[m_idx].speed = split.arg;
			break;
		case -4:
			motors[m_idx].dir = 1;
			motors[m_idx].motor.setSpeed(motors[m_idx].speed * motors[m_idx].dir);
			break;
		case -5:
			motors[m_idx].dir = -1;
			motors[m_idx].motor.setSpeed(motors[m_idx].speed * motors[m_idx].dir);
			break;
		case -6:
			motors[m_idx].linear = !motors[m_idx].linear;
			motors[m_idx].motor.setCurrentPosition(0);
			motors[m_idx].max_dist = 0;
			motors[m_idx].go = false;
			if (!motors[m_idx].linear) {
				motors[m_idx].motor.setSpeed(motors[m_idx].speed * motors[m_idx].dir);
			}
			break;
		case -7:
			motors[m_idx].max_dist -= motors[m_idx].motor.currentPosition();
			motors[m_idx].motor.setCurrentPosition(0);
			motors[m_idx].speed = 0;
			break;
		case -8:
			motors[m_idx].max_dist = motors[m_idx].motor.currentPosition();
			break;
		case -9:
			motors[m_idx].motor.move(split.arg);
			break;
		case -10:
			motors[m_idx].motor.setMaxSpeed(split.arg);
			break;
		case -11:
			motors[m_idx].motor.setAcceleration(split.arg);
			break;
		case -12:
			if (motors[m_idx].linear && motors[m_idx].enabled)
				motors[m_idx].go = !motors[m_idx].go;
			break;
		default:
			break;
	}
	return;
}

void loop() {
	for (int i = 0; i < NUM_MOTORS; ++i)
	{
		if (motors[i].linear) {
			linear_motion(&motors[i]);
		} else {
			motors[i].motor.runSpeed();
		}
	}

	if (SerialUSB.available()) {
		in = SerialUSB.read();
		if (in == '\n') { 
			// com();
			new_execute();
			input = "";
		} else {
			input += in;
		}
	}   

	if (millis() - temp_timer > INTERVAL) {
		update_values(sensors);
		temp_timer = millis();
		if (wait) {
			return;
		}
		String out = "";
		for (int i = 0; i < NUM_SENSORS; ++i)
		{
			out += ';';
			out += sensors[i].symbol;
			out += sensors[i].value;
		}
		SerialUSB.println(out);		
	}
}