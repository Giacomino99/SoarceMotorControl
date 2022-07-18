
#include <AccelStepper.h>
// #include <OneWire.h>
// #include <DallasTemperature.h>
// #include <NonBlockingDallas.h>

#define PUL_1 8
#define DIR_1 7
#define ENA_1 6

#define PUL_2 4
#define DIR_2 3
#define ENA_2 2

#define TMP A0
#define INTERVAL 500

typedef void (*SensorFunction) (void* s);

struct motor {
    char symbol;
    char* name;
    AccelStepper motor;
    bool dir;
    int ena_pin;
};


struct sensor {
    char symbol;
    float value;
    char* unit;
    char* name;
    SensorFunction update;
};

unsigned long temp_timer = 0;
float temp = 0;
String input = "";
char in;
int ctrl;
unsigned long lock = 0x0;
String config = "";

void com();
void incer(void* s);
void get_temp(void* s);
void rander(void* s);
void establish_comm();
void execute();

#define NUM_MOTORS 2
motor motors[NUM_MOTORS] = {
    {'A', "The First Motor", AccelStepper(1, PUL_1, DIR_1) , true, ENA_1},
    {'B', "The Second Motor", AccelStepper(1, PUL_2, DIR_2) , true, ENA_2},
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
        if (Serial.available())
        {
            lock = Serial.parseInt();
            Serial.flush();
            if (lock == 0xABADBABE) {
                break;
            }
            delay(200);
            // Serial.println("hello there");
        }
    }
    Serial.print(0XB16B00B5);
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
    config += '\n';
    Serial.print(config);
    temp_timer = millis();
}

void setup() {
    
    for (int i = 0; i < NUM_MOTORS; ++i) {
        motors[i].motor.setMaxSpeed(64000);
        motors[i].motor.setAcceleration(200.0);
        motors[i].motor.setSpeed(0);
        motors[i].motor.setEnablePin(motors[i].ena_pin);
        motors[i].motor.disableOutputs();
    }

    Serial.begin(19200);

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

// reads serial input. Identifies the motor that the command if for
void com() {
    for (int i = 0; i < NUM_MOTORS; ++i)
    {
        if (motors[i].symbol == input[0])
        {
            execute(&motors[i].motor);
            return;
        }
    }
    if (input.toInt() == 0xABADBABE)
    {
        Serial.print(0xB16B00B5);
        Serial.print(config);
    }
}

// executes the command stored in input on the given motor
void execute(AccelStepper* sel_motor) {
    ctrl = input.substring(1).toInt();
    if (ctrl == -4) {
        sel_motor->disableOutputs();
    }
    else if (ctrl == -1) {
        sel_motor->enableOutputs();
    }
    else if (ctrl == -2) {
        if (sel_motor->speed() < 0) {
            sel_motor->setSpeed(sel_motor->speed()*-1);
        }
    }
    else if (ctrl == -3) {
        if (sel_motor->speed() > 0) {
            sel_motor->setSpeed(sel_motor->speed()*-1);
        }
    }
    else {
        if (sel_motor->speed() < 0) { ctrl = ctrl * -1; }
        sel_motor->setSpeed(ctrl);
    }
}

void loop() {
    for (int i = 0; i < NUM_MOTORS; ++i)
    {
        motors[i].motor.runSpeed();
    }

    if (Serial.available()) {
        in = Serial.read();
        if (in == '\n') {
            com();
            input = "";
        } else {
            input += in;
        }
    }   

    if (millis() - temp_timer > INTERVAL) {
        update_values(sensors);
        String out = "";
        for (int i = 0; i < NUM_SENSORS; ++i)
        {
            out += ';';
            out += sensors[i].symbol;
            out += sensors[i].value;
        }
        Serial.println(out);
        temp_timer = millis();
    }
}
