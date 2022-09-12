#include <AccelStepper.h>
#include "fiber_factory.h"

#define SERIAL_PROTO Serial

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

const uint32_t PING = 0XABADBABE;
const uint32_t PONG  = 0XB16B00B5;

const uint16_t DEFAULT_ACCEL = 2000;
const uint16_t DEFAULT_MAX = 32000;

uint16_t MASKS[16];
uint32_t lock = 0x0;
uint8_t* config;
uint16_t conf_len = 0;
bool wait = false;

#define NUM_SENSORS 3
#define NUM_MOTORS 4

MotorData motors[NUM_MOTORS] = {
    {"Motor 1", AccelStepper(1, PUL_1, DIR_1), ENA_1},
    {"Motor 2", AccelStepper(1, PUL_2, DIR_2), ENA_2},
    {"Motor 3", AccelStepper(1, PUL_3, DIR_3), ENA_3},
    {"Motor 4", AccelStepper(1, PUL_4, DIR_4), ENA_4},
};

Sensor sensors[NUM_SENSORS] = {
    {'T', "C", "Temperature", get_temp, 0},
    {'I', "...", "Incrementor", incer, 0},
    {'R', "?", "Random", rander, 0},
};

void setup() {
    // Precalculate bitmasks
    MASKS[0] = 1;
    for(uint8_t i = 1; i < 16; ++i) {
        MASKS[i] = MASKS[i-1]*2;
    }

    for (uint16_t i = 0; i < NUM_MOTORS; ++i) {
        motors[i].motor.setEnablePin(motors[i].ena_pin);
        motors[i].motor.disableOutputs();
        motors[i].motor.setMaxSpeed(DEFAULT_MAX);
        motors[i].motor.setAcceleration(DEFAULT_ACCEL);
        motors[i].motor.setSpeed(0);
        // motors[i].motor.setPinsInverted(true, false, true);

        motors[i].dir = 1;
        motors[i].acceleration = 2000;
    }
    gen_config();
    SERIAL_PROTO.begin(115200);
    // SERIAL_PROTO.setTimeout(10);
    establish_comm();
}

void gen_config(void) {
    conf_len = 6;
    for (uint8_t i = 0; i < NUM_MOTORS; ++i)
    {
        conf_len += strlen(motors[i].name) + 1;
    }

    for (uint8_t i = 0; i < NUM_SENSORS; ++i)
    {
        conf_len += strlen(sensors[i].name) + 1;
        conf_len += strlen(sensors[i].unit) + 1;
    }

    config = (uint8_t*)malloc(conf_len);

    *(uint16_t*)(config) = DEFAULT_MAX;
    *(uint16_t*)(config+2) = DEFAULT_ACCEL;
    *(uint8_t*)(config+4) = NUM_MOTORS;
    *(uint8_t*)(config+5) = NUM_SENSORS;

    uint16_t idx = 6;
    for (uint8_t i = 0; i < NUM_MOTORS; ++i)
    {
        uint16_t name_len = strlen(motors[i].name) + 1;
        memcpy(config+idx, motors[i].name, name_len);
        idx += name_len;
    }

    for (uint8_t i = 0; i < NUM_SENSORS; ++i)
    {
        uint16_t sname_len = strlen(sensors[i].name) + 1;
        uint16_t unit_len = strlen(sensors[i].unit) + 1;
        memcpy(config+idx, sensors[i].name, sname_len);
        idx += sname_len;
        memcpy(config+idx, sensors[i].unit, unit_len);
        idx += unit_len;
    }
}

void establish_comm() {
    while (true) {
        if (SERIAL_PROTO.available())
        {
            SERIAL_PROTO.readBytes((byte*)(&lock), 4);
            if (lock == PING) {
                break;
            }
            delay(400);
        }
    }
    SERIAL_PROTO.write((byte*)&PONG, 4);
    SERIAL_PROTO.write(config, conf_len);
}

void update_values(Sensor* sensors) {
    for (uint16_t i = 0; i < NUM_SENSORS; ++i)
    {
        sensors[i].update((void*)&sensors[i]);
    }
}

