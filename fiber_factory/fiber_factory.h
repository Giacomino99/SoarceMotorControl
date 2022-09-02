#include <AccelStepper.h>
#define TMP A0

typedef void (*SensorFunction) (void* s);

struct MotorData {
    char* name;
    AccelStepper motor;
    uint16_t ena_pin, speed, max_dist, acceleration;
    int16_t  dir;
    bool linear, enabled, go;
};

struct Sensor {
    char symbol;
    char* unit;
    char* name;
    SensorFunction update;
    int32_t value;
};

void new_execute(uint16_t m_idx, uint16_t op, int16_t arg);
void linear_motion(MotorData* lm);
void controller_cmds(uint16_t op, int16_t arg);
void establish_comm();
void update_values(Sensor* sensors);
void new_comm(void);

void rander(void* s);
void get_temp(void* s);
void incer(void* s);

void rander(void* s) {
    ((Sensor*)(s))->value = (int32_t)random(-1000, 1000);
}

void get_temp(void* s) {
    ((Sensor*)(s))->value = analogRead(TMP);
}

void incer(void* s) {
    ((Sensor*)(s))->value++;
}