// [16 Bits - 1 per motor] [16 Bits - OP Code] [16 Bits - ARG]
void new_comm(void) {
    byte inp[sizeof(uint16_t)*3] = {0,0,0,0,0,0};
    SERIAL_PROTO.readBytes(inp, 6);

    uint32_t check = *((uint32_t*)(inp));
    uint16_t mtr = *((uint16_t*)(inp));
    uint16_t op = *((uint16_t*)(inp+2));
    int16_t arg = *((int16_t *)(inp+4));

    if (mtr == 0) {
        controller_cmds(op, arg);
    }

    if (check == PING) {
        wait = false;
        SERIAL_PROTO.write((byte*)&PONG, 4);
        SERIAL_PROTO.write(config, conf_len);
        SERIAL_PROTO.write((byte*)&PONG, 4);
        return;
    }

    for(uint16_t i = 0; i < NUM_MOTORS; ++i) {
        if(mtr & MASKS[i]) {
            new_execute(i, op, arg);
        }
    }
}

void controller_cmds(uint16_t op, int16_t arg) {
    switch(op) {
        case 77:
            update_values(sensors);
            if (wait) {
                return;
            }
            uint8_t s_out[NUM_SENSORS * 4];
            for (uint16_t i = 0; i < NUM_SENSORS; ++i)
            {
                *(int32_t*)(s_out+(i*4)) = sensors[i].value;
            }
            SERIAL_PROTO.write(s_out, NUM_SENSORS * 4);   
            break;

        case 69:
            for (uint8_t i = 0; i < NUM_MOTORS; ++i)
            {
                uint8_t out[10];
                out[0] = motors[i].enabled;
                out[1] = motors[i].dir + 1;
                out[2] = motors[i].linear;
                out[3] = motors[i].go;
                *(uint16_t*)(out+4) = motors[i].speed;
                *(uint16_t*)(out+6) = motors[i].acceleration;
                uint16_t ms = (uint16_t)motors[i].motor.maxSpeed();
                *(uint16_t*)(out+8) = ms;
                SERIAL_PROTO.write(out, 10);
            }
            break;

        case 42:
            wait = true;
            break;
    }
}

void new_execute(uint16_t m_idx, uint16_t op, int16_t arg) {

    switch(op) {
        case 1:
            motors[m_idx].motor.enableOutputs();
            motors[m_idx].enabled = true;
            break;
        case 2:
            motors[m_idx].motor.disableOutputs();
            motors[m_idx].enabled = false;
            motors[m_idx].go = false;
            if (motors[m_idx].linear) {
                motors[m_idx].motor.setSpeed(0);
                motors[m_idx].motor.moveTo(motors[m_idx].motor.currentPosition());
            }
            break;
        case 3:
            motors[m_idx].speed = arg;
            if (!motors[m_idx].linear)
                motors[m_idx].motor.setSpeed(arg * motors[m_idx].dir);
            break;
        case 4:
            motors[m_idx].dir = 1;
            if (!motors[m_idx].linear)
                motors[m_idx].motor.setSpeed(motors[m_idx].speed * motors[m_idx].dir);
            break;
        case 5:
            motors[m_idx].dir = -1;
            if (!motors[m_idx].linear)
                motors[m_idx].motor.setSpeed(motors[m_idx].speed * motors[m_idx].dir);
            break;
        case 6:
            motors[m_idx].linear = !motors[m_idx].linear;
            motors[m_idx].go = false;
            motors[m_idx].max_dist = 0;
            motors[m_idx].motor.setCurrentPosition(0);
            if (!motors[m_idx].linear) //Restore speed
                motors[m_idx].motor.setSpeed(motors[m_idx].speed * motors[m_idx].dir);
            break;

        case 7:
            //max_dist was set relative to old zero, offet accordingly
            motors[m_idx].max_dist -= motors[m_idx].motor.currentPosition();
            motors[m_idx].motor.setCurrentPosition(0);
            break;
        case 8:
            motors[m_idx].max_dist = motors[m_idx].motor.currentPosition();
            break;
        case 9:
            motors[m_idx].motor.move(arg);
            break;
        case 10:
            motors[m_idx].motor.setMaxSpeed(arg);
            break;
        case 11:
            motors[m_idx].acceleration = arg;
            motors[m_idx].motor.setAcceleration(arg);
            break;
        case 12:
            if (motors[m_idx].linear && motors[m_idx].enabled)
                motors[m_idx].go = !motors[m_idx].go;
            else
                motors[m_idx].go = false;
            break;
        default:
            break;
    }
    return;
}

void linear_motion(MotorData* lm) {

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

void loop() {

    for (uint16_t i = 0; i < NUM_MOTORS; ++i)
    {
        if (!motors[i].enabled)
            continue;

        if (motors[i].linear) {
            linear_motion(&motors[i]);
        } else {
            motors[i].motor.runSpeed();
        }
    }

    if (SERIAL_PROTO.available())
        new_comm();
}